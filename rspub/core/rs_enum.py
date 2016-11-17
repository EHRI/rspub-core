#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum, unique


@unique
class Strategy(Enum):
    """
    :samp:`Strategy for ResourceSync Publishing`
    """
    resourcelist = 0
    """
    ``0`` :samp:`New resourcelist {strategy}`

    Create new resourcelist(s) every run.
    """
    new_changelist = 1

    """
    ``1`` :samp:`New changelist {strategy}`

    Create a new changelist every run.
    If no resourcelist was found in the metadata directory switch to new resourcelist strategy.
    """
    inc_changelist = 2
    """
    ``2`` :samp:`Incremental changelist {strategy}`

    Add changes to an existing changelist. If no changelist exists, create a new one.
    If no resourcelist was found in the metadata directory switch to new resourcelist strategy.
    """
    # resourcedump = 3 # not implemented
    # changedump = 4 # not implemented

    @staticmethod
    def names():
        """
        :samp:`Get Strategy names`

        :return: List<str> of names
        """
        names = dir(Strategy)
        return [x for x in names if not x.startswith("_")]

    @staticmethod
    def sanitize(name):
        """
        :samp:`Verify a {Strategy} name`

        :param str name: string to test
        :return: name if it is the name of a strategy
        :raises: :exc:`ValueError` if the given name is not the name of a strategy
        """
        try:
            strategy = Strategy[name]
            return strategy.name
        except KeyError as err:
            raise ValueError(err)

    @staticmethod
    def strategy_for(value):
        """
        :samp:`Get a Strategy for the given value`

        :param value: may be :class:`Strategy`, str or int
        :return: :class:`Strategy`
        :raises: :exc:`KeyError` if the given value could not be converted to a :class:`Strategy`
        """
        if isinstance(value, Strategy):
            return value
        elif isinstance(value, int):
            return Strategy(value)
        else:
            return Strategy[value]


class Capability(Enum):
    """
    :samp:`Capabilities as defined in the ResourceSync Framework`

    """
    resourcelist = 0
    """
    ``0`` :samp:`resourcelist`
    """
    changelist = 1
    """
    ``1`` :samp:`changelist`
    """
    resourcedump = 2
    """
    ``2`` :samp:`resourcedump`
    """
    changedump = 3
    """
    ``3`` :samp:`changedump`
    """
    resourcedump_manifest = 4
    """
    ``4`` :samp:`resourcedump_manifest`
    """
    changedump_manifest = 5
    """
    ``5`` :samp:`changedump_manifest`
    """
    capabilitylist = 6
    """
    ``6`` :samp:`capabilitylist`
    """
    description = 7
    """
    ``7`` :samp:`description`
    """
