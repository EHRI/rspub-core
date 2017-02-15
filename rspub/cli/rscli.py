#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
:samp:`Command line interface to publish resources under the ResourceSync Framework`

The module :class:`rscli.py` offers an interface to configure, select and run the publishing of resources under
the `ResourceSync framework <http://www.openarchives.org/rs/1.0.9/resourcesync>`_. Start `rscli` from anywhere
on the system::

    python3 rspub/cli/rscli.py

The internals of the command line interface resemble a three-room house. You enter the house in
the ``rspub`` room. From there you can enter the rooms ``configure`` and ``select``. You leave the rooms and
the house by typing ``exit``. In all rooms you can get help by typing ``help``.

.. figure:: ../../img/rscli.png

    Fig. 1. Geography of `rscli`.

"""
import sys
import traceback

if sys.version_info[0] < 3:
    raise RuntimeError("Your Python has version 2. This application needs Python3.x")

import os
import cmd, glob

# Start this module from anywhere on the system: append root directory of project.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
#                rspub-core         rspub           cli               rscli.py
from rspub.core.rs import ResourceSync
from rspub.core.selector import Selector
from rspub.util.observe import EventObserver
from rspub.core.rs_paras import RsParameters
from rspub.core.config import Configuration, Configurations
from rspub.core.rs_enum import Strategy, SelectMode

# Set up gnureadline as readline if installed.
__GNU_READLINE__ = False
try:
    import gnureadline
    sys.modules['readline'] = gnureadline
    __GNU_READLINE__ = "gnu"
except ImportError:
    pass


PARAS = RsParameters()
SELECTOR = None


def str2bool(v, none=False):
    if v:
        return v.lower() in ["yes", "y", "true", "t", "1", "on", "o"]
    else:
        return none


#####################################################################################################
class SuperCmd(cmd.Cmd):

    _complete_ = "-> Press 2 x <tab> for options, 1 x <tab> for completion.\n" if __GNU_READLINE__ else ""
    _complete_ += "-> For help type: help"

    stop = False

    def __init__(self):
        cmd.Cmd.__init__(self)

    def __complete_path__(self, text, line, begidx, endidx):
        # see: http://stackoverflow.com/questions/16826172/filename-tab-completion-in-cmd-cmd-of-python#27256663
        before_arg = line.rfind(" ", 0, begidx)
        if before_arg == -1:
            return  # arg not found

        fixed = line[before_arg + 1:begidx]  # fixed portion of the arg
        arg = line[before_arg + 1:endidx]
        pattern = arg + '*'

        completions = []
        for path in glob.glob(pattern):
            path = self._append_slash_if_dir(path)
            completions.append(path.replace(fixed, "", 1))
        return completions

    def _append_slash_if_dir(self, p):
        if p and os.path.isdir(p) and p[-1] != os.sep:
            return p + os.sep
        else:
            return p

    def __confirm__(self, question):
        self.stdout.write(self.prompt + question + " (yes | no) ")
        self.stdout.flush()
        line = self.stdin.readline()
        if not len(line):
            line = 'EOF'
        else:
            line = line.rstrip('\r\n')
        return str2bool(line)

    def __ask__(self, question):
        self.stdout.write(self.prompt + question + " ")
        self.stdout.flush()
        line = self.stdin.readline()
        if not len(line):
            line = 'EOF'
        else:
            line = line.rstrip('\r\n')
        return line

    def postcmd(self, stop, line):
        # Hook method executed just after a command dispatch is finished
        return self.stop

    def do_exit(self, line):
        self.stop = True

    def help_exit(self):
        print("exit\n\tExit", self.__class__.__name__)

    def do_EOF(self, line):
        """
EOF, Ctrl+D, Ctrl+C::

    Exit the application.

        """
        print("Bye from", __file__)
        sys.exit()

    @staticmethod
    def complete_configuration(text):
        if not text:
            completions = Configurations.list_configurations()[:]
        else:
            completions = [x for x in Configurations.list_configurations() if x.startswith(text)]
        return completions

    def do_list_configurations(self, line):
        """
list_configurations::

    List saved configurations

        """
        print("====================")
        print("Saved configurations")
        print("====================")
        for config in Configurations.list_configurations():
            print(config)
        print("")
        print("====================")

    def do_list_parameters(self, line):
        """
