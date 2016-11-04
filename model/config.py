#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import logging, os, platform
from configparser import ConfigParser
from model.rs_enum import Strategy
from util import defaults

# Location for configuration files on Windows: ﻿
# os.path.expanduser("~")\AppData\Local\Programs\rsync\rsync.cfg
#
# Location for configuration files on unix-based systems:
# os.path.expanduser("~")/.config/rsync/rsync.cfg
#
# platform.system() returns
# Mac:      'Darwin'
# Windows:  ﻿'Windows'
# CentOS:   'Linux'

CFG_FILENAME = "resyto.cfg"
SECTION_CORE = "core"
SECTION_I18N = "i18n"
SECTION_WINDOW = "window"
SECTION_EXPLORER = "explorer"

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

        c_path = os.path.join(c_path, "resyto")
        if not os.path.exists(c_path): os.makedirs(c_path)
        Configuration.__get__logger().info("Configuration directory: %s", c_path)
        return c_path

    @staticmethod
    def _create_config_file(parser, location):
        f = open(location, "w")
        parser.read_dict({SECTION_CORE: {"resource_dir": os.path.expanduser("~"),
                                     "resync_dir": os.path.expanduser("~"),
                                     "sourcedesc": "/.well-known/resourcesync",
                                     "urlprefix": "http://www.example.com/"
                                     },
                          SECTION_I18N: {"language": "en-US"}
                          })
        parser.write(f)
        f.close()
        Configuration.__get__logger().info("Initial configuration file created at %s", location)

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            Configuration.__get__logger().info("Creating Configuration._instance")
            cls._instance = super(Configuration, cls).__new__(cls, *args)
            cls.config_path = cls._get_config_path()
            cls.config_file = os.path.join(cls.config_path, Configuration._get_configuration_filename())
            cls.parser = ConfigParser()
            if not os.path.exists(cls.config_file):
                cls._create_config_file(cls.parser, cls.config_file)
            else:
                Configuration.__get__logger().info("Reading configuration file: %s", cls.config_file)
                cls.parser.read(cls.config_file)

        return cls._instance

    def config_path(self):
        return self.config_path

    def config_file(self):
        return self.config_file

    def persist(self):
        f = open(self.config_file, "w")
        self.parser.write(f)
        f.close()
        Configuration.__get__logger().info("Persisted %s", self.config_file)

    def __set_option__(self, section, option, value):
        if not self.parser.has_section(section):
            self.parser.add_section(section)
        self.parser.set(section, option, value)

    def core_items(self):
        return self.parser.items(SECTION_CORE)

    def core_clear(self):
        self.parser.remove_section(SECTION_CORE)

    # core settings
    def core_resource_dir(self):
        return self.parser.get(SECTION_CORE, "resource_dir", fallback=os.path.expanduser("~"))

    def set_core_resource_dir(self, resource_dir):
        self.__set_option__(SECTION_CORE, "resource_dir", defaults.sanitize_directory_path(resource_dir))

    def core_metadata_dir(self):
        return self.parser.get(SECTION_CORE, "metadata_dir", fallback="metadata")

    def set_core_metadata_dir(self, metadata_dir):
        self.__set_option__(SECTION_CORE, "metadata_dir", metadata_dir)

    def core_plugin_dir(self):
        return self.parser.get(SECTION_CORE, "plugin_dir", fallback="")

    def set_core_plugin_dir(self, plugin_dir):
        self.__set_option__(SECTION_CORE, "plugin_dir", defaults.sanitize_directory_path(plugin_dir))

    def core_history_dir(self):
        return self.parser.get(SECTION_CORE, "history_dir", fallback="history")

    def set_core_history_dir(self, history_dir):
        self.__set_option__(SECTION_CORE, "history_dir", history_dir)

    def core_sourcedesc(self):
        return self.parser.get(SECTION_CORE, "sourcedesc", fallback="/.well-known/resourcesync")

    def set_core_sourcedesc(self, sourcedesc):
        self.__set_option__(SECTION_CORE, "sourcedesc", defaults.sanitize_source_desc(sourcedesc))

    def core_url_prefix(self):
        return self.parser.get(SECTION_CORE, "url_prefix", fallback="http://www.example.com/")

    def set_core_url_prefix(self, urlprefix):
        self.__set_option__(SECTION_CORE, "url_prefix", defaults.sanitize_url_prefix(urlprefix))

    def core_strategy(self):
        return Strategy[self.parser.get(SECTION_CORE, "strategy", fallback=Strategy.new_resourcelist.name)]

    def set_core_strategy(self, name):
        self.__set_option__(SECTION_CORE, "strategy", Strategy.sanitize(name))

    # i18n settings
    def settings_language(self):
        return self.parser.get(SECTION_I18N, "language", fallback="en-US")

    def set_settings_language(self, language):
        # ToDo: sanitize language string
        self.__set_option__(SECTION_I18N, "language", language)

    # window settings
    def window_width(self):
        return int(self.parser.get(SECTION_WINDOW, "width", fallback="700"))

    def set_window_width(self, width):
        self.__set_option__(SECTION_WINDOW, "width", str(width))

    def window_height(self):
        return int(self.parser.get(SECTION_WINDOW, "height", fallback="400"))

    def set_window_height(self, height):
        self.__set_option__(SECTION_WINDOW, "height", str(height))

    # explorer settings
    def explorer_width(self):
        return int(self.parser.get(SECTION_EXPLORER, "width", fallback="630"))

    def set_explorer_width(self, width):
        self.__set_option__(SECTION_EXPLORER, "width", str(width))

    def explorer_height(self):
        return int(self.parser.get(SECTION_EXPLORER, "height", fallback="400"))

    def set_explorer_height(self, height):
        self.__set_option__(SECTION_EXPLORER, "height", str(height))