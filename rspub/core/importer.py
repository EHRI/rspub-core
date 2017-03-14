#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import socket
from enum import Enum

import paramiko
from scp import SCPClient, SCPException

from rspub.core.rs_paras import RsParameters
from rspub.util.observe import Observable, ObserverInterruptException

LOG = logging.getLogger(__name__)


class ImportEvent(Enum):
    """
    :samp:`Events fired by {Import}`

    All events are broadcast in the format::

        [inform](source, event, **kwargs)

    where ``source`` is the calling instance, ``event`` is the relevant event and ``**kwargs`` hold relevant
    information about the event.
    """

    transfer_file = 4
    """
    ``4`` ``confirm`` :samp:`Transfer file confirm message with interrupt`
    """

    ssh_client_creation = 22
    """
    ``22`` ``inform`` :samp:`Trying to create ssh client`
    """

    scp_exception = 23
    """
    ``23`` ``inform`` :samp:`Encountered exception while importing files with scp`
    """

    scp_progress = 24
    """
    ``24`` ``inform`` :samp:`Progress as defined by SCPClient`
    """

    scp_transfer_complete = 25
    """
    ``25`` ``inform`` :samp:`Transfer of one file complete`
    """

    import_start = 30
    """
    ``30`` ``inform`` :samp:`Import started`
    """

    import_end = 31
    """
    ``31`` ``inform`` :samp:`Import ended`
    """


class Importer(Observable):

    def __init__(self, paras, password):
        Observable.__init__(self)
        assert isinstance(paras, RsParameters)
        self.paras = paras
        self.password = password
        self.count_imports = 0
        self.count_errors = 0

    def create_ssh_client(self, password):
        LOG.debug("Creating ssh client: server=%s, port=%d, user=%s" %
                  (self.paras.imp_scp_server, self.paras.imp_scp_port, self.paras.imp_scp_user))
        self.observers_inform(self, ImportEvent.ssh_client_creation,
                              server=self.paras.imp_scp_server,
                              port=self.paras.imp_scp_port,
                              user=self.paras.imp_scp_user)
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(self.paras.imp_scp_server, self.paras.imp_scp_port, self.paras.imp_scp_user, password)
        except paramiko.ssh_exception.AuthenticationException as err:
            LOG.exception("Not authorized")
            self.count_errors += 1
            self.observers_inform(self, ImportEvent.scp_exception, exception=str(err))
            ssh_client = None
        except socket.gaierror as err:
            LOG.exception("Socket error")
            self.count_errors += 1
            self.observers_inform(self, ImportEvent.scp_exception, exception=str(err))
            ssh_client = None
        except TimeoutError as err:
            LOG.exception("Timeout")
            self.count_errors += 1
            self.observers_inform(self, ImportEvent.scp_exception, exception=str(err))
            ssh_client = None
        return ssh_client

    def scp_get(self, recursive=True, preserve_times=True):
        try:
            ssh_client = self.create_ssh_client(self.password)
            if ssh_client:
                scp = SCPClient(transport=ssh_client.get_transport(), progress=self.progress)
                os.makedirs(self.paras.imp_scp_local_path, exist_ok=True)
                LOG.debug("Importing files from %s to %s" % (self.paras.imp_scp_server, self.paras.imp_scp_local_path))

                self.observers_inform(self, ImportEvent.import_start, server=self.paras.imp_scp_server,
                                      remote_path=self.paras.imp_scp_remote_path,
                                      recursive=recursive)
                scp.get(self.paras.imp_scp_remote_path, self.paras.imp_scp_local_path, recursive=recursive,
                        preserve_times=preserve_times)
        except SCPException as err:
            LOG.exception("Error while importing files")
            self.count_errors += 1
            self.observers_inform(self, ImportEvent.scp_exception, exception=str(err))
        finally:
            self.observers_inform(self, ImportEvent.import_end, count_imports=self.count_imports,
                                  count_errors=self.count_errors)

    def progress(self, filename, size, sent):
        filestr = filename.decode()
        self.observers_inform(self, ImportEvent.scp_progress, filename=filestr, size=size, sent=sent)
        if sent == 0:
            if not self.observers_confirm(self, ImportEvent.transfer_file, filename=filestr):
                raise ObserverInterruptException("Process interrupted on ImportEvent.confirm_transfer_file")
        if sent == size:
            self.count_imports += 1
            self.observers_inform(self, ImportEvent.scp_transfer_complete,
                                  filename=filestr,
                                  count_imports=self.count_imports)




