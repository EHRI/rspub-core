#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import platform
import unittest

import sys

from model.config import Configuration

# root = logging.getLogger()
# root.setLevel(logging.DEBUG)
#
# ch = logging.StreamHandler(sys.stdout)
# ch.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# ch.setFormatter(formatter)
# root.addHandler(ch)


class TestConfiguration(unittest.TestCase):

    def test01_set_test_config(self):
        # print("\n>>> Testing set_test_config")
        Configuration._set_configuration_filename(None)
        assert not Configuration._configuration_filename
        assert Configuration._get_configuration_filename() == "resyto.cfg"

        Configuration._set_configuration_filename("foo.bar")
        assert Configuration._get_configuration_filename() == "foo.bar"
        Configuration._set_configuration_filename(None)
        assert Configuration._get_configuration_filename() == "resyto.cfg"

    def test02_instance(self):
        # print("\n>>> Testing _instance")
        Configuration._set_configuration_filename("resyto_test.cfg")

        config1 = Configuration()
        config2 = Configuration()

        assert config1 == config2

        path1 = config1.config_path
        if platform.system() == "Darwin":
            assert path1 == os.path.expanduser("~") + "/.config/resyto"
        elif platform.system() == "Windows":
            path_expected = os.path.join(os.path.expanduser("~"), "AppData", "Local", "resyto")
            assert path1 == path_expected
        elif platform.system() == "Linux":
            assert path1 == os.path.expanduser("~") + "/.config/resyto"
        else:
            assert path1 == os.path.expanduser("~") + "/resyto"

        config1.core_clear()
        assert config1.core_resource_dir() == os.path.expanduser("~")
        new_path = os.path.dirname(os.path.realpath(__file__))
        config1.set_core_resource_dir(new_path)
        assert config2.core_resource_dir() == new_path + os.sep

        config2.persist()
        config1 = None
        config2 = None
        Configuration._set_configuration_filename(None)

    # No control over garbage collect, so read cannot be tested.
    def test03_read(self):
        # print("\n>>> Testing read")
        Configuration._set_configuration_filename("resyto_test.cfg")
        new_path = os.path.dirname(os.path.realpath(__file__))
        config1 = Configuration()
        config2 = Configuration()

        config1.set_core_plugin_dir(new_path)
        self.assertEquals(config1.core_plugin_dir(), new_path + os.sep)
        config1.set_core_plugin_dir("")
        self.assertEquals(config1.core_plugin_dir(), "")

        assert config1.core_resource_dir() == new_path + os.sep
        assert config2.core_resource_dir() == new_path + os.sep

    def test04_set_get_language(self):
        # print("\n>>> Testing language")
        Configuration._set_configuration_filename("resyto_test.cfg")
        config1 = Configuration()

        #print("current language: " + config1.settings_language())
        config1.set_settings_language("foo-BR")
        #print("now the language is: " + config1.settings_language())


    def test99_cleanup(self):
        # print("\n>>> Cleaning up")
        Configuration._set_configuration_filename("resyto_test.cfg")
        config1 = Configuration()

        os.remove(config1.config_file)
        assert not os.path.exists(config1.config_file)
        config1._instance = None
        Configuration._set_configuration_filename(None)







