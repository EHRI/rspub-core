#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import unittest

import sys
from rspub.util import plugg


class TestInspector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)

    def test_application_home(self):
        application_home = plugg.APPLICATION_HOME
        self.assertTrue(application_home.endswith("rspub-core"))

    def test_list_py_files_with_me(self):
        me = os.path.basename(__file__)
        found_myself = False
        for py_file in plugg.Inspector.list_py_files("."):
            if py_file.endswith(me):
                found_myself = True
                break

        self.assertTrue(found_myself, "Could not find %s in a py-file search from %s" % (me, plugg.APPLICATION_HOME))

    # def test_list_py_files(self):
    #     user_home = os.path.expanduser("~")
    #     for py_file in plugg.Inspector.list_py_files("rspub/util", os.path.join(user_home, "tmp")):
    #         print(py_file)
    #
    # def test_list_py_files_with_empty_string(self):
    #     # searches APPLICATION_HOME
    #     for py_file in plugg.Inspector.list_py_files(""):
    #         print(py_file)

    # def test_list_py_files_with_empty_None(self):
    #     # searches APPLICATION_HOME
    #     for py_file in plugg.Inspector.list_py_files(None):
    #         print(py_file)
    #
    # def test_load_modules(self):
    #     inspector = plugg.Inspector(stop_on_error=False)
    #     user_home = os.path.expanduser("~")
    #     for module in inspector.load_modules("plugins", os.path.join(user_home, "tmp")):
    #         print(module)
    #
    # def test_list_classes(self):
    #     inspector = plugg.Inspector(stop_on_error=False)
    #     user_home = os.path.expanduser("~")
    #     for cls in inspector.list_classes("plugins", os.path.join(user_home, "tmp")):
    #         print(cls)
    #
    # def test_list_classes_filtered(self):
    #     inspector = plugg.Inspector(stop_on_error=False)
    #     fs = [lambda cls: plugg.is_named("NameFilter"),
    #           plugg.from_module("py_test.filters")]
    #     directories = ["plugins", os.path.join(os.path.expanduser("~"), "tmp")]
    #     for cls in inspector.list_classes_filtered(fs, *directories):
    #         print(cls)
    #
    #     print ("===================no filter")
    #     for cls in inspector.list_classes_filtered(None, *directories):
    #         print(cls)
    #
    # def test_list_classes_filtered2(self):
    #     inspector = plugg.Inspector(stop_on_error=False)
    #     is_named = lambda cls: cls.__name__ == "NameFilter"
    #     from_module = lambda cls: cls.__module__.startswith("py_test")
    #
    #     fs = [nor_(is_named, from_module)
    #
    #           ]
    #
    #     directories = ["plugins", os.path.join(os.path.expanduser("~"), "tmp")]
    #
    #     for clazz in inspector.list_classes_filtered(fs, *directories):
    #         print(clazz)





