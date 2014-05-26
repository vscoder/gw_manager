#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import sys
import cgi
import cgitb
cgitb.enable()

import logging

sys.path.insert(0, "./lib")
from switches import Zabbix
from findmac import Switch

# Инициализация логирования
logging.basicConfig(filename='log/findmac.log', format='%(asctime)s %(message)s', level=logging.DEBUG)

# Разбор переданных аргументов
arguments = cgi.FieldStorage()
pattern = arguments.getvalue('pattern')
mac = arguments.getvalue('mac')
vlan = arguments.getvalue('vlan')

# Инициализация
zabbix = Zabbix(conf = 'conf/main.conf')

switches = zabbix.switchlist(pattern)

result = []

for ip, comm in switches:
    sw = Switch(host = ip)
    sw.proto = 'snmp'
    sw.vlan = vlan
    sw.model = 'A3100'
    sw.community = comm

    port = sw.find_mac(mac)

    if port:
        result.append("MAC '%s' found on %s port %s" % (mac, ip, port))
    else:
        result.append("MAC '%s' not found on %s vlan %s" % (mac, ip, sw.vlan))


print "Content-Type: text/html;charset=utf-8"
print

print "<br>".join(result)
logging.info("\n".join(result))
