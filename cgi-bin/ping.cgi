#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import sys
import cgi
import cgitb
cgitb.enable()

import logging

sys.path.insert(0, "./lib")
from ping import Ping

# Инициализация логирования
logging.basicConfig(filename='log/ping.log', format='%(asctime)s %(message)s', level=logging.DEBUG)

# Разбор переданных аргументов
arguments = cgi.FieldStorage()
host = arguments.getvalue('host')

# Инициализация класса
ping = Ping(host = host)

ping.timeout = 1
result = ping.ping_host()


print "Content-Type: text/html;charset=utf-8"
print

out = "returncode: %s\n%s" % result
print out
logging.info(out)
