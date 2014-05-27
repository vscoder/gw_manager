#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import xmlrpclib

import cgi
import cgitb
cgitb.enable()

import logging

# Инициализация логирования
logging.basicConfig(filename='log/scanner.log', format='%(asctime)s %(message)s', level=logging.DEBUG)

# Разбор переданных аргументов
arguments = cgi.FieldStorage()
host = arguments.getvalue('host')
port = arguments.getvalue('port')

# Инициализация класса
server = xmlrpclib.ServerProxy('http://localhost:1237')

result = server.do_scan(host, port)

print "Content-Type: text/html;charset=utf-8"
print

out = "TCP port %s on host '%s' is %s" % (port, host, result)
print out
logging.info(out)
