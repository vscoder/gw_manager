#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import re
import subprocess
from distutils import spawn


class Ping(object):
    """Пинг средствами комманды ping"""

    def __init__(self, host):
        # see RFC 1123, regex found in http://stackoverflow.com/questions/106179/regular-expression-to-match-hostname-or-ip-address
        self.re_host = re.compile("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$")

        self.ping = spawn.find_executable("ping")

        self.host = host
        self._count = "4"
        self._timeout = 1000


    @property
    def host(self):
        """Хост для проверки"""
        return self._host

    @host.setter
    def host(self, host):
        if not self.re_host.match(host):
            raise ValueError("%s is not valid host name" % host)
        self._host = host

    @property
    def count(self):
        """Количество посылаемых icmp-пакетов"""
        return str(self._count)

    @count.setter
    def count(self, count):
        if not count:
            count = self._count
        if not count.isdigit():
            raise ValueError("%s is not valid ping count" % count)
        self._count = count

    @property
    def timeout(self):
        """Время ожидания ответа, ms"""
        return str(self._timeout)

    @timeout.setter
    def timeout(self, timeout):
        timeout = str(timeout)
        if not timeout.isdigit():
            raise ValueError("%s is not valid timeout" % timeout)
        self._timeout = timeout

    def ping_host(self):
        """Выполнить пинг хоста host"""
        if not self._host:
            raise RuntimeError("host must be set")
        if not self.ping:
            raise RuntimeError("can't find 'ping' executable")
        
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
