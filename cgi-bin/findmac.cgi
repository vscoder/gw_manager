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

params = {'pattern': pattern,
          'mac': mac,
          'vlan': vlan,
          }
result = server.findmac_on_switches(params)
logging.info("\n".join(result))

status = result['status']
data = result['data']

if status:
    status = 'SUCCESS'
else:
    status = 'ERROR'

out = [status, ]
out.append('<table>')
out.extend(["<tr><td>%s</td><td>%s</td></tr>" % (k, "</td><td>".join((v['mac'], str(v['port'])))) for k, v in data.items()])
out.append('</table>')


print "Content-Type: text/html;charset=utf-8"
print

print "\n".join(out)
