#!/usr/bin/env python2
# -*- coding: utf_8 -*-

class switch(object):
    
    def __init__(self, host='127.0.0.1', port=161):
        #self.re_ip = re.compile("((2[0-5]|1[0-9]|[0-9])?[0-9]\.){3}((2[0-5]|1[0-9]|[0-9])?[0-9])")
        # see RFC 1123, regex found in http://stackoverflow.com/questions/106179/regular-expression-to-match-hostname-or-ip-address
        self.re_host = re.compile("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$")
        self._models = ['A3100', ]
        self._protocols = ['snmp', 'telnet']

        #self._host = '127.0.0.1'
        #self._port = 161

        self.host = host
        self.port = port
        self.timeout = 5

    @property
    def host(self):
        """Хост для проверки"""
        return self._host

    @host.setter
    def host(self, host):
        if not self.re_host.match(host):
            raise ValueError("%s is not valid ip address" % host)

        self._host = host

    @property
    def port(self):
        """Порт"""
        return self._port

    @port.setter
    def port(self, port):
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
        elif proto == 'telnet':
            self.port = 23

        self._proto = proto

    @property
    def timeout(self):
        """Время ожидания подключения"""
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        self._timeout = int(timeout)

    def find_mac_snmp(self):
        """Поиск mac-адреса с помощью snmp"""
        host = self.host
        port = int(self.port)


def main():
    # Обработка аргументов коммандной строки
    import argparse
    parser = argparse.ArgumentParser(
        description="""Анализ хоста""")
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
    

if __name__ == "__main__":
    main()
