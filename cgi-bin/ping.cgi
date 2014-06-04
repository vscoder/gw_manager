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

params = {'host': host,
          'count': count,
          }
result = server.ping(params)
logging.info(result)

status = result['status']
data = result['data']

if status:
    status = 'SUCCESS'
    if data['pinged']:
        pinged = 'OK'
    else:
        pinged = 'NO'
    ping_out = data['out']
    out = ("Pinged: %s<br>%s" % (pinged, "<br>".join(ping_out)), )
else:
    status = 'ERROR'
    out = [status, ]
    out.append('<table>')
    out.extend(["<tr><td>%s</td><td>%s</td></tr>" % (k, v) for k, v in data.items()])
    out.append('</table>')

print "Content-Type: text/html;charset=utf-8"
print

print "\n".join(out)
