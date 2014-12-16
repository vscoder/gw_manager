#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import re
import subprocess
from distutils import spawn

class gwman(object):
    
    _re_host = re.compile("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$")
    # see RFC 1123, regex found in http://stackoverflow.com/questions/106179/regular-expression-to-match-hostname-or-ip-address
    _re_ip = re.compile("^((2[0-5]|1[0-9]|[0-9])?[0-9]\.){3}((2[0-5]|1[0-9]|[0-9])?[0-9])$")
    _re_mac = re.compile("^([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})$")
    _re_community = re.compile("^[a-zA-Z1-9_\-]+$")

    def __init__(self):
        self._ip = None
        self._host = None
        self._mac = None
        self._port = None
        self._vlan = None
        self._timeout = None


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
    def host(self, value):
        if not self._re_host.match(value):
            raise ValueError("%s is not valid host" % value)

        self._host = value


    def _check_ip(self, ip):
        """Если ip адрес валидный, вернет ip
        иначе exception"""
        if not self._re_ip.match(ip):
            return False
        else:
            return ip

    @property
    def ip(self):
        """ip адрес"""
        return self._ip

    @ip.setter
    def ip(self, ip):
        if not self._check_ip(ip):
            raise ValueError("%s is not valid ip address" % ip)
        self._ip = ip


    @property
    def port(self):
        """Порт хоста (для подключения snmp, telnet etc..."""
        return str(self._port)

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
        """mac-адрес"""
        return self._mac

    @mac.setter
    def mac(self, mac):
        mac = self.mac_conv(mac)
        if not self._re_mac.match(mac):
            raise ValueError("%s is not valid mac address" % mac)

        self._mac = mac


    @property
    def vlan(self):
        """vlan"""
        return str(self._vlan)

    @vlan.setter
    def vlan(self, vlan):
        vlan = str(vlan)
        if not vlan.isdigit():
            raise ValueError("'%s' is not valid vlan number" % vlan)
        vlan = int(vlan)
        if vlan > 4000 or vlan < 1:
            raise ValueError("vlan must be integer between 1 and 4000")

        self._vlan = vlan


    @property
    def timeout(self):
        """Время ожидания"""
        return str(self._timeout)

    @timeout.setter
    def timeout(self, timeout):
        timeout = str(timeout)
        if not timeout.isdigit():
            raise ValueError("'%s' is not valid timeout" % timeout)

        self._timeout = timeout


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
    parser.add_argument('-v', '--vlan', 
        metavar = 'VLAN',
        help = 'Номер vlan для проверки')
    parser.add_argument('-t', '--timeout', 
        metavar = 'VLAN',
        help = 'Время ожидания для проверки')
    parser.add_argument('-e', '--executable', 
        metavar = 'EXECUTABLE',
        help = 'Исполняемый фаил для поиска')
    params = parser.parse_args()

    # Инициализация
    gwc = gwman()
    if params.host:
        gwc.host = params.host
        print gwc.host
    if params.ip:
        gwc.ip = params.ip
        print gwc.ip
    if params.port:
        gwc.port = params.port
        print gwc.port
    if params.mac:
        gwc.mac = params.mac
        print gwc.mac
    if params.vlan:
        gwc.vlan = params.vlan
        print gwc.vlan
    if params.timeout:
        gwc.timeout = params.timeout
        print gwc.timeout
    if params.executable:
        ex = gwc.find_exec(params.executable)
        print ex
    
    print "All tests complete sucefully"
    

if __name__ == "__main__":
    main()
