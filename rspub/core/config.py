#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import platform
from configparser import ConfigParser
from glob import glob

from rspub.core.rs_enum import Strategy


# Location for configuration files on Windows: ﻿
# os.path.expanduser("~")\AppData\Local\Programs\rspub\rspub_core.cfg
#
# Location for configuration files on unix-based systems:
# os.path.expanduser("~")/.config/rspub/rspub_core.cfg
#
# platform.system() returns
# Mac:      'Darwin'
# Windows:  ﻿'Windows'
# CentOS:   'Linux'

CFG_FILENAME = "rspub_core.cfg"
SECTION_CORE = "core"
EXT = ".cfg"


class Configurations(object):

    @staticmethod
    def list_configurations():
        config_path = Configuration._get_config_path()
        config_files = sorted(glob(os.path.join(config_path, "*" + EXT)))
        return map(lambda x: os.path.splitext(os.path.basename(x))[0], config_files)

    @staticmethod
    def load_configuration(name):
        if name not in Configurations.list_configurations():
            raise ValueError("No configuration named '%s'" % name)
        Configuration.reset()
        Configuration._set_configuration_filename(name + EXT)
        return Configuration()

    @staticmethod
    def save_configuration_as(name):
        if name is None or name == "":
            raise ValueError("Invalid configuration name '%s'", name)
        nam = os.path.splitext(name)[0]
        config_path = Configuration._get_config_path()
        config_file = os.path.join(config_path, nam + EXT)
        current_cfg = Configuration()
        current_cfg.config_file = config_file
        current_cfg.persist()

    @staticmethod
    def remove_configuration(name):
        if name is None or name == "":
            raise ValueError("Invalid configuration name '%s'", name)
        nam = os.path.splitext(name)[0]
        config_path = Configuration._get_config_path()
        config_file = os.path.join(config_path, nam + EXT)
        if os.path.exists(config_file):
            os.remove(config_file)


