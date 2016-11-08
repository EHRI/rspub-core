#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# Start this module from anywhere on the system: append root directory of project.
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
#                rspub-core         rspub           cli               rscli.py
from rspub.core.config import Configuration
from rspub.core.rs_enum import Strategy


import cmd, glob


# Set up gnureadline as readline if installed.
try:
    import gnureadline
    sys.modules['readline'] = gnureadline
    __GNU_READLINE__ = "gnu"
except ImportError:
    pass


class SuperCmd(cmd.Cmd):

    _complete_ = "Press <tab><tab> for options. Press <tab> for completion.\n" if __GNU_READLINE__ else ""
    doc_header = _complete_ + "Documented commands (type help <topic>):"

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

    def postcmd(self, stop, line):
        """Hook method executed just after a command dispatch is finished."""
        return self.stop

    def do_exit(self, line):
        self.stop = True

    def help_exit(self):
        print("exit\n\tExit", self.__class__.__name__, "mode.")

    def do_EOF(self, line):
        """EOF, Ctrl+D
        Exit the application."""
        print("Bye from", self.intro, line, "\n")
        sys.exit()


class RsPub(SuperCmd):

    prompt = "rspub > "
    intro = "Command Line Interface for ResourceSync Publishing. \n" + SuperCmd._complete_

    def do_configure(self, line):
        """configure
        Switch to configuration mode."""
        Configure().cmdloop()

    def do_select(self, line):
        """select
        Switch to select mode."""
        Select().cmdloop()

    def do_exit(self, line):
        """exit, EOF, Ctrl+D
        Exit the application."""
        self.do_EOF(line)
        exit()

    def do_EOF(self, line):
        """EOF, exit, Ctrl+D
        Exit the application."""
        print("Bye from", self.intro, line, "\n")
        return True


class Configure(SuperCmd):

    prompt = "configure > "
    intro = "Configure Metadata Publishing. \n" + SuperCmd._complete_

    config = Configuration()

    def __init__(self):
        cmd.Cmd.__init__(self)

    def do_list(self, line):
        """list
        List configuration."""
        print("=========================================================================")
        print("Configuration for Metadata Publishing")
        print("=========================================================================")
        print("resource_dir \t", self.config.resource_dir())
        print("metadata_dir \t", self.config.metadata_dir())
        print("description \t", self.config.core_sourcedesc())
        print("url_prefix \t", self.config.url_prefix())
        print("strategy \t", self.config.strategy())
        print("=========================================================================")

    def do_reset(self, line):
        """reset
        Reset the configuration to default settings."""
        self.config.core_clear()
        self.config.persist()
        self.do_list(line)

    def help_resource_dir(self):
        print('\n'.join(["resource_dir", "   Get the resources root directory.",
                   "resource_dir [path]", "   Set the resources root directory to path."
                   ]))

    def do_resource_dir(self, path):
        print("Was:" if path else "Current:", self.config.resource_dir())
        if path:
            try:
                self.config.set_resource_dir(path)
                self.config.persist()
                print("Now:", self.config.resource_dir())
            except ValueError as err:
                print("\nIllegal argument: {0}".format(err))

    def complete_resource_dir(self, text, line, begidx, endidx):
        return self.__complete_path__(text, line, begidx, endidx)

    def help_metadata_dir(self):
        print('\n'.join(["metadata_dir", "   Get the metadata directory.",
                   "metadata_dir [path]", "   Set the metadata directory to path."
                   ]))

    def do_metadata_dir(self, path):
        print("Was:" if path else "Current:", self.config.metadata_dir())
        if path:
            try:
                self.config.set_metadata_dir(path)
                self.config.persist()
                print("Now:", self.config.metadata_dir())
            except ValueError as err:
                print("\nIllegal argument: {0}".format(err))

    def complete_metadata_dir(self, text, line, begidx, endidx):
        return self.__complete_path__(text, line, begidx, endidx)

    def help_description(self):
        print('\n'.join(["description", "   Get the path to the source description document.",
                   "description [path]", "   Set the path to the source description document.",
                   "--------------------------------------------------------------",
                   "The sourcedescription document is an entry point for discovering ResourceSync Framework documents on a site.",
                   "It should be at {host}/.well-known/resourcesync",
                   "          or at {host/path}/.well-known/resourcesync"
                   ]))

    def do_description(self, url):
        print("Was:" if url else "Current:", self.config.core_sourcedesc())
        if url:
            try:
                self.config.set_core_sourcedesc(url)
                self.config.persist()
                print("Now:", self.config.core_sourcedesc())
            except ValueError as err:
                print("\nIllegal argument: {0}".format(err))

    def help_url_prefix(self):
        print('\n'.join(["url_prefix", "   Get the url prefix.",
                   "url_prefix [url]", "   Set the url prefix.",
                   "--------------------------------------------------------------",
                   "The url_prefix is used to prefix paths to ResourceSync Framework documents and resources."
                   ]))

    def do_url_prefix(self, url):
        print("Was:" if url else "Current:", self.config.url_prefix())
        if url:
            try:
                self.config.set_url_prefix(url)
                self.config.persist()
                print("Now:", self.config.url_prefix())
            except ValueError as err:
                print("\nIllegal argument: {0}".format(err))

    def help_strategy(self):
        print('\n'.join(["strategy", "   Get the strategy.",
                   "strategy [name]", "   Set the strategy.",
                   "--------------------------------------------------------------",
                   "The strategy determines what type of resource list is exposed.",
                   "Possible values: ",
                   ", ".join(Strategy.names())
                   ]))

    def do_strategy(self, name):
        print("Was:" if name else "Current:", self.config.strategy())
        if name:
            try:
                self.config.set_strategy(name)
                self.config.persist()
                print("Now:", self.config.strategy())
            except ValueError as err:
                print("\nIllegal argument: {0}".format(err))
                self.help_strategy()

    def complete_strategy(self, text, line, begidx, endidx):
        if not text:
            completions = Strategy.names()[:]
        else:
            completions = [
                f
                for f in Strategy.names()
                if f.startswith(text)
            ]
        return completions


class Select(SuperCmd):

    prompt = "select > "
    intro = "Select data for ResourceSync Publishing. \n" + SuperCmd._complete_

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

