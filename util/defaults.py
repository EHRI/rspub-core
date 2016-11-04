#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import base64
import hashlib
import mimetypes
import os, time
import urllib.parse
import urllib.request
from datetime import datetime
from functools import partial


def sanitize_directory_path(path):
    if path:
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        if not os.path.exists(path):
            raise ValueError("Path does not exist: " + path)
        elif not os.path.isdir(path):
            raise ValueError("Not a directory: " + path)
        if not path.endswith(os.path.sep):
            path += os.path.sep

    return sanitize_string(path)


def sanitize_source_desc(path):
    if path:
        if not path.endswith(".well-known/resourcesync"):
            if not path.endswith("/"):
                path += "/"
            path += ".well-known/resourcesync"
    else:
        path = "/.well-known/resourcesync"
    return path


def sanitize_url_prefix(value):
    if value:
        parts = urllib.parse.urlparse(value)
        if parts[0] not in ["http", "https"]: # scheme
            raise ValueError("URL schemes allowed are 'http' or 'https'. Given: " + value)
        if parts[1] == "": # netloc
            raise ValueError("URL should have a domain. Given: " + value)
        if parts[4] != "": # query
            raise ValueError("URL should not have a query string. Given: " + value)
        if parts[5] != "": # fragment
            raise ValueError("URL should not have a fragment. Given: " + value)

        if not value.endswith("/"):
            value += "/"

    return sanitize_string(value)

def sanitize_url_path(value):
    if value:
        value = urllib.parse.quote(value.replace("\\", "/"))
    return sanitize_string(value)

def sanitize_string(value):
    if (not value):
        value = ""
    return value


def w3c_datetime(i):
    """ given seconds since the epoch, return a dateTime string.
    from: https://gist.github.com/mnot/246088
    """
    assert type(i) in [int, float]
    year, month, day, hour, minute, second, wday, jday, dst = time.gmtime(i)
    o = str(year)
    if (month, day, hour, minute, second) == (1, 1, 0, 0, 0): return o
    o += '-%2.2d' % month
    if (day, hour, minute, second) == (1, 0, 0, 0): return o
    o += '-%2.2d' % day
    if (hour, minute, second) == (0, 0, 0): return o
    o += 'T%2.2d:%2.2d' % (hour, minute)
    if second != 0:
        o += ':%2.2d' % second
    o += 'Z'
    return o


def w3c_now():
    return w3c_datetime(datetime.now().timestamp())


def md5_for_file(filename, block_size=2**14):
    """Compute MD5 digest for a file

    Optional block_size parameter controls memory used to do MD5 calculation.
    This should be a multiple of 128 bytes.
    """
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, block_size), b''):
            d.update(buf)

    return base64.b64encode(d.digest()).decode('utf-8')


def mime_type(filename):
    """ Not too reliable mime type analyzer."""
    url = urllib.request.pathname2url(filename)
    return mimetypes.guess_type(url)[0]


