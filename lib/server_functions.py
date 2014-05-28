#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import sys
import os
import subprocess

#sys.path.insert(0, "./lib")
from scan import Scan
from firewall import Pf
from firewall import Ipfw
from mac_assoc import MacAssoc
from ping import Ping
from switches import Zabbix
from findmac import Switch


class GwManServerFunctions:

    def mac_find(self, addr):
        """Find ip-mac association"""
        result = dict()
        macs = MacAssoc('arp')
        try:
            rows = macs.find(addr)
        except Exception as e:
            result['status'] = False
            result['data'] = {'error:': e.message}
            return result

        result['status'] = True
        result['data'] = rows
        return result

    def mac_add(self, ip, mac):
        """Add ip-mac association"""
        macs = MacAssoc('ethers')
        macs.ip = ip
        macs.mac = mac
        result = dict()

        try:
            status = macs.set()
        except Exception as e:
            result['status'] = False
            result['data'] = {'error:': e.message}
            return result

        result['data'] = {'arptype': macs.arptype, 'ip': macs.ip, 'mac': macs.mac}
        if status:
            try:
                macs.ethers_to_arp()
            except Exception as e:
                result['status'] = False
                result['data'] = {'error:': e.message}
                return result

            result['status'] = True
            #"OK: set association from '%s' for ip: '%s', mac: '%s'" % (macs.arptype, macs.ip, macs.mac)
        else:
            result['status'] = False
            #"ERROR: set association from '%s' for ip: '%s', mac: '%s'" % (macs.arptype, macs.ip, macs.mac)

        return result

    def mac_del(self, ip):
        """Del ip-mac association"""
        macs = MacAssoc('ethers')
        macs.ip = ip
        result = dict()

        try:
            status = macs.delete()
        except Exception as e:
            result['status'] = False
            result['data'] = {'error:': e.message}
            return result

        result['data'] = {'arptype': macs.arptype, 'ip': macs.ip}
        if status:
            try:
                macs.ethers_to_arp()
            except Exception as e:
                result['status'] = False
                result['data'] = {'error:': e.message}
                return result

            result['status'] = True
            #"OK: del association from '%s' for ip: '%s'" % (macs.arptype, macs.ip)
        else:
            result['status'] = False
            result['data'] = {'ip': macs.ip, 'error:': 'not found in %s' % macs.ethers}
            #"ERROR: del association from '%s' for ip: '%s'" % (macs.arptype, macs.ip)

        return result

    
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
            result['data'] = {'error:': e.message}
            return result

        # IPFW
        try:
            ipfw = Ipfw(ip = ip)
            pipes = ipfw.check_ip()
        except Exception as e:
            result['status'] = False
            result['data'] = {'error:': e.message}
            return result

        if pipes:
            shape_in = pipes[3]
            shape_out = pipes[2]
        else:
            shape_in = 'unknown'
            shape_out = 'unknown'

        result['status'] = True
        result['data'] = {'ip': ip,
                          'ipstatus': ipstatus,
                          'shape_in': shape_in,
                          'shape_out': shape_out}

        return result

    
    def do_scan(self, *args, **kwargs):
        """scan tcp port"""
        host, port = args
        scanner = Scan(host = host, port = port)
        if scanner.check_tcp_port():
            result = 'OPEN'
        else:
            result = 'CLOSED'

        return result

    
    def ping(self, host, count=3):
        """ping <host> <count> times"""

        # Инициализация класса
        ping = Ping(host = host)
        ping.count = count

        result = ping.ping_host()

        return result


    def findmac_on_switches(self, pattern, mac, vlan):
        """find <mac> on switches like <pattern> in <vlan>"""
        zabbix = Zabbix(conf = 'conf/main.conf')
        switches = zabbix.switchlist(pattern)

        result = []
        for ip, comm in switches:
            sw = Switch(host = ip)
            sw.proto = 'snmp'
            sw.vlan = vlan
            sw.model = 'A3100'
            sw.community = comm

            port = sw.find_mac(mac)

            if port:
                result.append("MAC '%s' found on %s port %s" % (mac, ip, port))
            else:
                result.append("MAC '%s' not found on %s vlan %s" % (mac, ip, sw.vlan))
        
        return result

    #def run_cmd(self, cmd):
    #    """run shell cmd as current user"""
    #    run = tuple(cmd.split())
    #    result = subprocess.check_output(run)
    #    return result
        


if __name__ == "__main__":
    pass
