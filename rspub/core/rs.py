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
:func:`~rspub.util.gates.GateBuilder.build_includes` and :func:`~rspub.util.gates.GateBuilder.build_excludes`.
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

:class:`ResourceSync` is a subclass of :class:`~rspub.core.rs_paras.RsParameters` and so the parameters set on
:class:`ResourceSync` can be saved and reinstituted later on. :class:`~rspub.core.config.Configurations` has
methods for listing and removing previously saved configurations. Multiple collections of resources
could be synchronized, each collection with its own configuration. Synchronizing the collection 'spam' could
go along these lines::

    # get a list of previously saved configurations
    [print(x) for x in Configurations.list_configurations()]
    # rspub_core
    # spam_config
    # eggs_config

    # prepare for synchronization of collection 'all about spam'
    resourcesync = ResourceSync(config_name="spam_config")
    # spam resources are in two directories
    filenames = ["resources/green_spam", "resources/blue_spam"]
    # do the synchronization
    resourcesync.execute(filenames)


.. seealso:: :class:`rspub.core.rs_paras.RsParameters`, :class:`rspub.core.config.Configurations`, :func:`~rspub.core.rs_paras.RsParameters.save_configuration_as`

Observe execution
-----------------

:class:`ResourceSync` is a subclass of :class:`~rspub.util.observe.Observable`. The executor to which the execution
is delegated inherits all observers registered with :class:`ResourceSync`. :class:`ResourceSync` it self does not
fire events.

.. seealso::  :doc:`rspub.util.observe <rspub.util.observe>`, :class:`rspub.core.executors.ExecutorEvent`

"""
import logging
import os
from glob import glob

from rspub.core.exe_changelist import NewChangeListExecutor, IncrementalChangeListExecutor
from rspub.core.exe_resourcelist import ResourceListExecutor
from rspub.core.rs_enum import Strategy
from rspub.core.rs_paras import RsParameters
from rspub.core.selector import Selector
from rspub.util import defaults
from rspub.util.observe import Observable, EventObserver

LOG = logging.getLogger(__name__)


class ResourceSync(Observable, RsParameters):
    """
    :samp:`Main class for ResourceSync publishing`

    """

    def __init__(self, **kwargs):
        """
        :samp:`Initialization`

        :param str config_name: the name of the configuration to read. If given, sets the current configuration.
        :param kwargs: see :func:`rspub.core.rs_paras.RsParameters.__init__`

        .. seealso::  :doc:`rspub.core.rs_paras <rspub.core.rs_paras>`
        """
        Observable.__init__(self)
        RsParameters.__init__(self, **kwargs)

    def execute(self, filenames: iter=None, start_new=False):
        """
        :samp:`Publish ResourceSync documents under conditions of current {parameters}`

        Call appropriate executor and publish sitemap documents on the resources found in `filenames`.

        If no file/files 'resourcelist_*.xml' are found in metadata directory will always dispatch to
        strategy (new) ``resourcelist``.

        If ``parameter`` :func:`~rspub.core.rs_paras.RsParameters.is_saving_sitemaps` is ``False`` will do
        a dry run: no existing sitemaps will be changed and no new sitemaps will be written to disk.

        :param filenames: filenames and/or directories to scan
        :param start_new: erase metadata directory and create new resourcelists
        """
        # always start fresh publication with resourcelist
        resourcelist_files = sorted(glob(self.abs_metadata_path("resourcelist_*.xml")))
        start_new = start_new or len(resourcelist_files) == 0

        # do we have filenames or look for a saved Selector?
        if filenames is None and self.selector_file:
            try:
                filenames = Selector(self.selector_file)
                LOG.info("Loaded selector from '%s'" % self.selector_file)
            except Exception as err:
                LOG.warn("Unable to load selector: {0}".format(err))

        if filenames is None:
            raise RuntimeError("Unable to execute: no filenames.")

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

        # associate current parameters with a selector
        if isinstance(filenames, Selector):
            if filenames.location:
                try:
                    filenames.write()
                    self.selector_file = filenames.abs_location()
                    LOG.info("Associated parameters '%s' with selector at '%s'"
                             % (self.configuration_name(), self.selector_file))
                except Exception as err:
                    LOG.warn("Unable to save selector: {0}".format(err))

        # set a timestamp
        if self.is_saving_sitemaps:
            self.last_execution = defaults.w3c_now()

        self.save_configuration(True)


class ExecutionHistory(EventObserver):
    """
    :samp:`Execution report creator`

    Currently not in use.
    """

    def __init__(self, history_dir):
        self.history_dir = history_dir
        os.makedirs(self.history_dir, exist_ok=True)
        self.history_file = os.path.join(self.history_dir, "his.txt")

    def pass_inform(self, *args, **kwargs):
        #print(args)
        pass

    def inform_execution_start(self, *args, **kwargs):
        print(args, kwargs)
