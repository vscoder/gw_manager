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

        self._arptypes = ['ethers', 'ipfw']
        self._arptype = ""
        self._arptable = {}

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


    def addentry(self, ip, mac):
        """Добавить значение в ARP таблицу"""


if __name__ == "__main__":
    
    import argparse

    parser = argparse.ArgumentParser(
        description="""Привязка ip-адресов к mac-адресам""")
    parser.add_argument('-t', '--arptype',
                            help='Способ привязки (ethers, ipfw)')
    parser.add_argument('-f', '--find', 
                            help='Найти соответствия в ARP таблице')
    params = parser.parse_args()

    arptype = params.arptype
    sys.stderr.write("arptype: %s\n" % arptype)
    if type(params.find) == str:
        find = params.find.upper()
        sys.stderr.write("find: %s\n" % find)

    macs = MacAssoc()
    #arptable = macs.arptable

    entrys = macs.arpentrys(find)
    for ip, mac in entrys.items():
        print ip, mac

