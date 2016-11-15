#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:samp:`Publish resources under the ResourceSync Framework`

The class :class:`ResourceSync` is the main entrance to the rspub-core library. It is in essence a one-method
class, its main method: :func:`~ResourceSync.execute`. This method takes as argument ``filenames``:
a list of files and/or directories
to process. Upon execution :class:`ResourceSync` will call the correct :class:`~rspub.core.executors.Executor` that
will walk all the files and directories named in ``filenames`` and that takes care of creating the right type
of sitemap: resourcelist, changelist etc. and complete the corresponding
sitemaps as capabilitylist and description.

Before you call :func:`~ResourceSync.execute` on :class:`ResourceSync` it may be advisable to set the proper
parameters for your synchronization. :class:`ResourceSync` is a subclass of :class:`~rspub.core.rs_paras.RsParameters`
and the description of ``parameters`` in that class is a good starting point to learn about the type, meaning and
function of these parameters. Here we will highlight some and discuss aspects of these parameters.

Selecting resources
-------------------

The algorithm for selecting resources can be shaped by you, the user of this library. If the default algorithm
suites you - so much for the better - then you don't have to do anything and you can safely skip this paragraph.

The default algorithm is implemented
by the :class:`~rspub.util.gates.GateBuilder` class :class:`~rspub.pluggable.gate.ResourceGateBuilder`. This
default class builds a :func:`~rspub.util.gates.gate` that allows any file that is encountered in the list
of files and directories of the ``filenames`` argument. It will exclude however any file that
is not in :func:`~rspub.core.rs_paras.RsParameters.resource_dir` or any of its subdirectories, hidden files and
files from the directories :func:`~rspub.core.rs_paras.RsParameters.metadata_dir`,
:func:`~rspub.core.rs_paras.RsParameters.description_dir` and :func:`~rspub.core.rs_paras.RsParameters.plugin_dir`
in case any of these directories are situated on the search-paths described in ``filenames``.

You can implement your own resource :func:`~rspub.util.gates.gate` by supplying a class named
`ResourceGateBuilder` in a directory you specify under the
:func:`~rspub.core.rs_paras.RsParameters.plugin_dir` ``parameter``. Your `ResourceGateBuilder` should subclass
:class:`~rspub.pluggable.gate.ResourceGateBuilder` or at least implement the methods
:func:`~rspub.util.gates.GateBuilder.build_includes` and :class:`~rspub.util.gates.GateBuilder.build_excludes`.
A detailed description of how to create your own `ResourceGateBuilder` can be found in
:doc:`rspub.pluggable.gate <rspub.pluggable.gate>`.

By shaping your own selection algorithm you could for instance say "include all the files from directory `x` but
exclude the subdirectory `y` and from directory `z` choose only those files whose filenames start with 'abc' and
from directory `z/b` choose only xml-files where the x-path expression `//such/and/so` yields 'foo' or 'bar'."
Anything goes, as long as you can express it as a predicate, that is, say 'yes' or 'no' to a resource, given
the filename of the resource.


.. seealso:: :doc:`rspub.util.gates <rspub.util.gates>`, :doc:`rspub.pluggable.gate <rspub.pluggable.gate>`

Strategies and executors
------------------------

The :class:`~rspub.core.rs_enum.Strategy` tells :class:`ResourceSync` in what way you want your resources processed.
Or better: :class:`ResourceSync` will choose the :class:`~rspub.core.executors.Executor` that fits your chosen strategy.
Do you want new resourcelists every time you call :func:`ResourceSync.execute`, do you want
new changelists or perhaps an incremental changelist. There are slots for other strategies in rspub-core,
such as resourcedump and changedump, but these strategies are not yet implemented.

If new changelist or incremental changelist is your strategy and there is no resourcelist.xml yet in your
:func:`~rspub.core.rs_paras.RsParameters.metadata_dir` then :class:`ResourceSync` will create a resourcelist.xml
the first time you call :func:`~ResourceSync.execute`.

The :class:`~rspub.core.rs_enum.Strategy` ``resourcelist`` does not require much system resources. Resources will
be processed one after the other and sitemap documents are written to disk once they are processed and
these sitemaps will at most take 50000 records. The strategies ``new_changelist`` and ``inc_changelist`` will
compare previous and present state of all your selected resources. In order to do so they collect metadata from
all the present resources in your selection and compare it to the previous state as recorded in resourcelists
and subsequent changelists.
This will be perfectly OK in most situations, however if the number of resources is very large this
comparison might be undoable. Anyway, large amounts of resources will probably be managed by some kind of
repository system that enables to query for the requested data. It is perfectly alright to write your own
:class:`~rspub.core.executors.Executor` that handles the synchronisation of resources in your repository system
and you are invited to share these executors. A suitable plugin mechanism to accommodate such extraterrestrial
executors could be accomplished in a next version of rspub-core.

.. seealso:: :func:`rspub.core.rs_paras.RsParameters.strategy`, :class:`rspub.core.rs_enum.Strategy`, :doc:`rspub.core.executors <rspub.core.executors>`

Multiple collections
--------------------


"""
import logging
import os
from glob import glob

from rspub.core.exe_changelist import NewChangeListExecutor, IncrementalChangeListExecutor
from rspub.core.exe_resourcelist import ResourceListExecutor
from rspub.core.rs_enum import Strategy
from rspub.core.rs_paras import RsParameters
from rspub.util.observe import Observable, EventObserver

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

        if self.strategy == Strategy.resourcelist or start_new:
            executor = ResourceListExecutor(paras)
        elif self.strategy == Strategy.new_changelist:
            executor = NewChangeListExecutor(paras)
        elif self.strategy == Strategy.inc_changelist:
            executor = IncrementalChangeListExecutor(paras)

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
