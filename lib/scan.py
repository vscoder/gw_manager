#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import socket
import re


class Scan(object):
    
    def __init__(self, host='127.0.0.1', port=80):
        self.re_ip = re.compile("((2[0-5]|1[0-9]|[0-9])?[0-9]\.){3}((2[0-5]|1[0-9]|[0-9])?[0-9])")
        # TODO: Добавить возможность проверки UDP портов
        self._protocols = ['tcp', ]

        self._host = '127.0.0.1'
        self._port = 80

        self.host = host
        self.port = port

    @property
    def host(self):
        """Хост для проверки"""
        return self._host

    @host.setter
    def host(self, host):
        if not self.re_ip.match(host):
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
        """Протокол (tcp/udp)"""
        return self._proto


    def check_tcp_port(self):
        """Проверка статуса tcp-порта"""
        host = self.host
        port = int(self.port)

        #socket.socket().connect((host, port))
        try:
            socket.socket().connect((host, port))
            #if results is not None:
            #    results.append(port)
            return True
        except:
            return False


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
    params = parser.parse_args()

    _host = params.host
    _port = params.port

    # Инициализация
    scanner = Scan(host = _host, port = _port)
    
    if scanner.check_tcp_port():
        print('Open')
    else:
        print('Closed')

if __name__ == "__main__":
    main()
