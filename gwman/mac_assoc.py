#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import os
import sys
import re
import subprocess
from distutils import spawn

import dnet

from gwman import gwman

class MacAssoc(gwman):
    """Управление привязкой mac-адресов к ip-адресам"""
    _arptypes = ['ethers', 'ipfw', 'arp']

    def __init__(self, arptype):
        gwman.__init__(self)
        # Доступные типы привязки

        self.arptype = arptype

        self.arp = self.find_exec("arp")

        self._ethers = "/etc/ethers"
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

        if self._arptype == 'ethers':
            self.find = self.find_ethers
            self.get = self.get_ethers
            self.set = self.set_ethers
            self.delete = self.del_ethers
        elif self._arptype == 'arp':
            self.find = self.find_arp
            self.get = self.get_arp
            self.set = self.set_arp
            self.delete = self.del_arp
        elif self._arptype == 'ipfw':
            self._ipfw = self.find_exec("ipfw")
            self.find = self.find_ipfw
            self.get = self.get_ipfw
            self.set = self.set_ipfw
            self.delete = self.del_ipfw
        else:
            raise ValueError("%s is not valid arptype" % self._arptype)


    @property
    def arptable(self):
        """Получить соответствия mac-ip из ARP таблицы"""
        arp = dnet.arp()

        def add_entry((pa, ha), arg):
            arg[str(pa)] = str(ha).upper()

        arp.loop(add_entry, self._arptable)
        
        return self._arptable


    @property
    def ethers(self):
        """Фаил с соответствиями mac-ip"""
        return self._ethers

    @ethers.setter
    def ethers(self, ethers):
        ethers = os.path.abspath(ethers)
        if not os.path.isfile(ethers):
            self._ethers = ethers
        else:
            open(ethers, 'a').close()


    def find_arp(self, addr):
        """Получить значение из ARP таблицы
        addr -- ip или mac адрес"""
        addr = addr.upper()
        
        # Если нет точки в addr, то это mac-адрес
        if not "." in addr:
            addr = self.mac_conv(addr)

        result = list()
        arptable = self.arptable
        for ip, mac in arptable.items():
            mac = mac.upper()
            if addr in ip or addr in mac:
                result.append((ip, mac.upper()))
        return result


    def get_arp(self, addr):
        """Получить значение из ARP таблицы
        addr -- ip или mac адрес"""
        addr = addr.upper()
        result = []
        for ip, mac in self.arptable.items():
            mac = mac.upper()
            if addr == ip or addr == mac:
                result.append((ip, mac))
        return result

    #def set_arp(self, ip, mac):
    #    """Установить соответствие mac-ip в системной ARP-таблице"""
    #    mac = mac.upper()
    #    if not self._re_ip.match(ip):
    #        raise ValueError("%s is not valid ip address" % ip)
    #    if not self._re_mac.match(mac):
    #        raise ValueError("%s is not valid mac address" % mac)
    #    #arp = dnet.arp()
    #    #_ip = dnet.addr(ip)
    #    #_mac = dnet.addr(mac)
    #    #added = arp.add(_ip, _mac)
    #    added = subprocess.call([self.sudo, self.arp, "-s", ip, mac])
    #    return added

    def set_arp(self):
        """Установить соответствие mac-ip в системной ARP-таблице"""
        if not self.mac:
            raise RuntimeError("MacAssoc.mac must be set first")
        if not self.ip:
            raise RuntimeError("MacAssoc.ip must be set first")
        arp = dnet.arp()
        _ip = dnet.addr(self.ip)
        _mac = dnet.addr(self.mac)
        added = arp.add(_ip, _mac)
        return added

    #def del_arp(self, ip):
    #    """Установить соответствие mac-ip в системной ARP-таблице"""
    #    if not self._re_ip.match(ip):
    #        raise ValueError("%s is not valid ip address" % ip)
    #    #arp = dnet.arp()
    #    #_ip = dnet.addr(ip)
    #    #deleted = arp.delete(_ip)
    #    deleted = subprocess.call([self.sudo, self.arp, "-d", ip])
    #    return deleted

    def del_arp(self, ip):
        """Установить соответствие mac-ip в системной ARP-таблице"""
        if not self.ip:
            raise RuntimeError("MacAssoc.ip must be set first")
        arp = dnet.arp()
        _ip = dnet.addr(self.ip)
        deleted = arp.delete(_ip)
        return deleted


    def find_ethers(self, addr):
        """Поиск соответствия в файле self.ethers"""
        addr = addr.upper()
        result = list()
        with open(self.ethers, 'r') as f:
            for line in f:
                line = line.upper()
                if addr in line:
                    ip, mac = line.split()
                    result.append((ip, mac.upper()))
        return result


    def get_ethers(self, addr):
        """Получение соответствия из файла self.ethers"""
        addr = addr.upper()
        result = []
        with open(self.ethers, 'r') as f:
            for line in f:
                line = line.upper()
                ip, mac = line.split()
                if addr == ip or addr == mac:
                    result.append((ip, mac))
        return result


    def set_ethers(self):
        """Задание соответствия в файле self.ethers"""
        # Проверка на корректность ip и mac адресов
        if not self.mac:
            raise RuntimeError("MacAssoc.mac must be set first")
        if not self.ip:
            raise RuntimeError("MacAssoc.ip must be set first")
        # Преобразуем фаил в словарь {ip: mac, }
        entries = {}
        with open(self.ethers, 'r') as f:
            for line in f:
                _ip, _mac = line.split()
                entries[_ip] = _mac.upper()
        # Изменяем запись
        entries[self.ip] = self.mac

        # Перезаписываем фаил
        with open(self.ethers, 'w') as f:
            for _ip, _mac in entries.items():
                f.write("%s\t%s\n" % (_ip, _mac))

        return True
        

    def del_ethers(self):
        """Удаление соответствия из файла self.ethers"""
        if not self.ip:
            raise RuntimeError("MacAssoc.ip must be set first")
        # Преобразуем фаил в словарь {ip: mac, }
        # и если ip соответствует поиску не добавляем ее
        entries = {}
        deleted = False
        with open(self.ethers, 'r') as f:
            for line in f:
                _ip, _mac = line.split()
                if self.ip == _ip:
                    deleted = True
                else:
                    entries[_ip] = _mac.upper()

        # Перезаписываем фаил
        with open(self.ethers, 'w') as f:
            for _ip, _mac in entries.items():
                f.write("%s\t%s\n" % (_ip, _mac))

        return deleted


    def rulenum(self, ip):
        """Сгенерировать номер правила в ipfw
        на основе ip адреса"""
        octets = ip.split(".")
        num = int(octets[3])
        rulenum = self.ipfw_start + num
        return rulenum

    def split_ipfw(self, ipfw_str):
        """Получает из строки ipfw_str параметры правила
        00602 deny log logamount 5 ip from 84.253.120.2 to any out via ifwan0 not MAC any bc:f6:85:fb:d7:d1 mac-type 0x0800"""
        rule = ipfw_str.split()
        rulenum = int(rule[0])
        ip = rule[7]
        mac = rule[16]

        if self.rulenum(ip) != rulenum:
            raise RuntimeError("bad ipfw rule number for '%s'" % ipfw_str)
        if not self._re_ip.match(ip):
            raise ValueError("%s is not valid ip address" % ip)
        if not self._re_mac.match(mac):
            raise ValueError("%s is not valid mac address" % mac)

        return (ip, mac)

    def list_ipfw(self):
        """Список правил ipfw для фильтрации по mac-адресам"""
        if not self.ipfw:
            raise RuntimeError("'ipfw' not found in PATH")
        ipfw_range = "%s-%s" % (self.ipfw_start, self.ipfw_start + 255)
        rules = subprocess.check_output([self.ipfw, 'list', ipfw_range])
        arptable = {}
        for rule in rules:
            ip, mac = self.split_ipfw(rule)
            arptable[ip] = mac

        return arptable


    def find_ipfw(self, addr):
        """Поиск по части ip/mac адреса"""
        addr = addr.upper()
        arptable = self.list_ipfw()
        result = list()
        for ip, mac in arptable.items():
            if addr in ip or addr in mac:
                result.append((ip, mac.upper()))

        return result
            
    def get_ipfw(self, addr):
        """Получить ip/mac по точному совпадению"""
        addr = addr.upper()
        arptable = self.list_ipfw()
        result = []
        for ip, mac in arptable.items():
            if addr == ip or addr == mac:
                result.append((ip, mac.upper()))

        return result

    def set_ipfw(self, ip, mac):
        """Задать соответствие mac-ip в ipfw"""
        if not self.ipfw:
            raise RuntimeError("'ipfw' not found in PATH")
        if not self._re_ip.match(ip):
            raise ValueError("%s is not valid ip address" % ip)
        if not self._re_mac.match(mac):
            raise ValueError("%s is not valid mac address" % mac)

        self.del_ipfw(ip)

        # ipfw add $RULENUM deny log logamount 5 ip from $IP to any out via ifwan0 not MAC any $MAC mac-type ipv4
        result = subprocess.call([self.ipfw,
                                  'add', rulenum, 'deny',
                                  'log', 'logamount', '5',
                                  'ip', 'from', ip, 'to', 'any',
                                  'out', 'via', 'ifwan0',
                                  'not', 'MAC', 'any', mac, 'mac-type', 'ipv4'])

        return result

    def del_ipfw(self, ip):
        """Удалить соответствие из ipfw"""
        if not self.ipfw:
            raise RuntimeError("'ipfw' not found in PATH")
        if not self._re_ip.match(ip):
            raise ValueError("%s is not valid ip address" % ip)

        rulenum = self.rulenum(ip)
        
        result = subprocess.call([self.ipfw, 'delete', rulenum])

        return result

    def ethers_to_arp(self):
        """Запись фаила ethers в системную arp-таблицу"""
        if os.path.isfile(self.ethers):
            subprocess.call([self.arp, "-da"])
            return subprocess.call([self.arp, "-f", self.ethers])
        else:
            return False

    def arp_to_ethers(self):
        """Сгенерировать фаил ethers на основе системной arp таблицы"""
        arptable = self.arptable
        with open(self.ethers, 'w') as f:
            for _ip, _mac in arptable.items():
                f.write("%s\t%s\n" % (_ip, _mac))


