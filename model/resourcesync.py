#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
from glob import glob

from model.exe_changelist import NewChangelistExecutor, IncrementalChangelistExecutor
from model.exe_resourcelist import ResourceListExecutor
from model.rs_enum import Strategy
from model.rs_paras import RsParameters
from util.observe import Observable, EventObserver

LOG = logging.getLogger(__name__)


class ResourceSync(Observable, RsParameters):

    def __init__(self, **kwargs):
        Observable.__init__(self)
        RsParameters.__init__(self, **kwargs)

    def execute(self, filenames: iter, start_new=False):
        resourcelist_files = sorted(glob(self.abs_metadata_path("resourcelist_*.xml")))
        start_new = start_new or len(resourcelist_files) == 0
        paras = RsParameters(**self.__dict__)
        executor = None

        if self.strategy == Strategy.new_resourcelist or start_new:
            executor = ResourceListExecutor(paras)
        elif self.strategy == Strategy.new_changelist:
            executor = NewChangelistExecutor(paras)
        elif self.strategy == Strategy.inc_changelist:
            executor = IncrementalChangelistExecutor(paras)

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
        print(args, kwargs)
