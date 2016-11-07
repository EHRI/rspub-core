#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import platform
import sys
import unittest

from rspub.core.config import Configuration


class TestConfiguration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)

    def test01_set_test_config(self):
        # print("\n>>> Testing set_test_config")
        Configuration._set_configuration_filename(None)
        assert not Configuration._configuration_filename
        assert Configuration._get_configuration_filename() == "rspub_core.cfg"

        Configuration._set_configuration_filename("foo.bar")
        assert Configuration._get_configuration_filename() == "foo.bar"
        Configuration._set_configuration_filename(None)
        assert Configuration._get_configuration_filename() == "rspub_core.cfg"

    def test02_instance(self):
        # print("\n>>> Testing _instance")
        Configuration._set_configuration_filename("rspub_core.cfg")

        config1 = Configuration()
        config2 = Configuration()

        assert config1 == config2

        path1 = config1.config_path
        if platform.system() == "Darwin":
            assert path1 == os.path.expanduser("~") + "/.config/rspub"
        elif platform.system() == "Windows":
            path_expected = os.path.join(os.path.expanduser("~"), "AppData", "Local", "rspub")
            assert path1 == path_expected
        elif platform.system() == "Linux":
            assert path1 == os.path.expanduser("~") + "/.config/rspub"
        else:
            assert path1 == os.path.expanduser("~") + "/rspub"

        config1.core_clear()
        assert config1.resource_dir() == os.path.expanduser("~")
        new_path = os.path.dirname(os.path.realpath(__file__))
        config1.set_resource_dir(new_path)
        assert config2.resource_dir() == new_path

        config2.persist()
        config1 = None
        config2 = None

        Configuration.reset()

    def test03_read(self):
        # print("\n>>> Testing read")
        Configuration._set_configuration_filename("rspub_test.cfg")
        new_path = os.path.dirname(os.path.realpath(__file__))
        config1 = Configuration()
        config2 = Configuration()

        config1.set_plugin_dir(new_path)
        self.assertEquals(config1.plugin_dir(), new_path)
        config1.set_plugin_dir(None)
        self.assertEquals(config1.plugin_dir(), None)

        self.assertEquals(config2.plugin_dir(), None)

        Configuration.reset()

    def test_persist(self):
        filename = "rspub_test_persist.cfg"
        Configuration._set_configuration_filename(filename)

        cfg = Configuration()
        if os.path.exists(cfg.config_file):
            os.remove(cfg.config_file) # not atomic
        # time.sleep(2)
        self.assertFalse(os.path.exists(cfg.config_file))

        cfg.set_metadata_dir("foo/bar/md1")
        self.assertEquals(cfg.metadata_dir(), "foo/bar/md1")

        cfg.set_history_dir(None)
        self.assertIsNone(cfg.history_dir())

        cfg.set_max_items_in_list(42)
        self.assertEquals(42, cfg.max_items_in_list())
        cfg.set_is_saving_pretty_xml(False)
        self.assertEquals(False, cfg.is_saving_pretty_xml())

        cfg.persist()
        self.assertTrue(os.path.exists(cfg.config_file))
        #time.sleep(1)

        Configuration._set_configuration_filename(filename)
        cfg2 = Configuration()
        self.assertEquals(42, cfg2.max_items_in_list())
        self.assertEquals(False, cfg2.is_saving_pretty_xml())

        #Configuration.reset()












