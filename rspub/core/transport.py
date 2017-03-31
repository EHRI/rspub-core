#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:samp:`Transport resources and sitemaps to the web server`

"""
import logging
import os
import shutil
import socket
import tempfile
import urllib.parse
from enum import Enum
from glob import glob

import paramiko
from resync import ChangeList
from resync import ResourceList
from resync.list_base_with_index import ListBaseWithIndex
from resync.sitemap import Sitemap
from scp import SCPClient, SCPException

from rspub.core.rs_paras import RsParameters
from rspub.util.observe import Observable, ObserverInterruptException

LOG = logging.getLogger(__name__)


class TransportEvent(Enum):
    """
    :samp:`Events fired by {Transport}`

    All events are broadcast in the format::

        [inform][confirm](source, event, **kwargs)

    where ``source`` is the calling instance, ``event`` is the relevant event and ``**kwargs`` hold relevant
    information about the event.
    """
    copy_resource = 1
    """
    ``1`` ``inform`` :samp:`A resource was copied to a temporary location`
    """

    copy_sitemap = 2
    """
    ``2`` ``inform`` :samp:`A sitemap was copied to a temporary location`
    """

    copy_file = 3
    """
    ``3`` ``confirm`` :samp:`Copy file confirm message with interrupt`
    """

    transfer_file = 4
    """
    ``4`` ``confirm`` :samp:`Transfer file confirm message with interrupt`
    """

    resource_not_found = 10
    """
    ``10`` ``inform`` :samp:`A resource was not found`
    """

    start_copy_to_temp = 15
    """
    ``15`` ``inform`` :samp:`Start copy resources and sitemaps to temporary directory`
    """

    zip_resources = 20
    """
    ``20`` ``inform`` :samp:`Start packaging resources and sitemaps`
    """

    scp_resources = 21
    """
    ``21`` ``inform`` :samp:`Start transfer of files with scp`
    """

    ssh_client_creation = 22
    """
    ``22`` ``inform`` :samp:`Trying to create ssh client`
    """

    scp_exception = 23
    """
    ``23`` ``inform`` :samp:`Encountered exception while transferring files with scp`
    """

    scp_progress = 24
    """
    ``24`` ``inform`` :samp:`Progress as defined by SCPClient`
    """

    scp_transfer_complete = 25
    """
    ``25`` ``inform`` :samp:`Transfer of one file complete`
    """

    transport_start = 30
    """
    ``30`` ``inform`` :samp:`Transport started`
    """

    transport_end = 31
    """
    ``31`` ``inform`` :samp:`Transport ended`
    """


class ResourceAuditorEvent(Enum):
    """
    :samp:`Events fired by {Transport}`

    All events are broadcast in the format::

        [inform](source, event, **kwargs)

    where ``source`` is the calling instance, ``event`` is the relevant event and ``**kwargs`` hold relevant
    information about the event.
    """
    site_map_not_found = 11
    """
    ``11`` inform`` :samp:`A sitemap was not found`
    """


class ResourceAuditor(Observable):

    def __init__(self, paras):
        Observable.__init__(self)
        assert isinstance(paras, RsParameters)
        self.paras = paras
        self.count_errors = 0

    def all_resources(self):
        all_resources = {}

        # search for resourcelists
        resourcelist_files = sorted(glob(self.paras.abs_metadata_path("resourcelist_*.xml")))
        for rl_file_name in resourcelist_files:
            resourcelist = ResourceList()
            with open(rl_file_name, "r", encoding="utf-8") as rl_file:
                sm = Sitemap()
                sm.parse_xml(rl_file, resources=resourcelist)

            all_resources.update({resource.uri: resource for resource in resourcelist.resources})

        # search for changelists
        changelist_files = sorted(glob(self.paras.abs_metadata_path("changelist_*.xml")))
        for cl_file_name in changelist_files:
            changelist = ChangeList()
            with open(cl_file_name, "r", encoding="utf-8") as cl_file:
                sm = Sitemap()
                sm.parse_xml(cl_file, resources=changelist)

            for resource in changelist.resources:
                if resource.change == "created" or resource.change == "updated":
                    all_resources.update({resource.uri: resource})
                elif resource.change == "deleted" and resource.uri in all_resources:
                    del all_resources[resource.uri]

        return all_resources

    def all_resources_generator(self):

        def generator():
            for resource in self.all_resources():
                path, relpath = self.extract_paths(resource)
                yield resource, path, relpath

        return generator

    def last_resources_generator(self):

        def generator():
            for file_name in self.paras.last_sitemaps:
                listbase = ListBaseWithIndex()
                if os.path.exists(file_name):
                    with open(file_name, "r", encoding="utf-8") as lb_file:
                        sm = Sitemap()
                        sm.parse_xml(lb_file, resources=listbase)
                    for resource in listbase.resources:
                        if resource.change is None or not resource.change == "deleted":
                            path, relpath = self.extract_paths(resource.uri)
                            yield resource, path, relpath
                else:
                    LOG.warning("Unable to read sitemap: %s" % file_name)
                    self.count_errors += 1
                    self.observers_inform(self, ResourceAuditorEvent.site_map_not_found, file=file_name)

        return generator

    def extract_paths(self, resource):
        relpath = os.path.relpath(resource, self.paras.url_prefix)
        relpath = urllib.parse.unquote(relpath)
        path = os.path.join(self.paras.resource_dir, relpath)

        return path, relpath

    def get_generator(self, all_resources):
        if all_resources:
            LOG.debug("Creating generator for all resources.")
            generator = self.all_resources_generator()
        else:
            LOG.debug("Creating generator for last resources.")
            generator = self.last_resources_generator()
        return generator


class Transport(ResourceAuditor):

    def __init__(self, paras):
        ResourceAuditor.__init__(self, paras)
        self.sshClient = None
        self.count_resources = 0
        self.count_sitemaps = 0
        self.count_transfers = 0

    def handle_resources(self, function, all_resources=False, include_description=True):
        self.observers_inform(self, TransportEvent.start_copy_to_temp)
        with tempfile.TemporaryDirectory(prefix="rspub.core.transport_") as tmpdirname:
            LOG.info("Created temporary directory: %s" % tmpdirname)
            self.__copy_resources(tmpdirname, all_resources)
            self.__copy_metadata(tmpdirname)
            if include_description:
                self.__copy_description(tmpdirname)
            function(tmpdirname)

    def __copy_file(self, relpath, src, tmpdirname):
        # LOG.debug("Copy file. relpath=%s src=%s" % (relpath, src))
        if not self.observers_confirm(self, TransportEvent.copy_file, filename=src):
            raise ObserverInterruptException("Process interrupted on TransportEvent.copy_file")
        dest = os.path.join(tmpdirname, relpath)
        dirs = os.path.dirname(dest)
        os.makedirs(dirs, exist_ok=True)
        shutil.copy2(src, dest)

    def __copy_resources(self, tmpdirname, all_resources=False):
        generator = self.get_generator(all_resources)
        for resource, src, relpath in generator():
            try:
                self.__copy_file(relpath, src, tmpdirname)
                self.count_resources += 1
                self.observers_inform(self, TransportEvent.copy_resource, file=src,
                                      count_resources=self.count_resources)
            except FileNotFoundError:
                LOG.exception("Unable to copy file %s", src)
                self.count_errors += 1
                self.observers_inform(self, ResourceAuditorEvent.resource_not_found, file=src)

    def __copy_metadata(self, tmpdirname):
        xml_files = glob(self.paras.abs_metadata_path("*.xml"))
        for xml_file in xml_files:
            relpath = os.path.relpath(xml_file, self.paras.resource_dir)
            try:
                self.__copy_file(relpath, xml_file, tmpdirname)
                self.count_sitemaps += 1
                self.observers_inform(self, TransportEvent.copy_sitemap, file=xml_file,
                                      count_sitemaps=self.count_sitemaps)
            except FileNotFoundError:
                LOG.exception("Unable to copy file %s", xml_file)
                self.count_errors += 1
                self.observers_inform(self, ResourceAuditorEvent.site_map_not_found, file=xml_file)

    def __copy_description(self, tmpdirname):
        desc_file = self.paras.abs_description_path()
        self.count_sitemaps += 1
        if not self.paras.has_wellknown_at_root:
            # description goes in metadata_dir
            dest = os.path.join(tmpdirname, self.paras.metadata_dir, ".well-known", "resourcesync")
        else:
            # description should go at server root. should be moved at server if not correct. keep 1 zip file.
            dest = os.path.join(tmpdirname, ".well-known", "resourcesync")
        dirs = os.path.dirname(dest)
        os.makedirs(dirs, exist_ok=True)
        try:
            shutil.copy2(desc_file, dest)
            self.observers_inform(self, TransportEvent.copy_sitemap, file=desc_file,
                                  count_sitemaps=self.count_sitemaps)
        except FileNotFoundError:
            LOG.exception("Unable to copy file %s", desc_file)
            self.count_errors += 1
            self.observers_inform(self, ResourceAuditorEvent.site_map_not_found, file=desc_file)

    def __reset_counts(self):
        self.count_resources = 0
        self.count_sitemaps = 0
        self.count_transfers = 0
        self.count_errors = 0

    #############
    def zip_resources(self, all_resources=False):
        self.__reset_counts()
        self.observers_inform(self, TransportEvent.transport_start, mode="zip sources", all_resources=all_resources)
        #
        self.handle_resources(self.__function_zip, all_resources, include_description=True)
        #
        self.observers_inform(self, TransportEvent.transport_end, mode="zip sources",
                              count_resources=self.count_resources, count_sitemaps=self.count_sitemaps,
                              count_transfers=self.count_transfers, count_errors=self.count_errors)

    def __function_zip(self, tmpdirname):
        if self.count_resources + self.count_sitemaps > 0:
            zip_name = os.path.splitext(self.paras.zip_filename)[0]
            zip_dir = os.path.dirname(self.paras.zip_filename)
            os.makedirs(zip_dir, exist_ok=True)
            self.observers_inform(self, TransportEvent.zip_resources, zip_file=self.paras.zip_filename)
            shutil.make_archive(zip_name, 'zip', tmpdirname)
            LOG.info("Created zip archive: %s" % os.path.abspath(zip_name + ".zip"))
        else:
            LOG.info("Nothing to zip, not creating archive")

    #############
    # Password may not be needed with key-based authentication. See fi:
    # https://www.digitalocean.com/community/tutorials/how-to-configure-ssh-key-based-authentication-on-a-linux-server
    def scp_resources(self, all_resources=False, password="secret"):
        self.__reset_counts()
        self.observers_inform(self, TransportEvent.transport_start, mode="scp sources", all_resources=all_resources)
        self.create_ssh_client(password)
        #
        try:
            if self.sshClient:
                if self.paras.has_wellknown_at_root:
                    include_description = False
                    self.count_sitemaps += 1
                else:
                    include_description = True

                self.handle_resources(self.__function_scp, all_resources, include_description=include_description)
                if self.paras.has_wellknown_at_root:
                    self.__send_wellknown()
        except Exception as err:
            LOG.exception("Error while transfering files with scp")
            self.count_errors += 1
            self.observers_inform(self, TransportEvent.scp_exception, exception=str(err))
        finally:
            self.observers_inform(self, TransportEvent.transport_end, mode="scp sources",
                                  count_resources=self.count_resources, count_sitemaps=self.count_sitemaps,
                                  count_transfers=self.count_transfers, count_errors=self.count_errors)

    def __send_wellknown(self):
        files = self.paras.abs_description_path()
        # .well-known directory can only be made by root.
        # sudo mkdir .well-known
        # sudo chmod -R  a=rwx .well-known
        # or if only one user copies to .well-known
        # sudo chown user:group .well-known/
        remote_path = self.paras.exp_scp_document_root + "/.well-known"
        try:
            self.scp_put(files, remote_path)
        except FileNotFoundError:
            LOG.exception("Unable to send file %s", files)
            self.count_errors += 1
            self.observers_inform(self, ResourceAuditorEvent.site_map_not_found, file=files)

    def create_ssh_client(self, password):
        if self.sshClient is None:
            LOG.debug("Creating ssh client: server=%s, port=%d, user=%s" %
                      (self.paras.exp_scp_server, self.paras.exp_scp_port, self.paras.exp_scp_user))
            self.observers_inform(self, TransportEvent.ssh_client_creation,
                                  server=self.paras.exp_scp_server,
                                  port=self.paras.exp_scp_port,
                                  user=self.paras.exp_scp_user)
            self.sshClient = paramiko.SSHClient()
            self.sshClient.load_system_host_keys()
            self.sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                self.sshClient.connect(self.paras.exp_scp_server, self.paras.exp_scp_port, self.paras.exp_scp_user, password)
            except paramiko.ssh_exception.AuthenticationException as err:
                LOG.exception("Not authorized")
                self.count_errors += 1
                self.observers_inform(self, TransportEvent.scp_exception, exception=str(err))
                self.sshClient = None
            except socket.gaierror as err:
                LOG.exception("Socket error")
                self.count_errors += 1
                self.observers_inform(self, TransportEvent.scp_exception, exception=str(err))
                self.sshClient = None
            except TimeoutError as err:
                LOG.exception("Timeout")
                self.count_errors += 1
                self.observers_inform(self, TransportEvent.scp_exception, exception=str(err))
                self.sshClient = None

    def __function_scp(self, tmpdirname):
        if self.count_resources + self.count_sitemaps > 0:
            files = tmpdirname + os.sep
            remote_path = self.paras.exp_scp_document_root + self.paras.server_path()
            self.scp_put(files, remote_path)
            LOG.info("Secure copied resources and metadata")
        else:
            LOG.info("Nothing to send, not transferring with scp to remote")

    # files can be a single file, a directory, a list of files and/or directories.
    # mind that directories ending with a slash will transport the contents of the directory,
    # whereas directories not ending with a slash will transport the directory itself.
    def scp_put(self, files, remote_path):
        LOG.info("%s >>>> %s" % (files, remote_path))
        if self.sshClient is None:
            raise RuntimeError("Missing ssh client: see Transport.create_ssh_client(password).")
        scp = SCPClient(transport=self.sshClient.get_transport(), progress=self.progress)
        preserve_times = True
        recursive = True  # Can be used both for sending a single file and a directory
        msg = "scp -P %d -r [files] %s@%s:%s" % (self.paras.exp_scp_port, self.paras.exp_scp_user,
                                                 self.paras.exp_scp_server, remote_path)
        LOG.debug("Sending files: " + msg)
        self.observers_inform(self, TransportEvent.scp_resources, command=msg)
        try:
            scp.put(files=files, remote_path=remote_path, preserve_times=preserve_times, recursive=recursive)
        except SCPException as err:
            LOG.exception("Error while transferring files")
            self.count_errors += 1
            self.observers_inform(self, TransportEvent.scp_exception, exception=str(err))

    def progress(self, filename, size, sent):
        # @param progress: callback - called with (filename, size, sent) during transfers
        # @type progress: function(string, int, int)
        # b'Draaiboek Hilvarenbeek Gelderakkers.doc' 241664 0
        # b'Draaiboek Hilvarenbeek Gelderakkers.doc' 241664 16384
        # ...
        # b'Draaiboek Hilvarenbeek Gelderakkers.doc' 241664 241664
        filestr = filename.decode()
        self.observers_inform(self, TransportEvent.scp_progress, filename=filestr, size=size, sent=sent)
        if sent == 0:
            if not self.observers_confirm(self, TransportEvent.transfer_file, filename=filename):
                raise ObserverInterruptException("Process interrupted on TransportEvent.transfer_file")
        if sent == size:
            self.count_transfers += 1
            self.observers_inform(self, TransportEvent.scp_transfer_complete,
                                  filename=filestr,
                                  count_resources=self.count_resources,
                                  count_sitemaps=self.count_sitemaps,
                                  count_transfers=self.count_transfers,
                                  percentage = self.count_transfers / (self.count_resources + self.count_sitemaps))




