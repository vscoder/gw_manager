#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import sys


from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s: %(message)s',
                    filename='log/xmlrpcserver.log',
                    )


sys.path.insert(0, "./lib")
from server_functions import GwManServerFunctions


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

    def __init__(self, request, client_address, server):
        serversfile = 'conf/servers.lst'
        with open(serversfile, 'r') as f:
            hosts = map(lambda a: a.strip(), f.readlines())

        if client_address[0] in hosts:
            logging.info("accepted connection from host {0} port {1}".format(*client_address))
            SimpleXMLRPCRequestHandler.__init__(self, request, client_address, server)
        else:
            logging.error("{} not in list of allowed hosts, cancelled!".format(client_address[0]))
            raise ValueError("{} not in list of allowed hosts, cancelled!".format(client_address[0]))


def main():
    HOST, PORT = "0.0.0.0", 1237

    server = SimpleXMLRPCServer((HOST, PORT),
                                requestHandler=RequestHandler)
    server.register_introspection_functions()

    server.register_instance(GwManServerFunctions())

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    logging.info("Star server")
    server.serve_forever()   
    logging.info("Stop server")


if __name__ == "__main__":
    main()
