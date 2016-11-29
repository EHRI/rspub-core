#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

from rspub.core.rs_enum import Strategy


class Test_Strategy(unittest.TestCase):

    def test_names(self):
        names = Strategy.names()
        self.assertIsInstance(names, list)
        self.assertEqual(names, ['inc_changelist', 'new_changelist', 'resourcelist'])

    def test_ordinal(self):
        # get the int value of an enum
        self.assertEqual(Strategy.resourcelist.value, 0)

    def test_conversion(self):
        # get an enum by name
        self.assertIs(Strategy['resourcelist'], Strategy.resourcelist)
        # get a enum by value
        self.assertIs(Strategy(0), Strategy.resourcelist)
        self.assertIs(Strategy(1), Strategy.new_changelist)
        self.assertIs(Strategy(2), Strategy.inc_changelist)

    def test_name(self):
        # get the name of a strategy
        strat = Strategy.resourcelist
        self.assertEquals("resourcelist", strat.name)
        self.assertTrue(isinstance(strat.name, str))

    def test_strategy_for(self):
        self.assertIs(Strategy.inc_changelist, Strategy.strategy_for(Strategy.inc_changelist))
        self.assertIs(Strategy.inc_changelist, Strategy.strategy_for("inc_changelist"))
        self.assertIs(Strategy.inc_changelist, Strategy.strategy_for(2))

    def test_describe(self):
        self.assertEquals(Strategy.resourcelist.describe(), "New resourcelist strategy")



