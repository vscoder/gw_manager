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

result = server.scan_tcp(host, port)
logging.info(result)

status = result['status']
data = result['data']

if status:
    status = 'SUCCESS'
    if data['port_status']:
        port_status = 'OPEN'
    else:
        port_status = 'CLOSED'
    out = ("TCP port %s on host '%s' is %s" % (port, host, port_status), )
else:
    status = 'ERROR'
    out = [status, ]
    out.append('<table>')
    out.extend(["<tr><td>%s</td><td>%s</td></tr>" % (k, v) for k, v in data.items()])
    out.append('</table>')

print "Content-Type: text/html;charset=utf-8"
print

print "\n".join(out)
