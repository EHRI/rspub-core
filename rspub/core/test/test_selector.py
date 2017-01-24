#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import unittest

from rspub.core.selector import Selector


def test_dir():
    return os.path.join(os.path.expanduser("~"), "tmp", "rs", "test_data")


def precondition(as_string=False):
    msg = "Ok"
    dir = test_dir()
    if not os.path.exists(dir):
        msg = "Skip test: test directory does not exist: %s" % dir
    elif not os.path.isdir(dir):
        msg = "Skip test: not a directory: %s" % dir

    if as_string:
        return msg
    else:
        return msg == "Ok"


class TestSelector(unittest.TestCase):

    @unittest.skip
    def test_iter(self):
        selector = Selector()
        selector.include("foo", "bee")
        selector.include(["foo", "boz", ["kaz", "koz"]])
        selector.include("baz")

        selector2 = Selector()
        selector2.include("2foo", "2bar", ["2kaz", "2koz", {"2beez"}])

        selector.include(selector2)

        expected_length = 0
        selector_length = 0 #len(selector)

        self.assertEquals(expected_length, selector_length)
        names = []
        for filename in selector:
            names.append(filename)

        self.assertEquals(expected_length, len(names))

    @unittest.skipUnless(precondition(), precondition(as_string=True))
    def test_iter(self):
        selector = Selector()
        selector.include(os.path.join(test_dir(), "collection1"))
        selector.include(os.path.join(test_dir(), "collection2"))

        selector.exclude(os.path.join(test_dir(), "collection2/folder2"))
        selector.exclude(os.path.join(test_dir(), "collection2/.DS_Store"))

        selector2 = Selector()
        selector2.exclude(os.path.join(test_dir(), "collection2/folder1"))
        selector2.include(os.path.join(test_dir(), "directory_1"))
        selector2.exclude(os.path.join(test_dir(), "collection1"))

        selector.include(selector2)
        selector.exclude(selector2)

        for filename in selector:
            print(filename)

    @unittest.skipUnless(precondition(), precondition(as_string=True))
    def test_discard(self):
        selector = Selector()
        selector.include(os.path.join(test_dir(), "collection1"))
        selector.include(os.path.join(test_dir(), "collection2"))

        selector.exclude(os.path.join(test_dir(), "collection2/folder2"))
        selector.exclude(os.path.join(test_dir(), "collection2/.DS_Store"))

        # selector2 = Selector()
        # selector2.exclude(os.path.join(test_dir(), "collection2/folder1"))
        # selector2.include(os.path.join(test_dir(), "directory_1"))
        # selector2.exclude(os.path.join(test_dir(), "collection1"))
        #
        # selector.include(selector2)
        # selector.exclude(selector2)
        # selector.discard_exclude(selector2)

        for filename in selector:
            print(filename)

    def test_discard_self(self):
        selector = Selector()
        selector.include("collection1")
        selector.include("collection2")

        selector.discard_include(selector)

        self.assertEquals(0, len(selector))

    @unittest.skipUnless(precondition(), precondition(as_string=True))
    def test_list(self):
        selector = Selector()
        selector.include(os.path.join(test_dir(), "collection1"))
        selector.include(os.path.join(test_dir(), "collection2"))

        selector.exclude(os.path.join(test_dir(), "collection2/folder2"))
        selector.exclude(os.path.join(test_dir(), "collection2/.DS_Store"))

        for filename in selector.list_includes():
            print(filename)

        print(len([x for x in selector.list_includes()]))

    @unittest.skip
    def test_read_write(self):
        selector = Selector()
        selector.read_includes(os.path.join(test_dir(), "includes.txt"))
        selector.read_excludes(os.path.join(test_dir(), "excludes.txt"))

        print("\nselector 1")
        for filename in selector:
            print(filename)

        selector.write_includes(os.path.join(test_dir(), "includes_w.txt"))
        selector.write_excludes(os.path.join(test_dir(), "excludes_w.txt"))

        selector.write(os.path.join(test_dir(), "selector_1.txt"))
        selector2 = Selector(os.path.join(test_dir(), "selector_1.txt"))
        #
        print("\nselector 2")
        for filename in selector2:
            print(filename)

        selector2.clear_excludes()
        selector2.write(os.path.join(test_dir(), "test_data", "selector_2.txt"))

    @unittest.skipUnless(precondition(), precondition(as_string=True))
    def test_read_write(self):
        selector = Selector()
        selector.include("collection1")
        selector.exclude("collection2")

        selector.write(os.path.join(test_dir(), "test_selector.txt"))

        selector2 = Selector(os.path.join(test_dir(), "test_selector.txt"))
        self.assertEqual(selector2.get_included_entries().pop(), "collection1")
        self.assertEqual(selector2.get_excluded_entries().pop(), "collection2")

    def test_filter_base_path(self):
        paths = {"abc", "abc/def", "abc/def/ghi", "foo/bar", "abc/def"}
        base_paths = Selector.filter_base_paths(paths)
        self.assertEqual(2, len(base_paths))
        self.assertTrue("abc" in base_paths)
        self.assertTrue("foo/bar" in base_paths)

