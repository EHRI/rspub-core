#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import inspect
import logging
import os
import re
from abc import ABCMeta, abstractmethod

from util.gates import or_, and_, gate, is_one_arg_predicate, GateCreationException
from util.plugg import Inspector, has_function


def hidden_file_predicate():
    # in Python 3.5 this should work
    # return lambda file_path : bool(os.stat(file_path).st_file_attributes & os.stat.FILE_ATTRIBUTE_HIDDEN)
    return lambda file_path: isinstance(file_path, str) and os.path.basename(file_path).startswith(".")


def directory_pattern_predicate(name_pattern=""):
    pattern = re.compile(name_pattern)
    return lambda file_path: isinstance(file_path, str) and pattern.search(os.path.dirname(file_path))


def filename_pattern_predicate(name_pattern=""):
    pattern = re.compile(name_pattern)
    return lambda file_path: isinstance(file_path, str) and pattern.search(os.path.basename(file_path))


def last_modified_after_predicate(t=0):
    def _file_attribute_filter(file_path):
        if not os.path.exists(file_path):
            return False
        else:
            lm = os.stat(file_path).st_mtime
            return lm > t

    return _file_attribute_filter
