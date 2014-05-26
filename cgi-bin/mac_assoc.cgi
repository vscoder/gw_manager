#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import sys
import cgi
import socket
import cgitb
cgitb.enable()

import logging

#sys.path.insert(0, "./lib")

# Инициализация логирования
logging.basicConfig(filename='log/mac_assoc.log', format='%(asctime)s %(message)s', level=logging.DEBUG)

# Разбор переданных аргументов
arguments = cgi.FieldStorage()
action = arguments.getvalue('action')
addr = arguments.getvalue('addr')
ip = arguments.getvalue('ip')
mac = arguments.getvalue('mac')

error = None
# Формирование комманды для передачи серверу
if action == 'find':
    if not addr:
        error = "ERROR: 'addr' must be set!"
    cmd = "mac_ass %s %s" % (action, addr)
elif action == 'add':
    if not ip or not mac:
        error = "ERROR: IP and MAC must be set"
    cmd = "mac_ass %s %s %s" % (action, ip, mac)
elif action == 'del':
    if not ip:
        error = "ERROR: IP must be set"
    cmd = "mac_ass %s %s" % (action, ip)
else:
    error = "ERROR: wrong action '%s'" % action
logging.info(cmd)

if error:
    raise RuntimeError(error)

# Передача команды на сервер и получение результата
HOST, PORT = "localhost", 1237
data = cmd

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    sock.sendall(data + "\n")

    # Receive data from the server and shut down
    received = sock.recv(16384)
finally:
    sock.close()

print "Content-Type: text/html;charset=utf-8"
print

#print "Sent:     {}".format(data)
print "<br>".join(received.split("\n"))
logging.info(received)