list_parameters::

    List current parameters

        """
        print("================================================================================")
        print("Parameters for Metadata Publishing")
        print("================================================================================")
        print(PARAS.describe(True))
        print("================================================================================")


#####################################################################################################
class RsPub(SuperCmd, EventObserver):

    prompt = "rspub > "
    intro = "================================================== \n" + \
            "Command Line Interface for ResourceSync Publishing \n" + \
            "================================================== \n" + SuperCmd._complete_

    def __init__(self):
        SuperCmd.__init__(self)

    def do_configure(self, line):
        """
configure::

    Switch to configuration mode

        """
        Configure().cmdloop()

    def do_select(self, line):
        """
select::

    Switch to select mode

        """
        Select().cmdloop()

    def do_run(self, line):
        """
run::

    run rspub with the current configuration.

        """
        # SELECTOR ->   yes ->   SELECTOR.location -> yes -> associated -> yes -> [runs]
        #   no|                       no|                      no|
        # P.selector > y > [run]    [runs]                 P.selector -> yes -> ask ->yes-> [runs]
        #   no|                                                no|               no|
        # [abort]                                             [runs]           [abort]
        # ----------------------------------------------------------------------------------------
        global PARAS
        global SELECTOR
        run = False     # rs.execute()
        runs = False    # rs.execute(SELECTOR)
        abort = False

        if PARAS.select_mode == SelectMode.simple and PARAS.simple_select_file:
            SELECTOR = Selector()
            SELECTOR.include(PARAS.simple_select_file)

        if SELECTOR is None:
            if PARAS.selector_file is None:
                abort = "No selector and configuration not associated with selector. Run aborted."
            else:
                run = True
        else:
            if SELECTOR.location is None \
                    or SELECTOR.abs_location() == PARAS.selector_file \
                    or PARAS.selector_file is None:
                runs = True
            elif self.__confirm__("Associate current configuration with selector?"):
                runs = True
            else:
                abort = "Not associating current configuration with selector. Run aborted."

        if abort:
            print(abort)
        elif run or runs:
            try:
                rs = ResourceSync(**PARAS.__dict__)
                rs.register(self)
                rs.execute(SELECTOR)   # == rs.execute() if SELECTOR is None for [run]
                PARAS = RsParameters(**rs.__dict__) # catch up with updated paras
            except Exception as err:
                traceback.print_exc()
                print("\nUncompleted run: {0}".format(err))
        else: # we should not end here!
            location = None
            if SELECTOR:
                location = SELECTOR.abs_location()
            print("Missed a path in tree: ", SELECTOR, location, PARAS.selector_file)

    def do_exit(self, line):
        """
EOF, Ctrl+D, Ctrl+C::

    Exit the application.

        """
        self.do_EOF(line)

    # EventObserver callbacks
    def confirm_clear_metadata_directory(self, *args, **kwargs):
        return self.__confirm__("Clear metadata directory '%s'?" % kwargs["metadata_dir"])

    @staticmethod
    def inform_completed_document(*args, **kwargs):
        event = args[1].name
        sitemap_data = kwargs["sitemap_data"]
        path = ", sitemap: " + sitemap_data.path
        resource_count = ", resources: " + str(sitemap_data.resource_count)
        print(event, resource_count, path)

    @staticmethod
    def inform_execution_end(*args, **kwargs):
        event = args[1].name
        new_sitemaps = kwargs["new_sitemaps"]
        print(event)
        print("\tsitemaps created or updated:", len(new_sitemaps))
        for smd in new_sitemaps:
            print("\t", smd.capability_name, smd.path, "count:", smd.resource_count, "saved:", smd.document_saved)


#####################################################################################################
class Configure(SuperCmd):

    prompt = "configure > "
    intro = "============================= \n" + \
            "Configure Metadata Publishing \n" + \
            "============================= \n" + SuperCmd._complete_

    def __init__(self):
        SuperCmd.__init__(self)

    def do_open_configuration(self, name):
        """
open_configuration [name]::

    Open a saved configuration

        """
        global PARAS
        if name:
            try:
                PARAS = RsParameters(config_name=name)
                self.do_list_parameters(name)
            except ValueError as err:
                print("\nIllegal argument: {0}".format(err))
        else:
            print("Open a configuration. Specify a name:")
            self.do_list_configurations(name)

    def complete_open_configuration(self, text, line, begidx, endidx):
        return self.complete_configuration(text)

    def do_save_configuration(self, name):
        """
save_configuration [name]::

    Save the current configuration as (name)

        """
        if name:
            PARAS.save_configuration_as(name)
            print("Current configuration saved as '%s'" % name)
        else:
            print("Current configuration saved as '%s'" % PARAS.configuration_name())

    def do_remove_configuration(self, name):
        """
