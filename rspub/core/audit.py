#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import tempfile
from enum import Enum
from glob import glob

import requests
from resync import ResourceList
from resync.sitemap import Sitemap

from rspub.core.transport import ResourceAuditor
from rspub.util import defaults
from rspub.util.observe import ObserverInterruptException

LOG = logging.getLogger(__name__)

class AuditEvent(Enum):
    """
    :samp:`Events fired by {Transport}`

    All events are broadcast in the format::

        [inform][confirm](source, event, **kwargs)

    where ``source`` is the calling instance, ``event`` is the relevant event and ``**kwargs`` hold relevant
    information about the event.
    """
    test_resource_uri = 1
    """
    ``1`` ``confirm`` :samp:`A resource uri is being tested`
    """

    test_sitemap_uri = 2
    """
    ``2`` ``confirm`` :samp:`A sitemap uri is being tested`
    """

    resource_uri_ok = 5
    """
    ``5`` ``inform`` :samp:`A resource uri was found`
    """

    sitemap_uri_ok = 6
    """
    ``6`` ``inform`` :samp:`A sitemap uri was found`
    """

    resource_uri_404 = 10
    """
    ``10`` ``inform`` :samp:`A resource uri was not found`
    """

    sitemap_uri_404 = 11
    """
    ``11`` ``inform`` :samp:`A sitemap uri was not found`
    """

    resource_checksum_error = 15
    """
    ``15`` ``inform`` :samp:`Local and remote resource have different checksums`
    """

    sitemap_checksum_error = 16
    """
    ``16`` ``inform`` :samp:`Local and remote sitemap have different checksums`
    """

    audit_global_error = 20
    """
    ``20`` ``inform`` :samp:`A global error occurred`
    """

    audit_start = 30
    """
    ``30`` ``inform`` :samp:`Audit started`
    """

    audit_end = 31
    """
    ``31`` ``inform`` :samp:`Audit ended`
    """


