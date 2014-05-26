#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import cgi
import cgitb
cgitb.enable()

import sys
import os

import logging

sys.path.insert(0, "./lib")
from mac_assoc import MacAssoc

# Инициализация логирования
import logging
logging.basicConfig(filename='log/mac_assoc.log', format='%(asctime)s %(message)s', level=logging.DEBUG)

# Инициализация класса
macs = MacAssoc('ethers')

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
if mac:
    mac = mac.replace("-",":")


print "Content-Type: text/html;charset=utf-8"
print

if find:
    entries = macs.find_arp(find)

    print "<table>"
    for _ip, _mac in entries.items():
        print "<tr><td>%s</td><td>%s</td></tr>\n" % (_ip, _mac)
    print "</table>"
elif rm:
    macs.mac = rm
    if macs.arptype == 'ethers':
            macs.del_arp()
    if macs.delete():
        print "OK: del association from system arp table for ip: '%s'" % (macs.mac)
        logging.info("OK: del association from system arp table for ip: '%s'" % (macs.mac))
    else:
        print "ERROR: del association from system arp table for ip: '%s'" % (macs.mac)
        logging.warning("ERROR: del association from system arp table for ip: '%s'" % (macs.mac))
elif add:
    macs.ip = ip
    macs.mac = mac
    if macs.set():
        if macs.arptype == 'ethers':
            macs.ethers_to_arp()
        print "OK: set association from '%s' for ip: '%s', mac: '%s'" % (macs.arptype, macs.ip, macs.mac)
        logging.info("OK: set association from '%s' for ip: '%s', mac: '%s'" % (macs.arptype, macs.ip, macs.mac))
    else:
        print "ERROR: set association from '%s' for ip: '%s', mac: '%s'" % (macs.arptype, macs.ip, macs.mac)
        loggini.warning("ERROR: set association from '%s' for ip: '%s', mac: '%s'" % (macs.arptype, macs.ip, macs.mac))
