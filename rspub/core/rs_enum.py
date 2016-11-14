#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum, unique


@unique
class Strategy(Enum):
    resourcelist = 0
    new_changelist = 1
    inc_changelist = 2
    # resourcedump = 3 # not implemented
    # changedump = 4 # not implemented

    @staticmethod
    def names():
        """
        Get the names of this Enum, whithout other method names.
        :return: List<str> of names
        """
        names = dir(Strategy)
        return [x for x in names if not x.startswith("_")]

    @staticmethod
    def sanitize(name):
        try:
            strategy = Strategy[name]
            return strategy.name
        except KeyError as err:
            raise ValueError(err)

    @staticmethod
    def strategy_for(value):
        if isinstance(value, Strategy):
            return value
        elif isinstance(value, int):
            return Strategy(value)
        else:
            return Strategy[value]


class Capability(Enum):

    resourcelist = 0
    changelist = 1
    resourcedump = 2
    changedump = 3
    resourcedump_manifest = 4
    changedump_manifest = 5
    capabilitylist = 6
    description = 7