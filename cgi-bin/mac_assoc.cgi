#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import xmlrpclib

import cgi
import cgitb
cgitb.enable()

import logging


# Инициализация логирования
logging.basicConfig(filename='log/mac_assoc.log', format='%(asctime)s %(message)s', level=logging.DEBUG)

# Разбор переданных аргументов
arguments = cgi.FieldStorage()
action = arguments.getvalue('action')
addr = arguments.getvalue('addr')
ip = arguments.getvalue('ip')
mac = arguments.getvalue('mac')

# Передача команды на сервер и получение результата
server = xmlrpclib.ServerProxy('http://localhost:1237')

error = None
# Формирование комманды для передачи серверу
if action == 'find':
    if not addr:
        addr = ""
    result = server.mac_find(addr)
elif action == 'add':
    if not ip or not mac:
        error = "ERROR: IP and MAC must be set"
    result = server.mac_add(ip, mac)
elif action == 'del':
    if not ip:
        error = "ERROR: IP must be set"
    result = server.mac_del(ip)
else:
    error = "ERROR: wrong action '%s'" % action

logging.info(result)

if error:
    raise RuntimeError(error)


print "Content-Type: text/html;charset=utf-8"
print

#print "Sent:     {}".format(data)
print "<br>".join(result.split("\n"))
