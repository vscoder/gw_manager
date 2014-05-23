#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import re
import subprocess
from distutils import spawn

from gwman import gwman

class Switch(gwman):
    
    def __init__(self, host='127.0.0.1', port=161, community='public'):

        self._models = ['A3100', 'OTHER', ]
        self._protocols = ['snmp', 'telnet']

        self.snmpget = self.find_exec('snmpget')

        self.host = host
        self.port = port
        self.timeout = 5
        self.community = community

        self.mactable_oid = ''


    @property
    def community(self):
        """snmp community"""
        return self._community

    @community.setter
    def community(self, community):
        if not self._re_community.match(community):
            raise ValueError("Bad snmp community '%s'" % community)

        self._community = community


    @property
    def proto(self):
        """Протокол (snmp/telnet)"""
        return self._proto

    @proto.setter
    def proto(self, proto):
        if proto not in self._protocols:
            raise ValueError("'%s' is not valid protocol" % proto)

        if proto == 'telnet':
            raise ValueError("Protocol '%s' not implemented yet" % proto)

        # Do protocol-dependent actions
        if proto == 'snmp':
            self.port = 161
            self.find_mac = self.find_mac_snmp
        elif proto == 'telnet':
            self.port = 23
            self.find_mac = self.find_mac_telnet

        self._proto = proto


    @property
    def model(self):
        """Модель свича"""
        return self._model

    @model.setter
    def model(self, model):
        if model not in self._models:
            raise ValueError("wrong model '%s', see switch.models" % model)

        if model == 'A3100':
            if not self._vlan:
                raise RuntimeError("Switch.vlan must be set for model 'A3100'")
            self.mactable_oid = '.1.3.6.1.2.1.17.7.1.2.2.1.2.%d' % self.vlan
        elif model == 'OTHER':
            self.mactable_oid = '.1.3.6.1.2.1.17.4.3.1.2'
        else:
            self.mactable_oid = ''


    def mac_oid(self, mac):
        """Конвертирует mac вида XX:XX:XX:XX:XX:XX
        в десятичное предсятичное представление N.N.N.N.N.N"""
        mac = mac.upper()
        if not self._re_mac.match(mac):
            raise ValueError("Bad mac-address '%s'" % mac)

        mac_str = mac.translate(None, ':-')
        mac_arr = re.findall('..', mac_str)
        
        mac_oid_arr = [str(int(hh, base=16)) for hh in mac_arr]
        mac_oid = ".".join(mac_oid_arr)

        return mac_oid


    def find_mac_snmp(self, mac):
        """Поиск mac-адреса с помощью snmp"""

        oid = "%s.%s" % (self.mactable_oid, self.mac_oid(mac))

        cmd = [self.snmpget, '-v1', '-c', self.community, self.host, oid]
        print cmd
        
        try:
            out = subprocess.check_output(cmd)
        except:
            out = False

        if out:
            #out = out.split("=")[1].split(":")[1].strip()
            out = out.split()[-1]

        return out


def main():
    # Обработка аргументов коммандной строки
    import argparse
    parser = argparse.ArgumentParser(
        description="""Поиск мак-адреса на свиче""")
    parser.add_argument('-H', '--host', 
        metavar = 'HOST',
        help = 'Хост для проверки')
    parser.add_argument('-p', '--port', 
        metavar = 'PORT',
        help = 'Порт для проверки')
    parser.add_argument('-c', '--community', 
        metavar = 'COMMUNITY',
        help = 'Snmp community')
    parser.add_argument('-v', '--vlan', 
        metavar = 'VLAN',
        help = 'Vlan для поиска mac-адреса')
    parser.add_argument('-m', '--mac', 
        metavar = 'MAC',
        help = 'Mac-адрес для поиска')
    params = parser.parse_args()

    # Инициализация
    sw = Switch(host = params.host)
    sw.proto = 'snmp'
    sw.vlan = params.vlan
    sw.model = 'A3100'
    sw.community = params.community
    
    res = sw.find_mac(params.mac)

    print "MAC found on port %s" % res
    

if __name__ == "__main__":
    main()
