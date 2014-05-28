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
    out = error
else:
    status = result['status']
    data = result['data']
    
    if status:
        status = 'SUCCESS'
    else:
        status = 'ERROR'
    
    out = [status, ]
    out.append('<table>')
    out.extend(["<tr><td>%s</td><td>%s</td></tr>" % (k, v) for k, v in data.items()])
    out.append('</table>')


print "Content-Type: text/html;charset=utf-8"
print

print "\n".join(out)
