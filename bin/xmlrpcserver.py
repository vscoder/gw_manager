#!/usr/local/bin/python2.7
##!/usr/bin/env python2
# -*- coding: utf_8 -*-

# Command line args: start|stop|restart

import sys
import os

# Set current work directory
cwd = "{}/..".format(os.path.dirname(os.path.realpath(__file__)))
os.chdir(cwd)
sys.path.insert(0, "{}/lib".format(cwd))

from daemon import runner
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

#import logging
#logging.basicConfig(level=logging.DEBUG,
#                    format='%(asctime)s: %(message)s',
#                    filename='{}/log/xmlrpcserver.log'.format(cwd),
#                    )


from server_functions import GwManServerFunctions


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

    def __init__(self, request, client_address, server):
        serversfile = 'conf/servers.lst'
        with open(serversfile, 'r') as f:
            hosts = map(lambda a: a.strip(), f.readlines())

        if client_address[0] in hosts:
            #logging.info("accepted connection from host {0} port {1}".format(*client_address))
            print("accepted connection from host {0} port {1}".format(*client_address))
            SimpleXMLRPCRequestHandler.__init__(self, request, client_address, server)
        else:
            #logging.error("{} not in list of allowed hosts, cancelled!".format(client_address[0]))
            print("{} not in list of allowed hosts, cancelled!".format(client_address[0]))
            raise ValueError("{} not in list of allowed hosts, cancelled!".format(client_address[0]))


# Class to wrap around the XML-RPC server
class Server():
 
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = 'log/agent.log'
        self.stderr_path = 'log/agent.log'
        self.pidfile_path = '/tmp/gwman_agent.pid'
        self.pidfile_timeout = 5
     
    def run(self):
        os.chdir(cwd)
        HOST, PORT = "0.0.0.0", 1237
        self.server = SimpleXMLRPCServer((HOST, PORT),
                                        requestHandler=RequestHandler)
        self.server.register_introspection_functions()
         
        # Register functions
        self.server.register_instance(GwManServerFunctions())
        self.server.serve_forever()

if __name__ == "__main__":
    
    
    daemon = runner.DaemonRunner(Server())

    # Set the owning UID and GID the daemon
    #daemon.daemon_context.uid = 1001
    #daemon.daemon_context.gid = 1001

    # perfom the action - start, stop, restart
    daemon.do_action()
