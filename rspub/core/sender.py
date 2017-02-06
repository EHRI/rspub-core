#! /usr/bin/env python3
# -*- coding: utf-8 -*-
from rspub.core.rs_paras import RsParameters


class Zipper(object):

    def __init__(self, paras):
        assert isinstance(paras, RsParameters)
        self.paras = paras

    def enabled(self):
        return self.paras.last_execution is not None

    def create_zip(self):
        if not self.enabled():
            return

