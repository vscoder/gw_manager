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


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


def main():
    HOST, PORT = "localhost", 1237

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
