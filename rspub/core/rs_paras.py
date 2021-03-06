#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:samp:`Parameters for ResourceSync publishing`

The class :class:`RsParameters` validates parameters for ResourceSync publishing that are used throughout the
application. RsParameters can be persisted as configuration.

Multiple sets of parameters can be saved and reused as named configurations.
This enables configuring rspub-core to publish metadata on different sets of resources. Each configuration
can have its own selection mechanism, metadata directory, strategy etc. Each set of resources can than be published
in its own capability list.

The class :class:`RsParameters` in this module and the class :class:`rspub.core.config.Configurations` are
important assets in this endeavour. RsParameters can be associated with a saved :class:`rspub.core.selector.Selector`.

"""
import os
import urllib.parse
from numbers import Number

import validators
from rspub.core.config import Configuration, Configurations
from rspub.core.rs_enum import Strategy, SelectMode
from rspub.util import defaults

WELL_KNOWN_PATH = os.path.join(".well-known", "resourcesync")
WELL_KNOWN_URL = ".well-known/resourcesync"
config = None


class RsParameters(object):
    """
    :samp:`Class capturing the core parameters for ResourceSync publishing`

    Parameters can be set in the :func:`__init__` method of this class and as properties. Each parameter gets a
    screening on validity and a `ValueError` will be raised if it is not valid. Parameters can be saved collectively
    as a configuration. Multiple named configurations can be stored by using the method :func:`save_configuration_as`.
    Named configurations can be restored by giving the `config_name` at initialisation::

        # paras is an instance of RsParameters with configuration adequately set for collection 1
        # it is saved as 'collection_1_config':
        paras.save_configuration_as("collection_1_config")

        # ...
        # Later on it is restored...
        paras = RsParameters(config_name="collection_1_config")

    Note that the class :class:`rspub.core.Configurations` has a method for listing saved configurations by name.

    RsParameters can be cloned::

        # paras1 is an instance of RsParameters
        paras2 = RsParameters(**paras1.__dict__)
        paras1 == paras2    # False
        paras1.__dict__ == paras2.__dict__  # True

    Besides parameters the RsParameters class also has methods for derived properties.

    .. seealso:: :doc:`rspub.core.config <rspub.core.config>`

    """
    def __init__(self, config_name=None, resource_dir=config, metadata_dir=config, description_dir=config,
                 url_prefix=config, strategy=config, selector_file=config,
                 simple_select_file=config, select_mode=config, plugin_dir=config,
                 history_dir=config, max_items_in_list=config, zero_fill_filename=config, is_saving_pretty_xml=config,
                 is_saving_sitemaps=config, has_wellknown_at_root=config,
                 exp_scp_server=config, exp_scp_port=config, exp_scp_user=config,
                 exp_scp_document_root=config, zip_filename=config,
                 imp_scp_server=config, imp_scp_port=config, imp_scp_user=config,
                 imp_scp_remote_path=config, imp_scp_local_path=config,
                 **kwargs):
        """
        :samp:`Construct an instance of {RsParameters}`

        All ``parameters`` will get their value from

        1. the _named argument in `\*\*kwargs`. (this is for cloning instances of RsParameters). If not available:
        2. the named argument. If not available:
        3. the parameter as saved in the current configuration. If not available:
        4. the default configuration value.

        :param str config_name: the name of the configuration to read. If given, sets the current configuration.
        :param str resource_dir: ``parameter`` :func:`resource_dir`
        :param str metadata_dir: ``parameter`` :func:`metadata_dir`
        :param str description_dir: ``parameter`` :func:`description_dir`
        :param str url_prefix: ``parameter`` :func:`url_prefix`
        :param Union[Strategy, int, str] strategy: ``parameter`` :func:`strategy`
        :param str selector_file: ``parameter`` :func:`selector_file`
        :param str simple_select_file: ``parameter`` :func:`simple_select_file`
        :param SelectMode select_mode: ``parameter`` :func:`select_mode`
        :param str plugin_dir: ``parameter`` :func:`plugin_dir`
        :param str history_dir: ``parameter`` :func:`history_dir`
        :param int max_items_in_list: ``parameter`` :func:`max_items_in_list`
        :param int zero_fill_filename: ``parameter`` :func:`zero_fill_filename`
        :param bool is_saving_pretty_xml: ``parameter`` :func:`is_saving_pretty_xml`
        :param bool is_saving_sitemaps: ``parameter`` :func:`is_saving_sitemaps`
        :param bool has_wellknown_at_root: ``parameter`` :func:`has_wellknown_at_root`
        :param str exp_scp_server: ``parameter`` :func:`exp_scp_server`
        :param int exp_scp_port: ``parameter`` :func:`exp_scp_port`
        :param str exp_scp_user: ``parameter`` :func:`exp_scp_user`
        :param str exp_scp_document_root: ``parameter`` :func:`exp_scp_document_root`
        :param str zip_filename: ``parameter`` :func:`zip_filename`
        :param str imp_scp_server: ``parameter`` :func:`imp_scp_server`
        :param int imp_scp_port: ``parameter`` :func:`imp_scp_port`
        :param str imp_scp_user: ``parameter`` :func:`imp_scp_user`
        :param str imp_scp_remote_path: ``parameter`` :func:`imp_scp_remote_path`
        :param str imp_scp_local_path: ``parameter`` :func:`imp_scp_local_path`
        :param kwargs: named arguments, same as parameters, but preceded by _
        :raises: :exc:`ValueError` if a parameter is not valid or if the configuration with the given `config_name` is not found
        """
        kwargs.update({
            "resource_dir": resource_dir,
            "metadata_dir": metadata_dir,
            "description_dir": description_dir,
            "url_prefix": url_prefix,
            "strategy": strategy,
            "selector_file": selector_file,
            "simple_select_file": simple_select_file,
            "select_mode": select_mode,
            "plugin_dir": plugin_dir,
            "history_dir": history_dir,
            "max_items_in_list": max_items_in_list,
            "zero_fill_filename": zero_fill_filename,
            "is_saving_pretty_xml": is_saving_pretty_xml,
            "is_saving_sitemaps": is_saving_sitemaps,
            "has_wellknown_at_root": has_wellknown_at_root,
            "exp_scp_server": exp_scp_server,
            "exp_scp_port": exp_scp_port,
            "exp_scp_user": exp_scp_user,
            "exp_scp_document_root": exp_scp_document_root,
            "zip_filename": zip_filename,
            "imp_scp_server": imp_scp_server,
            "imp_scp_port": imp_scp_port,
            "imp_scp_user": imp_scp_user,
            "imp_scp_remote_path": imp_scp_remote_path,
            "imp_scp_local_path": imp_scp_local_path,
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

        self._description_dir = None
        _description_dir_ = self.__arg__("_description_dir", cfg.description_dir(), **kwargs)
        self.description_dir = _description_dir_

        self._url_prefix = None
        _url_prefix_ = self.__arg__("_url_prefix", cfg.url_prefix(), **kwargs)
        self.url_prefix = _url_prefix_

        self._strategy = None
        _strategy_ = self.__arg__("_strategy", cfg.strategy(), **kwargs)
        self.strategy = _strategy_

        self._selector_file = None
        _selector_file_ = self.__arg__("_selector_file", cfg.selector_file(), **kwargs)
        self.selector_file = _selector_file_

        self._simple_select_file = None
        _simple_select_file_ = self.__arg__("_simple_select_file", cfg.simple_select_file(), **kwargs)
        self.simple_select_file = _simple_select_file_

        self._select_mode = None
        _select_mode_ = self.__arg__("_select_mode", cfg.select_mode(), **kwargs)
        self.select_mode = _select_mode_

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

        self._is_saving_pretty_xml = self.__arg__("_is_saving_pretty_xml", cfg.is_saving_pretty_xml(), **kwargs)
        self._is_saving_sitemaps = self.__arg__("_is_saving_sitemaps", cfg.is_saving_sitemaps(), **kwargs)
        self._has_wellknown_at_root = self.__arg__("_has_wellknown_at_root", cfg.has_wellknown_at_root(), **kwargs)

        self._exp_scp_server = None
        _exp_scp_server_ = self.__arg__("_exp_scp_server", cfg.exp_scp_server(), **kwargs)
        self.exp_scp_server = _exp_scp_server_

        self._exp_scp_port = None
        _exp_scp_port_ = self.__arg__("_exp_scp_port", cfg.exp_scp_port(), **kwargs)
        self.exp_scp_port = _exp_scp_port_

        self._exp_scp_user = None
        _exp_scp_user_ = self.__arg__("_exp_scp_user", cfg.exp_scp_user(), **kwargs)
        self.exp_scp_user = _exp_scp_user_

        self._exp_scp_document_root = None
        _exp_scp_document_root_ = self.__arg__("_exp_scp_document_root", cfg.exp_scp_document_root(), **kwargs)
        self.exp_scp_document_root = _exp_scp_document_root_

        self._zip_filename = None
        _zip_filename_ = self.__arg__("_zip_filename", cfg.zip_filename(), **kwargs)
        self.zip_filename = _zip_filename_

        self._imp_scp_server = None
        _imp_scp_server_ = self.__arg__("_imp_scp_server", cfg.imp_scp_server(), **kwargs)
        self.imp_scp_server = _imp_scp_server_

        self._imp_scp_port = None
        _imp_scp_port_ = self.__arg__("_imp_scp_port", cfg.imp_scp_port(), **kwargs)
        self.imp_scp_port = _imp_scp_port_

        self._imp_scp_user = None
        _imp_scp_user_ = self.__arg__("_imp_scp_user", cfg.imp_scp_user(), **kwargs)
        self.imp_scp_user = _imp_scp_user_

        self._imp_scp_remote_path = None
        _imp_scp_remote_path_ = self.__arg__("_imp_scp_remote_path", cfg.imp_scp_remote_path(), **kwargs)
        self.imp_scp_remote_path = _imp_scp_remote_path_

        self._imp_scp_local_path = None
        _imp_scp_local_path_ = self.__arg__("_imp_scp_local_path", cfg.imp_scp_local_path(), **kwargs)
        self.imp_scp_local_path = _imp_scp_local_path_

        self.last_execution = self.__arg__("last_execution", cfg.last_excution(), **kwargs)
        self.last_strategy = self.__arg__("last_strategy", cfg.last_strategy(), **kwargs)
        self.last_sitemaps = self.__arg__("last_sitemaps", cfg.last_sitemaps(), **kwargs)

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
        ``parameter`` :samp:`The local root directory for ResourceSync publishing` (str)

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
        if not (path.endswith(os.path.sep) or path.endswith("\\") or path.endswith("/")):
            path += os.path.sep
        self._resource_dir = path

    @property
    def metadata_dir(self):
        """
        ``parameter`` :samp:`The directory for ResourceSync documents` (str)

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
        if path is None or path == "":
            raise ValueError("Invalid value for metadata_dir: path should not be empty")
        self._metadata_dir = path

    @property
    def description_dir(self):
        """
        ``parameter`` :samp:`Directory where a version of the description document is kept` (str)

        The description document, also known as `.well-known/resourcesync`, is keeping links to the
        capability list(s) at the site. A local copy of the description document (or the real description
        document if synchronization takes place at the server) will be updated with newly created
        capability lists. The `description_dir` should point to a directory where the
        :samp:`.well-known/resourcesync` document can be found.

        If `description_dir` is **None** the :func:`abs_metadata_dir` will be taken as `description_dir`.

        If the document :samp:`{{description_dir}}/.well-known/resourcesync` does not exist it will be created.

        ``default:`` **None**

        See also: :func:`abs_description_path`
        """
        return self._description_dir

    @description_dir.setter
    def description_dir(self, path):
        if path:
            path = self._assert_directory(path, "description_dir")
        self._description_dir = path

    @property
    def url_prefix(self):
        """
        ``parameter`` :samp:`The URL-prefix for ResourceSync publishing` (str)

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
        """
        ``parameter`` :samp:`Strategy for ResourceSync publishing` (str | int | :class:`~rspub.core.rs_enum.Strategy`)

        The `strategy` determines what will be done by :class:`~rspub.core.resourcesync.ResourceSync` upon execution.
        At the moment valid values for `strategy` are:

        - ``0`` :attr:`~rspub.core.rs_enum.Strategy.resourcelist` - new resourcelist: create new resourcelist(s)
        - ``1`` :attr:`~rspub.core.rs_enum.Strategy.new_changelist` - new changelist: create a new changelist on every execution
        - ``2`` :attr:`~rspub.core.rs_enum.Strategy.inc_changelist` - incremental changelist: add changes to an existing changelist

        If strategies new resourcelist or incremental changelist are chosen and there is no previous resourcelist
        found in the metadata directory the strategy :attr:`~rspub.core.rs_enum.Strategy.resourcelist` will be executed.

        ``default:`` :attr:`rspub.core.rs_enum.Strategy.resourcelist`

        """
        return self._strategy

    @strategy.setter
    def strategy(self, value):
        self._strategy = Strategy.strategy_for(value)

    @property
    def selector_file(self):
        """
        ``parameter`` :samp:`Location of file to construct a {Selector}` (str)

        A :class:`rspub.core.selector.Selector` can be used as input for the execute methods. The `selector_file`
        specifies the location of the selector file.

        ``default:`` **None**
        """
        return self._selector_file

    @selector_file.setter
    def selector_file(self, filename):
        if filename and not isinstance(filename, str):
            raise ValueError("Value for selector_file should be string. %s is %s" % (filename, type(filename)))
        if filename == "":
            filename = None

        self._selector_file = filename

    @property
    def simple_select_file(self):
        return self._simple_select_file

    @simple_select_file.setter
    def simple_select_file(self, filename):
        if filename and not isinstance(filename, str):
            raise ValueError("Value for simple_select_file should be string. %s is %s" % (filename, type(filename)))
        if filename == "":
            filename = None

        self._simple_select_file = filename

    @property
    def select_mode(self):
        return self._select_mode

    @select_mode.setter
    def select_mode(self, mode):
        self._select_mode = SelectMode.select_mode_for(mode)

    @property
    def history_dir(self):
        """
        ``parameter`` :samp:`Directory for storing reports on executed synchronisations` (str)

        Currently not in use.
        """
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
        """
        ``parameter`` :samp:`Directory where plugins can be found` (str)

        The given value should point to an existing directory. A relative path will be made absolute, calculated
        from the current working directory (`os.getcwd()`).

        At the moment plugins for :class:`~rspub.pluggable.gate.ResourceGateBuilder` can be provided.

        ``default:`` **None**

        See also: :doc:`rspub.util.gates <rspub.util.gates>`
        """
        return self._plugin_dir

    @plugin_dir.setter
    def plugin_dir(self, path):
        if path:
            path = self._assert_directory(path, "plugin_dir")
        self._plugin_dir = path

    @property
    def max_items_in_list(self):
        """
        ``parameter`` :samp:`The maximum amount of records in a sitemap` (int, 1 - 50000)

        The 'community defined' maximum amount of records in a sitemap document is 50000. If on execution
        the maximum amount is reached, new sitemaps of the same category will be created with the remaining
        records.

        ``default:`` 50000
        """
        return self._max_items_in_list

    @max_items_in_list.setter
    def max_items_in_list(self, max_items):
        self._assert_number(max_items, 1, 50000, "max_items_in_list")
        self._max_items_in_list = max_items

    @property
    def zero_fill_filename(self):
        """
        ``parameter`` :samp:`The amount of digits in a sitemap filename` (int, 1 - 10)

        Filenames of resourcelist, changelist etc. are numbered and are post-fixed with this number filled with
        zero's up to `zero_fill_filename`. Examples of filenames with `zero_fill_filename` set at 4::

            changelist_0002.xml
            changelist_0003.xml

        ``default:`` 4
        """
        return self._zero_fill_filename

    @zero_fill_filename.setter
    def zero_fill_filename(self, zfill):
        self._assert_number(zfill, 1, 10, "zero_fill_filename")
        self._zero_fill_filename = zfill

    @property
    def is_saving_pretty_xml(self):
        """
        ``parameter`` :samp:`Determines appearance of sitemap xml` (bool)

        If no humans need to read or inspect sitemaps there is no need for linebreaks etc.

        ``default:`` **True**, with linebreaks
        """
        return self._is_saving_pretty_xml

    @is_saving_pretty_xml.setter
    def is_saving_pretty_xml(self, pretty_xml):
        self._is_saving_pretty_xml = pretty_xml

    @property
    def is_saving_sitemaps(self):
        """
        ``parameter`` :samp:`Determines if sitemaps will be written to disk` (bool)

        An execution can be a dry-run. With this parameter set to **False** sitemaps will be generated,
        but not written to disk.

        ``default:`` **True**, write sitemaps to disk
        """
        return self._is_saving_sitemaps

    @is_saving_sitemaps.setter
    def is_saving_sitemaps(self, saving):
        self._is_saving_sitemaps = saving

    @property
    def has_wellknown_at_root(self):
        """
        ``parameter`` :samp:`Where is the description document {.well-known/resourcesync} on the server` (bool)

        The description document is the main entry point for third parties trying to discover resources at
        a source. Capability lists point toward this document in their `rel:up` attribute. If for some
        reason the `.well-known/resourcesync` cannot be at the root of the server the `rel:up` link in
        capability lists will be made to be pointing at `.well-known/resourcesync` relative to
        :func:`abs_metadata_dir`.

        ``default:`` **True**, the `.well-known/resourcesync` is at the root of the server
        """
        return self._has_wellknown_at_root

    @has_wellknown_at_root.setter
    def has_wellknown_at_root(self, at_root):
        self._has_wellknown_at_root = at_root

    @property
    def exp_scp_server(self):
        return self._exp_scp_server

    @exp_scp_server.setter
    def exp_scp_server(self, server):
        if server is None or server == "":
            raise ValueError("Invalid value for exp_scp_server: server name should not be empty")
        self._exp_scp_server = server

    @property
    def exp_scp_port(self):
        return self._exp_scp_port

    @exp_scp_port.setter
    def exp_scp_port(self, port):
        self._assert_number(port, 1, 65535, "exp_scp_port")
        self._exp_scp_port = port

    @property
    def exp_scp_user(self):
        return self._exp_scp_user

    @exp_scp_user.setter
    def exp_scp_user(self, user):
        if user is None or user == "":
            raise ValueError("Invalid value for exp_scp_user: name should not be empty")
        self._exp_scp_user = user

    @property
    def exp_scp_document_root(self):
        """
        ``parameter`` :samp:`The directory from which the web server will serve files` (str)

        Example. Paths to resources are relative to the server host::

            url_prefix:         http://www.example.com
            url to resource:    http://www.example.com/path/to/resource
            scp_document_root:           /var/www/html/
            scp_document_path:
            path on server:              /var/www/html/path/to/resource

        Example. Paths to resources are relative to some directory on the server::

            url_prefix:         http://www.example.com/my/resources
            url to resource:    http://www.example.com/my/resources/path/to/resource
            scp_document_root:           /var/www/html/
            scp_document_path:                         my/resources
            path on server:              /var/www/html/my/resources/path/to/resource

        ``default:`` '/var/www/html/'
        """
        return self._exp_scp_document_root

    @exp_scp_document_root.setter
    def exp_scp_document_root(self, value):
        if value.endswith("/"):
            value = value[:-1]
        if value == "":
            raise ValueError("Invalid value for scp_document_root: path should not be empty")
        self._exp_scp_document_root = value

    @property
    def zip_filename(self):
        return self._zip_filename

    @zip_filename.setter
    def zip_filename(self, value):
        if value is None or value == "":
            raise ValueError("Invalid value for zip_filename: filename should not be empty")
        ext = os.path.splitext(value)[1]
        if ext == "":
            value += ".zip"
        if ext == ".":
            value += "zip"
        self._zip_filename = value

    @property
    def imp_scp_server(self):
        return self._imp_scp_server

    @imp_scp_server.setter
    def imp_scp_server(self, server):
        if server is None or server == "":
            raise ValueError("Invalid value for imp_scp_server: server name should not be empty")
        self._imp_scp_server = server

    @property
    def imp_scp_port(self):
        return self._imp_scp_port

    @imp_scp_port.setter
    def imp_scp_port(self, port):
        self._assert_number(port, 1, 65535, "imp_scp_port")
        self._imp_scp_port = port

    @property
    def imp_scp_user(self):
        return self._imp_scp_user

    @imp_scp_user.setter
    def imp_scp_user(self, user):
        if user is None or user == "":
            raise ValueError("Invalid value for imp_scp_user: name should not be empty")
        self._imp_scp_user = user

    @property
    def imp_scp_remote_path(self):
        """
        ``parameter`` :samp:`The directory at the remote server from which to import files` (str)

        ``default:`` '~'
        """
        return self._imp_scp_remote_path

    @imp_scp_remote_path.setter
    def imp_scp_remote_path(self, value):
        if value.endswith("/"):
            value = value[:-1]
        if value == "":
            raise ValueError("Invalid value for imp_scp_remote_path: path should not be empty")
        self._imp_scp_remote_path = value

    @property
    def imp_scp_local_path(self):
        return self._imp_scp_local_path

    @imp_scp_local_path.setter
    def imp_scp_local_path(self, value):
        if value == "":
            raise ValueError("Invalid value for imp_scp_local_path: path should not be empty")
        self._imp_scp_local_path = value

    def save_configuration(self, on_disk=True):
        """
        ``function`` :samp:`Save current configuration`

        Save the current values of parameters to configuration. If `on_disk` is **True** (the default)
        persist the configuration to disk under the current configuration name.

        :param on_disk: **True** if configuration should be saved to disk, **False** otherwise

        See also: :func:`~rspub.core.config.Configurations.current_configuration_name`
        """
        cfg = Configuration()

        cfg.set_resource_dir(self.resource_dir)
        cfg.set_metadata_dir(self.metadata_dir)
        cfg.set_description_dir(self.description_dir)
        cfg.set_url_prefix(self.url_prefix)
        cfg.set_strategy(self.strategy)
        cfg.set_selector_file(self.selector_file)
        cfg.set_simple_select_file(self.simple_select_file)
        cfg.set_select_mode(self.select_mode)
        cfg.set_history_dir(self.history_dir)
        cfg.set_plugin_dir(self.plugin_dir)
        cfg.set_max_items_in_list(self.max_items_in_list)
        cfg.set_zero_fill_filename(self.zero_fill_filename)
        cfg.set_is_saving_pretty_xml(self.is_saving_pretty_xml)
        cfg.set_is_saving_sitemaps(self.is_saving_sitemaps)
        cfg.set_has_wellknown_at_root(self.has_wellknown_at_root)
        cfg.set_last_execution(self.last_execution)
        cfg.set_last_strategy(self.last_strategy)
        cfg.set_last_sitemaps(self.last_sitemaps)
        #
        cfg.set_exp_scp_server(self.exp_scp_server)
        cfg.set_exp_scp_port(self.exp_scp_port)
        cfg.set_exp_scp_user(self.exp_scp_user)
        cfg.set_exp_scp_document_root(self.exp_scp_document_root)
        #
        cfg.set_zip_filename(self.zip_filename)
        #
        cfg.set_imp_scp_server(self.imp_scp_server)
        cfg.set_imp_scp_port(self.imp_scp_port)
        cfg.set_imp_scp_user(self.imp_scp_user)
        cfg.set_imp_scp_remote_path(self.imp_scp_remote_path)
        cfg.set_imp_scp_local_path(self.imp_scp_local_path)

        if on_disk:
            cfg.persist()

    def save_configuration_as(self, name: str):
        """
        ``function`` :samp:`Save current configuration under {name}`

        Save the current configuration under the given `name`. If a configuration under the given `name` already
        exists it will be overwritten without warning.

        :param str name: the name under which the configuration will be saved

        See also: :func:`~rspub.core.config.Configurations.load_configuration`
        """
        self.save_configuration(False)
        Configurations.save_configuration_as(name)

    def reset(self):
        name = self.configuration_name()
        cfg = Configuration()
        cfg.core_clear()
        cfg.persist()
        self.__init__(config_name=name)

    def abs_metadata_dir(self) -> str:
        """
        ``derived`` :samp:`The absolute path to metadata directory`

        :return: absolute path to metadata directory
        """
        return os.path.join(self.resource_dir, self._metadata_dir)

    def abs_metadata_path(self, filename):
        """
        ``derived`` :samp:`The absolute path to file in the metadata directory`

        :param str filename: the filename to position relative to the :func:`abs_metadata_dir`
        :return: absolute path to file in the metadata directory
        """
        return os.path.join(self.abs_metadata_dir(), filename)

    def abs_description_path(self):
        """
        ``derived`` :samp:`The absolute path to (the local copy of) the file {.well-known/resourcesync}`

        :return: absolute path to (the local copy of) the file ``.well-known/resourcesync``
        """
        desc_dir = self.description_dir
        if desc_dir is None or desc_dir == "":
            desc_dir = self.abs_metadata_dir()
        return os.path.join(desc_dir, WELL_KNOWN_PATH)

    def server_root(self):
        """
        ``derived`` :samp:`The server root (of the web server) as derived from {url_prefix}`

        :return: server root
        """
        r = urllib.parse.urlsplit(self.url_prefix)
        return urllib.parse.urlunsplit([r[0], r[1], "", "", ""])

    def server_path(self):
        """
        ``derived`` :samp:`The server path as derived from {url_prefix}`

        :return: server path
        """
        r = urllib.parse.urlsplit(self.url_prefix)
        return urllib.parse.urlunsplit(["", "", r[2], "", ""])

    def description_url(self):
        """
        ``derived`` :samp:`The current description url`

        The current description url either points to ``{server root}/.well-known/resourcesync``
        or to a file in the metadata directory.

        :return: current description url

        See also: :func:`has_wellknown_at_root`
        """
        if self.has_wellknown_at_root:
            r = urllib.parse.urlsplit(self.url_prefix)
            return urllib.parse.urlunsplit([r[0], r[1], WELL_KNOWN_URL, "", ""])
        else:
            path = self.abs_metadata_path(WELL_KNOWN_URL)
            rel_path = os.path.relpath(path, self.resource_dir)
            return self.url_prefix + defaults.sanitize_url_path(rel_path)

    def capabilitylist_url(self) -> str:
        """
        ``derived`` :samp:`The current capabilitylist url`

        The current capabilitylist url points to 'capabilitylist.xml' in the metadata directory.

        :return: current capabilitylist url
        """
        path = self.abs_metadata_path("capabilitylist.xml")
        rel_path = os.path.relpath(path, self.resource_dir)
        return self.url_prefix + defaults.sanitize_url_path(rel_path)

    def uri_from_path(self, path):
        """
        ``derived`` :samp:`Calculate the url of a path relative to {resource_dir}`

        :param str path: the path to calculate the url from
        :return: the url of the path relative to ``resource_dir``
        """
        rel_path = os.path.relpath(path, self.resource_dir)
        return self.url_prefix + defaults.sanitize_url_path(rel_path)

    def abs_history_dir(self):
        """
        ``derived`` :samp:`The absolute path to directory for reports on synchronizations`

        Currently not in use.

        :return: absolute path to directory for reports
        """
        if self.history_dir:
            return os.path.join(self.abs_metadata_dir(), self.history_dir)
        else:
            return None

    @staticmethod
    def configuration_name():
        """
        ``function`` :samp:`Current configuration name`

        :return: current configuration name
        """
        return Configurations.current_configuration_name()

    def example_filename(self, ordinal):
        if self.strategy == Strategy.resourcelist:
            return "resourcelist_" + str(ordinal).zfill(self.zero_fill_filename) + ".xml"
        else:
            return "changelist_" + str(ordinal).zfill(self.zero_fill_filename) + ".xml"

    def describe(self, as_string=False, fill=23):
        """
        ``function`` :samp:`List parameters and derived values`

        List parameters, values and derived values as a list of tuples. Each tuple contains:

        ===  =====  ========================================================
        n    field  contents
        ===  =====  ========================================================
        0    bool   **True** for ``parameter``, **False** for derived value
        1    name   The name of the parameter or derived value
        2    value  The value of the parameter or derived value
        3..  ...    Anything else
        ===  =====  ========================================================

        :param as_string: return contents as a printable string
        :param fill: if as_string: fill column 'name' with `fill` spaces
        :return: list[list] or str
        """
        tuples = [
            [False, "configuration_name", self.configuration_name()],
            [True, "resource_dir", self.resource_dir],
            [True, "metadata_dir", self.metadata_dir],
            [False, "abs_metadata_dir", self.abs_metadata_dir()],
            [True, "description_dir", self.description_dir],
            [False, "abs_description_path", self.abs_description_path()],
            [True, "url_prefix", self.url_prefix],
            [True, "has_wellknown_at_root", self.has_wellknown_at_root],
            [False, "description_url", self.description_url()],
            [False, "capabilitylist_url", self.capabilitylist_url()],
            [True, "strategy", self.strategy, self.strategy.describe()],
            [True, "selector_file", self.selector_file],
            [True, "simple_select_file", self.simple_select_file],
            [True, "select_mode", self.select_mode],
            [True, "plugin_dir", self.plugin_dir],
            [True, "max_items_in_list", self.max_items_in_list],
            [True, "zero_fill_filename", self.zero_fill_filename],
            [False, "example_filename", self.example_filename(42)],
            [True, "is_saving_pretty_xml", self.is_saving_pretty_xml],
            [True, "is_saving_sitemaps", self.is_saving_sitemaps],
            #
            [False, "last_execution", self.last_execution],
            #[False, "last_strategy", self.last_strategy],
            #[False, "last_sitemaps_count", len(self.last_sitemaps)]
            #
        ]
        if as_string:
            f = "{:" + str(fill) + "s}"
            s = ""
            for t in tuples:
                s += " - " if t[0] else " + "
                s += f.format(t[1])
                s += str(t[2])
                for extra in t[3:]:
                    s += " | "
                    s += str(extra)
                s += "\n"
            return s
        else:
            return tuples





