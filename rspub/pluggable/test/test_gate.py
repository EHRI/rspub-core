#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import unittest

from rspub.pluggable.gate import ResourceGateBuilder


class TestResourceGateBuilder(unittest.TestCase):

    def test_path_predicates(self):
        resource_dir = os.path.expanduser("~")
        builder = ResourceGateBuilder(resource_dir=resource_dir)
        includes = builder.build_includes([])
        pred = includes[0]
        # print(resource_dir)
        a_resource = os.path.join(resource_dir, "file.txt")
        self.assertTrue(pred(a_resource))

        another_resource = os.path.join(os.path.dirname(resource_dir), "file.txt")
        self.assertFalse(pred(another_resource))


