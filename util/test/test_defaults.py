#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import unittest

from util import defaults


class TestDefaults(unittest.TestCase):

    def test_sanitize_directory_path(self):
        self.assertEquals("", defaults.sanitize_directory_path(""))
        path = os.path.expanduser("~")
        self.assertEquals(path + os.sep, defaults.sanitize_directory_path(path))

    def test_sanitize_url_path(self):
        self.assertEquals("foo/bar/baz.txt", defaults.sanitize_url_path("foo/bar/baz.txt"))
        self.assertEquals("foo/bar/baz.txt", defaults.sanitize_url_path("foo\\bar\\baz.txt"))

    def test_sanitize_url(self):
        self.assertEquals("", defaults.sanitize_url_prefix(None))
        self.assertEquals("http://foo.com/path/", defaults.sanitize_url_prefix("http://foo.com/path"))
        self.assertEquals("http://foo.com/path;parameter/", defaults.sanitize_url_prefix("http://foo.com/path;parameter"))

        with self.assertRaises(Exception) as context:
            defaults.sanitize_url_prefix("http://foo.com/path?this=that")
        self.assertIsInstance(context.exception, ValueError)

    def test_w3c_datetime(self):
        self.assertEquals("2016-10-15T14:08:31Z", defaults.w3c_datetime(1476540511))

    @unittest.skip("no automated test")
    def test_w3c_now(self):
        print(defaults.w3c_now())

    @unittest.skip("no automated test")
    def test_mime_type(self):

        print(defaults.mime_type("/Users/ecco/Documents/DANS/ehri/tm-2016-02-26.xls"))
        print(defaults.mime_type("/Users/ecco/Documents/DANS/ehri/tm-2016-02-26 copy.xml"))




