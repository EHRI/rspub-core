#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import re
from abc import ABCMeta, abstractmethod
from enum import Enum
from glob import glob

from model.config import Configuration
from model.rs_enum import Strategy, Capability
from pluggable.gate import ResourceGateBuilder
from resync import CapabilityList
from resync import Resource
from resync import SourceDescription
from resync.list_base_with_index import ListBaseWithIndex
from resync.sitemap import Sitemap
from util import defaults
from util.gates import PluggedInGateBuilder
from util.observe import Observable, ObserverInterruptException

LOG = logging.getLogger(__name__)

CLASS_NAME_RESOURCE_GATE_BUILDER = "ResourceGateBuilder"

WELL_KNOWN_PATH = os.path.join(".well-known", "resourcesync")


class ExecutorEvent(Enum):
    # # information events
    # common low-level events
    rejected_file = 1
    start_file_search = 2
    created_resource = 3

    # common mid-level events
    completed_document = 10

    # common high-level events
    found_changes = 20
    execution_start = 30
    execution_end = 31

    # # confirmation events
    clear_metadata_directory = 100


class SitemapData(object):

    def __init__(self, resource_count=0, ordinal=0, uri=None, path=None, capability_name=None,
                 document_saved=False):
        self.resource_count = resource_count
        self.ordinal = ordinal
        self.uri = uri
        self.path = path
        self.capability_name = capability_name
        self.document_saved = document_saved
        self.doc_start = None
        self.doc_end = defaults.w3c_now()

    def __str__(self):
        return "%s, resource_count: %d, ordinal: %d, saved: %s\n\t  uri: %s\n\t path: %s" \
               % (self.capability_name, self.resource_count, self.ordinal, str(self.document_saved),
                  self.uri, self.path)


class ExecutorParameters(object):

    def __init__(self, **kwargs):
        config = Configuration()
        self.resource_dir = self.__arg__("resource_dir", config.core_resource_dir(), **kwargs)
        self.metadata_dir = self.__arg__("metadata_dir", config.core_metadata_dir(), **kwargs)
        self.url_prefix = self.__arg__("url_prefix", config.core_url_prefix(), **kwargs)
        self.strategy = self.__arg__("strategy", config.core_strategy(), **kwargs)
        self.valid_strategy()  # check conversion for Strategy
        self.history_dir = self.__arg__("history_dir", config.core_history_dir(), **kwargs)
        self.plugin_dir = self.__arg__("plugin_dir", config.core_plugin_dir(), **kwargs)
        if self.plugin_dir is "":
            self.plugin_dir = None

        self.passes_resourcegate = self.__arg__("passes_resourcegate", None, **kwargs)
        if self.passes_resourcegate is None:
            default_builder = ResourceGateBuilder(self.abs_resource_dir(), self.abs_metadata_dir(), self.plugin_dir)
            gate_builder = PluggedInGateBuilder(CLASS_NAME_RESOURCE_GATE_BUILDER, default_builder, self.plugin_dir)
            self.passes_resourcegate = gate_builder.build_gate()

        self.max_items_in_list = self.__arg__("max_items_in_list", 50000, **kwargs)
        self.zfill_doc_count = self.__arg__("zfill_doc_count", 4, **kwargs)
        self.is_saving_pretty_xml = self.__arg__("is_saving_pretty_xml", True, **kwargs)
        self.is_saving_sitemaps = self.__arg__("is_saving_sitemaps", True, **kwargs)

        self.has_wellknown_at_root = self.__arg__("has_wellknown_at_root", True, **kwargs)

    @staticmethod
    def __arg__(name, default, **kwargs):
        value = default
        if name in kwargs and kwargs[name] is not None:
                value = kwargs[name]
        return value

    def abs_resource_dir(self):
        return defaults.sanitize_directory_path(self.resource_dir)

    def abs_metadata_dir(self):
        return os.path.join(self.abs_resource_dir(), self.metadata_dir)

    def abs_metadata_path(self, filename):
        return os.path.join(self.abs_metadata_dir(), filename)

    def valid_url_prefix(self):
        return defaults.sanitize_url_prefix(self.url_prefix)

    def uri_from_path(self, path):
        rel_path = os.path.relpath(path, self.abs_resource_dir())
        return self.valid_url_prefix() + defaults.sanitize_url_path(rel_path)

    def valid_strategy(self):
        return Strategy.strategy_for(self.strategy)


