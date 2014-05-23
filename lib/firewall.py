#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import re
import subprocess
from distutils import spawn

from gwman import gwman

class Pf(gwman):
    """Управление фаерволом pf"""

    def __init__(self, ip):

        self.pf = self.find_exec("pfctl")

        self.table = 'clients'

        self.ip = ip


    def check_ip(self):
        """Проверить наличие ip в таблице self.table"""
        if not self.ip:
            raise RuntimeError("ip must be set")
        
        if not self.pf:
            raise RuntimeError("can't find 'pfctl' executable")
        
        cmd = [self.pf, '-t', self.table, '-T', 'test', self.ip]
        result = subprocess.call(cmd)
        if result == 0:
            return True
        else:
            return False


class Ipfw(gwman):
    """Работа с фаерволом ipfw"""

    def __init__(self, ip):
        self.ipfw = self.find_exec("ipfw")

        self.tables = (range(2,4))

        self.ip = ip


    def pipenum(self, table):
        """Возвращает номер пайпа для ip-адреса из таблицы ipfw"""
        if not self.ip:
            raise RuntimeError("ip must be set")
        
        # ipfw table N list
        cmd_str = "%s table %d list" % (self.ipfw, table)
        cmd = cmd_str.split()
        cmd_out = subprocess.check_output(cmd)
        table_items = cmd_out.split("\n")
        
        for item in table_items:
            if not item:
                continue
            (net, pipe) = item.split()
            (ip, masklen) = net.split("/")
            if ip == self.ip:
                result = pipe
                break
            result = False

        return result


    def get_shape(self, pipenum):
        """Полоса пропускашия пайпа pipenum"""
        if not str(pipenum).isdigit():
            raise ValueError("'%s' is not valid pipe number" % pipenum)

        cmd = [self.ipfw, 'pipe', pipenum, 'show']
        cmd_out = subprocess.check_output(cmd)

        pipe_items = cmd_out.split("\n")

        pipe_params = pipe_items[0].split()

        shape = pipe_params[1]

        return shape


    def check_ip(self):
        """Проверить шейпер для ipfw"""
        if not self.ip:
            raise RuntimeError("ip must be set")
        
        shape = {}
        for table in self.tables:
            pipenum = self.pipenum(table)
            if pipenum:
                shape[table] = self.get_shape(pipenum)
            else:
                shape[table] = 'unknown'

        return shape


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

    # PF
    pf = Pf(ip = _ip)

    if pf.check_ip():
        print "client '%s' is ON" % _ip
    else:
        print "client '%s' is OFF" % _ip

    # IPFW
    ipfw = Ipfw(ip = _ip)

    pipes = ipfw.check_ip()
    if pipes:
        print "in shape: %s Kbit/s" % pipes[3]
        print "out shape: %s Kbit/s" % pipes[2]
    else:
        print "no shaping found for ip '%s'" % _ip


if __name__ == "__main__":
    main()
