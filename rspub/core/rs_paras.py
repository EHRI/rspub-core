#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import urllib.parse
from numbers import Number

import validators
from rspub.core.config import Configuration
from rspub.core.rs_enum import Strategy
from rspub.util import defaults

WELL_KNOWN_PATH = os.path.join(".well-known", "resourcesync")

config = None


class RsParameters(object):
    def __init__(self, resource_dir=config, metadata_dir=config, url_prefix=config, strategy=config, plugin_dir=config,
                 history_dir=config, max_items_in_list=config, zero_fill_filename=config, is_saving_pretty_xml=config,
                 is_saving_sitemaps=config, has_wellknown_at_root=config, **kwargs):
        kwargs.update({
            "resource_dir": resource_dir,
            "metadata_dir": metadata_dir,
            "url_prefix": url_prefix,
            "strategy": strategy,
            "plugin_dir": plugin_dir,
            "history_dir": history_dir,
            "max_items_in_list": max_items_in_list,
            "zero_fill_filename": zero_fill_filename,
            "is_saving_pretty_xml": is_saving_pretty_xml,
            "is_saving_sitemaps": is_saving_sitemaps,
            "has_wellknown_at_root": has_wellknown_at_root
        })
        cfg = Configuration()

        self._resource_dir = None
        _resource_dir_ = self.__arg__("_resource_dir", cfg.resource_dir(), **kwargs)
        self.resource_dir = _resource_dir_

        self._metadata_dir = None
        _metadata_dir_ = self.__arg__("_metadata_dir", cfg.metadata_dir(), **kwargs)
        self.metadata_dir = _metadata_dir_

        self._url_prefix = None
        _url_prefix_ = self.__arg__("_url_prefix", cfg.url_prefix(), **kwargs)
        self.url_prefix = _url_prefix_

        self._strategy = None
        _strategy_ = self.__arg__("_strategy", cfg.strategy(), **kwargs)
        self.strategy = _strategy_

        self._plugin_dir = None
        _plugin_dir_ = self.__arg__("_plugin_dir", cfg.plugin_dir(), **kwargs)
        self.plugin_dir = _plugin_dir_

        self._history_dir = None
        _history_dir_ = self.__arg__("_history_dir", cfg.history_dir(), **kwargs)
        self.history_dir = _history_dir_

        self._max_items_in_list = None
        _max_items_in_list_ = self.__arg__("_max_items_in_list", cfg.max_items_in_list(), **kwargs)
        self.max_items_in_list = _max_items_in_list_

        self._zero_fill_filename = None
        _zero_fill_filename_ = self.__arg__("_zero_fill_filename", cfg.zero_fill_filename(), **kwargs)
        self.zero_fill_filename = _zero_fill_filename_

        self.is_saving_pretty_xml = self.__arg__("is_saving_pretty_xml", cfg.is_saving_pretty_xml(), **kwargs)
        self.is_saving_sitemaps = self.__arg__("is_saving_sitemaps", cfg.is_saving_sitemaps(), **kwargs)
        self.has_wellknown_at_root = self.__arg__("has_wellknown_at_root", cfg.has_wellknown_at_root(), **kwargs)

    @staticmethod
    def __arg__(name, default=None, **kwargs):
        value = default
        ame = name[1:]
        if name in kwargs and kwargs[name] is not None:
            value = kwargs[name]  # _argument_x
        elif ame in kwargs and kwargs[ame] is not None:
            value = kwargs[ame]  # argument_x
        return value

    @staticmethod
    def assert_directory(path, arg):
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        if not os.path.exists(path):
            raise ValueError("Invalid value for %s: path does not exist: %s" % (arg, path))
        elif not os.path.isdir(path):
            raise ValueError("Invalid value for %s: not a directory: %s" % (arg, path))
        return path

    @staticmethod
    def assert_number(n, min, max, arg):
        if not isinstance(n, Number):
            raise ValueError("Invalid value for %s: not a number %s" % (arg, n))
        if not min <= n <= max:
            raise ValueError("Invalid value for %s: value should be between %d and %d" % (arg, min, max))

    @property
    def resource_dir(self):
        return self._resource_dir

    @resource_dir.setter
    def resource_dir(self, path):
        assert isinstance(path, str)
        path = self.assert_directory(path, "resource_dir")
        if not path.endswith(os.path.sep):
            path += os.path.sep
        self._resource_dir = path

    @property
    def metadata_dir(self):
        return os.path.join(self.resource_dir, self._metadata_dir)

    @metadata_dir.setter
    def metadata_dir(self, path):
        if os.path.isabs(path) and not path.startswith(self.resource_dir):
            raise ValueError("Invalid metadata_dir: %s not on path resource_dir (%s)." % (path, self.resource_dir))
        if os.path.isabs(path):
            path = os.path.relpath(path, self.resource_dir)
        md_dir = os.path.join(self.resource_dir, path)
        if os.path.isfile(md_dir):
            raise ValueError("Invalid metadata_dir: not a directory: %s" % md_dir)
        self._metadata_dir = path

    @property
    def url_prefix(self):
        return self._url_prefix

    @url_prefix.setter
    def url_prefix(self, value):
        if value.endswith("/"):
            value = value[:-1]
        parts = urllib.parse.urlparse(value)
        if parts[0] not in ["http", "https"]:  # scheme
            raise ValueError("URL schemes allowed are 'http' or 'https'. Given: '%s'" % value)
        is_valid_domain = validators.domain(parts[1])  # netloc
        if not is_valid_domain:
            raise ValueError("URL has invalid domain name: '%s'. Given: '%s'" % (parts[1], value))
        if parts[4] != "":  # query
            raise ValueError("URL should not have a query string. Given: '%s'" % value)
        if parts[5] != "":  # fragment
            raise ValueError("URL should not have a fragment. Given: '%s'" % value)
        is_valid_url = validators.url(value)
        if not is_valid_url:
            raise ValueError("URL is invalid. Given: '%s'" % value)
        if not value.endswith("/"):
            value += "/"
        self._url_prefix = value

    @property
    def strategy(self):
        return self._strategy

    @strategy.setter
    def strategy(self, value):
        self._strategy = Strategy.strategy_for(value)

    @property
    def history_dir(self):
        return self._history_dir

    @history_dir.setter
    def history_dir(self, path):
        if path and not isinstance(path, str):
            raise ValueError("Value for history_dir should be string. %s is %s" % (path, type(path)))
        if path == "":
            path = None
        self._history_dir = path

    @property
    def plugin_dir(self):
        return self._plugin_dir

    @plugin_dir.setter
    def plugin_dir(self, path):
        if path:
            path = self.assert_directory(path, "plugin_dir")
        self._plugin_dir = path

    @property
    def max_items_in_list(self):
        return self._max_items_in_list

    @max_items_in_list.setter
    def max_items_in_list(self, max_items):
        self.assert_number(max_items, 1, 50000, "max_items_in_list")
        self._max_items_in_list = max_items

    @property
    def zero_fill_filename(self):
        return self._zero_fill_filename

    @zero_fill_filename.setter
    def zero_fill_filename(self, zfill):
        self.assert_number(zfill, 1, 200, "zero_fill_filename")
        self._zero_fill_filename = zfill

    def save_configuration(self, on_disk=True):
        cfg = Configuration()

        cfg.set_resource_dir(self.resource_dir)
        cfg.set_metadata_dir(self.metadata_dir)
        cfg.set_url_prefix(self.url_prefix)
        cfg.set_strategy(self.strategy)
        cfg.set_history_dir(self.history_dir)
        cfg.set_plugin_dir(self.plugin_dir)
        cfg.set_max_items_in_list(self.max_items_in_list)
        cfg.set_zero_fill_filename(self.zero_fill_filename)
        cfg.set_is_saving_pretty_xml(self.is_saving_pretty_xml)
        cfg.set_is_saving_sitemaps(self.is_saving_sitemaps)
        cfg.set_has_wellknown_at_root(self.has_wellknown_at_root)

        if on_disk:
            cfg.persist()

    # # derived properties
    def abs_metadata_path(self, filename):
        return os.path.join(self.metadata_dir, filename)

    def uri_from_path(self, path):
        rel_path = os.path.relpath(path, self.resource_dir)
        return self.url_prefix + defaults.sanitize_url_path(rel_path)

    def current_description_url(self):
        if self.has_wellknown_at_root:
            rel_path = WELL_KNOWN_PATH
        else:
            path = self.abs_metadata_path(WELL_KNOWN_PATH)
            rel_path = os.path.relpath(path, self.resource_dir)
        return self.url_prefix + defaults.sanitize_url_path(rel_path)

    def abs_history_dir(self):
        if self.history_dir:
            return os.path.join(self.metadata_dir, self.history_dir)
        else:
            return None
