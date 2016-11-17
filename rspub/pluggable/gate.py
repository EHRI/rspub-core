#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:samp:`Pluggable resource gate and builder`

Build your own
--------------

The selection mechanism for resources is implemented as a :func:`~rspub.util.gates.gate` that uses
predicates for including and excluding resources based on their filename.
The :class:`~rspub.pluggable.gate.ResourceGateBuilder` hook allows you to shape this resource gate and adapt it
completely to your needs. You can build your own ResourceGateBuilder by creating a class that subclasses
:class:`rspub.pluggable.gate.ResourceGateBuilder` or - to avoid dependencies in your code - that implements the two
methods :func:`~rspub.util.gates.GateBuilder.build_includes` and :func:`~rspub.util.gates.GateBuilder.build_excludes`.
In any case your gate builder should be named ResourceGateBuilder, because by this name your plugin will be
recognized by rspub-core.

Register a ResourceGateBuilder
++++++++++++++++++++++++++++++

Your ResourceGateBuilder should be placed in a directory that is registered
as :func:`~rspub.core.rs_paras.RsParameters.plugin_dir` at :class:`~rspub.core.rs.ResourceSync`.
(There may be multiple ResourceGateBuilders in your plugin directory but this could unnecessarily complicate
the building process.)

Build predicates
++++++++++++++++

Predicates you supply in the lists of including and excluding predicates should be one-argument predicates
that take the filename of a resource as input. The logic in your predicates could take advantage of the
logical functions offered by :mod:`rspub.util.gates` and file selection filters offered
in :mod:`rspub.util.resourcefilter`.

Example: Construct a predicate for directory names that end with 'abc'::

    import rspub.util.resourcefilter as rf
    dir_ends_with_abc = rf.directory_pattern_predicate("abc$")

    assert dir_ends_with_abc("/foo/bar/folder_abc/my_resource.txt")
    assert not dir_ends_with_abc("/foo/bar/folder_def/my_resource.txt")


Example: Construct a predicate for xml files::

    xml_file = rf.filename_pattern_predicate(".xml$")

    assert xml_file("my_resource.xml")
    assert not xml_file("my_resource.txt")

Example: Construct a predicate for xml files in folders that end with 'abc'::

    import rspub.util.gates as lf
    xml_file_in_abc = lf.and_(dir_ends_with_abc, xml_file)

    assert xml_file_in_abc("/foo/bar/folder_abc/my_resource.xml")
    assert not xml_file_in_abc("/foo/bar/folder_abc/my_resource.txt")
    assert not xml_file_in_abc("/foo/bar/folder_def/my_resource.xml")

Example: Construct a predicate for files modified after 31 July 2016::

    recent = rf.last_modified_after_predicate("2016-08-01")

Example: Test a gate that will allow xml files from folders that end with 'abc', but that excludes files modified
after 31 July 2016::

    includes = [xml_files_in_abc]
    excludes = [recent]
    resource_gate = lf.gate(includes, excludes)

If you are satisfied with your gate the `includes` and `excludes` can be contributed by your ResourceGateBuilder.

Implement the build methods
+++++++++++++++++++++++++++

When implementing the build methods :func:`~rspub.util.gates.GateBuilder.build_includes`
and :func:`~rspub.util.gates.GateBuilder.build_excludes` it is good to know that the first builder in the chain
is the default :class:`ResourceGateBuilder` as implemented below. It defines the includes very wide: allow anything
found in the :func:`~rspub.core.rs_paras.RsParameters.resource_dir`. In order to effectively contribute your
including predicates, you should not append them to the given list but replace the list with your own list
of predicates. The excluding list as defined by the default class:`ResourceGateBuilder` contains niceties as
filter out hidden files, exclude files in your :func:`~rspub.core.rs_paras.RsParameters.metadata_dir` etc.
If these default excluding predicates are not in your way you can append your excludes to this default list
in the method :func:`~rspub.util.gates.GateBuilder.build_excludes`.

"""
from rspub.util.gates import GateBuilder, not_
from rspub.util.resourcefilter import directory_pattern_predicate, hidden_file_predicate


class ResourceGateBuilder(GateBuilder):
    """
    :samp:`Default {ResourceGateBuilder}`

    This
    default class builds a :func:`~rspub.util.gates.gate` that allows any file that is encountered.
    It will exclude however any file that
    is not in :func:`~rspub.core.rs_paras.RsParameters.resource_dir` or any of its subdirectories, hidden files and
    files from the directories :func:`~rspub.core.rs_paras.RsParameters.metadata_dir`,
    :func:`~rspub.core.rs_paras.RsParameters.description_dir` and :func:`~rspub.core.rs_paras.RsParameters.plugin_dir`.
    """

    def __init__(self, resource_dir=None, metadata_dir=None, plugin_dir=None, description_dir=None):
        self.resource_dir = resource_dir
        self.metadata_dir = metadata_dir
        self.plugin_dir = plugin_dir
        self.description_dir = description_dir

    def build_includes(self, includes: list):
        if self.resource_dir:
            includes.append(directory_pattern_predicate("^" + self.resource_dir))

        return includes

    def build_excludes(self, excludes: list):

        # exclude everything outside the resource directory
        if self.resource_dir:
            excludes.append(not_(directory_pattern_predicate("^" + self.resource_dir)))

        excludes.append(hidden_file_predicate())

        # exclude metadata dir, description_dir and plugin dir
        # (in case they happen to be on the search path and within resource dir).
        if self.metadata_dir:
            excludes.append(directory_pattern_predicate(("^" + self.metadata_dir)))

        if self.description_dir:
            excludes.append(directory_pattern_predicate(("^" + self.description_dir)))

        if self.plugin_dir:
            excludes.append(directory_pattern_predicate(("^" + self.plugin_dir)))

        return excludes
