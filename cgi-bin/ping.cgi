#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import xmlrpclib

import cgi
import cgitb
cgitb.enable()

import logging

# Инициализация логирования
logging.basicConfig(filename='log/ping.log', format='%(asctime)s %(message)s', level=logging.DEBUG)

# Разбор переданных аргументов
arguments = cgi.FieldStorage()
host = arguments.getvalue('host') or '127.0.0.1'
count = arguments.getvalue('count') or '3'

# Инициализация класса
server = xmlrpclib.ServerProxy('http://localhost:1237')

retcode, result = server.ping(host, count)


print "Content-Type: text/html;charset=utf-8"
print

print "<br>".join(result.split('\n'))
logging.info(result)