remove_configuration [name]::

    Remove a saved configuration

        """
        if name:
            if self.__confirm__("Remove configuration '%s'?" % name):
                if Configurations.remove_configuration(name):
                    print("Removed configuration %s" % name)
                else:
                    print("No configuration with the name %s" % name)
        else:
            print("Remove a configuration. Specify a name:")
            self.do_list_configurations(name)

    def complete_remove_configuration(self, text, line, begidx, endidx):
        return self.complete_configuration(text)

    def do_reset(self, line):
        """
reset::

    Reset the configuration to default settings.

        """
        global PARAS
        if self.__confirm__("Reset configuration '%s' to default settings?" % PARAS.configuration_name()):
            Configuration().core_clear()
            PARAS = RsParameters()
            PARAS.save_configuration()
            self.do_list_parameters(line)

    def do_resource_dir(self, path):
        """
resource_dir::

    resource_dir         - Get the parameter
    resource_dir [path]  - Set the parameter
    ----------------------------------------
    The resource_dir acts as the root of the resources to be published.
    The urls to the resources are calculated relative to the resource_dir.

        """
        print("Was:" if path else "Current:", PARAS.resource_dir)
        if path:
            try:
                PARAS.resource_dir = path
                PARAS.save_configuration(True)
                print("Now:", PARAS.resource_dir)
            except ValueError as err:
                print("\nIllegal argument: {0}".format(err))

    def complete_resource_dir(self, text, line, begidx, endidx):
        return self.__complete_path__(text, line, begidx, endidx)

    def do_metadata_dir(self, path):
        """
metadata_dir::

    metadata_dir         - Get the parameter
    metadata_dir [path]  - Set the parameter
    ----------------------------------------
    The metadata_dir is where sitemaps will be stored.
    The metadata_dir is always relative to the resource_dir

        """
        print("Was:" if path else "Current:", PARAS.metadata_dir)
        if path:
            try:
                PARAS.metadata_dir = path
                PARAS.save_configuration(True)
                print("Now:", PARAS.metadata_dir)
            except ValueError as err:
                print("\nIllegal argument: {0}".format(err))

    def do_description_dir(self, path):
        """
description_dir::

    description_dir         - Get the parameter
    description_dir [path]  - Set the parameter
    description_dir None    - Reset the parameter
    ---------------------------------------------
    The path to the directory of the (local copy of) the source description,
    aka '.well-known/resourcesync'

        """
        print("Was:" if path else "Current:", PARAS.description_dir)
        if path:
            try:
                if path == "None":
                    path = None
                PARAS.description_dir = path
                PARAS.save_configuration(True)
                print("Now:", PARAS.description_dir)
            except ValueError as err:
                print("\nIllegal argument: {0}".format(err))

    def complete_description_dir(self, text, line, begidx, endidx):
        return self.__complete_path__(text, line, begidx, endidx)

    def do_url_prefix(self, url):
        """
url_prefix::

    url_prefix           - Get the parameter
    url_prefix [prefix]  - Set the parameter
    ----------------------------------------
    The url_prefix is used to prefix urls to documents and resources.

        """
        print("Was:" if url else "Current:", PARAS.url_prefix)
        if url:
            try:
                PARAS.url_prefix = url
                PARAS.save_configuration(True)
                print("Now:", PARAS.url_prefix)
            except ValueError as err:
                print("\nIllegal argument: {0}".format(err))

    def do_has_wellknown_at_root(self, value):
        """
has_wellknown_at_root::

    has_wellknown_at_root             - Get the parameter
    has_wellknown_at_root (yes | no)  - Set the parameter
    ----------------------------------------------------
    The description document '.well-known/resourcesync' is at the root
    of the server address.

        """
        print("Was:" if value else "Current:", PARAS.has_wellknown_at_root)
        if value:
            PARAS.has_wellknown_at_root = str2bool(value, none=PARAS.has_wellknown_at_root)
            PARAS.save_configuration(True)
            print("Now:", PARAS.has_wellknown_at_root)

    def do_strategy(self, name):
        """
