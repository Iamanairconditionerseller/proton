#!/usr/bin/env python3

#            ---------------------------------------------------
#                             Proton Framework              
#            ---------------------------------------------------
#                Copyright (C) <2019-2020>  <Entynetproject>
#
#        This program is free software: you can redistribute it and/or modify
#        it under the terms of the GNU General Public License as published by
#        the Free Software Foundation, either version 3 of the License, or
#        any later version.
#
#        This program is distributed in the hope that it will be useful,
#        but WITHOUT ANY WARRANTY; without even the implied warranty of
#        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#        GNU General Public License for more details.
#
#        You should have received a copy of the GNU General Public License
#        along with this program.  If not, see <http://www.gnu.org/licenses/>.

try:
    from SocketServer import ThreadingMixIn
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
except:
    # why is python3 so terrible for backward compatibility?
    from socketserver import ThreadingMixIn
    from http.server import BaseHTTPRequestHandler, HTTPServer

import core.handler
import core.session
import core.loader
import core.payload

import socket
import random
import threading
import os
import ssl
import io
import time
import datetime
import copy

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class Server(threading.Thread):
    def __init__(self, port, handler, keypath, certpath, shell, options):
        threading.Thread.__init__(self)
        self.daemon = True

        self.handler_class = handler
        self.port = port
        self.keypath = keypath
        self.certpath = certpath
        self.shell = shell
        self.options = options
        self.killed = False

        self._setup_server()

    def _setup_server(self):
        self.http = ThreadedHTTPServer(('0.0.0.0', self.port), self.handler_class)
        self.http.timeout = None
        self.http.daemon_threads = True
        self.http.server = self
        self.http.shell = self.shell
        self.http.options = self.options

        if self.keypath and self.certpath:
            self.keypath = os.path.abspath(self.keypath)
            self.certpath = os.path.abspath(self.certpath)
            self.http.socket = ssl.wrap_socket(self.http.socket, keyfile=self.keypath, certfile=self.certpath, server_side = True)

    def run(self):

        try:
            self.http.serve_forever()
        except:
            pass

    def shutdown(self):

        # shut down the server/socket
        self.http.shutdown()
        self.http.socket.close()
        self.http.server_close()
        self._Thread__stop()

        # make sure all the threads are killed
        for thread in threading.enumerate():
            if thread.isAlive():
                try:
                    thread._Thread__stop()
                except:
                    pass
