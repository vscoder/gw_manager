#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import cgi
import cgitb
cgitb.enable()

import logging

sys.path.insert(0, "./lib")
from scan import Scan

# Инициализация логирования
logging.basicConfig(filename='log/scanner.log', format='%(asctime)s %(message)s', level=logging.DEBUG)

# Разбор переданных аргументов
arguments = cgi.FieldStorage()
host = arguments.getvalue('host')
port = arguments.getvalue('port')

# Инициализация класса
scanner = Scan(host = host, port = port)

if scanner.check_tcp_port():
    result = 'OPEN'
else:
    result = 'CLOSED'


print "Content-Type: text/html;charset=utf-8"
print

out = "TCP port %s on host '%s' is %s" % (port, host, result)
print out
logging.info(out)
