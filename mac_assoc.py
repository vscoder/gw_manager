#!/usr/bin/env python
# -*- coding: utf_8 -*-

import sys
import re

import dnet

class MacAssoc(object):
    """Управление привязкой mac-адресов к ip-адресам"""


    def __init__(self):
        self._re_ip = re.compile("((2[0-5]|1[0-9]|[0-9])?[0-9]\.){3}((2[0-5]|1[0-9]|[0-9])?[0-9])")
        self._re_mac = re.compile("^([0-9A-F]{2}[:-]){5}([0-9A-F]{2})$")

        self._arptypes = ['ethers', 'ipfw', 'script']
        self._script = ""
        self._arptype = ""
        self._arptable = {}

        self.ipfw_start = 600

        self.arptable


    @property
    def arptype(self):
        """Тип ARP-фильтрации"""
        return self._arptype

    @arptype.setter
    def arptype(self, arptype):
        if arptype not in self._arptypes:
            raise ValueError("wrong arp type")
        self._arptype = arptype


    @property
    def arptable(self):
        """Получить соответствия mac-ip из ARP таблицы"""
        arp = dnet.arp()

        def add_entry((pa, ha), arg):
            arg[str(pa)] = str(ha).upper()

        arp.loop(add_entry, self._arptable)

        return self._arptable


    def arpentrys(self, addr):
        """Получить значение из ARP таблицы
        addr -- ip или mac адрес"""
        
        result = {}
        for ip, mac in self._arptable.items():
            if ip.find(addr) >= 0 or mac.find(addr) >= 0:
                result[ip] = mac

        return result

    def rulenum(self, ip):
        """Сгенерировать номер правила в ipfw
        на основе ip адреса"""
        octets = ip.split(".")
        num = int(octets[3])
        rulenum = self.ipfw_start + num
        return rulenum

    def add_arp(self, ip, mac):
        """Добавить значение в ARP таблицу"""

    def add_ipfw(self, ip, mac):
        """Добавить правило в ipfw"""

    def add_script(self, ip, mac):
        """Выполнить скрипт с параметрами ip, mac"""

if __name__ == "__main__":
    
    import subprocess
    import argparse

    parser = argparse.ArgumentParser(
        description="""Привязка ip-адресов к mac-адресам""")
    parser.add_argument('-t', '--arptype',
                            help='Способ привязки (ethers, ipfw, script)')
    parser.add_argument('-s', '--script',
                            help='Скрипт при --arptype=script')
    parser.add_argument('-f', '--find', 
                            help='Найти соответствия в ARP таблице')
    params = parser.parse_args()

    arptype = params.arptype
    sys.stderr.write("arptype: %s\n" % arptype)
    if type(params.find) == str:
        find = params.find.upper()
        sys.stderr.write("find: %s\n" % find)

    if arptype == 'script':
        if type(params.script) == str:
            script = params.script
            sys.stderr.write("script: %s\n" % script)
        else:
            parser.print_usage()
            sys.exit()

    macs = MacAssoc()

    entrys = macs.arpentrys(find)
    for ip, mac in entrys.items():
        rulenum = macs.rulenum(ip)
        #print ip, mac, rulenum
        if arptype == 'script':
            output = subprocess.check_output([script, ip, mac])
            print output