strategy::

    strategy             - Get the parameter
    strategy [strategy]  - Set the parameter
    ----------------------------------------
    The strategy determines what will be done by ResourceSync upon execution.

        """
        print("Was:" if name else "Current:", PARAS.strategy)
        if name:
            try:
                PARAS.strategy = name
                PARAS.save_configuration(True)
                print("Now:", PARAS.strategy)
            except ValueError as err:
                print("\nIllegal argument: {0}".format(err))

    def complete_strategy(self, text, line, begidx, endidx):
        if not text:
            completions = Strategy.names()[:]
        else:
            completions = [x for x in Strategy.names() if x.startswith(text)]
        return completions

# # Too troublesome to actively set a selector file on parameters.
# What if not there. How keep association between parameters and selector.
# Solution: Keep a weak association between parameters and selector.
# 1. associate selector file and parameters upon execution, if selector and selector is saved.
# 2. upon execution and no filenames, look for saved selector in parameters.
#     def do_selector_file(self, path):
#         """
# selector_file::
#
#     selector_file        Get the parameter
#     selector_file [path] Set the parameter
#     selector_file None   Reset the parameter
#     ---------------------------------------
#     The selector_file points to the location of the file that stores
#     (the contents of) a rspub.core.selector.Selector
#
#         """
#         print("Was:" if path else "Current:", PARAS.selector_file)
#         if path:
#             try:
#                 if path == "None":
#                     path = None
#                 PARAS.selector_file = path
#                 PARAS.save_configuration(True)
#                 print("Now:", PARAS.selector_file)
#             except ValueError as err:
#                 print("\nIllegal argument: {0}".format(err))
#
#     def complete_selector_file(self, text, line, begidx, endidx):
#         return self.__complete_path__(text, line, begidx, endidx)

    def do_discard_selector_file(self, line):
        """
discard_selector_file::

    Remove the association between this configuration and selector (if any).
    An association between a configuration and a selector is set after execution
    of ResourceSync with a Selector as file selector.

        """
        if PARAS.selector_file:
            if self.__confirm__("Discard association between configuration '%s' and selector at '%s'?"
                                % (PARAS.configuration_name(), PARAS.selector_file)):
                PARAS.selector_file = None
                PARAS.save_configuration(True)
        else:
            print("Configuration '%s' is not associated with a selector." % PARAS.configuration_name())

    def do_select_mode(self, mode):
        """
select_mode::

    select_mode         - Get the parameter
    select_mode [mode]  - Set the parameter
    ---------------------------------------
    Mode for selecting resources.

        """
        print("Was:" if mode else "Current:", PARAS.select_mode)
        if mode:
            try:
                PARAS.select_mode = mode
                PARAS.save_configuration(True)
                print("Now:", PARAS.select_mode)
            except ValueError as err:
                print("\nIllegal argument: {0}".format(err))

    def complete_select_mode(self, text, line, begidx, endidx):
        if not text:
            completions = SelectMode.names()[:]
        else:
            completions = [x for x in SelectMode.names() if x.startswith(text)]
        return completions

    def do_plugin_dir(self, path):
        """
plugin_dir::

    plugin_dir         - Get the parameter
    plugin_dir [path]  - Set the parameter
    plugin_dir None    - Reset the parameter
    ---------------------------------------
    The directory where plugins can be found.

        """
        print("Was:" if path else "Current:", PARAS.plugin_dir)
        if path:
            try:
                if path == "None":
                    path = None
                PARAS.plugin_dir = path
                PARAS.save_configuration(True)
                print("Now:", PARAS.plugin_dir)
            except ValueError as err:
                print("\nIllegal argument: {0}".format(err))

    def complete_plugin_dir(self, text, line, begidx, endidx):
        return self.__complete_path__(text, line, begidx, endidx)

    def do_max_items_in_list(self, value):
        """
max_items_in_list::

    max_items_in_list                   - Get the parameter
    max_items_in_list (int, 1 - 50000)  - Set the parameter
    ------------------------------------------------------
    The maximum amount of records in a sitemap.

        """
        print("Was:" if value else "Current:", PARAS.max_items_in_list)
        if (value):
            try:
                PARAS.max_items_in_list = int(value)
                PARAS.save_configuration(True)
                print("Now:", PARAS.max_items_in_list)
            except ValueError as err:
                print("\nIllegal argument: {0}".format(err))

    def do_zero_fill_filename(self, value):
        """
zero_fill_filename::

    zero_fill_filename                - Get the parameter
    zero_fill_filename (int, 1 - 10)  - Set the parameter
    ----------------------------------------------------
    The amount of digits in a sitemap filename.

        """
        print("Was:" if value else "Current:", PARAS.zero_fill_filename)
        if (value):
            try:
                PARAS.zero_fill_filename = int(value)
                PARAS.save_configuration(True)
                print("Now:", PARAS.zero_fill_filename)
            except ValueError as err:
                print("\nIllegal argument: {0}".format(err))

    def do_is_saving_pretty_xml(self, value):
        """
is_saving_pretty_xml::

    is_saving_pretty_xml             - Get the parameter
    is_saving_pretty_xml (yes | no)  - Set the parameter
    ---------------------------------------------------
    Determines appearance of sitemap xml.

        """
        print("Was:" if value else "Current:", PARAS.is_saving_pretty_xml)
        if value:
            PARAS.is_saving_pretty_xml = str2bool(value, none=PARAS.is_saving_pretty_xml)
            PARAS.save_configuration(True)
            print("Now:", PARAS.is_saving_pretty_xml)

    def do_is_saving_sitemaps(self, value):
        """
is_saving_sitemaps::

    is_saving_sitemaps             - Get the parameter
    is_saving_sitemaps (yes | no)  - Set the parameter
    -------------------------------------------------
    Determines if sitemaps will be written to disk.

        """
        print("Was:" if value else "Current:", PARAS.is_saving_sitemaps)
        if value:
            PARAS.is_saving_sitemaps = str2bool(value, none=PARAS.is_saving_sitemaps)
            PARAS.save_configuration(True)
            print("Now:", PARAS.is_saving_sitemaps)


