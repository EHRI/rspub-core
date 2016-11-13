#! /usr/bin/env python3
# -*- coding: utf-8 -*-
""" Py-module and -class inspector.


-------

Classes and functions
---------------------

"""
import importlib
import inspect
import logging
import os, sys

#: :samp:`The absolute path to the directory that is the application home or root directory.`
#:
#: During run time. So the value shown in documentation is not a constant!
APPLICATION_HOME = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

LOG = logging.getLogger(__name__)


class Inspector(object):
    """
    :samp:`Find py-modules and -classes in directories.`

    This class loads modules during its inspection. What the behavior will be upon encountering an ImportError
    can be set by the constructor parameter `stop_on_error` (boolean). It will then either log the exception
    (default) or raise the exception.
    """
    def __init__(self, stop_on_error=False):
        """
        :samp:`Initialize an {Inspector}.`

        :param stop_on_error: **True** for stop on error, **False** otherwise
        """
        self.stop_on_error = stop_on_error

    @staticmethod
    def list_py_files(*directories) -> str:
        """
        :samp:`Generator of py filenames.`

        Walks the given directories one-by-one recursively and yields each py-file it encounters. A file
        is considered py-file when its filename ends with `.py`. Files `__init__.py` and
        `setup.py` are neglected.

        :param str directories: directories to search
        :return: yields absolute filenames of py-files
        """
        # LOG.info("Application home is '%s'", APPLICATION_HOME)
        for di in directories:
            if di:
                abs_dir = os.path.join(APPLICATION_HOME, di)
                for root, _directories, _filenames in os.walk(abs_dir):
                    for filename in _filenames:
                        if filename.endswith(".py") and not (filename == "__init__.py"
                                                             or filename == "setup.py"):
                            py_file = os.path.join(root, filename)
                            yield py_file

    def load_modules(self, *directories):
        """
        :samp:`Generator of modules.`

        Walks the given directories one-by-one recursively and yields each module it encounters.
        The encountered modules will be imported. What the behavior will be upon encountering an ImportError
        can be set by the constructor parameter `stop_on_error` (boolean).

        :param str directories: directories to search
        :return: yields imported modules
        """
        for di in directories:
            if di:
                abs_dir = os.path.join(APPLICATION_HOME, di)
                plugin_home = APPLICATION_HOME
                if not abs_dir.startswith(APPLICATION_HOME):
                    plugin_home = abs_dir
                    sys.path.append(plugin_home)

                for py_file in self.list_py_files(abs_dir):
                    names = py_file.rsplit(".", 1)  # everything but the extension
                    path = os.path.relpath(names[0], plugin_home).replace(os.sep, ".")
                    try:
                        module = importlib.import_module(path)
                        yield module
                    except ImportError as ex:
                        if self.stop_on_error:
                            raise ex
                        else:
                            LOG.exception(ex)

    def list_classes(self, *directories):
        """
        :samp:`Generator of classes.`

        Walks the given directories one-by-one recursively and yields each class it encounters.

        :param str directories: directories to search
        :return: yields encountered classes
        """
        for module in self.load_modules(*directories):
            clsmembers = inspect.getmembers(module, inspect.isclass)
            for cls in clsmembers:
                if cls[1].__module__ == module.__name__:
                    yield cls[1]

    def list_classes_filtered(self, predicates=list(), *directories):
        """
        :samp:`Generator of filtered classes.`

        Walks the given directories one-by-one recursively and yields encountered classes *if* they pass
        all the predicates given in `predicates`.

        :param list predicates: a list of one-argument predicates that filter classes
        :param str directories: directories to search
        :return: yields encountered classes that pass the predicates
        """
        for cls in self.list_classes(*directories):
            passes = True
            if predicates:
                for f in predicates:
                    if not f(cls):
                        passes = False
                        break
            if passes:
                yield cls


# # functions and closures for class filtering
def is_subclass_of(super):
    """
    :samp:`Predicate for subclass detection`

    ::

        f(cls) = issubclass(cls, super)

    :param super: the superclass in the detection
    :return: lambda for class subclass detection
    """
    return lambda cls: issubclass(cls, super)


def is_qnamed(qname):
    """
    :samp:`Predicate for qualified class-name detection.`

    ::

        f(cls) = cls.qualified_name == qname

    :param qname: the qualified name in the detection
    :return: lambda for qualified class-name detection
    """
    return lambda cls: qname == cls.__module__ + "." + cls.__name__


def is_named(name):
    """
    :samp:`Predicate for loose class-name detection.`

    ::

        f(cls) = cls.name == name or cls.qualified_name == name

    :param name: the class-name or qualified class-name in the detection
    :return: lambda for loose class-name detection
    """
    return lambda cls: name == cls.__name__ or name == cls.__module__ + "." + cls.__name__


def from_module(module_name):
    """
    :samp:`Predicate for module-name detection.`

    ::

        f(cls) = cls.module_name == module_name

    :param module_name: the module-name in the detection
    :return: lambda for module-name detection
    """
    return lambda cls: cls.__module__.startswith(module_name)


def has_function(function_name):
    """
    :samp:`Predicate for class function detection.`

    ::

        f(cls) = cls.has_function_name(function_name)

    :param function_name: the function name in the detection
    :return: closure for function name detection
    """
    def _has_function(cls):
        if isinstance(cls, type):
            clazz = cls
        else:
            clazz = cls.__class__

        func_descs = inspect.getmembers(clazz, inspect.isfunction)
        for func_desc in func_descs:
            if func_desc[0] == function_name:
                return True
        return False

    return _has_function
