#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import unittest

import rspub.util.resourcefilter as rf


class TestPredicates(unittest.TestCase):

    def test_directory_pattern_filter_empty(self):
        dpf = rf.directory_pattern_predicate() # should pass all strings
        self.assertTrue(dpf(""))
        self.assertTrue(dpf("."))
        self.assertTrue(dpf("\n"))
        self.assertTrue(dpf("foo"))
        # rejects not string
        self.assertFalse(dpf(None))
        self.assertFalse(dpf(42))
        self.assertFalse(dpf(self))

    def test_directory_pattern_filter(self):
        dpf = rf.directory_pattern_predicate("abc")
        self.assertTrue(dpf("foo/babcd/bar/some.txt"))
        self.assertTrue(dpf("foo\\babcd\\bar\\some.txt"))
        self.assertTrue(dpf("/abc/bar/some.txt"))
        self.assertTrue(dpf("c:\\abc\\bar\\some.txt"))
        self.assertTrue(dpf("/foo/bar/abc/some.txt"))
        self.assertTrue(dpf("c:\\foo\\bar\\abc\\some.txt"))
        #
        self.assertFalse(dpf("/foo/bar/baz/abc.txt"))
        self.assertFalse(dpf("c:\\foo\\bar\\baz\\abc.txt"))

        # ##
        dpf = rf.directory_pattern_predicate("^/abc")
        self.assertTrue(dpf("/abc/bar/some.txt"))
        #
        self.assertFalse(dpf("abc/bar/some.txt"))
        # #
        dpf = rf.directory_pattern_predicate("^c:\\abc")
        self.assertTrue(dpf("c:\\abc\\bar\\some.txt"))
        #
        self.assertFalse(dpf("abc\\bar\\some.txt"))

        dpf = rf.directory_pattern_predicate("abc$")
        self.assertTrue(dpf("foo/bar/abc/some.txt"))
        self.assertTrue(dpf("foo\\bar\\abc\\some.txt"))
        #
        self.assertFalse(dpf("abc/abc/bar/some.txt"))
        self.assertFalse(dpf("abc\\abc\\bar\\some.txt"))
        self.assertFalse(dpf("abc/abc/bar/abc.abc"))
        self.assertFalse(dpf("abc\\abc\\bar\\abc.abc"))

    def test_last_modified_filter(self):
        file_name = os.path.realpath(__file__)

        lmaf = rf.last_modified_after_predicate()
        self.assertTrue(lmaf(file_name))

        lmaf = rf.last_modified_after_predicate(3000000000)
        # valid until 2065-01-24 06:20:00
        self.assertFalse(lmaf(file_name))

        lmaf = rf.last_modified_after_predicate("2016-08-01")
        self.assertTrue(lmaf(file_name))

    def test_example(self):
        import rspub.util.resourcefilter as rf

        dir_ends_with_abc = rf.directory_pattern_predicate("abc$")
        assert dir_ends_with_abc("/foo/bar/folder_abc/my_resource.txt")
        assert not dir_ends_with_abc("/foo/bar/folder_def/my_resource.txt")

        xml_file = rf.filename_pattern_predicate(".xml$")
        assert xml_file("my_resource.xml")
        assert not xml_file("my_resource.txt")

        import rspub.util.gates as lf

        xml_files_in_abc = lf.and_(dir_ends_with_abc, xml_file)
        assert xml_files_in_abc("/foo/bar/folder_abc/my_resource.xml")
        assert not xml_files_in_abc("/foo/bar/folder_abc/my_resource.txt")
        assert not xml_files_in_abc("/foo/bar/folder_def/my_resource.xml")

        assert xml_files_in_abc("c:\\foo\\bar\\folder_abc\\my_resource.xml")
        assert not xml_files_in_abc("c:\\foo\\bar\\folder_abc\\my_resource.txt")
        assert not xml_files_in_abc("c:\\foo\\bar\\folder_def\\my_resource.xml")

        recent = rf.last_modified_after_predicate("2016-08-01")

        includes = [xml_files_in_abc]
        excludes = [recent]
        resource_gate = lf.gate(includes, excludes)
        # print(type(resource_gate))

    def test_windows_to_unix(self):
        path = os.path.expanduser("~")
        dpf = rf.directory_pattern_predicate("^" + path)
        self.assertTrue(dpf(os.path.join(path, "bla")))

        dpf = rf.directory_pattern_predicate("^C:\\Users")
        self.assertTrue(dpf(os.path.join(path, "bla")))








