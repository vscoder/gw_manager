#!/usr/bin/env python
# -*- coding: utf_8 -*-

import cgi
import cgitb
cgitb.enable()

import sys
import os

import logging

sys.path.insert(0, "./")
from mac_assoc import MacAssoc

# Инициализация логирования
import logging
logging.basicConfig(filename='log/wrapper.log', format='%(asctime)s %(message)s', level=logging.DEBUG)

# Инициализация класса
macs = MacAssoc()
macs.arptype = 'ethers'

# Разбор переданных аргументов
arguments = cgi.FieldStorage()
# find
find = arguments.getvalue('find')
# remove
rm = arguments.getvalue('del')
# set assignment
add = arguments.getvalue('set')
ip = arguments.getvalue('ip')
mac = arguments.getvalue('mac')

print "Content-Type: text/html;charset=utf-8"
print

if find:
    entries = macs.find_assoc(find)

    print "<table>"
    for ip, mac in entries.items():
        print "<tr><td>%s</td><td>%s</td></tr>\n" % (ip, mac)
    print "</table>"
elif rm:
    if macs.del_assoc(rm):
        if macs.arptype == 'ethers':
            macs.ethers_to_arp()
        print "OK: del association from '%s' for ip: '%s'" % (macs.arptype, rm)
        logging.info("OK: del association from '%s' for ip: '%s'" % (macs.arptype, rm))
    else:
        print "ERROR: del association from '%s' for ip: '%s'" % (macs.arptype, rm)
        logging.warning("ERROR: del association from '%s' for ip: '%s'" % (macs.arptype, rm))
elif add:
    if macs.set_assoc(ip, mac):
        if macs.arptype == 'ethers':
            macs.ethers_to_arp()
        print "OK: set association from '%s' for ip: '%s', mac: '%s'" % (macs.arptype, ip, mac)
        logging.info("OK: set association from '%s' for ip: '%s', mac: '%s'" % (macs.arptype, ip, mac))
    else:
        print "ERROR: set association from '%s' for ip: '%s', mac: '%s'" % (macs.arptype, ip, mac)
        loggini.warning("ERROR: set association from '%s' for ip: '%s', mac: '%s'" % (macs.arptype, ip, mac))
