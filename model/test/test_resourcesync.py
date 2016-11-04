#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import sys
import unittest

import time

from model.resourcesync import ResourceSync
from model.rs_enum import Strategy
from resync import ChangeList
from resync.sitemap import Sitemap
from util.observe import EventLogger


#@unittest.skip
class TestResourceSync(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)

    def test_strategy_new_resourcelist(self):
        user_home = os.path.expanduser("~")
        metadata_dir = os.path.join(user_home, "tmp", "rs", "metadata")
        plugin_dir = os.path.join(user_home, "tmp", "rs", "plugins")
        rs = ResourceSync(resource_dir=user_home, metadata_dir=metadata_dir, plugin_dir=plugin_dir)
        rs.register(EventLogger(logging_level=logging.INFO))
        #rs.max_items_in_list = 3
        rs.strategy = Strategy.new_resourcelist

        filenames = [os.path.join(user_home, "tmp", "rs")]
        rs.execute(filenames)

    def test_strategy_new_changelist(self):
        user_home = os.path.expanduser("~")
        metadata_dir = os.path.join(user_home, "tmp", "rs", "metadata")
        plugin_dir = os.path.join(user_home, "tmp", "rs", "plugins")
        rs = ResourceSync(resource_dir=user_home, metadata_dir=metadata_dir, plugin_dir=plugin_dir)
        rs.register(EventLogger(logging_level=logging.INFO))
        #rs.max_items_in_list = 3
        #rs.is_saving_sitemaps = False
        rs.strategy = Strategy.new_changelist

        filenames = [os.path.join(user_home, "tmp", "rs")]
        rs.execute(filenames)

    def test_strategy_incremental_changelist(self):
        user_home = os.path.expanduser("~")
        metadata_dir = os.path.join(user_home, "tmp", "rs", "metadata")
        plugin_dir = os.path.join(user_home, "tmp", "rs", "plugins")
        rs = ResourceSync(resource_dir=user_home, metadata_dir=metadata_dir, plugin_dir=plugin_dir)
        rs.register(EventLogger(logging_level=logging.INFO))
        #rs.max_items_in_list = 3
        # rs.is_saving_sitemaps = False
        rs.strategy = Strategy.inc_changelist

        filenames = [os.path.join(user_home, "tmp", "rs")]
        rs.execute(filenames)

