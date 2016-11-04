#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging
import os
from glob import glob

from model.executor_changelist import NewChangelistExecutor, IncrementalChangelistExecutor
from model.executor_resourcelist import ResourceListExecutor
from model.executors import ExecutorParameters
from model.rs_enum import Strategy
from util.observe import Observable, Observer, EventObserver

LOG = logging.getLogger(__name__)

CLASS_NAME_RESOURCE_GATE_BUILDER = "ResourceGateBuilder"


class ResourceSync(Observable, ExecutorParameters):

    def __init__(self, **kwargs):
        Observable.__init__(self)
        ExecutorParameters.__init__(self, **kwargs)
        self.register(ExecutionHistory(self.abs_history_dir()))

    def abs_history_dir(self):
        if os.path.isabs(self.history_dir):
            return self.history_dir
        else:
            return self.abs_metadata_path(self.history_dir)

    def execute(self, filenames: iter, start_new=False):
        resourcelist_files = sorted(glob(os.path.join(self.abs_metadata_dir(), "resourcelist_*.xml")))
        start_new = start_new or len(resourcelist_files) == 0

        executor = None
        valid_strategy = self.valid_strategy()
        if valid_strategy == Strategy.new_resourcelist or start_new:
            executor = ResourceListExecutor(**self.__dict__)
        elif valid_strategy == Strategy.new_changelist:
            executor = NewChangelistExecutor(**self.__dict__)
        elif valid_strategy == Strategy.inc_changelist:
            executor = IncrementalChangelistExecutor(**self.__dict__)

        if executor:
            executor.register(*self.observers)
            executor.execute(filenames)
        else:
            raise NotImplementedError("Strategy not implemented: %s" % self.strategy)


class ExecutionHistory(EventObserver):

    def __init__(self, history_dir):
        self.history_dir = history_dir
        os.makedirs(self.history_dir, exist_ok=True)
        self.history_file = os.path.join(self.history_dir, "his.txt")

    def pass_inform(self, *args, **kwargs):
        #print(args)
        pass

    def inform_execution_start(self, *args, **kwargs):
        pass
