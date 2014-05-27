#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import xmlrpclib

import cgi
import cgitb
cgitb.enable()

import logging

# Инициализация логирования
logging.basicConfig(filename='log/findmac.log', format='%(asctime)s %(message)s', level=logging.DEBUG)

# Разбор переданных аргументов
arguments = cgi.FieldStorage()
pattern = arguments.getvalue('pattern')
mac = arguments.getvalue('mac')
vlan = arguments.getvalue('vlan')

# Инициализация
server = xmlrpclib.ServerProxy('http://localhost:1237')

result = server.findmac_on_switches(pattern, mac, vlan)


print "Content-Type: text/html;charset=utf-8"
print

print "<br>".join(result)
logging.info("\n".join(result))
