#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:samp:`Transport resources and sitemaps to the web server`

"""
import logging
import os
import shutil
import tempfile
import urllib.parse
from glob import glob

import paramiko
from resync import ChangeList
from resync import ResourceList
from resync.list_base_with_index import ListBaseWithIndex
from resync.sitemap import Sitemap
from scp import SCPClient

from rspub.core.rs_paras import RsParameters

# See also http://httpd.apache.org/docs/2.4/urlmapping.html

# scp -P 2222 test_data.zip user@localhost:/home/user
# on server: unzip -u test_data.zip
from rspub.util.observe import Observable

LOG = logging.getLogger(__name__)


class TransportException(Exception):
    pass


class Transport(Observable):

    def __init__(self, paras):
        Observable.__init__(self)
        assert isinstance(paras, RsParameters)
        self.paras = paras
        self.sshClient = None

    def enabled(self):
        return self.paras.last_execution is not None

    def handle_resources(self, function, all_resources=False, include_description=True):
        with tempfile.TemporaryDirectory(prefix="rspub.core.transport_") as tmpdirname:
            LOG.info("Created temporary directory: %s" % tmpdirname)
            self.__copy_resources(tmpdirname, all_resources)
            self.__copy_metadata(tmpdirname)
            if include_description:
                self.__copy_description(tmpdirname)
            function(tmpdirname)

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

        return  all_resources

    def all_resources_generator(self):

        def generator():
            for resource in self.all_resources():
                path, relpath = self.__extract_paths(resource)
                yield path, relpath

        return  generator

    def last_resources_generator(self):

        def generator():
            for file_name in self.paras.last_sitemaps:
                listbase = ListBaseWithIndex()
                with open(file_name, "r", encoding="utf-8") as lb_file:
                    sm = Sitemap()
                    sm.parse_xml(lb_file, resources=listbase)
                for resource in listbase.resources:
                    if resource.change is None or not resource.change == "deleted":
                        path, relpath = self.__extract_paths(resource)
                        yield path, relpath

        return generator

    def __extract_paths(self, resource):
        relpath = os.path.relpath(resource.uri, self.paras.url_prefix)
        relpath = urllib.parse.unquote(relpath)
        path = os.path.join(self.paras.resource_dir, relpath)
        return path, relpath

    def __copy_file(self, relpath, src, tmpdirname):
        dest = os.path.join(tmpdirname, relpath)
        dirs = os.path.dirname(dest)
        os.makedirs(dirs, exist_ok=True)
        shutil.copy2(src, dest)

    def __copy_resources(self, tmpdirname, all_resources=False):
        if all_resources:
            LOG.debug("Creating generator for all resources.")
            generator = self.all_resources_generator()
        else:
            LOG.debug("Creating generator for last resources.")
            generator = self.last_resources_generator()
        for src, relpath in generator():
            self.__copy_file(relpath, src, tmpdirname)

    def __copy_metadata(self, tmpdirname):
        xml_files = glob(self.paras.abs_metadata_path("*.xml"))
        for xml_file in xml_files:
            relpath = os.path.relpath(xml_file, self.paras.resource_dir)
            self.__copy_file(relpath, xml_file, tmpdirname)

    def __copy_description(self, tmpdirname):
        desc_file = self.paras.abs_description_path()
        if not self.paras.has_wellknown_at_root:
            # description goes in metadata_dir
            dest = os.path.join(tmpdirname, self.paras.metadata_dir, ".well-known", "resourcesync")
        else:
            # description should go at server root. should be moved at server if not correct. keep 1 zip file.
            dest = os.path.join(tmpdirname, ".well-known", "resourcesync")
        dirs = os.path.dirname(dest)
        os.makedirs(dirs, exist_ok=True)
        shutil.copy2(desc_file, dest)

    #############
    def zip_resources(self, all_resources=False):
        self.handle_resources(self.function_zip, all_resources, include_description=True)

    def function_zip(self, tmpdirname):
        zip_name = os.path.splitext(self.paras.zip_filename)[0]
        zip_dir = os.path.dirname(self.paras.zip_filename)
        os.makedirs(zip_dir, exist_ok=True)
        shutil.make_archive(zip_name, 'zip', tmpdirname)
        LOG.info("Created zip archive: %s" % os.path.abspath(zip_name + ".zip"))

    #############
    # Password may not be needed with key-based authentication. See fi:
    # https://www.digitalocean.com/community/tutorials/how-to-configure-ssh-key-based-authentication-on-a-linux-server
    def scp_resources(self, all_resources=False, password="secret"):
        self.create_ssh_client(password)
        self.handle_resources(self.function_scp, all_resources,
                              include_description=not self.paras.has_wellknown_at_root)
        if self.paras.has_wellknown_at_root:
            files = self.paras.abs_description_path()
            # .well-known directory can only be made by root.
            # sudo mkdir .well-known
            # sudo chmod -R  a=rwx .well-known
            remote_path = self.paras.scp_document_root + ".well-known"
            self.scp_put(files, remote_path)

    def create_ssh_client(self, password):
        if self.sshClient is None:
            LOG.debug("Creating ssh client: server=%s, port=%d, user=%s" %
                      (self.paras.scp_server, self.paras.scp_port, self.paras.scp_user))
            self.sshClient = paramiko.SSHClient()
            self.sshClient.load_system_host_keys()
            self.sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.sshClient.connect(self.paras.scp_server, self.paras.scp_port, self.paras.scp_user, password)

    def function_scp(self, tmpdirname):
        files = tmpdirname + os.sep
        remote_path = self.paras.scp_document_root + self.paras.scp_document_path
        self.scp_put(files, remote_path)

    # files can be a single file, a directory, a list of files and/or directories.
    # mind that directories ending with a slash will transport the contents of the directory,
    # whereas directories not ending with a slash will transport the directory itself.
    def scp_put(self, files, remote_path):
        LOG.info("%s >>>> %s" % (files, remote_path))
        scp = SCPClient(self.sshClient.get_transport())
        preserve_times = True
        recursive = True  # Can be used both for sending a single file and a directory
        LOG.debug("Sending files: scp -P %d -r [files] %s@%s:%s" % (self.paras.scp_port, self.paras.scp_user,
                                                                    self.paras.scp_server, remote_path))
        scp.put(files=files, remote_path=remote_path, preserve_times=preserve_times, recursive=recursive)
