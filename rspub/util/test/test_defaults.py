#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

from rspub.util import defaults


class TestDefaults(unittest.TestCase):

    def test_sanitize_url_path(self):
        self.assertEquals("foo/bar/baz.txt", defaults.sanitize_url_path("foo/bar/baz.txt"))
        self.assertEquals("foo/bar/baz.txt", defaults.sanitize_url_path("foo\\bar\\baz.txt"))

    def test_w3c_datetime(self):
        self.assertEquals("2016-10-15T14:08:31Z", defaults.w3c_datetime(1476540511))

    # def test_md5_for_file(self):
    #     file = "/Users/ecco/tmp/rs/collection1/source1/dance/guide1.xml"
    #     print(defaults.md5_for_file(file))
    # # 124ce03d22f9b27b88ffde554216cceb == outcome with http://onlinemd5.com/







