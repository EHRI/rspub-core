#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import unittest

import logging

import sys

from rspub.core.importer import Importer
from rspub.core.rs_paras import RsParameters
from rspub.util.observe import EventLogger

CFG_FILE = "src/importer_test_on_nzandbak.cfg"


def precondition_remote_server_config(as_string=False):
    msg = "Ok"
    cfg_file = os.path.join(os.path.expanduser("~"), CFG_FILE)
    if not os.path.exists(cfg_file):
        msg = "Skip test: importertest configuration file does not exist: %s" % cfg_file
    if as_string:
        return msg
    else:
        return msg == "Ok"


@unittest.skipUnless(precondition_remote_server_config(), precondition_remote_server_config(as_string=True))
class TestImporter(unittest.TestCase):
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

    @unittest.skipUnless(precondition_remote_server_config(), precondition_remote_server_config(as_string=True))
    def test_scp_get(self):
        paras, password = self.read_parameters()
        importer = Importer(paras=paras, password=password)
        importer.register(EventLogger(logging_level=logging.INFO))
        importer.scp_get()

    def read_parameters(self):
        paras = RsParameters(config_name="DEFAULT")
        # configuration:
        cfg_file = os.path.join(os.path.expanduser("~"), CFG_FILE)
        with open(cfg_file) as cfg:
            line = cfg.readline()
        spup = line.split(",")
        paras.imp_scp_server = spup[0]
        paras.imp_scp_port = int(spup[1])
        paras.imp_scp_user = spup[2]
        password = spup[3]
        paras.imp_scp_remote_path = spup[4]
        paras.imp_scp_local_path = spup[5].strip()
        return paras, password