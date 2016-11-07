#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import unittest

from rspub.core.config import Configuration
from rspub.core.rs_enum import Strategy
from rspub.core.rs_paras import RsParameters


class TestRsParameters(unittest.TestCase):

    def test_resource_dir(self):
        user_home = os.path.expanduser("~")

        # defaults to configuration defaults
        Configuration().core_clear()
        rsp = RsParameters()
        self.assertEquals(rsp.resource_dir, user_home + os.sep)

        resource_dir = user_home

        rsp = RsParameters(resource_dir=resource_dir)
        self.assertEquals(rsp.resource_dir, resource_dir + os.sep)

        # contamination test
        rsp2 = RsParameters(**rsp.__dict__)
        self.assertEquals(rsp2.resource_dir, resource_dir + os.sep)

        with self.assertRaises(Exception) as context:
            rsp.resource_dir = "/foo/bar"
        #print(context.exception)
        self.assertIsInstance(context.exception, ValueError)

        self.save_configuration_test(rsp)

    def test_metadata_dir(self):
        user_home = os.path.expanduser("~")

        # defaults to configuration defaults
        Configuration().core_clear()
        rsp = RsParameters()
        self.assertEquals(rsp.metadata_dir, os.path.join(user_home, "metadata"))

        resource_dir = user_home

        rsp = RsParameters(metadata_dir="foo/md1", resource_dir=resource_dir)
        self.assertEquals(rsp.metadata_dir, os.path.join(resource_dir, "foo", "md1"))
        # @ToDo test for windows pathnames: 'foo\md1', 'C:foo\bar\baz'

        here = os.path.dirname(__file__)
        rsp.resource_dir = here
        self.assertEquals(rsp.metadata_dir, os.path.join(here, "foo", "md1"))

        # contamination test
        rsp2 = RsParameters(**rsp.__dict__)
        self.assertEquals(rsp2.metadata_dir, os.path.join(here, "foo", "md1"))


        with self.assertRaises(Exception) as context:
            rsp.metadata_dir = "/foo/bar"
        #print(context.exception)
        self.assertIsInstance(context.exception, ValueError)

        this = os.path.basename(__file__)
        with self.assertRaises(Exception) as context:
            rsp.metadata_dir = this
        #print(context.exception)
        self.assertIsInstance(context.exception, ValueError)

        self.save_configuration_test(rsp)

    def test_url_prefix(self):
        # defaults to configuration defaults
        Configuration().core_clear()
        rsp = RsParameters()
        self.assertEquals(rsp.url_prefix, "http://www.example.com/")

        rsp = RsParameters(url_prefix="http://foo.bar.com")
        self.assertEquals(rsp.url_prefix, "http://foo.bar.com/")

        # contamination test
        rsp2 = RsParameters(**rsp.__dict__)
        self.assertEquals(rsp2.url_prefix, "http://foo.bar.com/")

        with self.assertRaises(Exception) as context:
            rsp.url_prefix = "nix://foo.bar.com"
        #print(context.exception)
        self.assertEquals("URL schemes allowed are 'http' or 'https'. Given: 'nix://foo.bar.com'", context.exception.args[0])
        self.assertIsInstance(context.exception, ValueError)

        with self.assertRaises(Exception) as context:
            rsp.url_prefix = "https://.nl"
        #print(context.exception)
        self.assertEquals("URL has invalid domain name: '.nl'. Given: 'https://.nl'", context.exception.args[0])
        self.assertIsInstance(context.exception, ValueError)

        with self.assertRaises(Exception) as context:
            rsp.url_prefix = "https://foo.bar.com#foo"
        #print(context.exception)
        self.assertEquals("URL should not have a fragment. Given: 'https://foo.bar.com#foo'", context.exception.args[0])
        self.assertIsInstance(context.exception, ValueError)

        with self.assertRaises(Exception) as context:
            rsp.url_prefix = "http://foo.bar.com?what=this"
        #print(context.exception)
        self.assertEquals("URL should not have a query string. Given: 'http://foo.bar.com?what=this'", context.exception.args[0])
        self.assertIsInstance(context.exception, ValueError)

        with self.assertRaises(Exception) as context:
            rsp.url_prefix = "http://foo.bar.com/fragment#is"
        #print(context.exception)
        self.assertEquals("URL should not have a fragment. Given: 'http://foo.bar.com/fragment#is'", context.exception.args[0])
        self.assertIsInstance(context.exception, ValueError)

        with self.assertRaises(Exception) as context:
            rsp.url_prefix = "http://foo.bar.com/ uhr.isrong"
        #print(context.exception)
        self.assertEquals("URL is invalid. Given: 'http://foo.bar.com/ uhr.isrong'", context.exception.args[0])
        self.assertIsInstance(context.exception, ValueError)

        self.save_configuration_test(rsp)

    def test_strategy(self):
        # defaults to configuration defaults
        Configuration().core_clear()
        rsp = RsParameters()
        self.assertEquals(Strategy.new_resourcelist, rsp.strategy)

        rsp = RsParameters(strategy=Strategy.inc_changelist)
        self.assertEquals(Strategy.inc_changelist, rsp.strategy)

        # contamination test
        rsp2 = RsParameters(**rsp.__dict__)
        self.assertEquals(rsp2.strategy, Strategy.inc_changelist)

        rsp = RsParameters(strategy=1)
        self.assertEquals(Strategy.new_changelist, rsp.strategy)

        rsp = RsParameters(strategy="inc_changelist")
        self.assertEquals(Strategy.inc_changelist, rsp.strategy)

        with self.assertRaises(Exception) as context:
            rsp.strategy = 20056
        #print(context.exception)
        self.assertEquals("20056 is not a valid Strategy", context.exception.args[0])
        self.assertIsInstance(context.exception, ValueError)

        self.save_configuration_test(rsp)

    def test_history_dir(self):
        # defaults to configuration defaults
        Configuration().core_clear()
        rsp = RsParameters()
        self.assertEquals(None, rsp.history_dir)

        rsp = RsParameters(history_dir="foo/bar/baz")
        self.assertEquals("foo/bar/baz", rsp.history_dir)

        # contamination test
        rsp2 = RsParameters(**rsp.__dict__)
        self.assertEquals("foo/bar/baz", rsp2.history_dir)

        expected = os.path.join(rsp.metadata_dir, "foo/bar/baz")
        self.assertEquals(expected, rsp.abs_history_dir())

        rsp.history_dir = None
        self.assertIsNone(rsp.abs_history_dir())

        rsp.history_dir = "history"
        self.assertEquals("history", rsp.history_dir)

        rsp.history_dir = ""
        self.assertEquals(None, rsp.history_dir)

        with self.assertRaises(Exception) as context:
            rsp.history_dir = 42
        #print(context.exception)
        self.assertEquals("Value for history_dir should be string. 42 is <class 'int'>", context.exception.args[0])
        self.assertIsInstance(context.exception, ValueError)

        self.save_configuration_test(rsp)

    def test_plugin_dir(self):
        # defaults to configuration defaults
        Configuration().core_clear()
        rsp = RsParameters()
        self.assertEquals(None, rsp.plugin_dir)

        user_home = os.path.expanduser("~")
        rsp.plugin_dir = user_home
        self.assertEquals(user_home, rsp.plugin_dir)

        # contamination test
        rsp.plugin_dir = None
        rsp2 = RsParameters(**rsp.__dict__)
        self.assertEquals(None, rsp2.plugin_dir)

        rsp.plugin_dir = user_home
        rsp3 = RsParameters(**rsp.__dict__)
        self.assertEquals(user_home, rsp3.plugin_dir)

        self.save_configuration_test(rsp)

    def test_max_items_in_list(self):
        # defaults to configuration defaults
        Configuration().core_clear()
        rsp = RsParameters()
        self.assertEquals(50000, rsp.max_items_in_list)

        rsp = RsParameters(max_items_in_list=1)
        self.assertEquals(1, rsp.max_items_in_list)

        # contamination test
        rsp.max_items_in_list = 12345
        rsp2 = RsParameters(**rsp.__dict__)
        self.assertEquals(12345, rsp2.max_items_in_list)

        with self.assertRaises(Exception) as context:
            rsp.max_items_in_list = "foo"
        #print(context.exception)
        self.assertEquals("Invalid value for max_items_in_list: not a number foo", context.exception.args[0])
        self.assertIsInstance(context.exception, ValueError)

        with self.assertRaises(Exception) as context:
            rsp.max_items_in_list = 0
        #print(context.exception)
        self.assertEquals("Invalid value for max_items_in_list: value should be between 1 and 50000", context.exception.args[0])
        self.assertIsInstance(context.exception, ValueError)

        with self.assertRaises(Exception) as context:
            rsp.max_items_in_list = 50001
        #print(context.exception)
        self.assertEquals("Invalid value for max_items_in_list: value should be between 1 and 50000", context.exception.args[0])
        self.assertIsInstance(context.exception, ValueError)

        self.save_configuration_test(rsp)

    def test_zero_fill_filename(self):
        # defaults to configuration defaults
        Configuration().core_clear()
        rsp = RsParameters()
        self.assertEquals(4, rsp.zero_fill_filename)

        rsp = RsParameters(zero_fill_filename=10)
        self.assertEquals(10, rsp.zero_fill_filename)

        # contamination test
        rsp.zero_fill_filename = 123
        rsp2 = RsParameters(**rsp.__dict__)
        self.assertEquals(123, rsp2.zero_fill_filename)

        self.save_configuration_test(rsp)

    def test_booleans(self):
        # defaults to configuration defaults
        Configuration().core_clear()
        rsp = RsParameters()
        self.assertTrue(rsp.is_saving_pretty_xml)
        self.assertTrue(rsp.is_saving_sitemaps)
        self.assertTrue(rsp.has_wellknown_at_root)

        rsp = RsParameters(is_saving_pretty_xml=False, is_saving_sitemaps=False, has_wellknown_at_root=False)
        self.assertFalse(rsp.is_saving_pretty_xml)
        self.assertFalse(rsp.is_saving_sitemaps)
        self.assertFalse(rsp.has_wellknown_at_root)

        # contamination test
        rsp2 = RsParameters(**rsp.__dict__)
        self.assertFalse(rsp2.is_saving_pretty_xml)
        self.assertFalse(rsp2.is_saving_sitemaps)
        self.assertFalse(rsp2.has_wellknown_at_root)

        self.save_configuration_test(rsp)

    def save_configuration_test(self, rsp):
        Configuration.reset()
        rsp.save_configuration()
        Configuration.reset()

        rsp2 = RsParameters()
        self.assertEquals(rsp.__dict__, rsp2.__dict__)