if __name__ == "__main__":
    
    import argparse

    parser = argparse.ArgumentParser(
        description="""Привязка ip-адресов к mac-адресам
                       Все привязки дублируются в --ethers""")
    parser.add_argument('-t', '--arptype',
                        metavar = 'TYPE',
                        default = MacAssoc._arptypes[0],
                        choices = MacAssoc._arptypes,
                        help = 'Способ привязки (%s)' % ", ".join(MacAssoc._arptypes))
    gr_ethers = parser.add_argument_group("arptype = ethers")
    gr_ethers.add_argument('-e', '--ethers',
                        metavar = 'FILE',
                        default = MacAssoc.ethers,
                        help = 'Фаил с соответствиями mac\tip')
    gr_action = parser.add_mutually_exclusive_group(required=True)
    gr_action.add_argument('-f', '--find', 
                        metavar = 'PATTERN',
                        help = 'Найти соответствия в ARP таблице')
    gr_action.add_argument('-g', '--get', 
                        metavar = 'IP or MAC',
                        help = 'Получить соответствие из текущего хранилища (arptype)')
    gr_action.add_argument('--set',
                        dest='set',
                        action='store_true',
                        help = 'Задать соответствие ip-mac в хранилище (arptype).\
                            Необходимо так же указать --ip IP и --mac MAC')
    gr_action.add_argument('--rm',
                        metavar='IP',
                        help = 'Удалить соответствие ip-mac из хранилища (arptype).')
    gr_set = parser.add_argument_group("set")
    gr_set.add_argument('--ip', 
                        metavar = 'IP',
                        help = 'IP-адрес для соответствия')
    gr_set.add_argument('--mac', 
                        metavar = 'MAC',
                        help = 'MAC-адрес для соответствия')
    params = parser.parse_args()

    macs = MacAssoc(params.arptype)
    sys.stderr.write("arptype: %s\n" % macs.arptype)

    # FIND
    if type(params.find) == str:
        find = params.find
        sys.stderr.write("find: %s\n" % find)
    else:
        find = None

    # GET
    if type(params.get) == str:
        get = params.get
        sys.stderr.write("get: %s\n" % get)
    else:
        get = None

    # ETHERS
    if type(params.ethers) == str:
        macs.ethers = params.ethers
    sys.stderr.write("ethers: %s\n" % macs.ethers)

    # IP and MAC (SET)
    if params.set:
        if params.ip and params.mac:
            ip = params.ip
            mac = params.mac
            sys.stderr.write("ip: %s\n" % ip)
            sys.stderr.write("mac: %s\n" % mac)
        else:
            raise ValueError("--ip and --mac must be assigned in this mode")

    # REMOVE
    if type(params.rm) == str:
        rm = params.rm
    else:
        rm = None

    # FIND
    if find is not None:
        entries = macs.find(find)
        for ip, mac in entries:
            #rulenum = macs.rulenum(ip)
            print "in %s found ip: %s\tmac: %s" % (macs.arptype, ip, mac)

    # GET
    if get is not None:
        result = macs.get(get)[0]
        if result:
            print "in %s found ip: %s\tmac: %s" % (macs.arptype, result[0], result[1])
        else:
            print "Association for %s not found" % get

    # SET
    if params.set:
        #if macs.arptype != 'ethers':
        #    macs.set_ethers(ip, mac)
        macs.ip = ip
        macs.mac = mac
        macs.set()
        if macs.arptype == 'ethers':
            macs.ethers_to_arp()
        print "set association from '%s' for ip: '%s', mac: '%s'" % (macs.arptype, ip, mac)

    # REMOVE
    if rm is not None:
        #if macs.arptype != 'ethers':
        #    macs.del_ethers(rm)
        macs.ip = rm
        macs.delete()
        if macs.arptype == 'ethers':
            macs.ethers_to_arp()
        print "del association from '%s' for ip: '%s'" % (macs.arptype, rm)
