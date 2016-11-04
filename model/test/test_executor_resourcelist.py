#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import unittest

import sys

from model.executor_resourcelist import ResourceListExecutor
from model.resourcesync import ResourceSync
from util.observe import EventLogger, Observer, ObserverInterruptException


class RefusingObserver(Observer):

    def confirm(self, *args, **kwargs):
        return False

@unittest.skip("no automated test")
class TestResourcelistEcecutor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)

    def test_resourcelist_generator(self):
        user_home = os.path.expanduser("~")
        metadata_dir = os.path.join(user_home, "tmp", "rs", "metadata")

        filenames = [os.path.join(user_home, "tmp", "rs")]

        executor = ResourceListExecutor(resource_dir=user_home, metadata_dir=metadata_dir)
        executor.max_items_in_list = 3
        generator = executor.resourcelist_generator(filenames)
        for sitemap_data, resourcelist in generator():
            print(sitemap_data)

    def test_execute(self):
        user_home = os.path.expanduser("~")
        metadata_dir = os.path.join(user_home, "tmp", "rs", "metadata")

        filenames = [os.path.join(user_home, "tmp", "rs")]

        resourcesync = ResourceSync(resource_dir=user_home, metadata_dir=metadata_dir, strategy=0)
        #resourcesync.save_sitemaps = False
        resourcesync.max_items_in_list = 3
        resourcesync.register(EventLogger(event_level=1))

        resourcesync.execute(filenames)

    def test_execute_with_observer_Interrupt(self):
        user_home = os.path.expanduser("~")
        metadata_dir = os.path.join(user_home, "tmp", "rs", "metadata")

        filenames = [os.path.join(user_home, "tmp", "rs")]

        resourcesync = ResourceSync(resource_dir=user_home, metadata_dir=metadata_dir, strategy=0)
        resourcesync.register(EventLogger(), RefusingObserver())

        with self.assertRaises(Exception) as context:
            resourcesync.execute(filenames)
        self.assertIsInstance(context.exception, ObserverInterruptException)

        #resourcesync.execute(filenames)




