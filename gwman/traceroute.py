#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import re
import subprocess
from distutils import spawn

from gwman import gwman

class Traceroute(gwman):
    """Трасировка средствами комманды traceroute"""

    def __init__(self, host='127.0.0.1', hops='8'):
        gwman.__init__(self)

        self.traceroute = self.find_exec("traceroute")

        self.host = host
        self._hops = hops
        #self.timeout = 0


    @property
    def hops(self):
        """Максимальное количество промежуточных узлов"""
        return str(self._hops)

    @hops.setter
    def hops(self, hops):
        if not hops:
            hops = self._count
        hops = str(hops)
        if not hops.isdigit():
            raise ValueError("%s is not valid traceroute count" % hops)
        self._hops = hops


    def traceroute_host(self):
        """Выполнить трасировку до хоста host"""
        if not self.host:
            raise RuntimeError("host must be set")
        
        cmd = [self.traceroute, '-m', self.hops, self.host]
        PIPE = subprocess.PIPE
        traceroute = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output = traceroute.stdout.read()
        retcode = traceroute.poll()
        return (retcode, output)


def main():
    # Обработка аргументов коммандной строки
    import argparse
    parser = argparse.ArgumentParser(
        description="""traceroute host""")
    parser.add_argument('-H', '--host',
        metavar = 'HOST',
        help = 'host для пинга')
    parser.add_argument('-m', '--hops',
        metavar = 'HOPS',
        default = 8,
        help = 'максимальное количество промежуточных узлов (по умолчанию: 8)')
    params = parser.parse_args()

    traceroute = Traceroute(params.host, params.hops)
    #traceroute.timeout = 1
    result = traceroute.traceroute_host()

    print "returncode: %s\n%s" % result


if __name__ == "__main__":
    main()