class Executor(Observable, ExecutorParameters, metaclass=ABCMeta):

    def __init__(self, **kwargs):
        Observable.__init__(self)
        ExecutorParameters.__init__(self, **kwargs)
        self.date_start_processing = None
        self.date_end_processing = None

    def execute(self, filenames: iter):
        self.date_start_processing = defaults.w3c_now()
        self.observers_inform(self, ExecutorEvent.execution_start, filenames=filenames, parameters=self.__dict__)
        if not os.path.exists(self.abs_metadata_dir()):
            os.makedirs(self.abs_metadata_dir())

        self.prepare_metadata_dir()
        sitemap_data_iter = self.generate_rs_documents(filenames)
        self.post_process_documents(sitemap_data_iter)
        self.date_end_processing = defaults.w3c_now()
        self.create_index(sitemap_data_iter)

        capabilitylist_data = self.create_capabilitylist()
        self.update_resource_sync(capabilitylist_data)

        self.observers_inform(self, ExecutorEvent.execution_end, new_sitemaps=sitemap_data_iter)

    # # Execution steps - start
    def prepare_metadata_dir(self):
        pass

    @abstractmethod
    def generate_rs_documents(self, filenames: iter) -> [SitemapData]:
        raise NotImplementedError

    def post_process_documents(self, sitemap_data_iter: iter):
        pass

    @abstractmethod
    def create_index(self, sitemap_data_iter: iter):
        raise NotImplementedError

    def create_capabilitylist(self) -> SitemapData:
        capabilitylist_path = os.path.join(self.metadata_dir, "capabilitylist.xml")
        if os.path.exists(capabilitylist_path) and self.is_saving_sitemaps:
            os.remove(capabilitylist_path)

        doc_types = ["resourcelist", "changelist", "resourcedump", "changedump"]
        capabilitylist = CapabilityList()
        for doc_type in doc_types:
            index_path = self.abs_metadata_path(doc_type + "-index.xml")
            if os.path.exists(index_path):
                capabilitylist.add(Resource(uri=self.uri_from_path(index_path), capability=doc_type))
            else:
                doc_list_files = sorted(glob(self.abs_metadata_path(doc_type + "_*.xml")))
                for doc_list in doc_list_files:
                    capabilitylist.add(Resource(uri=self.uri_from_path(doc_list), capability=doc_type))

        return self.finish_sitemap(-1, capabilitylist)

    def update_resource_sync(self, capabilitylist_data):
        src_desc_path = self.abs_metadata_path(WELL_KNOWN_PATH)
        well_known_dir = os.path.dirname(src_desc_path)
        os.makedirs(well_known_dir, exist_ok=True)

        src_description = SourceDescription()
        if os.path.exists(src_desc_path):
            src_description = self.read_sitemap(src_desc_path, src_description)

        src_description.add(Resource(uri=capabilitylist_data.uri, capability=Capability.capabilitylist.name),
                            replace=True)
        sitemap_data = SitemapData(len(src_description), -1, self.current_description_url(), src_desc_path,
                                   Capability.description.name)
        if self.is_saving_sitemaps:
            self.save_sitemap(src_description, src_desc_path)
            sitemap_data.document_saved = True

        self.observers_inform(self, ExecutorEvent.completed_document, document=src_description, **sitemap_data.__dict__)
        return sitemap_data
    # # Execution steps - end

    def clear_metadata_dir(self):
        ok = self.observers_confirm(self, ExecutorEvent.clear_metadata_directory, metadata_dir=self.abs_metadata_dir())
        if not ok:
            raise ObserverInterruptException("Process interrupted by observer: event: %s, metadata directory: %s"
                                             % (ExecutorEvent.clear_metadata_directory, self.abs_metadata_dir()))
        xml_files = glob(os.path.join(self.abs_metadata_dir(), "*.xml"))
        for xml_file in xml_files:
            os.remove(xml_file)

        wellknown = os.path.join(self.abs_metadata_dir(), WELL_KNOWN_PATH)
        if os.path.exists(wellknown):
            os.remove(wellknown)

    def resource_generator(self) -> iter:

        def generator(filenames: iter, count=0) -> [int, Resource]:
            for filename in filenames:
                if not isinstance(filename, str):
                    LOG.warn("Not a string: %s" % filename)
                    filename = str(filename)

                file = os.path.abspath(filename)
                if not os.path.exists(file):
                    LOG.warn("File does not exist: %s" % file)
                elif os.path.isdir(file):
                    for cr, rsc in generator(self.walk_directories(file), count=count):
                        yield cr, rsc
                        count = cr
                elif os.path.isfile(file):
                    if self.passes_resourcegate(file):
                        count += 1
                        path = os.path.relpath(file, self.abs_resource_dir())
                        uri = self.valid_url_prefix() + defaults.sanitize_url_path(path)
                        stat = os.stat(file)
                        resource = Resource(uri=uri, length=stat.st_size,
                                            lastmod=defaults.w3c_datetime(stat.st_ctime),
                                            md5=defaults.md5_for_file(file),
                                            mime_type=defaults.mime_type(file))
                        yield count, resource
                        self.observers_inform(self, ExecutorEvent.created_resource, resource=resource,
                                              count=count)
                    else:
                        self.observers_inform(self, ExecutorEvent.rejected_file, file=file)
                else:
                    LOG.warn("Not a regular file: %s" % file)

        return generator

    def walk_directories(self, *directories) -> [str]:
        for directory in directories:
            abs_dir = os.path.abspath(directory)
            self.observers_inform(self, ExecutorEvent.start_file_search, directory=abs_dir)
            for root, _directories, _filenames in os.walk(abs_dir):
                for filename in _filenames:
                    file = os.path.join(root, filename)
                    yield file

    def find_ordinal(self, capability):
        rs_files = sorted(glob(os.path.join(self.abs_metadata_dir(), capability + "_*.xml")))
        if len(rs_files) == 0:
            return -1
        else:
            filename = os.path.basename(rs_files[len(rs_files) - 1])
            digits = re.findall("\d+", filename)
            return int(digits[0]) if len(digits) > 0 else 0

    def format_ordinal(self, ordinal):
        # prepends '_' before zfill to distinguish between indexes (*list-index.xml) and regular lists (*list_001.xml)
        return "_" + str(ordinal).zfill(self.zfill_doc_count)

    def finish_sitemap(self, ordinal, sitemap, doc_start=None, doc_end=None) -> SitemapData:
        capability_name = sitemap.capability_name
        file_name = capability_name
        if sitemap.sitemapindex:
            file_name += "-index"
        elif ordinal >= 0:
            file_name += self.format_ordinal(ordinal)

        file_name += ".xml"

        path = self.abs_metadata_path(file_name)
        url = self.uri_from_path(path)
        sitemap.link_set(rel="up", href=self.current_rel_up_for(sitemap))
        sitemap_data = SitemapData(len(sitemap), ordinal, url, path, capability_name)
        sitemap_data.doc_start = doc_start
        sitemap_data.doc_end = doc_end if doc_end else defaults.w3c_now()

        if self.is_saving_sitemaps:
            sitemap.pretty_xml = self.is_saving_pretty_xml
            with open(path, "w") as sm_file:
                sm_file.write(sitemap.as_xml())
            sitemap_data.document_saved = True

        self.observers_inform(self, ExecutorEvent.completed_document, document=sitemap, **sitemap_data.__dict__)
        return sitemap_data

    def current_rel_up_for(self, sitemap):
        if sitemap.capability_name == Capability.capabilitylist.name:
            return self.current_description_url()
        else:
            return self.current_capabilitylist_url()

    def current_capabilitylist_url(self) -> str:
        path = self.abs_metadata_path("capabilitylist.xml")
        rel_path = os.path.relpath(path, self.abs_resource_dir())
        return self.valid_url_prefix() + defaults.sanitize_url_path(rel_path)

    def current_description_url(self):
        if self.has_wellknown_at_root:
            rel_path = WELL_KNOWN_PATH
        else:
            rel_path = self.abs_metadata_path(WELL_KNOWN_PATH)

        return self.valid_url_prefix() + defaults.sanitize_url_path(rel_path)

    def update_rel_index(self, index_url, path):
        sitemap = self.read_sitemap(path)
        sitemap.link_set(rel="index", href=index_url)
        self.save_sitemap(sitemap, path)

    def save_sitemap(self, sitemap, path):
        sitemap.pretty_xml = self.is_saving_pretty_xml
        with open(path, "w") as sm_file:
            sm_file.write(sitemap.as_xml())

    def read_sitemap(self, path, sitemap=None):
        if sitemap is None:
            sitemap = ListBaseWithIndex()
        with open(path, "r") as file:
            sm = Sitemap()
            sm.parse_xml(file, resources=sitemap)
        return sitemap
