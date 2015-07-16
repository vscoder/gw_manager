#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import sys
import os
import subprocess
import ConfigParser

#import logging
#logging.basicConfig(level=logging.DEBUG,
#                    format='%(asctime)s: %(message)s',
#                    filename='log/server_functions.log',
#                    )

#sys.path.insert(0, "./lib")

# Заеомментировано за ненадобностью,
# вместо декоратора @as_dict используется метод _dispatch
# см. документацию https://docs.python.org/2/library/simplexmlrpcserver.html#simplexmlrpcserver-objects
#def as_dict(fn):
#    """get function params from dict"""
#    def wrapped(self, params):
#        logging.debug("func: '%s', params: %s" % (fn.__name__, params))
#        return fn(self, **params)
#    
#    return wrapped


def readconf(config):
    """Read config from conffile
    and store it in self.conf dictionary"""
    conf = dict()
    #config = ConfigParser.RawConfigParser()
    #try:
    #    config.read(conffile)
    #except:
    #    raise IOError("Error reading file '{}' in dir '{}'".format(conffile, os.getcwd()))
    for section in config.sections():
        conf[section] = dict()
        for item, value in config.items(section):
            conf[section][item] = value

    return conf


class GwManServerFunctions(object):
    """Каждая функция должна принимать 2 аргумента:
    self и словарь с параметрами.
    
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

    def _listMethods(self):
        """
        Возвращает список доступных методов
        """
        return list_public_methods(self) + ['string.' + method for method in list_public_methods(self.string)]

    def _dispatch(self, method, params):
        """Rules of dispatching functions to xmlrpc server
        см. документацию https://docs.python.org/2/library/simplexmlrpcserver.html#simplexmlrpcserver-objects
        """
        functions = self.conf['main']['functions']
        func_list = functions.split(",")
        func_list = map(lambda f: f.strip(), func_list)

        if func_list[0] == '*' or method in func_list:
            func = getattr(self, method)
            params_dict = params[0]
            return func(**params_dict)
        else:
            func = getattr(self, "func_locked")
            return func(method)


    def __init__(self, config):
        self.conf = readconf(config)
        assert type(self.conf) == type(dict()), "GwManServerFunctions.__init__(): Error reading config file"


    def func_locked(self, method):
        """Called if function not found or locked"""
        result = dict()

        result['status'] = False
        result['data'] = (('error:', "Method '{}' not found on this agent".format(method)), )
        return result


    def mac_find(self, addr):
        """Find ip-mac association"""
        from mac_assoc import MacAssoc
        result = dict()
        macs = MacAssoc(self.conf['mac_assoc']['find_arptype'])
        try:
            rows = macs.get(addr)
        except Exception as e:
            result['status'] = False
            result['data'] = (('error:', e.message), )
            return result

        result['status'] = True
        result['data'] = rows
        return result


    def mac_add(self, ip, mac):
        """Add ip-mac association"""
        from mac_assoc import MacAssoc
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

    def mac_del(self, ip):
        """Del ip-mac association"""
        from mac_assoc import MacAssoc
        macs = MacAssoc(self.conf['mac_assoc']['arptype'])
        macs.ip = ip
        result = dict()

        try:
            status = macs.delete()
        except Exception as e:
            result['status'] = False
            result['data'] = (('error:', e.message), )
            return result

        result['data'] = (('arptype', macs.arptype),
                          ('ip', macs.ip),
                          )

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

    
    def check_ip(self, ip):
        """Check block status and shape of ip address"""
        from firewall import Pf
        from firewall import Ipfw
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


    def ip_info(self, ip):
        """Get info about ip from billing"""
        from billing import Dbi
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
    
    
    def ip_stat(self, ip, dfrom, dto, det):
        """Get info about ip from billing"""
        from billing import Dbi
        result = dict()

        try:
            dbi = Dbi(ip)
            _stat = dbi._get_stat(dfrom, dto, det)
            #print _stat
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

    
    def scan_tcp(self, host, port):
        """scan tcp port"""
        from scan import Scan
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


    def ping(self, host, count=3):
        """ping <host> <count> times"""
        from ping import Ping
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


    def traceroute(self, host, hops=8):
        """traceroute -m <hops> <host>"""
        from traceroute import Traceroute
        result = dict()
        # Инициализация класса
        try:
            traceroute = Traceroute(host = host, hops = hops)
            traceroute.hops = hops or 8

            (retcode, out) = traceroute.traceroute_host()
            if retcode == 0:
                tracerouted = True
            else:
                tracerouted = False
            result['status'] = True
            result['data'] = (('tracerouted', tracerouted),
                              ('out', out.split("\n"))
                              )
        except Exception as e:
            result['status'] = False
            result['data'] = (('error:', e.message), )
            return result

        return result

    def ipstatuses(self):
        """run script /root/billing/scripts/ips_status.sh"""
        from ipstatuses import Ipstatuses
        result = dict()
        # Инициализация класса
        try:
            ipstatuses = Ipstatuses()

            (retcode, out) = ipstatuses.set_statuses()
            if retcode == 0:
                allok = True
            else:
                allok = False
            result['status'] = True
            result['data'] = (('tracerouted', allok),
                              ('out', out.split("\n"))
                              )
        except Exception as e:
            result['status'] = False
            result['data'] = (('error:', e.message), )
            return result

        return result


    def findmac_on_switches(self, pattern, mac, vlan):
        """find <mac> on switches like <pattern> in <vlan>"""
        from switches import Zabbix
        from findmac import Switch
        result = dict()
        try:
            zabbix = Zabbix(conf = 'db.conf')
            switches = zabbix.switchlist(pattern)
        except Exception as e:
            result['status'] = False
            result['data'] = (('error:', e.message), )
            return result

        data = list()
        for ip, comm in switches:
            sw = Switch(host = ip, getmodel = True)
            sw.proto = 'snmp'
            sw.vlan = vlan
            #sw.model = 'A3100'
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
