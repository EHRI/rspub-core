#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:samp:`Save and load multiple configurations`

The class :class:`Configurations` (mark the `s` at the end) enables you to save, load, remove and list
multiple configurations.

Class :class:`Configuration` (mark the absence of `s` at the end) is a singleton.
It should not be used directly. In stead use :class:`rspub.core.rs_paras.RsParameters`.

The location where configurations are stored is system-dependent:

 - ``{user-home}\\AppData\\Local\\Programs\\rspub\\config\\`` on Windows
 - ``{user-home}/.config/rspub/config/`` on Mac and Linux
 - ``{user-home}/rspub/config/`` fallback

.. seealso:: :doc:`RsParameters <rspub.core.rs_paras>`

"""
import logging
import os
import platform
from configparser import ConfigParser
from glob import glob

from rspub.core.rs_enum import Strategy, SelectMode

CFG_FILENAME = "DEFAULT.cfg"
CFG_DIRNAME = "core"
SECTION_CORE = "core"
EXT = ".cfg"


class Configurations(object):
    """
    :samp:`Enables saving, loading, listing and removing {configurations}`

    All methods are static::

        Configurations.list_configurations()
        Configurations.load_configuration("collection_1")
        # etc.

    """
    @staticmethod
    def __get__logger():
        logger = logging.getLogger(__name__)
        return logger

    @staticmethod
    def list_configurations() -> list:
        """
        :samp:`List available configurations`

        :return: list of names of previously saved configurations
        """
        config_path = Configuration._get_config_path()
        config_files = sorted(glob(os.path.join(config_path, "*" + EXT)))
        return [os.path.splitext(os.path.basename(x))[0] for x in config_files]

    @staticmethod
    def load_configuration(name: str):
        """
        :samp:`Load the configuration with the given name`

        :param name: name of a previously saved configuration
        :return: the restored Configuration
        """
        if name not in Configurations.list_configurations():
            raise ValueError("No configuration named '%s'" % name)
        Configuration.reset()
        Configuration._set_configuration_filename(name + EXT)
        Configurations.__get__logger().info("Loaded configuration %s" % name)
        return Configuration()

    @staticmethod
    def save_configuration_as(name: str):
        """
        :samp:`Save the current configuration under the given name`

        Any previously saved configurations with the same name will be overwritten without warning.

        :param name: name under which the configuration will be saved
        """
        if name is None or name == "":
            raise ValueError("Invalid configuration name. (None or empty string)")
        nam = os.path.splitext(name)[0]
        config_path = Configuration._get_config_path()
        config_file = os.path.join(config_path, nam + EXT)
        current_cfg = Configuration()
        current_cfg.config_file = config_file
        current_cfg.persist()
        Configurations.__get__logger().info("Saved configuration %s" % name)

    @staticmethod
    def remove_configuration(name: str):
        """
        :samp:`Remove the configuration with the given name`

        :param name: the name of the configuration to remove
        :return: **True** if the configuration was successfully removed, **False** otherwise
        """
        if name is None or name == "":
            raise ValueError("Invalid configuration name '%s'", name)
        nam = os.path.splitext(name)[0]
        config_path = Configuration._get_config_path()
        config_file = os.path.join(config_path, nam + EXT)
        if os.path.exists(config_file):
            os.remove(config_file)
            Configurations.__get__logger().info("Removed configuration %s" % name)
            return True
        else:
            return False

    @staticmethod
    def current_configuration_name():
        """
        :samp:`Get the name of the current configuration`

        :return: name of the current configuration
        """
        current_cfg = Configuration()
        return os.path.splitext(os.path.basename(current_cfg.config_file))[0]

    @staticmethod
    def rspub_config_dir():
        current_cfg = Configuration()
        return os.path.dirname(os.path.dirname(current_cfg.config_file))


class Configuration(object):
    """
    :samp:`Singleton persisting object for storing configuration parameters`

    .. warning::

        Do not use class Configuration directly. Use :doc:`RsParameters <rspub.core.rs_paras>` in stead.

    """

    _configuration_filename = CFG_FILENAME

    @staticmethod
    def __get__logger():
        logger = logging.getLogger(__name__)
        return logger

    @staticmethod
    def _set_configuration_filename(cfg_filename):
        Configuration.__get__logger().debug("Setting configuration filename to %s", cfg_filename)
        Configuration._configuration_filename = cfg_filename

    @staticmethod
    def _get_configuration_filename():
        if not Configuration._configuration_filename:
            Configuration._set_configuration_filename(CFG_FILENAME)

        return Configuration._configuration_filename

    @staticmethod
    def reset():
        Configuration._instance = None
        Configuration.__get__logger().debug("Configuration was reset.")

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

        c_path = os.path.join(c_path, "rspub", CFG_DIRNAME)
        if not os.path.exists(c_path):
            os.makedirs(c_path)
        #Configuration.__get__logger().info("Configuration directory: %s", c_path)
        return c_path

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            Configuration.__get__logger().debug("Creating Configuration._instance")
            cls._instance = super(Configuration, cls).__new__(cls, *args)
            cls.config_path = cls._get_config_path()
            cls.config_file = os.path.join(cls.config_path, Configuration._get_configuration_filename())
            cls.parser = ConfigParser()
            if os.path.exists(cls.config_file):
                cls.parser.read(cls.config_file, encoding="utf-8")
        return cls._instance

    def config_path(self):
        return self.config_path

    def config_file(self):
        return self.config_file

    def name(self):
        return os.path.splitext(os.path.basename(self.config_file))[0]

    def persist(self):
        f = open(self.config_file, "w", encoding="utf-8")
        self.parser.write(f)
        f.close()
        Configuration.__get__logger().debug("Persisted %s", self.config_file)

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

    def __get_list__(self, section, option, fallback=list()):
        value = self.parser.get(section, option, fallback="\n".join(fallback))
        if value == "":
            return []
        else:
            return value.split("\n")

    def __set_list__(self, section, option, value):
        self.__set_option__(section, option, "\n".join(value))

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

    def description_dir(self, fallback=None):
        return self.parser.get(SECTION_CORE, "description_dir", fallback=fallback)

    def set_description_dir(self, description_dir):
        self.__set_option__(SECTION_CORE, "description_dir", description_dir)

    def selector_file(self, fallback=None):
        return self.parser.get(SECTION_CORE, "selector_file", fallback=fallback)

    def set_selector_file(self, selector_file):
        self.__set_option__(SECTION_CORE, "selector_file", selector_file)

    def simple_select_file(self, fallback=None):
        return self.parser.get(SECTION_CORE, "simple_select_file", fallback=fallback)

    def set_simple_select_file(self, simple_file):
        self.__set_option__(SECTION_CORE, "simple_select_file", simple_file)

    def select_mode(self, fallback=SelectMode.simple.name):
        return SelectMode[self.parser.get(SECTION_CORE, "select_mode", fallback=fallback)]

    def set_select_mode(self, mode):
        self.__set_int__(SECTION_CORE, "select_mode", mode.name)

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

    # execution results
    def last_excution(self):
        return self.parser.get(SECTION_CORE, "last_excution", fallback=None)

    def set_last_execution(self, date_string):
        self.__set_option__(SECTION_CORE, "last_excution", date_string)

    def last_strategy(self):
        value = self.parser.get(SECTION_CORE, "last_strategy", fallback="")
        if value is None or value == "":
            return None
        return Strategy[value]

    def set_last_strategy(self, strategy):
        if strategy:
            self.__set_option__(SECTION_CORE, "last_strategy", strategy.name)
        else:
            self.__set_option__(SECTION_CORE, "last_strategy", "")

    def last_sitemaps(self, fallback=list()):
        return self.__get_list__(SECTION_CORE, "last_sitemaps", fallback=fallback)

    def set_last_sitemaps(self, sitemaplist):
        self.__set_list__(SECTION_CORE, "last_sitemaps", sitemaplist)

    # # scp parameters for exporting to remote web server
    def exp_scp_server(self, fallback="example.com"):
        return self.parser.get(SECTION_CORE, "exp_scp_server", fallback=fallback)

    def set_exp_scp_server(self, exp_scp_server):
        self.__set_option__(SECTION_CORE, "exp_scp_server", exp_scp_server)

    def exp_scp_port(self, fallback=22):
        return self.__get_int__(SECTION_CORE, "exp_scp_port", fallback=fallback)

    def set_exp_scp_port(self, exp_scp_port):
        self.__set_int__(SECTION_CORE, "exp_scp_port", exp_scp_port)

    def exp_scp_user(self, fallback="username"):
        return self.parser.get(SECTION_CORE, "exp_scp_user", fallback=fallback)

    def set_exp_scp_user(self, exp_scp_user):
        self.__set_option__(SECTION_CORE, "exp_scp_user", exp_scp_user)

    def exp_scp_document_root(self, fallback="/var/www/html/"):
        return self.parser.get(SECTION_CORE, "exp_scp_document_root", fallback=fallback)

    def set_exp_scp_document_root(self, exp_scp_document_root):
        self.__set_option__(SECTION_CORE, "exp_scp_document_root", exp_scp_document_root)

    # # zip parameters
    def zip_filename(self, fallback=os.path.join(os.path.expanduser("~"), "resourcesync.zip")):
        return self.parser.get(SECTION_CORE, "zip_filename", fallback=fallback)

    def set_zip_filename(self, zip_filename):
        return self.__set_option__(SECTION_CORE, "zip_filename", zip_filename)

    # # scp parameters for importing (resources) from remote server
    def imp_scp_server(self, fallback="example.com"):
        return self.parser.get(SECTION_CORE, "imp_scp_server", fallback=fallback)

    def set_imp_scp_server(self, imp_scp_server):
        self.__set_option__(SECTION_CORE, "imp_scp_server", imp_scp_server)

    def imp_scp_port(self, fallback=22):
        return self.__get_int__(SECTION_CORE, "imp_scp_port", fallback=fallback)

    def set_imp_scp_port(self, imp_scp_port):
        self.__set_int__(SECTION_CORE, "imp_scp_port", imp_scp_port)

    def imp_scp_user(self, fallback="username"):
        return self.parser.get(SECTION_CORE, "imp_scp_user", fallback=fallback)

    def set_imp_scp_user(self, imp_scp_user):
        self.__set_option__(SECTION_CORE, "imp_scp_user", imp_scp_user)

    def imp_scp_remote_path(self, fallback="~"):
        return self.parser.get(SECTION_CORE, "imp_scp_remote_path", fallback=fallback)

    def set_imp_scp_remote_path(self, imp_scp_remote_path):
        self.__set_option__(SECTION_CORE, "imp_scp_remote_path", imp_scp_remote_path)

    def imp_scp_local_path(self, fallback=os.path.expanduser("~")):
        return self.parser.get(SECTION_CORE, "imp_scp_local_path", fallback=fallback)

    def set_imp_scp_local_path(self, imp_scp_local_path):
        self.__set_option__(SECTION_CORE, "imp_scp_local_path", imp_scp_local_path)
