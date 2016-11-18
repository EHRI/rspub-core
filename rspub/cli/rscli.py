#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import cmd, glob

from rspub.core.rs_paras import RsParameters

if sys.version_info[0] < 3:
    raise RuntimeError("Your Python has version 2. This application needs Python3.x")

# Start this module from anywhere on the system: append root directory of project.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
#                rspub-core         rspub           cli               rscli.py
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


def str2bool(v, none=False):
    if v:
        return v.lower() in ["yes", "y", "true", "t", "1", "on", "o"]
    else:
        return none


class SuperCmd(cmd.Cmd):

    _complete_ = "-> Press 2 x <tab> for options, 1 x <tab> for completion.\n" if __GNU_READLINE__ else ""
    doc_header = "Documented commands (type: help <topic>):"

    stop = False

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
        print("exit\n\tExit", self.__class__.__name__, "mode.")

    def do_EOF(self, line):
        """EOF, Ctrl+D:
        Exit the application."""
        print("Bye from", __file__)
        sys.exit()


class RsPub(SuperCmd):

    prompt = "rspub > "
    intro = "================================================== \n" + \
            "Command Line Interface for ResourceSync Publishing \n" + \
            "================================================== \n" + SuperCmd._complete_

    def do_configure(self, line):
        """configure:
        Switch to configuration mode."""
        Configure().cmdloop()

    def do_select(self, line):
        """select:
        Switch to select mode."""
        Select().cmdloop()

    def do_exit(self, line):
        """exit, EOF, Ctrl+D:
        Exit the application."""
        self.do_EOF(line)


