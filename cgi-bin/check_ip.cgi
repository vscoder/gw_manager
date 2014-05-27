#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import xmlrpclib

import cgi
import cgitb
cgitb.enable()

import logging

# Инициализация логирования
logging.basicConfig(filename='log/check_ip.log', format='%(asctime)s %(message)s', level=logging.DEBUG)

# Разбор переданных аргументов
arguments = cgi.FieldStorage()
ip = arguments.getvalue('ip')

# Передача команды на сервер и получение результата
server = xmlrpclib.ServerProxy('http://localhost:1237')

result = server.check_ip(ip)

print "Content-Type: text/html;charset=utf-8"
print

#print "Sent:     {}".format(data)
print "<br>".join(result.split("\n"))
logging.info(result)
