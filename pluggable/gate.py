#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from util.gates import GateBuilder, not_
from util.resourcefilter import directory_pattern_predicate, hidden_file_predicate


class ResourceGateBuilder(GateBuilder):

    def __init__(self, resource_dir=None, metadata_dir=None, plugin_dir=None):
        self.resource_dir = resource_dir
        self.metadata_dir = metadata_dir
        self.plugin_dir = plugin_dir

    def build_includes(self, includes: list):
        if self.resource_dir:
            includes.append(directory_pattern_predicate("^" + self.resource_dir))

        return includes

    def build_excludes(self, excludes: list):
        # exclude everything outside the resource directory
        if self.resource_dir:
            excludes.append(not_(directory_pattern_predicate("^" + self.resource_dir)))

        excludes.append(hidden_file_predicate())

        # exclude metadata dir and plugin dir (in case they happen to be on the search path and within resource dir).
        if self.metadata_dir:
            excludes.append(directory_pattern_predicate(("^" + self.metadata_dir)))

        if self.plugin_dir:
            excludes.append(directory_pattern_predicate(("^" + self.plugin_dir)))

        return excludes
