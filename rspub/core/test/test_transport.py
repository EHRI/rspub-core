#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import unittest

import logging

import sys

import time

from rspub.core.rs_paras import RsParameters
from rspub.core.transport import Transport

# test expects a configuration file with one line of text:
#       server,port,user,password,document_root,document_path
# password can be fake if key-based authentication is enabled.
# see: https://www.digitalocean.com/community/tutorials/how-to-configure-ssh-key-based-authentication-on-a-linux-server
CFG_FILE = "src/sender_test_on_zandbak.cfg"


def precondition_remote_server_config(as_string=False):
    msg = "Ok"
    cfg_file = os.path.join(os.path.expanduser("~"), CFG_FILE)
    if not os.path.exists(cfg_file):
        msg = "Skip test: sendertest configuration file does not exist: %s" % cfg_file
    if as_string:
        return msg
    else:
        return msg == "Ok"


class TestTransport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # logging:
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)

    @unittest.skip("Half-way implementation test")
    def test_handle_resources(self):
        paras = RsParameters(config_name="DEFAULT")
        trans = Transport(paras)
        trans.handle_resources(self.pauze_execution)

    def pauze_execution(self, tmpdirname):
        print(tmpdirname)
        time.sleep(60)

    def test_zip_resources(self):
        paras = RsParameters(config_name="DEFAULT")
        filename = os.path.splitext(paras.zip_filename)[0] + ".zip"
        if os.path.exists(filename):
            os.remove(filename)
        trans = Transport(paras)
        trans.zip_resources()
        self.assertTrue(os.path.exists(filename))

    @unittest.skipUnless(precondition_remote_server_config(), precondition_remote_server_config(as_string=True))
    def test_scp_resources(self):
        paras = RsParameters(config_name="DEFAULT")
        # configuration:
        cfg_file = os.path.join(os.path.expanduser("~"), CFG_FILE)
        with open(cfg_file) as cfg:
            line = cfg.readline()
        spup = line.split(",")
        paras.scp_server = spup[0]
        paras.scp_port = int(spup[1])
        paras.scp_user = spup[2]
        password = spup[3]
        paras.scp_document_root = spup[4]
        paras.scp_document_path = spup[5].strip()

        trans = Transport(paras)
        # if used with key-based authentication than 'password' is ignored
        trans.scp_resources(password=password)

