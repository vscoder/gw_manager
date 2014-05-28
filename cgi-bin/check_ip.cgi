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
logging.info(result)

status = result['status']
data = result['data']

if status:
    status = 'SUCCESS'
    if data['ipstatus']:
        data['ipstatus'] = 'ON'
    else:
        data['ipstatus'] = 'OFF'
else:
    status = 'ERROR'


out = [status, ]
out.append('<table>')
out.extend(["<tr><td>%s</td><td>%s</td></tr>" % (k, v) for k, v in data.items()])
out.append('</table>')

print "Content-Type: text/html;charset=utf-8"
print

print "\n".join(out)
