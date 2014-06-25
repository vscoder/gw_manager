#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import sys
import os
import subprocess
import ConfigParser

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s: %(message)s',
                    filename='log/server_functions.log',
                    )

#sys.path.insert(0, "./lib")
from scan import Scan
from firewall import Pf
from firewall import Ipfw
from mac_assoc import MacAssoc
from ping import Ping
from switches import Zabbix
from findmac import Switch
from billing import Dbi


def as_dict(fn):
    """get function params from dict"""
    def wrapped(self, params):
        logging.debug("func: '%s', params: %s" % (fn.__name__, params))
        return fn(self, **params)
    
    return wrapped


def readconf(conffile='conf/agent.conf'):
    """Read config from conffile
    and store it in self.conf dictionary"""
    conf = dict()
    config = ConfigParser.RawConfigParser()
    config.read(conffile)
    for section in config.sections():
        conf[section] = dict()
        for item, value in config.items(section):
            conf[section][item] = value

    return conf


class GwManServerFunctions(object):
    """Каждая функция должна принимать 2 аргумента:
    self и словарь с параметрами.
    Можно использовать декоратор @as_dict
    для достижения такого поведения.
    
    Каждая функция должна возвращать словарь
    со следующими атрибутами:
    status: True/False
        True если во время выполнения функции
            не возникло исключений
        False в случае если они возникли
    data:
        Если status False, то словарь
            с элементом 'error' -- описанием ошибки
        Если status True, то словарь, где
            ключ -- название элемента
            значение -- описание
    """


    def __init__(self):
        self.conf = readconf()
        assert type(self.conf) == type(dict()), "GwManServerFunctions.__init__(): Error reading config file"


    @as_dict
    def mac_find(self, addr):
        """Find ip-mac association"""
        result = dict()
        macs = MacAssoc(self.conf['mac_assoc']['find_arptype'])
        try:
            rows = macs.find(addr)
        except Exception as e:
            result['status'] = False
            result['data'] = (('error:', e.message), )
            return result

        result['status'] = True
        result['data'] = rows
        return result


    @as_dict
    def mac_add(self, ip, mac):
        """Add ip-mac association"""
        result = dict()

        macs = MacAssoc(self.conf['mac_assoc']['arptype'])

        macs.ip = ip
        macs.mac = mac

        try:
            status = macs.set()
        except Exception as e:
            result['status'] = False
            result['data'] = (('error:', e.message), )
            return result

        result['data'] = (('arptype', macs.arptype),
                          ('ip', macs.ip),
                          ('mac', macs.mac),
                          )
        if status:
            try:
                macs.ethers_to_arp()
            except Exception as e:
                result['status'] = False
                result['data'] = (('error:', e.message), )
                return result

            result['status'] = True
            #"OK: set association from '%s' for ip: '%s', mac: '%s'" % (macs.arptype, macs.ip, macs.mac)
        else:
            result['status'] = False
            #"ERROR: set association from '%s' for ip: '%s', mac: '%s'" % (macs.arptype, macs.ip, macs.mac)

        return result

    @as_dict
    def mac_del(self, ip):
        """Del ip-mac association"""
        macs = MacAssoc(self.conf['mac_assoc']['arptype'])
        macs.ip = ip
        result = dict()

        try:
            status = macs.delete()
        except Exception as e:
            result['status'] = False
            result['data'] = (('error:', e.message), )
            return result

        result['data'] = (('arptype', macs.arptype), )

        if status:
            try:
                macs.ethers_to_arp()
            except Exception as e:
                result['status'] = False
                result['data'] = (('error:', e.message), )
                return result

            result['status'] = True
            #"OK: del association from '%s' for ip: '%s'" % (macs.arptype, macs.ip)
        else:
            result['status'] = False
            result['data'] = (('ip', macs.ip),
                              ('error:', 'not found in {0}'.format(macs.ethers)),
                              )
            #"ERROR: del association from '%s' for ip: '%s'" % (macs.arptype, macs.ip)

        return result

    
    @as_dict
    def check_ip(self, ip):
        """Check block status and shape of ip address"""
        result = dict()

        # PF
        ipstatus = False
        try:
            pf = Pf(ip = ip)
            if pf.check_ip():
                ipstatus = True
        except Exception as e:
            result['status'] = False
            result['data'] = (('error:', e.message), )
            return result

        # IPFW
        try:
            ipfw = Ipfw(ip = ip)
            pipes = ipfw.check_ip()
        except Exception as e:
            result['status'] = False
            result['data'] = (('error:', e.message), )
            return result

        if pipes:
            shape_in = pipes[3]
            shape_out = pipes[2]
        else:
            shape_in = 'unknown'
            shape_out = 'unknown'

        result['status'] = True
        result['data'] = (('ip', ip),
                          ('ipstatus', ipstatus),
                          ('shape_in', shape_in),
                          ('shape_out', shape_out)
                          )

        return result


    @as_dict
    def ip_info(self, ip):
        """Get info about ip from billing"""
        result = dict()

        try:
            dbi = Dbi(ip)
        except Exception as e:
            result['status'] = False
            result['data'] = (('error:', e.message), )
            return result

        result['status'] = True
        result['data'] = [(dbi.field_descr(k).decode('utf-8'), v) for (k, v) in dbi._ipinfo.items()]

        return result
    
    
    @as_dict
    def ip_stat(self, ip, dfrom, dto, det):
        """Get info about ip from billing"""
        result = dict()

        try:
            dbi = Dbi(ip)
            _stat = dbi._get_stat(dfrom, dto, det)
            print _stat
        except Exception as e:
            result['status'] = False
            result['data'] = (('error:', e.message), )
            return result

        #TODO: data.tpl должен принимать в качестве параметров список а не словарь
        # Необходимо переделать все функции!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        stat = list()
        stat.append(_stat['header'])
        stat.extend(_stat['body'])

        result['status'] = True
        result['data'] = stat

        return result

    
    @as_dict
    def scan_tcp(self, host, port):
        """scan tcp port"""
        result = dict()
        try:
            scanner = Scan(host = host, port = port)
            if scanner.check_tcp_port():
                result['status'] = True
                result['data'] = (('port_status', True), )
            else:
                result['status'] = True
                result['data'] = (('port_status', False), )
        except Exception as e:
            result['status'] = False
            result['data'] = (('error:', e.message), )
            return result

        return result


    @as_dict
    def ping(self, host, count=3):
        """ping <host> <count> times"""
        result = dict()
        # Инициализация класса
        try:
            ping = Ping(host = host)
            ping.count = count

            (retcode, out) = ping.ping_host()
            if retcode == 0:
                pinged = True
            else:
                pinged = False
            result['status'] = True
            result['data'] = (('pinged', pinged),
                              ('out', out.split("\n"))
                              )
        except Exception as e:
            result['status'] = False
            result['data'] = (('error:', e.message), )
            return result

        return result


    @as_dict
    def findmac_on_switches(self, pattern, mac, vlan):
        """find <mac> on switches like <pattern> in <vlan>"""
        result = dict()
        try:
            zabbix = Zabbix(conf = 'conf/db.conf')
            switches = zabbix.switchlist(pattern)
        except Exception as e:
            result['status'] = False
            result['data'] = (('error:', e.message), )
            return result

        data = list()
        for ip, comm in switches:
            sw = Switch(host = ip)
            sw.proto = 'snmp'
            sw.vlan = vlan
            sw.model = 'A3100'
            sw.community = comm

            port = sw.find_mac(mac)

            data.append((sw.host, port))

        result['status'] = True
        result['mac'] = mac
        result['vlan'] = sw.vlan
        result['data'] = data
        
        return result

    #def run_cmd(self, cmd):
    #    """run shell cmd as current user"""
    #    run = tuple(cmd.split())
    #    result = subprocess.check_output(run)
    #    return result


if __name__ == "__main__":
    pass
