#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import unittest

import sys

from model.config import Configuration
from model.executors import ExecutorParameters, Executor
from model.executor_resourcelist import ResourceListExecutor
from model.rs_enum import Capability


class TestExecutorParameters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)

    def test_init(self):
        config = Configuration()
        path1 = os.path.dirname(__file__)
        ep = ExecutorParameters(resource_dir = path1)
        self.assertEquals(path1, ep.resource_dir)
        self.assertEquals(path1 + os.sep, ep.abs_resource_dir())
        self.assertEquals(config.core_metadata_dir(), ep.metadata_dir)

        ep.metadata_dir = "bar"
        ep2 = ExecutorParameters(**ep.__dict__)
        self.assertEquals(path1, ep2.resource_dir)
        self.assertEquals("bar", ep.metadata_dir)

    def test_init_subclass(self):
        path1 = os.path.dirname(__file__)
        executor1 = ResourceListExecutor(metadata_dir="bor/bok/boo")
        executor1.resource_dir = path1
        self.assertTrue(executor1.is_saving_sitemaps)
        executor1.is_saving_sitemaps = False
        self.assertFalse(executor1.is_saving_sitemaps)
        self.assertFalse(executor1.__dict__["is_saving_sitemaps"])

        executor2 = ResourceListExecutor(**executor1.__dict__)
        self.assertEquals(path1, executor2.resource_dir)
        self.assertEquals("bor/bok/boo", executor2.metadata_dir)
        self.assertFalse(executor2.is_saving_sitemaps)


class TestExecutor(unittest.TestCase):

    def test_format_ordinal(self):
        executor = ResourceListExecutor()
        self.assertEquals("_0001", executor.format_ordinal("1"))
        executor.zfill_doc_count = 2
        self.assertEquals("_01", executor.format_ordinal("1"))

    @unittest.skip("no automated test")
    def test_clear_metadata_dir(self):
        user_home = os.path.expanduser("~")
        metadata_dir = "tmp/rs/metadata"
        executor = ResourceListExecutor(resource_dir=user_home, metadata_dir=metadata_dir)
        executor.clear_metadata_dir()

    @unittest.skip("no automated test")
    def test_resource_generator(self):
        user_home = os.path.expanduser("~")
        filenames = [os.path.join(user_home, "tmp", "rs")]

        executor = ResourceListExecutor(resource_dir=user_home)
        resource_generator = executor.resource_generator()
        for resource in resource_generator(filenames):
            print(resource)

    @unittest.skip("no automated test")
    def test_list_ordinal(self):
        user_home = os.path.expanduser("~")
        metadata_dir = "tmp/rs/metadata"
        executor = ResourceListExecutor(resource_dir=user_home, metadata_dir=metadata_dir)
        print(executor.find_ordinal(Capability.resourcelist.name))
        print(executor.find_ordinal("foo"))
