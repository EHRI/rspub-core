from setuptools import setup

setup(
    name='rspub-core',
    version='0.1',
    packages=['rspub.util', 'rspub.pluggable', 'rspub.core', 'rspub.cli'],
    url='https://github.com/EHRI/rspub-core',
    license='Apache License 2.0',
    author='henk van den berg',
    author_email='henk.van.den.berg at dans.knaw.nl',
    description='Core Python library for ResourceSync publishing',
    install_requires=['resync', 'validators']
)
