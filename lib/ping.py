#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import re
import subprocess
from distutils import spawn

from gwman import gwman

class Ping(gwman):
    """Пинг средствами комманды ping"""

    def __init__(self, host='127.0.0.1'):

        self.ping = self.find_exec("ping")

        self.host = host

        self._count = "4"
        self.timeout = 1000


    @property
    def count(self):
        """Количество посылаемых icmp-пакетов"""
        return str(self._count)

    @count.setter
    def count(self, count):
        if not count:
            count = self._count
        count = str(count)
        if not count.isdigit():
            raise ValueError("%s is not valid ping count" % count)
        self._count = count


    def ping_host(self):
        """Выполнить пинг хоста host"""
        if not self.host:
            raise RuntimeError("host must be set")
        
        cmd = [self.ping, '-c', self.count, '-W', self.timeout, self.host]
        PIPE = subprocess.PIPE
        ping = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output = ping.stdout.read()
        retcode = ping.poll()
        return (retcode, output)


def main():
    # Обработка аргументов коммандной строки
    import argparse
    parser = argparse.ArgumentParser(
        description="""ping host""")
    parser.add_argument('-H', '--host',
        metavar = 'HOST',
        help = 'host для пинга')
    params = parser.parse_args()

    ping = Ping(params.host)
    ping.timeout = 1
    result = ping.ping_host()

    print "returncode: %s\n%s" % result


if __name__ == "__main__":
    main()
