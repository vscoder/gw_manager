#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import re

class Switch(object):
    
    def __init__(self, host='127.0.0.1', port=161):
        #self.re_ip = re.compile("((2[0-5]|1[0-9]|[0-9])?[0-9]\.){3}((2[0-5]|1[0-9]|[0-9])?[0-9])")
        # see RFC 1123, regex found in http://stackoverflow.com/questions/106179/regular-expression-to-match-hostname-or-ip-address
        self.re_host = re.compile("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$")
        self.re_mac = re.compile("^([0-9A-F]{2}[:-]){5}([0-9A-F]{2})$")

        self._models = ['A3100', 'OTHER', ]
        self._protocols = ['snmp', 'telnet']

        #self._host = '127.0.0.1'
        #self._port = 161

        self.host = host
        self.port = port
        self.timeout = 5

        self.mactable_oid = ''


    @property
    def host(self):
        """Хост для поиска на нем мак-адреса"""
        return self._host

    @host.setter
    def host(self, host):
        if not self.re_host.match(host):
            raise ValueError("%s is not valid ip address" % host)

        self._host = host

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
    def proto(self):
        """Протокол (snmp/telnet)"""
        return self._proto

    @proto.setter
    def proto(self, proto):
        if proto not in self._protocols:
            raise ValueError("'%s' is not valid protocol" % proto)

        if proto == 'telnet':
            raise ValueError("Protocol '%s' not implemented yet" % proto)

        # Do protocol-dependent actions
        if proto == 'snmp':
            self.port = 161
            self.find_mac = self.find_mac_snmp
        elif proto == 'telnet':
            self.port = 23
            self.find_mac = self.find_mac_telnet

        self._proto = proto

    @property
    def model(self):
        """Модель свича"""
        return self._model

    @model.setter
    def model(self, model):
        if model not in self._models:
            raise ValueError("wrong model '%s', see switch.models" % model)

        if model == 'A3100':
            self.mactable_oid = '.1.3.6.1.2.1.17.7.1.2.2.1.2.1'
        elif model == 'OTHER':
            self.mactable_oid = '.1.3.6.1.2.1.17.4.3.1.2'
        else:
            self.mactable_oid = ''


    @property
    def timeout(self):
        """Время ожидания подключения"""
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        self._timeout = int(timeout)


    def mac_oid(self, mac):
        """Конвертирует mac вида XX:XX:XX:XX:XX:XX
        в десятичное предсятичное представление N.N.N.N.N.N"""
        mac = mac.upper()
        if not self.re_mac.match(mac):
            raise ValueError("Bad mac-address '%s'" % mac)

        mac_str = mac.translate(None, ':-')
        mac_arr = re.findall('..', mac_str)
        
        mac_oid_arr = [str(int(hh, base=16)) for hh in mac_arr]
        mac_oid = ".".join(mac_oid_arr)

        return mac_oid


    def find_mac_snmp(self, mac):
        """Поиск mac-адреса с помощью snmp"""
        host = self.host
        port = self.port

        oid = "%s.%s" % (self.mactable_oid, self.mac_oid(mac))

        return oid


#class model(object):
#    """Модель свича. Реализует mactable_oid или набор комманд telnet"""


def main():
    # Обработка аргументов коммандной строки
    import argparse
    parser = argparse.ArgumentParser(
        description="""Поиск мак-адреса на свиче""")
    parser.add_argument('-H', '--host', 
        metavar = 'HOST',
        help = 'Хост для проверки')
    parser.add_argument('-p', '--port', 
        metavar = 'PORT',
        help = 'Порт для проверки')
    parser.add_argument('-m', '--mac', 
        metavar = 'MAC',
        help = 'Mac-адрес для поиска')
    params = parser.parse_args()

    _host = params.host
    _port = params.port

    # Инициализация
    sw = Switch(host = params.host)
    sw.proto = 'snmp'
    sw.model = 'A3100'
    
    res = sw.find_mac(params.mac)

    print res
    

if __name__ == "__main__":
    main()