class Configuration(object):

    _configuration_filename = CFG_FILENAME

    @staticmethod
    def __get__logger():
        logger = logging.getLogger(__name__)
        return logger

    @staticmethod
    def _set_configuration_filename(cfg_filename):
        Configuration.__get__logger().info("Setting configuration filename to %s", cfg_filename)
        Configuration._configuration_filename = cfg_filename

    @staticmethod
    def _get_configuration_filename():
        if not Configuration._configuration_filename:
            Configuration._set_configuration_filename(CFG_FILENAME)

        return Configuration._configuration_filename

    @staticmethod
    def reset():
        Configuration._instance = None
        Configuration._set_configuration_filename(None)
        Configuration.__get__logger().info("Configuration was reset.")

    @staticmethod
    def _get_config_path():

        c_path = os.path.expanduser("~")
        opsys = platform.system()
        if opsys == "Windows":
            win_path = os.path.join(c_path, "AppData", "Local")
            if os.path.exists(win_path): c_path = win_path
        elif opsys == "Darwin":
            dar_path = os.path.join(c_path, ".config")
            if not os.path.exists(dar_path): os.makedirs(dar_path)
            if os.path.exists(dar_path): c_path = dar_path
        elif opsys == "Linux":
            lin_path = os.path.join(c_path, ".config")
            if not os.path.exists(lin_path): os.makedirs(lin_path)
            if os.path.exists(lin_path): c_path = lin_path

        c_path = os.path.join(c_path, "rspub")
        if not os.path.exists(c_path):
            os.makedirs(c_path)
        Configuration.__get__logger().info("Configuration directory: %s", c_path)
        return c_path

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            Configuration.__get__logger().info("Creating Configuration._instance")
            cls._instance = super(Configuration, cls).__new__(cls, *args)
            cls.config_path = cls._get_config_path()
            cls.config_file = os.path.join(cls.config_path, Configuration._get_configuration_filename())
            cls.parser = ConfigParser()
            if os.path.exists(cls.config_file):
                cls.parser.read(cls.config_file)
        return cls._instance

    def config_path(self):
        return self.config_path

    def config_file(self):
        return self.config_file

    def name(self):
        return os.path.splitext(os.path.basename(self.config_file))[0]

    def persist(self):
        f = open(self.config_file, "w")
        self.parser.write(f)
        f.close()
        Configuration.__get__logger().info("Persisted %s", self.config_file)

    def __set_option__(self, section, option, value):
        if not self.parser.has_section(section):
            self.parser.add_section(section)
        if value is None:
            self.parser.remove_option(section, option)
        else:
            self.parser.set(section, option, value)

    def __get_int__(self, section, option, fallback=0):
        value = self.parser.get(section, option, fallback=str(fallback))
        return int(value)

    def __set_int__(self, section, option, value):
        self.__set_option__(section, option, str(value))

    def __get_boolean__(self, section, option, fallback=True):
        value = self.parser.get(section, option, fallback=str(fallback))
        return not(value == "False" or value == "None")

    def __set_boolean__(self, section, option, value):
        self.__set_option__(section, option, str(value))

    def core_items(self):
        return self.parser.items(SECTION_CORE)

    def core_clear(self):
        self.parser.remove_section(SECTION_CORE)

    # core settings
    def resource_dir(self, fallback=os.path.expanduser("~")):
        return self.parser.get(SECTION_CORE, "resource_dir", fallback=fallback)

    def set_resource_dir(self, resource_dir):
        self.__set_option__(SECTION_CORE, "resource_dir", resource_dir)

    def metadata_dir(self, fallback="metadata"):
        return self.parser.get(SECTION_CORE, "metadata_dir", fallback=fallback)

    def set_metadata_dir(self, metadata_dir):
        self.__set_option__(SECTION_CORE, "metadata_dir", metadata_dir)

    def plugin_dir(self, fallback=None):
        return self.parser.get(SECTION_CORE, "plugin_dir", fallback=fallback)

    def set_plugin_dir(self, plugin_dir):
        self.__set_option__(SECTION_CORE, "plugin_dir", plugin_dir)

    def history_dir(self, fallback=None):
        return self.parser.get(SECTION_CORE, "history_dir", fallback=fallback)

    def set_history_dir(self, history_dir):
        self.__set_option__(SECTION_CORE, "history_dir", history_dir)

    def url_prefix(self, fallback="http://www.example.com"):
        return self.parser.get(SECTION_CORE, "url_prefix", fallback=fallback)

    def set_url_prefix(self, urlprefix):
        self.__set_option__(SECTION_CORE, "url_prefix", urlprefix)

    def strategy(self, fallback=Strategy.resourcelist.name):
        return Strategy[self.parser.get(SECTION_CORE, "strategy", fallback=fallback)]

    def set_strategy(self, strategy):
        self.__set_option__(SECTION_CORE, "strategy", strategy.name)

    def max_items_in_list(self, fallback=50000):
        return self.__get_int__(SECTION_CORE, "max_items_in_list", fallback)

    def set_max_items_in_list(self, max_items):
        self.__set_int__(SECTION_CORE, "max_items_in_list", max_items)

    def zero_fill_filename(self, fallback=4):
        return self.__get_int__(SECTION_CORE, "zero_fill_filename", fallback)

    def set_zero_fill_filename(self, zfill):
        self.__set_int__(SECTION_CORE, "zero_fill_filename", zfill)

    def is_saving_pretty_xml(self, fallback=True):
        return self.__get_boolean__(SECTION_CORE, "is_saving_pretty_xml", fallback)

    def set_is_saving_pretty_xml(self, p_xml):
        self.__set_boolean__(SECTION_CORE, "is_saving_pretty_xml", p_xml)

    def is_saving_sitemaps(self, fallback=True):
        return self.__get_boolean__(SECTION_CORE, "is_saving_sitemaps", fallback)

    def set_is_saving_sitemaps(self, is_saving):
        self.__set_boolean__(SECTION_CORE, "is_saving_sitemaps", is_saving)

    def has_wellknown_at_root(self, fallback=True):
        return self.__get_boolean__(SECTION_CORE, "has_wellknown_at_root", fallback)

    def set_has_wellknown_at_root(self, at_root):
        self.__set_boolean__(SECTION_CORE, "has_wellknown_at_root", at_root)