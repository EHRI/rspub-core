#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from rspub.core.selector import Selector

if sys.version_info[0] < 3:
    raise RuntimeError("Your Python has version 2. This application needs Python3.x")

import os
import cmd, glob

# Start this module from anywhere on the system: append root directory of project.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
#                rspub-core         rspub           cli               rscli.py
from rspub.core.rs_paras import RsParameters
from rspub.core.config import Configuration, Configurations
from rspub.core.rs_enum import Strategy

# Set up gnureadline as readline if installed.
__GNU_READLINE__ = False
try:
    import gnureadline
    sys.modules['readline'] = gnureadline
    __GNU_READLINE__ = "gnu"
except ImportError:
    pass


PARAS = RsParameters()


def str2bool(v, none=False):
    if v:
        return v.lower() in ["yes", "y", "true", "t", "1", "on", "o"]
    else:
        return none


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

    def postcmd(self, stop, line):
        """Hook method executed just after a command dispatch is finished."""
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


class RsPub(SuperCmd):

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

    def do_exit(self, line):
        """
EOF, Ctrl+D, Ctrl+C::

    Exit the application.

        """
        self.do_EOF(line)


class Configure(SuperCmd):

    prompt = "configure > "
    intro = "============================= \n" + \
            "Configure Metadata Publishing \n" + \
            "============================= \n" + SuperCmd._complete_

    def __init__(self):
        SuperCmd.__init__(self)

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

    def help_resource_dir(self):
        print('\n'.join(["resource_dir", "   Get the resources root directory.",
                   "resource_dir [path]", "   Set the resources root directory to path."
                   ]))

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

    def do_selector_file(self, path):
        """
selector_file::

    selector_file        Get the parameter
    selector_file [path] Set the parameter
    selector_file None   Reset the parameter
    ---------------------------------------
    The selector_file points to the location of the file that stores
    (the contents of) a rspub.core.selector.Selector

        """
        print("Was:" if path else "Current:", PARAS.selector_file)
        if path:
            try:
                if path == "None":
                    path = None
                PARAS.selector_file = path
                PARAS.save_configuration(True)
                print("Now:", PARAS.selector_file)
            except ValueError as err:
                print("\nIllegal argument: {0}".format(err))

    def complete_selector_file(self, text, line, begidx, endidx):
        return self.__complete_path__(text, line, begidx, endidx)

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


class Select(SuperCmd):

    prompt = "select > "
    intro = "======================================= \n" + \
            "Select data for ResourceSync Publishing \n" + \
            "======================================= \n" + SuperCmd._complete_

    def __init__(self):
        SuperCmd.__init__(self)
        self.selector = None
        if PARAS.selector_file:
            try:
                self.selector = Selector(PARAS.abs_selector_file())
                print("Loaded Selector from", self.selector.abs_location())
            except Exception as err:
                print("\nSelector error: {0}".format(err))

        if self.selector is None:
            self.selector = Selector()

    def do_load_selector(self, path):
        """
load_selector::

    load_selector [path] - Load Selector from location [path]
    ---------------------------------------------------------
    If the current Selector has unsaved changes, you will be
    prompted to save or discard.

        """
        if path:
            self.check_exit()
            try:
                self.selector = Selector(path)
                print("Loaded Selector from", self.selector.abs_location())
            except Exception as err:
                print("\nSelector error: {0}".format(err))

    def complete_load_selector(self, text, line, begidx, endidx):
        return self.__complete_path__(text, line, begidx, endidx)

    def do_include_path(self, path):
        """
include_path::

    include_path [path] - Add a file or directory to the collection of includes.
    ----------------------------------------------------------------------------
    The [path] can be relative or absolute.

        """
        if path:
            self.selector.include(path)
            print("Included:", path)

    def complete_include_path(self, text, line, begidx, endidx):
        return self.__complete_path__(text, line, begidx, endidx)

    def do_list_includes(self, line):
        """
list_includes::

    List absolute filenames of the included files.

        """
        print("======================================================")
        print("Included files. Selector.location = %s" % self.selector.abs_location())
        print("======================================================")
        file_count = 0
        for file in self.selector.list_includes():
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
            self.selector.exclude(path)
            print("Excluded:", path)

    def complete_exclude_path(self, text, line, begidx, endidx):
        return self.__complete_path__(text, line, begidx, endidx)

    def do_list_excludes(self, line):
        """
list_excludes::

    List absolute filenames of the excluded files.

        """
        print("======================================================")
        print("Excluded files. Selector.location = %s" % self.selector.abs_location())
        print("======================================================")
        file_count = 0
        for file in self.selector.list_excludes():
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
        print("Selected files. Selector.location = %s" % self.selector.abs_location())
        print("======================================================")
        file_count = 0
        for file in self.selector:
            file_count += 1
            print(file)
        print("Total selected files: %d" % file_count)
        print("======================================================")

    def save_selector(self):
        print("saved!")

    def check_exit(self):
        if self.selector and self.selector.dirty:
            if self.__confirm__("Selection has unsaved changes. Save current selection?"):
                self.save_selector()

    def do_exit(self, line):
        self.check_exit()
        self.stop = True

    def do_EOF(self, line):
        """
EOF, Ctrl+D, Ctrl+C::

    Exit the application.

        """
        self.check_exit()
        print("Bye from", __file__)
        sys.exit()


if __name__ == '__main__':
    try:
        RsPub().cmdloop()
    except KeyboardInterrupt:
        print("Bye\n")

