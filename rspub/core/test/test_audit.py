#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

import logging

import sys

from rspub.core.audit import Audit
from rspub.core.rs_paras import RsParameters


@unittest.skip("Run only when configuration DEFAULT has been properly executed.")
class TestAudit(unittest.TestCase):
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

    def test_run_audit(self):
        paras = RsParameters(config_name="DEFAULT")
        audit = Audit(paras)
        audit.run_audit()