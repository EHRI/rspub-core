#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

import logging

import sys

from resync import Resource

from rspub.core.audit import Audit
from rspub.core.rs_paras import RsParameters
from rspub.core.transport import ResourceAuditor


@unittest.skip("Run only when configuration DEFAULT has been properly executed.")
class TestResourceAuditor(unittest.TestCase):
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

    def test_generators(self):
        paras = RsParameters(config_name="DEFAULT")
        raud = ResourceAuditor(paras)
        generator = raud.get_generator(all_resources=False)
        for resource, src, relpath in generator():
            self.assertEquals(Resource, type(resource))

        generator = raud.get_generator(all_resources=True)
        for resource, src, relpath in generator():
            self.assertEquals(Resource, type(resource))
