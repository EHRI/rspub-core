#! /usr/bin/env python3
# -*- coding: utf-8 -*-
""" Parameters for ResourceSync publishing.

Class RsParameters
------------------

"""
import os
import urllib.parse
from numbers import Number

import validators
from rspub.core.config import Configuration, Configurations
from rspub.core.rs_enum import Strategy
from rspub.util import defaults


WELL_KNOWN_PATH = os.path.join(".well-known", "resourcesync")
config = None


class RsParameters(object):
    """
    :samp:`Class capturing the core parameters for ResourceSync publishing.`

    Parameters can be set in the :func:`__init__` method of this class and as properties. Each parameter gets a
    screening on validity and a `ValueError` will be raised if it is not valid. Parameters can be saved collectively
    as a configuration. Multiple named configurations can be stored by using the method :func:`save_configuration_as`.
    Named configurations can be restored by giving the `config_name` at initialisation::

        # paras is an instance of RsParameters with configuration adequately set for set 1
        # it is saved as 'set_1_config':
        paras.save_configuration_as("set_1_config")

        # ...
        # Later on it is restored...
        paras = RsParameters(config_name="set_1_config")

    Note that the class :class:`rspub.core.Configurations` has a method for listing saved configurations by name.

    RsParameters can be cloned::

        # paras1 is an instance of RsParameters
        paras2 = RsParameters(**paras1.__dict__)
        paras1 == paras2    # False
        paras1.__dict__ == paras2.__dict__  # True

    Besides parameters the RsParameters class also has methods for derived properties.

    .. seealso:: :doc:`Configuration <rspub.core.config>`

    """
    def __init__(self, resource_dir=config, metadata_dir=config, url_prefix=config, strategy=config, plugin_dir=config,
                 history_dir=config, max_items_in_list=config, zero_fill_filename=config, is_saving_pretty_xml=config,
                 is_saving_sitemaps=config, has_wellknown_at_root=config, config_name=None, **kwargs):
        """
        :samp:`Construct an instance of {RsParameters}.`

        All ``parameters`` will get their value from

        1. the _named argument in `\*\*kwargs`. (this is for cloning instances of RsParameters). If not available:
        2. the named argument. If not available:
        3. the parameter as saved in the current configuration. If not available:
        4. the default configuration value.

        :param str resource_dir: ``parameter`` :func:`resource_dir`
        :param str metadata_dir: ``parameter`` :func:`metadata_dir`
        :param str url_prefix: ``parameter`` :func:`url_prefix`
        :param strategy: ``parameter`` :func:`resource_dir`
        :param str plugin_dir: ``parameter`` :func:`plugin_dir`
        :param str history_dir: ``parameter`` :func:`history_dir`
        :param int max_items_in_list: ``parameter`` :func:`max_items_in_list`
        :param int zero_fill_filename: ``parameter`` :func:`zero_fill_filename`
        :param bool is_saving_pretty_xml: ``parameter`` :func:`is_saving_pretty_xml`
        :param bool is_saving_sitemaps: ``parameter`` :func:`is_saving_sitemaps`
        :param bool has_wellknown_at_root: ``parameter`` :func:`has_wellknown_at_root`
        :param str config_name: the name of the configuration to read. If given, sets the current configuration.
        :param kwargs: named arguments, same as parameters, but preceded by _
        :raises: :exc:`ValueError` if a parameter is not valid or if the configuration with the given `config_name` is not found
        """
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
        if config_name:
            cfg = Configurations.load_configuration(config_name)
        else:
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
    def _assert_directory(path, arg):
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        if not os.path.exists(path):
            raise ValueError("Invalid value for %s: path does not exist: %s" % (arg, path))
        elif not os.path.isdir(path):
            raise ValueError("Invalid value for %s: not a directory: %s" % (arg, path))
        return path

    @staticmethod
    def _assert_number(n, min, max, arg):
        if not isinstance(n, Number):
            raise ValueError("Invalid value for %s: not a number %s" % (arg, n))
        if not min <= n <= max:
            raise ValueError("Invalid value for %s: value should be between %d and %d" % (arg, min, max))

    @property
    def resource_dir(self):
        """
        :samp:`The root directory for ResourceSync publishing.` (str)

        The given value should point to an existing directory. A relative path will be made absolute, calculated
        from the current working directory (`os.getcwd()`).

        The resource_dir acts as the root of the resources to be published. The urls to the resources are
        calculated relative to the resource_dir. Example::

            resourece_dir:  /abs/path/to/resource_dir
            resource:       /abs/path/to/resource_dir/sub/path/to/resource
            url:                        url_prefix + /sub/path/to/resource

        ``default:`` user home directory

        See also: :func:`url_prefix`
        """
        return self._resource_dir

    @resource_dir.setter
    def resource_dir(self, path):
        assert isinstance(path, str)
        path = self._assert_directory(path, "resource_dir")
        if not path.endswith(os.path.sep):
            path += os.path.sep
        self._resource_dir = path

    @property
    def metadata_dir(self):
        """
        :samp:`The directory for ResourceSync documents.` (str)

        The metadata_dir is the directory where sitemap documents will be saved.
        Names and relative path names are allowed. An absolute path will raise a
        :exc:`ValueError`.

        The metadata directory will be calculated relative to the :func:`resource_dir`.

        If the metadata directory does not exist it will be created during execution of a synchronization.

        ``default:`` 'metadata'

        See also: :func:`abs_metadata_dir`
        """
        return self._metadata_dir

    @metadata_dir.setter
    def metadata_dir(self, path):
        if os.path.isabs(path):
            raise ValueError("Invalid value for metadata_dir: path should not be absolute: %s" % path)
        self._metadata_dir = path

    @property
    def url_prefix(self):
        """
        :samp:`The URL-prefix for ResourceSync publishing.` (str)

        The url_prefix substitutes :func:`resource_dir` when calculating urls to resources. The `url_prefix`
        should be the host name of the server or host name + path that points to the root directory of the
        resources. `url_prefix + relative/path/to/resource` should yield a valid url.

        Example. Paths to resources are relative to the server host::

            path to resource:           {resource_dir}/path/to/resource
            url_prefix:         http://www.example.com
            url to resource:    http://www.example.com/path/to/resource

        Example. Paths to resources are relative to some directory on the server::

            path to resource:                        {resource_dir}/path/to/resource
            url_prefix:         http://www.example.com/my/resources
            url to resource:    http://www.example.com/my/resources/path/to/resource

        ``default:`` 'http://www.example.com'

        See also: :func:`resource_dir`
        """
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
            path = self._assert_directory(path, "plugin_dir")
        self._plugin_dir = path

    @property
    def max_items_in_list(self):
        return self._max_items_in_list

    @max_items_in_list.setter
    def max_items_in_list(self, max_items):
        self._assert_number(max_items, 1, 50000, "max_items_in_list")
        self._max_items_in_list = max_items

    @property
    def zero_fill_filename(self):
        return self._zero_fill_filename

    @zero_fill_filename.setter
    def zero_fill_filename(self, zfill):
        self._assert_number(zfill, 1, 200, "zero_fill_filename")
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

    def save_configuration_as(self, name: str):
        self.save_configuration(False)
        Configurations.save_configuration_as(name)

    # # derived properties
    def abs_metadata_dir(self):
        return os.path.join(self.resource_dir, self._metadata_dir)

    def abs_metadata_path(self, filename):
        return os.path.join(self.abs_metadata_dir(), filename)

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
            return os.path.join(self.abs_metadata_dir(), self.history_dir)
        else:
            return None
