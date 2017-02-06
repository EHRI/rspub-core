#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import paramiko
from scp import SCPClient

from rspub.core.rs_paras import RsParameters

# See also http://httpd.apache.org/docs/2.4/urlmapping.html

# scp -P 2222 test_data.zip user@localhost:/home/user
# on server: unzip -u test_data.zip

class Zipper(object):

    def __init__(self, paras):
        assert isinstance(paras, RsParameters)
        self.paras = paras

    def enabled(self):
        return self.paras.last_execution is not None

    def create_zip(self):
        if not self.enabled():
            return


class ScpTransport(object):

    def __init__(self, server, port, user, password):
        self.server = server
        self.port = port
        self.user = user
        self.password = password
        self.sshClient = None

    def create_ssh_client(self):
        if self.sshClient is None:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.server, self.port, self.user, self.password)
            self.sshClient = client
        return self.sshClient

    def scp_put(self, files):
        ssh = self.create_ssh_client()
        scp = SCPClient(ssh.get_transport())
        remote_path = "/home/user/"
        preserve_times = True
        scp.put(files=files, remote_path=remote_path, preserve_times=preserve_times)
