#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import platform
import sys
import unittest

from rspub.core import config
from rspub.core.config import Configuration, Configurations


class TestConfigurations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)

    def test_current_configuration_name(self):
        # No name change
        current_name = Configurations.current_configuration_name()
        Configuration.reset()
        self.assertEquals(current_name, Configurations.current_configuration_name())

        cfg1 = Configuration()
        Configurations.save_configuration_as("test_current")
        self.assertEquals("test_current", Configurations.current_configuration_name())

        Configurations.remove_configuration("test_current")

    @unittest.skip
    def test_list_configurations(self):
        configurations = Configurations()
        for c in configurations.list_configurations():
            print(c)

    def test_load_configuration(self):
        Configurations.remove_configuration("test_load_1")
        Configurations.remove_configuration("test_load_2")
        Configuration.reset()

        cfg1 = Configuration()
        cfg2 = Configuration()
        self.assertIs(cfg1, cfg2)
        self.assertEquals(Configurations.current_configuration_name(), cfg1.name())
        self.assertEquals(Configurations.current_configuration_name(), cfg2.name())

        Configurations.save_configuration_as("test_load_1")
        self.assertEquals("test_load_1", cfg1.name())
        Configuration.reset()

        cfg3 = Configuration()
        self.assertIsNot(cfg1, cfg3)
        self.assertEquals(Configurations.current_configuration_name(), cfg3.name())

        Configurations.save_configuration_as("test_load_2")
        self.assertEquals("test_load_1", cfg1.name())
        self.assertEquals("test_load_1", cfg2.name())
        self.assertEquals("test_load_2", cfg3.name())

        Configurations.load_configuration("test_load_1")
        cfg4 = Configuration()
        self.assertEquals("test_load_1", cfg1.name())
        self.assertEquals("test_load_1", cfg2.name())
        self.assertEquals("test_load_2", cfg3.name())
        self.assertEquals("test_load_1", cfg4.name())

    unittest.skip("visual test")
    def test_rspub_config_dir(self):
        print(Configurations.rspub_config_dir())


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
        assert Configuration._get_configuration_filename() == config.CFG_FILENAME

        Configuration._set_configuration_filename("foo.bar")
        assert Configuration._get_configuration_filename() == "foo.bar"
        Configuration._set_configuration_filename(None)
        assert Configuration._get_configuration_filename() == config.CFG_FILENAME

    def test02_instance(self):
        # print("\n>>> Testing _instance")
        Configuration._set_configuration_filename("rspub_core.cfg")

        config1 = Configuration()
        config2 = Configuration()

        assert config1 == config2

        path1 = config1.config_path
        if platform.system() == "Darwin":
            assert path1 == os.path.expanduser("~") + "/.config/rspub/core"
        elif platform.system() == "Windows":
            path_expected = os.path.join(os.path.expanduser("~"), "AppData", "Local", "rspub", "core")
            assert path1 == path_expected
        elif platform.system() == "Linux":
            assert path1 == os.path.expanduser("~") + "/.config/rspub/core"
        else:
            assert path1 == os.path.expanduser("~") + "/rspub/core"

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












