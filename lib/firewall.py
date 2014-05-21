#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import re
import subprocess
from distutils import spawn


class Pf(object):
    """Управление фаерволом pf"""

    def __init__(self, ip):
        self.re_ip = re.compile("((2[0-5]|1[0-9]|[0-9])?[0-9]\.){3}((2[0-5]|1[0-9]|[0-9])?[0-9])")

        self.pf = spawn.find_executable("pfctl")

        self.table = 'clients'

        self.ip = ip


    @property
    def ip(self):
        """Хост для проверки"""
        return self._ip

    @ip.setter
    def ip(self, ip):
        if not self.re_ip.match(ip):
            raise ValueError("%s is not valid ip address" % ip)

        self._ip = ip

    def check_ip(self):
        """Проверить наличие ip в таблице self.table"""
        if not self.ip:
            raise RuntimeError("ip must be set")
        
        cmd = [self.pf, '-t', self.table, '-T', 'test', self.ip]
        result = subprocess.call(cmd)
        if result == 0:
            return True
        else:
            return False


class Ipfw(object):
    """Управление фаерволом ipfw"""
    pass


def main():
    # Обработка аргументов коммандной строки
    import argparse
    parser = argparse.ArgumentParser(
        description="""Проверка ip""")
    parser.add_argument('-i', '--ip',
        metavar = 'IP',
        help = 'IP для проверки')
    params = parser.parse_args()

    _ip = params.ip

    # Инициализация
    pf = Pf(ip = _ip)

    if pf.check_ip():
        print "client '%s' is ON" % _ip
    else:
        print "client '%s' is OFF" % _ip


if __name__ == "__main__":
    main()
