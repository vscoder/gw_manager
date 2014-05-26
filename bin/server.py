#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import sys
import os
import subprocess
import SocketServer

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s: %(message)s',
                    filename='log/server.log',
                    )

sys.path.insert(0, "./lib")
from scan import Scan
from firewall import Pf
from firewall import Ipfw


class GwManagerHandler(SocketServer.StreamRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    
    def __init__(self, request, client_address, server):
        self.Scan = Scan

        self.logger = logging.getLogger('GwManagerHandler')
        self.logger.debug('__init__')
        SocketServer.StreamRequestHandler.__init__(self, request, client_address, server)
        return

    #def setup(self):
    #    self.logger.debug('setup')
    #    return SocketServer.BaseRequestHandler.setup(self)

    def handle(self):
        # self.request is the TCP socket connected to the client
        #self.data = self.request.recv(1024).strip()
        self.data = self.rfile.readline().strip()
        cur_pid = os.getpid()
        uid = os.getuid()
        self.logger.debug("{} connected".format(self.client_address[0]))
        self.logger.debug("child process id: '%s', uid: '%s'" % (cur_pid, uid))
        self.logger.debug('recieved data: %s' % self.data)
        ##host, port = self.data.split()
        ##result = self.do_scan(host, port)
        #result = self.run_cmd(self.data)
        #self.logger.debug('send reply: %s' % result)
        ## just send back the same data, but upper-cased
        ##self.request.sendall(result)
        #self.wfile.write(result)

        data = self.data.split()
        cmd = data[0]
        args = data[1:]

        if cmd == "check_ip":
            ip = args[0]
            result = self.check_ip(ip)
        else:
            result = "bad input data '%s'" % data

        self.logger.debug('send reply: %s' % result)
        self.wfile.write(result)


    #def finish(self):
    #    self.logger.debug('finish')
    #    return SocketServer.BaseRequestHandler.finish(self)

    
    def check_ip(self, ip):
        """Check block status and shape of ip address"""
        # PF
        pf = Pf(ip = ip)

        if pf.check_ip():
            status = 'ON'
        else:
            status = 'OFF'

        # IPFW
        ipfw = Ipfw(ip = ip)

        pipes = ipfw.check_ip()
        if pipes:
            shape_in = pipes[3]
            shape_out = pipes[2]
        else:
            shape_in = 'unknown'
            shape_out = 'unknown'

        result = """
                 IP '%(ip)s' status: %(status)s
                 rx traffic shape: %(in)s Kbit/s
                 tx traffic shape: %(out)s Kbit/s
                 """ % {'ip': ip, 'status': status, 'in': shape_in, 'out': shape_out}

        return result

    
    def do_scan(self, *args, **kwargs):
        """scan tcp port"""
        host, port = args
        scanner = self.Scan(host = host, port = port)
        if scanner.check_tcp_port():
            result = 'OPEN'
        else:
            result = 'CLOSED'

        return result

       
    def run_cmd(self, cmd):
        """run shell cmd as current user"""
        run = tuple(cmd.split())
        result = subprocess.check_output(run)
        return result
        


class ForkingGwManagerServer(SocketServer.ForkingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    HOST, PORT = "localhost", 1237

    # Create the server, binding to localhost on port 9999
    server = ForkingGwManagerServer((HOST, PORT), GwManagerHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
