#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup

version = {}
with open("rspub/version.py") as fp:
    exec(fp.read(), version)
# later on we use: version['__version__']

setup(
    name='rspub-core',
    version=version['__version__'],
    packages=['rspub.util', 'rspub.pluggable', 'rspub.core', 'rspub.cli'],
    url='https://github.com/EHRI/rspub-core',
    license='Apache License 2.0',
    author='henk van den berg',
    author_email='henk.van.den.berg at dans.knaw.nl',
    description='Core Python library for ResourceSync publishing',
    install_requires=['resyncehri', 'validators', 'paramiko', 'scp']
)
