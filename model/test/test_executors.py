#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

from model.exe_resourcelist import ResourceListExecutor


class TestExecutor(unittest.TestCase):

    def test_format_ordinal(self):
        executor = ResourceListExecutor()
        executor.para.zero_fill_filename = 4
        self.assertEquals("_0001", executor.format_ordinal("1"))
        executor.para.zero_fill_filename = 2
        self.assertEquals("_01", executor.format_ordinal("1"))
