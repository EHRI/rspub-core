#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import importlib
import logging
import os
import sys
import unittest

from rspub.util.gates import not_, or_, nor_, and_, nand_, xor_, xnor_, gate, is_one_arg_predicate, \
    set_stop_on_creation_error

LOG = logging.getLogger(__name__)




class TestGates(unittest.TestCase):
    def test_some(self):
        spamm = lambda word : word.startswith("spam")
        eggs = lambda word: word.endswith("eggs")
        ampersand = lambda word: len(word.split("&")) > 1
        spam_and_eggs = and_(spamm, eggs, ampersand)
        self.assertTrue(spam_and_eggs("spam & eggs"))
        self.assertFalse(spam_and_eggs("spamming leggs"))

    def test_not_(self):
        is_zero = lambda x: x == 0
        not_zero = not_(is_zero)

        self.assertTrue(is_zero(0))
        self.assertFalse(is_zero(1))

        self.assertTrue(not_zero(1))
        self.assertFalse(not_zero(0))

    def test_or_(self):
        one = lambda x: x == 1
        two = lambda x: x == 2
        one_or_two = or_(one, two)

        # print(one_or_two(0))
        # print(one_or_two(1))
        # print(one_or_two(2))
        # print(one_or_two(3))

        self.assertFalse(one_or_two(0))
        self.assertTrue(one_or_two(1))
        self.assertTrue(one_or_two(2))
        self.assertFalse(one_or_two(3))

    def test_or_fast(self):

        def one(x):
            # print("one")
            self.one_called = True
            return x == 1

        def two(x):
            # print("two")
            self.two_called = True
            return x == 2

        one_or_two = or_(one, two)

        self.one_called = False
        self.two_called = False

        self.assertFalse(one_or_two(0))
        self.assertTrue(self.one_called)
        self.assertTrue(self.two_called)

        self.one_called = False
        self.two_called = False

        self.assertTrue(one_or_two(1))
        self.assertTrue(self.one_called)
        self.assertFalse(self.two_called)

    def test_nor_(self):
        three = lambda x: x == 3
        four = lambda x: x == 4

        three_nor_four = nor_(three, four)
        self.assertTrue(three_nor_four(2))
        self.assertFalse(three_nor_four(3))
        self.assertFalse(three_nor_four(4))
        self.assertTrue(three_nor_four(42))

    def test_and_(self):
        big = lambda x: x >= 100
        even = lambda x: x % 2 == 0

        big_and_even = and_(big, even)

        self.assertFalse(big_and_even(98))
        self.assertFalse(big_and_even(99))
        self.assertTrue(big_and_even(100))
        self.assertFalse(big_and_even(101))
        self.assertTrue(big_and_even(102))

    def test_nand_(self):
        big = lambda x: x >= 100
        even = lambda x: x % 2 == 0

        nand_big_even = nand_(big, even)

        self.assertTrue(nand_big_even(98))
        self.assertTrue(nand_big_even(99))
        self.assertFalse(nand_big_even(100))
        self.assertTrue(nand_big_even(101))
        self.assertFalse(nand_big_even(102))

    def test_xor_(self):
        a = lambda word: "a" in word
        b = lambda word: "b" in word
        c = lambda word: "c" in word

        xor_abc = xor_(a, b, c)

        self.assertFalse(xor_abc("word"))
        self.assertTrue(xor_abc("a word"))
        self.assertFalse(xor_abc("a word box"))
        self.assertFalse(xor_abc("a word box captured"))
        self.assertFalse(xor_abc("captured"))
        self.assertTrue(xor_abc("rainy day"))
        self.assertFalse(xor_abc("raincoat"))

    def test_xnor_(self):
        a = lambda word: "a" in word
        b = lambda word: "b" in word
        c = lambda word: "c" in word

        xnor_abc = xnor_(a, b, c)

        self.assertTrue(xnor_abc("acb"))
        self.assertTrue(xnor_abc("not uh single letter is .. or . in here"))
        self.assertTrue(xnor_abc("a word box captured"))
        self.assertTrue(xnor_abc("be captured"))
        self.assertTrue(xnor_abc("rainy day at the club"))
        self.assertTrue(xnor_abc("black raincoat"))

        self.assertFalse(xnor_abc("a word box"))
        self.assertFalse(xnor_abc("captured"))
        self.assertFalse(xnor_abc("rainy day"))
        self.assertFalse(xnor_abc("raincoat"))

    def test_gate(self):
        a = lambda word: "a" in word
        b = lambda word: "b" in word
        c = lambda word: "c" in word

        sa = lambda word: word.startswith("a")
        ea = lambda word: word.endswith("a")
        eb = lambda word: word.endswith("b")

        g = gate([a, b, c], [sa, ea, eb])

        self.assertFalse(g("word"))  # no includes, no excludes
        self.assertTrue(g("ward"))  # include cause of 'a', no excludes
        self.assertFalse(g("warb"))  # include cause of 'a', exclude cause of end 'b'
        self.assertFalse(g("curb"))  # include cause of 'c', exclude cause of end 'b'
        self.assertTrue(g("curs"))  # include cause of 'c', no excludes
        self.assertFalse(g("aa"))  # include cause of 'a', exclude cause of start 'a'

    def test_gate_fast(self):
        self.print = False

        def a(word):
            self.a_called = True
            out = "a" in word
            if self.print: print("a in word =", out)
            return out

        def b(word):
            self.b_called = True
            out = "b" in word
            if self.print: print("b in word =", out)
            return out

        def c(word):
            self.c_called = True
            out = "c" in word
            if self.print: print("c in word =", out)
            return out

        def sa(word):
            self.sa_called = True
            out = word.startswith("a")
            if self.print: print("word starts with a =", out)
            return out

        def ea(word):
            self.ea_called = True
            out = word.endswith("a")
            if self.print: print("word ends with a =", out)
            return out

        def eb(word):
            self.eb_called = True
            out = word.endswith("b")
            if self.print: print("word ends with b =", out)
            return out

        g = gate([a, b, c], [sa, ea, eb])

        self.reset_gate_fast()
        self.assertFalse(g("word"))  # no includes, no excludes
        self.assert_gate_fast(True, True, True, False, False, False)

        if self.print: print("-----------------------------")
        self.reset_gate_fast()
        self.assertTrue(g("ward"))  # include cause of 'a', no excludes
        self.assert_gate_fast(True, False, False, True, True, True)

        if self.print: print("-----------------------------")
        self.reset_gate_fast()
        self.assertFalse(g("warb"))  # include cause of 'a', exclude cause of end 'b'
        self.assert_gate_fast(True, False, False, True, True, True)

        if self.print: print("-----------------------------")
        self.reset_gate_fast()
        self.assertFalse(g("dabba"))  # include cause of 'a', exclude cause of end 'a'
        self.assert_gate_fast(True, False, False, True, True, False)

        if self.print: print("-----------------------------")
        self.reset_gate_fast()
        self.assertFalse(g("a"))  # include cause of 'a', exclude cause of start 'a'
        self.assert_gate_fast(True, False, False, True, False, False)

    def assert_gate_fast(self, a, b, c, sa, ea, eb):
        self.assertEquals(self.a_called, a)
        self.assertEquals(self.b_called, b)
        self.assertEquals(self.c_called, c)
        self.assertEquals(self.sa_called, sa)
        self.assertEquals(self.ea_called, ea)
        self.assertEquals(self.eb_called, eb)

    def reset_gate_fast(self):
        self.a_called = False
        self.b_called = False
        self.c_called = False
        self.sa_called = False
        self.ea_called = False
        self.eb_called = False

    def test_gate_with_not_one_arg_predicates(self):
        one_default = self.make_one_default_arg()
        g = gate([one_default], [])
        self.assertFalse((g(True)))
        self.assertTrue((g(False)))

    def make_one_default_arg(self):
        def one_default_arg(foo=True):
            return not foo

        return one_default_arg

    #### function creation for test_is_all_predicate
    def is_bound_method(self, one_arg):
        pass

    def make_two_arg_predicate(self, foo, bar):
        def two_args(foo, bar):
            return False

        return two_args

    def make_one_arg_predicate(self, foo):
        def one_args(foo):
            return False

        return one_args

    def make_one_arg_default_arg(self):
        def one_arg_default_arg(bar, foo=True):
            return False

        return one_arg_default_arg

    def make_var_args(self):
        def var_args(*args):
            return False

        return var_args

    def make_kwargs(self):
        def kw_args(**kwargs):
            return False

        return kw_args

    def make_arg_var_args(self):
        def arg_var_args(normal_arg, *args):
            return normal_arg in args

        return arg_var_args

    def make_arg_kwargs(self):
        def arg_kw_args(kormal, **kwargs):
            return kormal in kwargs

        return arg_kw_args

    @unittest.skip("u d'nt wanna c all err msgs from " + __file__)
    def test_is_all_predicate(self):
        previous_value = set_stop_on_creation_error(False)

        LOG.warn("==> next 12 warn statements from %s"
                 % ".".join([self.__module__, self.__class__.__name__, "test_is_all_predicate"]))
        self.assertFalse(is_one_arg_predicate(TestGates))
        self.assertFalse(is_one_arg_predicate(TestGates()))
        self.assertFalse(is_one_arg_predicate(self.reset_gate_fast))
        self.assertFalse(is_one_arg_predicate(self.is_bound_method))
        self.assertFalse(is_one_arg_predicate(self.make_two_arg_predicate("", "")))
        self.assertFalse(is_one_arg_predicate(self.make_one_arg_default_arg()))
        self.assertFalse(is_one_arg_predicate(self.make_var_args()))
        self.assertFalse(is_one_arg_predicate(self.make_kwargs()))
        self.assertFalse(is_one_arg_predicate(self.make_arg_var_args()))
        self.assertFalse(is_one_arg_predicate(self.make_arg_kwargs()))
        self.assertFalse(is_one_arg_predicate(lambda x, y: x > y))

        app_home = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        # print(app_home)
        sys.path.append(app_home)
        module = importlib.import_module("util.gates")
        self.assertFalse(is_one_arg_predicate(module))

        self.assertTrue(is_one_arg_predicate(lambda word: "a" in word))
        self.assertTrue(is_one_arg_predicate(self.make_one_arg_predicate("")))
        self.assertTrue(is_one_arg_predicate(self.make_one_default_arg()))

        set_stop_on_creation_error(previous_value)