class Configure(SuperCmd):

    prompt = "configure > "
    intro = "============================= \n" + \
            "Configure Metadata Publishing \n" + \
            "============================= \n" + SuperCmd._complete_

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.paras = RsParameters()

    @staticmethod
    def complete_configuration(text):
        if not text:
            completions = Configurations.list_configurations()[:]
        else:
            completions = [x for x in Configurations.list_configurations() if x.startswith(text)]
        return completions

    def do_list_configurations(self, line):
        """list_configurations:
        List saved configurations"""
        print("====================")
        print("Saved configurations")
        print("====================")
        for config in Configurations.list_configurations():
            print(config)
        print("")
        print("====================")

    def do_save_configuration(self, name):
        """save_configuration [name]:
        Save the current configuration as (name)"""
        if (name):
            self.paras.save_configuration_as(name)
            print("Current configuration saved as '%s'" % name)
        else:
            print("Current configuration saved as '%s'" % self.paras.configuration_name())

    def do_open_configuration(self, name):
        """open_configuration [name]:
        Open a saved configuration"""
        if name:
            try:
                self.paras = RsParameters(config_name=name)
                self.do_list_parameters(name)
            except ValueError as err:
                print("\nIllegal argument: {0}".format(err))
        else:
            print("Open a configuration. Specify a name:")
            self.do_list_configurations(name)

    def complete_open_configuration(self, text, line, begidx, endidx):
        return self.complete_configuration(text)

    def do_remove_configuration(self, name):
        """remove_configuration [name]:
        Remove a saved configuration"""
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

    def do_list_parameters(self, line):
        """list_parameters:
        List current parameters."""
        print("==================================================================================")
        print("Parameters for Metadata Publishing")
        print("==================================================================================")
        print(self.paras.describe(True))
        print("==================================================================================")

    def do_reset(self, line):
        """reset:
        Reset the configuration to default settings."""
        if self.__confirm__("Reset configuration '%s' to default settings?" % self.paras.configuration_name()):
            Configuration().reset()
            Configuration().core_clear()
            self.paras = RsParameters()
            self.paras.save_configuration()
            self.do_list_parameters(line)

    def help_resource_dir(self):
        print('\n'.join(["resource_dir", "   Get the resources root directory.",
                   "resource_dir [path]", "   Set the resources root directory to path."
                   ]))

    def do_resource_dir(self, path):
        print("Was:" if path else "Current:", self.paras.resource_dir)
        if path:
            try:
                self.paras.resource_dir = path
                self.paras.save_configuration(True)
                print("Now:", self.paras.resource_dir)
            except ValueError as err:
                print("\nIllegal argument: {0}".format(err))

    def complete_resource_dir(self, text, line, begidx, endidx):
        return self.__complete_path__(text, line, begidx, endidx)

    def help_metadata_dir(self):
        print('\n'.join(["metadata_dir", "   Get the metadata directory.",
                   "metadata_dir [path]", "   Set the metadata directory to path."
                   ]))

    def do_metadata_dir(self, path):
        print("Was:" if path else "Current:", self.paras.metadata_dir)
        if path:
            try:
                self.paras.metadata_dir = path
                self.paras.save_configuration(True)
                print("Now:", self.paras.metadata_dir)
            except ValueError as err:
                print("\nIllegal argument: {0}".format(err))

    def help_description_dir(self):
        print('\n'.join(["description_dir", "   Get the directory of the source description document.",
                   "description_dir [path]", "   Set the directory of the source description document.",
                   "--------------------------------------------------------------",
                   "The sourcedescription document is an entry point for discovering ResourceSync Framework documents on a site."
                   "Type 'None' to reset"
                   ]))

    def do_description_dir(self, path):
        print("Was:" if path else "Current:", self.paras.description_dir)
        if path:
            try:
                if path == "None":
                    path = None
                self.paras.description_dir = path
                self.paras.save_configuration(True)
                print("Now:", self.paras.description_dir)
            except ValueError as err:
                print("\nIllegal argument: {0}".format(err))

    def complete_description_dir(self, text, line, begidx, endidx):
        return self.__complete_path__(text, line, begidx, endidx)

    def help_url_prefix(self):
        print('\n'.join(["url_prefix", "   Get the url prefix.",
                       "url_prefix [url]", "   Set the url prefix.",
                       "--------------------------------------------------------------",
                       "The url_prefix is used to prefix paths to ResourceSync Framework documents and resources."
                       ]))

    def do_url_prefix(self, url):
        print("Was:" if url else "Current:", self.paras.url_prefix)
        if url:
            try:
                self.paras.url_prefix = url
                self.paras.save_configuration(True)
                print("Now:", self.paras.url_prefix)
            except ValueError as err:
                print("\nIllegal argument: {0}".format(err))

    def do_has_wellknown_at_root(self, value):
        """has_wellknown_at_root:
        The description document '.well-known/resourcesync' is at the root of the server address."""
        print("Was:" if value else "Current:", self.paras.has_wellknown_at_root)
        if value:
            self.paras.has_wellknown_at_root = str2bool(value, none=self.paras.has_wellknown_at_root)
            self.paras.save_configuration(True)
            print("Now:", self.paras.has_wellknown_at_root)

    def help_strategy(self):
        print('\n'.join(["strategy", "   Get the strategy.",
                   "strategy [name]", "   Set the strategy.",
                   "--------------------------------------------------------------",
                   "The strategy determines what type of resource list is exposed.",
                   "Possible values: ",
                   ", ".join(Strategy.names())
                   ]))

    def do_strategy(self, name):
        print("Was:" if name else "Current:", self.paras.strategy)
        if name:
            try:
                self.paras.strategy = name
                self.paras.save_configuration(True)
                print("Now:", self.paras.strategy)
            except ValueError as err:
                print("\nIllegal argument: {0}".format(err))
                self.help_strategy()

    def complete_strategy(self, text, line, begidx, endidx):
        if not text:
            completions = Strategy.names()[:]
        else:
            completions = [x for x in Strategy.names() if x.startswith(text)]
        return completions

    def help_plugin_dir(self):
        print('\n'.join(["plugin_dir", "   Get the path to the plugin directory.",
                   "description_dir [path]", "   Set the path to the plugin directory.",
                   "--------------------------------------------------------------",
                   "The plugin_dir is the directory where plugins can be found.",
                   "Type 'None' to reset"
                   ]))

    def do_plugin_dir(self, path):
        print("Was:" if path else "Current:", self.paras.plugin_dir)
        if path:
            try:
                if path == "None":
                    path = None
                self.paras.plugin_dir = path
                self.paras.save_configuration(True)
                print("Now:", self.paras.plugin_dir)
            except ValueError as err:
                print("\nIllegal argument: {0}".format(err))

    def complete_plugin_dir(self, text, line, begidx, endidx):
        return self.__complete_path__(text, line, begidx, endidx)

    def do_max_items_in_list(self, value):
        """max_items_in_list:
        The maximum amount of records in a sitemap (int, 1 - 50000)
        """
        print("Was:" if value else "Current:", self.paras.max_items_in_list)
        if (value):
            try:
                self.paras.max_items_in_list = int(value)
                self.paras.save_configuration(True)
                print("Now:", self.paras.max_items_in_list)
            except ValueError as err:
                print("\nIllegal argument: {0}".format(err))

    def do_zero_fill_filename(self, value):
        """zero_fill_filename:
        The amount of digits in a sitemap filename (int, 1 - 10)
        """
        print("Was:" if value else "Current:", self.paras.zero_fill_filename)
        if (value):
            try:
                self.paras.zero_fill_filename = int(value)
                self.paras.save_configuration(True)
                print("Now:", self.paras.zero_fill_filename)
            except ValueError as err:
                print("\nIllegal argument: {0}".format(err))

    def do_is_saving_pretty_xml(self, value):
        """is_saving_pretty_xml:
        Determines appearance of sitemap xml (yes | no)"""
        print("Was:" if value else "Current:", self.paras.is_saving_pretty_xml)
        if value:
            self.paras.is_saving_pretty_xml = str2bool(value, none=self.paras.is_saving_pretty_xml)
            self.paras.save_configuration(True)
            print("Now:", self.paras.is_saving_pretty_xml)

    def do_is_saving_sitemaps(self, value):
        """is_saving_sitemaps:
        Determines if sitemaps will be written to disk (yes | no)"""
        print("Was:" if value else "Current:", self.paras.is_saving_sitemaps)
        if value:
            self.paras.is_saving_sitemaps = str2bool(value, none=self.paras.is_saving_sitemaps)
            self.paras.save_configuration(True)
            print("Now:", self.paras.is_saving_sitemaps)


class Select(SuperCmd):

    prompt = "select > "
    intro = "======================================= \n" + \
            "Select data for ResourceSync Publishing \n" + \
            "======================================= \n" + SuperCmd._complete_

    config = Configuration()

    def do_directory(self, path):
        print("set directory", path)

    def complete_directory(self, text, line, begidx, endidx):
        if line == "directory ":
            return [self.config.resource_dir()]
        else:
            return self.__complete_path__(text, line, begidx, endidx)


if __name__ == '__main__':
    try:
        RsPub().cmdloop()
    except KeyboardInterrupt:
        print("Bye\n")

