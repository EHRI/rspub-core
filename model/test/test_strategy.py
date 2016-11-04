#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

from model.rs_enum import Strategy


class Test_Strategy(unittest.TestCase):

    def test_names(self):
        names = Strategy.names()
        self.assertIsInstance(names, list)
        self.assertEqual(names, ['changedump', 'inc_changelist', 'new_changelist', 'new_resourcelist', 'resourcedump'])

    def test_ordinal(self):
        # get the int value of an enum
        self.assertEqual(Strategy.new_resourcelist.value, 0)

    def test_conversion(self):
        # get an enum by name
        self.assertIs(Strategy['new_resourcelist'], Strategy.new_resourcelist)
        # get a enum by value
        self.assertIs(Strategy(0), Strategy.new_resourcelist)
        self.assertIs(Strategy(1), Strategy.new_changelist)
        self.assertIs(Strategy(3), Strategy.resourcedump)
        self.assertIs(Strategy(4), Strategy.changedump)

    def test_name(self):
        # get the name of a strategy
        strat = Strategy.new_resourcelist
        self.assertEquals("new_resourcelist", strat.name)
        self.assertTrue(isinstance(strat.name, str))

    def test_strategy_for(self):
        self.assertIs(Strategy.inc_changelist, Strategy.strategy_for(Strategy.inc_changelist))
        self.assertIs(Strategy.inc_changelist, Strategy.strategy_for("inc_changelist"))
        self.assertIs(Strategy.inc_changelist, Strategy.strategy_for(2))


