#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import unittest

from util import defaults


class TestDefaults(unittest.TestCase):

    def test_sanitize_url_path(self):
        self.assertEquals("foo/bar/baz.txt", defaults.sanitize_url_path("foo/bar/baz.txt"))
        self.assertEquals("foo/bar/baz.txt", defaults.sanitize_url_path("foo\\bar\\baz.txt"))

    def test_w3c_datetime(self):
        self.assertEquals("2016-10-15T14:08:31Z", defaults.w3c_datetime(1476540511))