class Audit(ResourceAuditor):

    def __init__(self, paras):
        ResourceAuditor.__init__(self, paras)
        self.count_resources = 0
        self.count_resources_uri_ok = 0
        self.count_resources_uri_404 = 0
        self.count_resources_checksum_error = 0

        self.count_sitemaps = 0
        self.count_sitemaps_uri_ok = 0
        self.count_sitemaps_uri_404 = 0
        self.count_sitemaps_checksum_error = 0

        self.count_global_errors = 0

    def __reset_counts(self):
        self.count_resources = 0
        self.count_resources_uri_ok = 0
        self.count_resources_uri_404 = 0
        self.count_resources_checksum_error = 0

        self.count_sitemaps = 0
        self.count_sitemaps_uri_ok = 0
        self.count_sitemaps_uri_404 = 0
        self.count_sitemaps_checksum_error = 0

        self.count_global_errors = 0

    def run_audit(self, all_resources=False):
        self.__reset_counts()
        self.observers_inform(self, AuditEvent.audit_start, all_resources=all_resources)
        try:
            session = requests.Session()
            self.audit_resources(session, all_resources)
            self.audit_sitemaps(session)
        except Exception as err:
            LOG.exception("Error while auditing")
            self.count_global_errors += 1
            self.observers_inform(self, AuditEvent.audit_global_error, exception=str(err))
        finally:
            self.observers_inform(self, AuditEvent.audit_end,
                                  count_resources=self.count_resources,
                                  count_resources_uri_ok=self.count_resources_uri_ok,
                                  count_resources_uri_404=self.count_resources_uri_404,
                                  count_resources_checksum_error=self.count_resources_checksum_error,
                                  count_sitemaps=self.count_sitemaps,
                                  count_sitemaps_uri_ok=self.count_sitemaps_uri_ok,
                                  count_sitemaps_uri_404=self.count_sitemaps_uri_404,
                                  count_sitemaps_checksum_error=self.count_sitemaps_checksum_error,
                                  count_global_errors=self.count_global_errors)

    def audit_sitemaps(self, session):
        with tempfile.TemporaryDirectory(prefix="rspub.core.audit.resources_") as tmpdirname:
            resourcelist_files = sorted(glob(self.paras.abs_metadata_path("resourcelist_*.xml")))
            for filename in resourcelist_files:
                self.do_audit_sitemap(session, tmpdirname, filename)

            changelist_files = sorted(glob(self.paras.abs_metadata_path("changelist_*.xml")))
            for filename in changelist_files:
                self.do_audit_sitemap(session, tmpdirname, filename)

            filename = self.paras.abs_metadata_path("capabilitylist.xml")
            self.do_audit_sitemap(session, tmpdirname, filename)

            filename = self.paras.abs_description_path()
            self.do_audit_sitemap(session, tmpdirname, filename, uri=self.paras.description_url())

    def do_audit_sitemap(self, session, tmpdirname, filename, uri = None, chunk_size=1024):
        if uri is None:
            uri = self.paras.uri_from_path(filename)
        if not self.observers_confirm(self, AuditEvent.test_sitemap_uri, uri=uri):
            raise ObserverInterruptException("Process interrupted on AuditEvent.test_sitemap_uri")
        self.count_sitemaps += 1
        try:
            response = session.get(uri, stream=True)
            if response.status_code == requests.codes.ok:
                basename = os.path.basename(filename)
                new_file = os.path.join(tmpdirname, basename)
                with open(new_file, 'wb') as fd:
                    for chunk in response.iter_content(chunk_size):
                        fd.write(chunk)

                md5_local = defaults.md5_for_file(filename)
                md5_remote = defaults.md5_for_file(new_file)
                if md5_local != md5_remote:
                    LOG.info("md5 not equal: %s" % uri)
                    self.count_sitemaps_checksum_error += 1
                    self.observers_inform(self, AuditEvent.sitemap_checksum_error, uri=uri,
                                          count_checksum_error=self.count_sitemaps_checksum_error)
                else:
                    self.count_sitemaps_uri_ok += 1
                    self.observers_inform(self, AuditEvent.sitemap_uri_ok, uri=uri,
                                          count_ok=self.count_sitemaps_uri_ok)
                os.remove(new_file)

            else:
                LOG.info("Sitemap not found: %s" % uri)
                self.count_sitemaps_uri_404 += 1
                self.observers_inform(self, AuditEvent.sitemap_uri_404, uri=uri,
                                      count_404=self.count_sitemaps_uri_404)

        except Exception as err:
            LOG.exception("Error while trying to audit %s" % uri)
            self.count_global_errors += 1
            self.observers_inform(self, AuditEvent.audit_global_error, exception=str(err))

    def audit_resources(self, session, all_resources=False):
        generator = self.get_generator(all_resources)
        with tempfile.TemporaryDirectory(prefix="rspub.core.audit.resources_") as tmpdirname:
            for resource, path, relpath in generator():
                self.do_audit_resource(session, tmpdirname, resource, path)

    def do_audit_resource(self, session, tempdirname, resource, path, chunk_size=1024):
        if not self.observers_confirm(self, AuditEvent.test_resource_uri, uri=resource.uri):
            raise ObserverInterruptException("Process interrupted on AuditEvent.test_resource_uri")
        self.count_resources += 1
        try:
            response = session.get(resource.uri, stream=True)
            if response.status_code == requests.codes.ok:
                filename = os.path.basename(path)
                new_file = os.path.join(tempdirname, filename)
                with open(new_file, 'wb') as fd:
                    for chunk in response.iter_content(chunk_size):
                        fd.write(chunk)

                md5 = defaults.md5_for_file(new_file)
                if resource.md5 != md5:
                    LOG.info("md5 not equal: %s" % resource.uri)
                    self.count_resources_checksum_error += 1
                    self.observers_inform(self, AuditEvent.resource_checksum_error, uri=resource.uri,
                                          count_checksum_error=self.count_resources_checksum_error)
                else:
                    self.count_resources_uri_ok += 1
                    self.observers_inform(self, AuditEvent.resource_uri_ok, uri=resource.uri,
                                          count_ok=self.count_resources_uri_ok)
                os.remove(new_file)

            else:
                LOG.info("Resource not found: %s" % resource.uri)
                self.count_resources_uri_404 += 1
                self.observers_inform(self, AuditEvent.resource_uri_404, uri=resource.uri,
                                      count_404=self.count_resources_uri_404)
        except Exception as err:
            LOG.exception("Error while trying to audit %s" % resource.uri)
            self.count_global_errors += 1
            self.observers_inform(self, AuditEvent.audit_global_error, exception=str(err))


