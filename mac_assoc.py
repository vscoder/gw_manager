#!/usr/bin/env python
# -*- coding: utf_8 -*-

import sys
import re
import subprocess
from distutils import spawn

import dnet

class MacAssoc(object):
    """Управление привязкой mac-адресов к ip-адресам"""


    def __init__(self):
        self._re_ip = re.compile("((2[0-5]|1[0-9]|[0-9])?[0-9]\.){3}((2[0-5]|1[0-9]|[0-9])?[0-9])")
        self._re_mac = re.compile("^([0-9A-F]{2}[:-]){5}([0-9A-F]{2})$")


        self._arptypes = ['ethers', 'ipfw', 'arp', 'script']

        self._arptype = ""
        self.ethers = "/etc/ethers"
        self._script = "echo"
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


    def find_arp(self, addr):
        """Получить значение из ARP таблицы
        addr -- ip или mac адрес"""
        result = {}
        for ip, mac in self.arptable.items():
            if addr in ip or addr in mac:
                result[ip] = mac
        return result

    def get_arp(self, addr):
        """Получить значение из ARP таблицы
        addr -- ip или mac адрес"""
        result = []
        for ip, mac in self.arptable.items():
            if addr == ip or addr == mac:
                result = (ip, mac)
        return result

    def rulenum(self, ip):
        """Сгенерировать номер правила в ipfw
        на основе ip адреса"""
        octets = ip.split(".")
        num = int(octets[3])
        rulenum = self.ipfw_start + num
        return rulenum

    def find_ethers(self, addr):
        """Поиск соответствия в файле self.ethers"""
        result = {}
        with open(self.ethers, 'r') as f:
            for line in f:
                if addr in line:
                    ip, mac = line.split()
                    result[ip] = mac
        return result

    def get_ethers(self, addr):
        """Получение соответствия из файла self.ethers"""
        result = []
        with open(self.ethers, 'r') as f:
            for line in f:
                ip, mac = line.split()
                if addr == ip or addr == mac:
                    result = (ip, mac)
        return result

    def set_ethers(self, (ip, mac)):
        """Задание соответствия в файле self.ethers"""
        # Преобразуем фаил в словарь {ip: mac, }
        entries = {}
        with open(self.ethers, 'r') as f:
            _ip, _mac = f.readline().split()
            entries[_ip] = _mac
        # Изменяем запись
        entries[ip] = mac

        # Перезаписываем фаил
        with open(self.ethers, 'w') as f:
            for _ip, _mac in entries.items():
                f.write("%s\t%s\n" % (_ip, _mac))
        
    def del_ethers(self, addr):
        """Удаление соответствия из файла self.ethers"""
        # Преобразуем фаил в словарь {ip: mac, }
        # и если строка соответствует поиску не добавляем ее
        entries = {}
        with open(self.ethers, 'r') as f:
            line = f.readline()
            if addr not in line:
                _ip, _mac = line.split()
                entries[_ip] = _mac

        # Перезаписываем фаил
        with open(self.ethers, 'w') as f:
            for _ip, _mac in entries.items():
                f.write("%s\t%s\n" % (_ip, _mac))
        

    def find_assoc(self, addr):
        """Команда для поиска записи
        в текущем хранилище ARP-привязок"""
        print "arptype == %s" % self._arptype
        if self.arptype == 'ethers':
            return self.find_ethers(addr)
        elif self.arptype == 'arp':
            return self.find_arp(addr)
        elif self.arptype == 'ipfw':
            pass

        elif self.arptype == 'script':
            pass

        else:
            pass

    def get_assoc(self, addr):
        """Команда для получения записи
        из текущего хранилища ARP-привязок"""
        print "arptype == %s" % self._arptype
        if self.arptype == 'ethers':
            return self.get_ethers(addr)
        elif self.arptype == 'arp':
            return self.get_arp(addr)
        elif self.arptype == 'ipfw':
            pass

        elif self.arptype == 'script':
            pass

        else:
            pass


    def set_assoc(self, ip, mac):
        """Команда для добавления записи
        в текущее хранилище ARP-привязок"""

    
    def del_assoc(self):
        """Команда для удаления записи
        из текущего хранилища ARP-привязок"""


    def add_arp(self, ip, mac):
        """Добавить значение в ARP таблицу"""

    def add_ipfw(self, ip, mac):
        """Добавить правило в ipfw"""

    def add_script(self, ip, mac):
        """Выполнить скрипт с параметрами ip, mac"""

if __name__ == "__main__":
    
    import argparse

    macs = MacAssoc()

    parser = argparse.ArgumentParser(
        description="""Привязка ip-адресов к mac-адресам
                       Все привязки дублируются в --ethers""")
    parser.add_argument('-t', '--arptype',
                        metavar = 'TYPE',
                        default = macs._arptypes[0],
                        choices = macs._arptypes,
                        help = 'Способ привязки (%s)' % ", ".join(macs._arptypes))
    parser.add_argument('-s', '--script',
                        metavar = 'FILE',
                        help = 'Скрипт при --arptype=script')
    parser.add_argument('-e', '--ethers',
                        metavar = 'FILE',
                        default = macs.ethers,
                        help = 'Фаил с соответствиями mac\tip')
    parser.add_argument('-f', '--find', 
                        metavar = 'PATTERN',
                        help = 'Найти соответствия в ARP таблице')
    parser.add_argument('-g', '--get', 
                        metavar = 'PATTERN',
                        help = 'Получить соответствие из текущего хранилища (arptype)')
    params = parser.parse_args()

    macs.arptype = params.arptype
    sys.stderr.write("arptype: %s\n" % macs.arptype)

    # FIND
    if type(params.find) == str:
        find = params.find.upper()
        sys.stderr.write("find: %s\n" % find)
    else:
        find = None

    # GET
    if type(params.get) == str:
        get = params.get.upper()
        sys.stderr.write("get: %s\n" % get)
    else:
        get = None

    # SCRIPT
    if type(params.script) == str:
        script = params.script
        sys.stderr.write("script: %s\n" % script)

    # ETHERS
    if type(params.ethers) == str:
        macs.ethers = params.ethers
    sys.stderr.write("ethers: %s\n" % macs.ethers)

    if find:
        entries = macs.find_assoc(find)
        for ip, mac in entries.items():
            #rulenum = macs.rulenum(ip)
            print "in %s found ip: %s\tmac: %s" % (macs.arptype, ip, mac)
            #if arptype == 'script':
            #    if (rulenum - macs.ipfw_start) > 128: continue
            #    output = subprocess.check_output([script, ip, mac])
            #    print output

    if get:
        result = macs.get_assoc(get)
        if result:
            print "in %s found ip: %s\tmac: %s" % (macs.arptype, result[0], result[1])
        else:
            print "Association for %s not found" % get

