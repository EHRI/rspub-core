#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import logging
import os
import sys
import unittest

from rspub.core.config import Configuration, Configurations
from rspub.core.rs import ResourceSync
from rspub.core.rs_enum import Strategy
from rspub.core.rs_paras import RsParameters
from rspub.core.selector import Selector
from rspub.util.observe import EventLogger


def resource_dir():
    return os.path.expanduser("~")


def metadata_dir():
    return os.path.join("tmp", "rs", "metadata")


def test_resource():
    return os.path.join(resource_dir(), "tmp", "rs")


def precondition(as_string=False):
    msg = "Ok"
    test_dir = test_resource()
    if not os.path.exists(test_dir):
        msg = "Skip test: test directory does not exist: %s" % test_dir
    elif not os.path.isdir(test_dir):
        msg = "Skip test: not a directory: %s" % test_dir

    if as_string:
        return msg
    else:
        return msg == "Ok"


@unittest.skipUnless(precondition(), precondition(as_string=True))
class TestResourceSync(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)
        #Configuration().persist()
        Configuration.reset()

    def test_strategy_new_resourcelist(self):
        rs = ResourceSync(resource_dir=resource_dir(), metadata_dir=metadata_dir())
        rs.register(EventLogger(logging_level=logging.INFO))
        #rs.max_items_in_list = 3

        rs.strategy = Strategy.resourcelist
        # must exist
        #rs.description_dir = "/Users/Shared/foo"

        filenames = [test_resource()]
        rs.execute(filenames)

    def test_strategy_new_changelist(self):
        self.change_file_contents()

        rs = ResourceSync(resource_dir=resource_dir(), metadata_dir=metadata_dir())
        rs.register(EventLogger(logging_level=logging.INFO))
        #rs.max_items_in_list = 3
        #rs.is_saving_sitemaps = False
        rs.zero_fill_filename = 4
        rs.strategy = Strategy.new_changelist

        rs.metadata_dir = "tmp/rs/md1"
        # must exist
        # rs.description_dir = "/Users/Shared/foo"

        filenames = [test_resource()]
        rs.execute(filenames)

    def test_strategy_incremental_changelist(self):
        self.change_file_contents()
        rs = ResourceSync(resource_dir=resource_dir(), metadata_dir=metadata_dir())

        rs.register(EventLogger(logging_level=logging.INFO))
        #rs.max_items_in_list = 3
        # rs.is_saving_sitemaps = False
        rs.strategy = Strategy.inc_changelist

        filenames = [test_resource()]
        rs.execute(filenames)

    def change_file_contents(self):
        folder = os.path.join(test_resource(), "directory_1")
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)

        filename = os.path.join(folder, "document_1.txt")
        with open(filename, "a") as file:
            file.write("\n%s" % str(datetime.datetime.now()))

    def test_with_selector(self):
        metadata = os.path.join("tmp", "rs", "md_select")

        selector = Selector()
        os.makedirs(os.path.join(resource_dir(), "tmp", "rs", "test_data"), exist_ok=True)
        selector.location = os.path.join(resource_dir(), "tmp", "rs", "test_data", "selector1.txt")
        selector.include(test_resource())
        selector.exclude(os.path.join(test_resource(), "collection2"))

        rs = ResourceSync(resource_dir=resource_dir(), metadata_dir=metadata)
        rs.register(EventLogger(logging_level=logging.INFO))

        rs.execute(selector)
        # once executed we can just call rs.execute() because selector associated with paras
        rs.execute()

    def test_instantiate_from_RsParameters(self):
        paras = RsParameters()
        paras.metadata_dir = "test_instantiate_from_RsParameters"

        rs = ResourceSync(**paras.__dict__)
        self.assertEquals("test_instantiate_from_RsParameters", rs.metadata_dir)


