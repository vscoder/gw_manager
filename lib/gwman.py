#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import re
import subprocess
from distutils import spawn

class gwman(object):
    
    def __init__(self):
        self.re_ip = re.compile("((2[0-5]|1[0-9]|[0-9])?[0-9]\.){3}((2[0-5]|1[0-9]|[0-9])?[0-9])")
        # see RFC 1123, regex found in http://stackoverflow.com/questions/106179/regular-expression-to-match-hostname-or-ip-address
        self.re_host = re.compile("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$")
        self.re_mac = re.compile("^([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})$")
        self.re_snmpcommunity = re.compile("^[a-zA-Z1-9_\-]+$")

        self.timeout = 5


    def find_exec(self, cmd):
        """Вернет полный путь к исполняемому файлу
        или выдаст исключение"""
        result = spawn.find_executable(cmd)

        if not result:
            raise RuntimeError("Can't find executable '%s' in PATH\n%s" % \
                              (cmd, spawn.os.environ['PATH']))

        return result

    def mac_conv(self, mac):
        """Приводит мак-адрес к виду HH:HH:HH:HH:HH:HH"""
        mac = mac.upper()
        mac_str = mac.translate(None, ':-')
        mac_arr = re.findall('..', mac_str)
        mac = ":".join(mac_arr)

        return mac


    @property
    def host(self):
        """Хост"""
        return self._host

    @host.setter
    def host(self, host):
        if not self.re_host.match(host):
            raise ValueError("%s is not valid host" % host)

        self._host = host


    @property
    def ip(self):
        """ip"""
        return self._ip

    @ip.setter
    def ip(self, ip):
        if not self.re_ip.match(ip):
            raise ValueError("%s is not valid ip address" % ip)

        self._ip = ip


    @property
    def port(self):
        """Порт хоста (для подключения snmp, telnet etc..."""
        return self._port

    @port.setter
    def port(self, port):
        port = str(port)
        if port.isdigit():
            port = int(port)
        else:
            raise ValueError("'%s' is not valid port number" % port)

        if port <= 0 or port > 65535:
            raise ValueError("'%s' is not in range 0-65535" % port)

        self._port = port


    @property
    def mac(self):
        """mac"""
        return self._mac

    @mac.setter
    def mac(self, mac):
        mac = self.mac_conv(mac)
        if not self.re_mac.match(mac):
            raise ValueError("%s is not valid mac address" % mac)

        self._mac = mac


    @property
    def timeout(self):
        """Время ожидания"""
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        self._timeout = int(timeout)


def main():
    # Обработка аргументов коммандной строки
    import argparse
    parser = argparse.ArgumentParser(
        description="""Проверка правильности переданных параметров""")
    parser.add_argument('-H', '--host', 
        metavar = 'HOST',
        help = 'Имя хоста для проверки')
    parser.add_argument('-i', '--ip', 
        metavar = 'IP',
        help = 'IP адрес для проверки')
    parser.add_argument('-p', '--port', 
        metavar = 'PORT',
        help = 'Номер порта для проверки')
    parser.add_argument('-m', '--mac', 
        metavar = 'MAC',
        help = 'Mac-адрес для проверки')
    parser.add_argument('-e', '--executable', 
        metavar = 'EXECUTABLE',
        help = 'Исполняемый фаил для поиска')
    params = parser.parse_args()

    # Инициализация
    gwc = gwman()
    if params.host:
        gwc.host = params.host
    if params.ip:
        gwc.ip = params.ip
    if params.port:
        gwc.port = params.port
    if params.mac:
        gwc.mac = params.mac
    if params.executable:
        ex = gwc.find_exec(params.executable)
    
    print "All tests complete sucefully"
    

if __name__ == "__main__":
    main()