#####################################################################################################
class Select(SuperCmd):

    prompt = "select > "
    intro = "======================================= \n" + \
            "Select data for ResourceSync Publishing \n" + \
            "======================================= \n" + SuperCmd._complete_

    def __init__(self):
        global SELECTOR
        SuperCmd.__init__(self)
        if PARAS.selector_file:
            try:
                SELECTOR = Selector(PARAS.selector_file)
                print("Loaded Selector from", SELECTOR.abs_location())
            except Exception as err:
                print("\nSelector error: {0}".format(err))

        if SELECTOR is None:
            SELECTOR = Selector()

    def do_load_selector(self, path):
        """
load_selector::

    load_selector [path] - Load Selector from location [path]
    ---------------------------------------------------------
    If the current Selector has unsaved changes, you will be
    prompted to save or discard.

        """
        global SELECTOR
        if path and self.check_exit():
            try:
                SELECTOR = Selector(path)
                print("Loaded Selector from", SELECTOR.abs_location())
            except Exception as err:
                print("\nSelector error: {0}".format(err))

    def complete_load_selector(self, text, line, begidx, endidx):
        return self.__complete_path__(text, line, begidx, endidx)

    def do_save_selector(self, path):
        """
save_selector::

    save_selector         - Save current selector
    save_selector [path]  - Save current selector as [path]

        """
        try:
            if path:
                SELECTOR.write(path)
            else:
                SELECTOR.write()
            print("Saved selector as %s" % SELECTOR.abs_location())
        except Exception as err:
            print("\nUnable to save: {0}".format(err))

    def complete_save_selector(self, text, line, begidx, endidx):
        return self.__complete_path__(text, line, begidx, endidx)

    def do_include_path(self, path):
        """
include_path::

    include_path [path] - Add a file or directory to the collection of includes.
    ----------------------------------------------------------------------------
    The [path] can be relative or absolute.

        """
        if path:
            SELECTOR.include(path)
            print("Included:", path)
        else:
            print("Usage: include_path [path] - Include the given path or directory")

    def complete_include_path(self, text, line, begidx, endidx):
        return self.__complete_path__(text, line, begidx, endidx)

    def do_list_includes(self, line):
        """
list_includes::

    List absolute filenames of the included files.

        """
        print("======================================================")
        print("Included files. Selector.location = %s" % SELECTOR.abs_location())
        print("======================================================")
        file_count = 0
        for file in SELECTOR.list_includes():
            file_count += 1
            print(file)
        print("Total included files: %d" % file_count)
        print("======================================================")

    def do_exclude_path(self, path):
        """
exclude_path::

    exclude_path [path] - Add a file or directory to the collection of excludes.
    ----------------------------------------------------------------------------
    The [path] can be relative or absolute.

        """
        if path:
            SELECTOR.exclude(path)
            print("Excluded:", path)
        else:
            print("Usage: exclude_path [path] - Exclude the given path or directory")

    def complete_exclude_path(self, text, line, begidx, endidx):
        return self.__complete_path__(text, line, begidx, endidx)

    def do_list_excludes(self, line):
        """
list_excludes::

    List absolute filenames of the excluded files.

        """
        print("======================================================")
        print("Excluded files. Selector.location = %s" % SELECTOR.abs_location())
        print("======================================================")
        file_count = 0
        for file in SELECTOR.list_excludes():
            file_count += 1
            print(file)
        print("Total excluded files: %d" % file_count)
        print("======================================================")

    def do_list_selected(self, line):
        """
list_selected::

    List absolute filenames of the selected files. The selected files are
    the relative complement of excludes with respect to includes.
    (list_includes \ list_excludes)

        """
        print("======================================================")
        print("Selected files. Selector.location = %s" % SELECTOR.abs_location())
        print("======================================================")
        file_count = 0
        for file in SELECTOR:
            file_count += 1
            print(file)
        print("Total selected files: %d" % file_count)
        print("======================================================")

    def do_read_includes(self, path):
        """
read_includes::

    read_includes [path]  - Read included filenames from a file at [path]

        """
        if path:
            try:
                SELECTOR.read_includes(path)
                print("Filenames from '%s' included." % path)
            except Exception as err:
                print("\nUnable to read includes: {0}".format(err))
        else:
            print("Usage: read_includes [path]  - Read included filenames from a file at [path]")

    def complete_read_includes(self, text, line, begidx, endidx):
        return self.__complete_path__(text, line, begidx, endidx)

    def do_read_excludes(self, path):
        """
read_excludes::

    read_excludes [path]  - Read excluded filenames from a file at [path]

        """
        if path:
            try:
                SELECTOR.read_excludes(path)
                print("Filenames from '%s' excluded." % path)
            except Exception as err:
                print("\nUnable to read excludes: {0}".format(err))
        else:
            print("Usage: read_excludes [path]  - Read excluded filenames from a file at [path]")

    def complete_read_excludes(self, text, line, begidx, endidx):
        return self.__complete_path__(text, line, begidx, endidx)

    def do_clear_includes(self, line):
        """
clear_includes::

    Clear included filenames from selector.

        """
        if self.__confirm__("Clear included filenames from selector?"):
            SELECTOR.clear_includes()
            self.do_list_includes(line)

    def do_clear_excludes(self, line):
        """
clear_excludes::

    Clear excluded filenames from selector.

        """
        if self.__confirm__("Clear excluded filenames from selector?"):
            SELECTOR.clear_excludes()
            self.do_list_excludes(line)

    def do_discard_include(self, path):
        """
discard_include::

    discard_include [path]  - Remove [path] from included filenames.

        """
        if path:
            SELECTOR.discard_include(path)
        else:
            print("Usage: discard_include [path]  - remove [path] from included filenames.")

    def complete_discard_include(self, text, line, begidx, endidx):
        return self.__complete_path__(text, line, begidx, endidx)

    def do_discard_exclude(self, path):
        """
discard_exclude::

    discard_exclude [path]  - Remove [path] from excluded filenames.

        """
        if path:
            SELECTOR.discard_exclude(path)
        else:
            print("Usage: discard_exclude [path]  - remove [path] from excluded filenames.")

    def complete_discard_exclude(self, text, line, begidx, endidx):
        return self.__complete_path__(text, line, begidx, endidx)

    def do_get_included_entries(self, line):
        """
get_included_entries::

    List included entries.

        """
        print("=========================================================")
        print("Included entries. Selector.location = %s" % SELECTOR.abs_location())
        print("=========================================================")
        [print(x) for x in SELECTOR.get_included_entries()]
        print("=========================================================")

    def do_get_excluded_entries(self, line):
        """
get_excluded_entries::

    List excluded entries.

        """
        print("=========================================================")
        print("Excluded entries. Selector.location = %s" % SELECTOR.abs_location())
        print("=========================================================")
        [print(x) for x in SELECTOR.get_excluded_entries()]
        print("=========================================================")

    def check_exit(self):
        save = self.__confirm__("Selector might have unsaved changes. Save changes to disk?")
        if save and SELECTOR.location:
            self.do_save_selector(SELECTOR.location)
            return True
        elif save:
            print("Use command 'save_selector' to save current selector.")
            return False
        return True

    def do_exit(self, line):
        if self.check_exit():
            self.stop = True


    def do_EOF(self, line):
        """
EOF, Ctrl+D, Ctrl+C::

    Exit the application.

        """
        if self.check_exit():
            print("Bye from", __file__)
            sys.exit()


if __name__ == '__main__':
    try:
        RsPub().cmdloop()
    except KeyboardInterrupt:
        print("Bye\n")

