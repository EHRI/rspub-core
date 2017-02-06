#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

from rspub.core.sender import ScpTransport


class TestScpTransport(unittest.TestCase):

    def test_scp_put(self):
        #scp_put(self, server, port, user, password):
        server = "localhost"
        port = 2222
        user = "user"
        password = "user"

        trans = ScpTransport(server, port, user, password)
        files = "/Users/ecco/tmp/resource-dump1.xml"
        trans.scp_put(files)