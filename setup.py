from distutils.core import setup

setup(
    name='rspub-core',
    version='0.1',
    packages=['src/resync', 'util', 'pluggable', 'model'],
    url='https://github.com/EHRI/rspub-core',
    license='Apache License 2.0',
    author='henk van den berg',
    author_email='henk.van.den.berg at dans.knaw.nl',
    description='Core Python library for ResourceSync publishing'
)
