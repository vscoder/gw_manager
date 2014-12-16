#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import socket

from gwman import gwman


class Scan(gwman):

    _protocols = ['tcp', ]
    
    def __init__(self, host='127.0.0.1', port=80, timeout=5, proto='tcp'):
        gwman.__init__(self)
        # TODO: Добавить возможность проверки UDP портов

        self.host = host
        self.port = port
        self.timeout = timeout
        self.proto = proto


    @property
    def proto(self):
        """Протокол (tcp/udp)"""
        return self._proto

    @proto.setter
    def proto(self, proto):
        if proto not in self._protocols:
            raise ValueError('Scan.proto must be in Scan._protocols')

        if proto == 'tcp':
            self.check_port = self.check_tcp_port
        else:
            raise RuntimeError("Checking for protocol '%s' not implemented yet" % proto)

        self._proto = proto


    def check_tcp_port(self):
        """Проверка статуса tcp-порта"""
        host = self.host
        port = int(self.port)

        sock = socket.socket()
        sock.settimeout(float(self.timeout))
        try:
            sock.connect((host, port))
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

    # Инициализация
    scanner = Scan(host = params.host, port = params.port)
    
    if scanner.check_tcp_port():
        print('Open')
    else:
        print('Closed')

if __name__ == "__main__":
    main()
