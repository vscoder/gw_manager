#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import sys
import cgi
import cgitb
cgitb.enable()

import logging

sys.path.insert(0, "./lib")
from firewall import Pf
from firewall import Ipfw

# Инициализация логирования
logging.basicConfig(filename='log/check_ip.log', format='%(asctime)s %(message)s', level=logging.DEBUG)

# Разбор переданных аргументов
arguments = cgi.FieldStorage()
ip = arguments.getvalue('ip')

# Инициализация класса
# PF
pf = Pf(ip = ip)

if pf.check_ip():
    status = 'ON'
else:
    status = 'OFF'

# IPFW
ipfw = Ipfw(ip = ip)

pipes = ipfw.check_ip()
if pipes:
    shape_in = pipes[3]
    shape_out = pipes[2]
else:
    shape_in = 'unknown'
    shape_out = 'unknown'


print "Content-Type: text/html;charset=utf-8"
print

st = "client '%s' is %s" % (ip, status)
s_in = "in shape: %s Kbit/s" % shape_in
s_out = "out shape: %s Kbit/s" % shape_out
print st
print s_in
print s_out
logging.info(st)
logging.info(s_in)
logging.info(s_out)
