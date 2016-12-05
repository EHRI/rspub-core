#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
import logging
import os
from enum import Enum
from itertools import takewhile

from rspub.util.observe import Observable

LOG = logging.getLogger(__name__)


class SelectorEvent(Enum):

    file_does_not_exist = 0
    not_a_regular_file = 1
    file_excluded = 2


class Selector(Observable):

    def __init__(self, location=None):
        Observable.__init__(self)
        self.location = location
        self._includes = set()
        self._excludes = set()
        if self.location:
            self.read(self.location)

        self._abs_excludes = None
        self._exc_count = 0

    def __iter__(self):
        # alternative implementation would take 2 blobs of filenames (recursive through directories) in memory:
        # abs_includes = {x for x in self.list_includes()}
        # abs_excludes = {x for x in self.list_excludes()}
        # abs_includes.difference_update(abs_excludes)
        # return iter(sorted(abs_includes))

        # this implementation only expands the excludes to absolute paths (not recursive) and yields the includes.
        #   + less memory but
        #   - repeatedly iterating the abs_excludes but
        #   + sorted output
        self._abs_excludes = {os.path.abspath(x) for x in self._excludes}
        self._exc_count = len(self._abs_excludes)
        generator = self._file_generator()
        return generator(sorted(self._includes))

    def __len__(self):
        return len([x for x in self])

    def _file_generator(self):

        def generator(filenames):
            for name in filenames:
                file = os.path.abspath(name)
                if not os.path.exists(file):
                    LOG.warning("File does not exist: %s" % file)
                    self.observers_inform(self, SelectorEvent.file_does_not_exist, filename=file)
                elif os.path.isdir(file):
                    for rfile in generator(self._walk_directories(file)):
                        yield  rfile
                elif os.path.isfile(file):
                    if len(list(takewhile(lambda x: not file.startswith(x), self._abs_excludes))) == self._exc_count:
                        yield file
                    else:
                        if not self.observers_confirm(self, SelectorEvent.file_excluded, filename=file):
                            break
                else:
                    LOG.warning("Not a regular file: %s" % file)
                    self.observers_inform(self, SelectorEvent.not_a_regular_file, filename=file)

        return generator

    @staticmethod
    def _walk_directories(*directories):
        for directory in directories:
            abs_dir = os.path.abspath(directory)
            for root, _directories, _filenames in os.walk(abs_dir):
                for filename in _filenames:
                    file = os.path.join(root, filename)
                    yield file

    def include(self, *filenames):
        for item in filenames:
            if isinstance(item, str):
                self._includes.add(item)
            elif isinstance(item, Selector):
                self._includes.update(item._includes)
            elif hasattr(item, '__iter__'):
                for thing in item:
                    self.include(thing)
            else:
                raise ValueError("Illegal argument: %s" % item)

    def exclude(self, *filenames):
        for item in filenames:
            if isinstance(item, str):
                self._excludes.add(item)
            elif isinstance(item, Selector):
                self._excludes.update(item._excludes)
            elif hasattr(item, '__iter__'):
                for thing in item:
                    self.exclude(thing)
            else:
                raise ValueError("Illegal argument: %s" % item)

    def discard_include(self, *filenames):
        for item in filenames:
            if isinstance(item, str):
                self._includes.discard(item)
            elif isinstance(item, Selector):
                self._includes.difference_update(item._includes)
            elif hasattr(item, '__iter__'):
                for thing in item:
                    self.discard_include(thing)
            else:
                raise ValueError("Illegal argument: %s" % item)

    def discard_exclude(self, *filenames):
        for item in filenames:
            if isinstance(item, str):
                self._excludes.discard(item)
            elif isinstance(item, Selector):
                self._excludes.difference_update(item._excludes)
            elif hasattr(item, '__iter__'):
                for thing in item:
                    self.discard_exclude(thing)
            else:
                raise ValueError("Illegal argument: %s" % item)

    def clear_includes(self):
        self._includes.clear()

    def clear_excludes(self):
        self._excludes.clear()

    def list_includes(self):
        return self._list_files()(sorted(self._includes))

    def list_excludes(self):
        return self._list_files()(sorted(self._excludes))

    def _list_files(self):

        def generator(filenames):
            for name in filenames:
                file = os.path.abspath(name)
                if not os.path.exists(file):
                    LOG.warning("File does not exist: %s" % file)
                elif os.path.isdir(file):
                    for rfile in generator(self._walk_directories(file)):
                        yield  rfile
                    pass
                elif os.path.isfile(file):
                    yield file
                else:
                    LOG.warning("Not a regular file: %s" % file)

        return generator

    def relativize_includes(self, root_path):
        self._includes = {os.path.relpath(x, root_path) for x in self._includes}
        return self.get_included_entries()

    def relativize_excludes(self, root_path):
        self._excludes = {os.path.relpath(x, root_path) for x in self._excludes}
        return self.get_excluded_entries()

    def get_included_entries(self):
        return self._includes

    def get_excluded_entries(self):
        return self._excludes

    def is_empty(self):
        return len(self._includes) + len(self._excludes) == 0

    def read_includes(self, filename):
        with open(filename, "r") as file:
            self.include(file.read().splitlines())

    def read_excludes(self, filename):
        with open(filename, "r") as file:
            self.exclude(file.read().splitlines())

    def write_includes(self, filename):
        with open(filename, 'w') as file:
            for item in sorted(self._includes):
                file.write("{}\n".format(item))

    def write_excludes(self, filename):
        with open(filename, 'w') as file:
            for item in sorted(self._excludes):
                file.write("{}\n".format(item))

    def write(self, filename=None):
        if filename is None:
            filename = self.location
        if filename is None:
            raise RuntimeError("No filename, no location. Cannot save selector.")
        with open(filename, 'w') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_ALL)
            for item in self._includes:
                writer.writerow(["+", item])
            for item in self._excludes:
                writer.writerow(["-", item])
        self.location = filename

    def read(self, filename):
        filename = os.path.abspath(filename)
        row_count = 0
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                row_count += 1
                if row[0] == "+":
                    self.include(row[1])
                elif row[0] == "-":
                    self.exclude(row[1])
                else:
                    raise RuntimeError("Invalid line in file: line %d: %s, file='%s'" % (row_count, row, filename))

    def abs_location(self):
        if self.location:
            return os.path.abspath(self.location)
        else:
            return None



