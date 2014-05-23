#!/usr/bin/env python2
# -*- coding: utf_8 -*-

from os import path
import ConfigParser
import MySQLdb
import MySQLdb.cursors

class Zabbix(object):
    
    def __init__(self, conf='conf/main.conf'):

        self.conf = conf

        self.open_db()

    def __del__(self):
        self.close_db()


    @property
    def conf(self):
        """Фаил конфигурации"""
        return self._conf

    @conf.setter
    def conf(self, filename):
        if not path.isfile(filename):
            raise ValueError("'%s' must be regular file" % filename)

        filepath = path.abspath(filename)

        self._conf = filepath

        self.close_db()
        self.open_db()


    def open_db(self):
        """Подключиться к БД на основе файла Zabbix.conf
        и задать текущие Zabbix._db_ и Zabbix._cursor_"""
        if not self.conf:
            raise ValueError("Zabbix.conf must be set")

        db_params = self.parse_conf('db')
        self._db_ = MySQLdb.connect(**db_params)
        #self._cur_ = self._db_.cursor(MySQLdb.cursors.DictCursor)
        self._cur_ = self._db_.cursor()

    def close_db(self):
        """Закрыть соединение с Zabbix._db_"""
        try:
            self._db_.close()
        except:
            return False


    def parse_conf(self, section):
        """ Parse configuration file """
        config = ConfigParser.RawConfigParser()
        config.read(self.conf)
        if config.has_section(section):
            return dict(config.items(section))


    def switchlist(self, pattern=''):
        """Возвращает список свичей, ip-адреса которых
        соответствуют mysql шаблону pattern"""
        if not self._cur_:
            raise RuntimeError("You must first Zabbix.open_db")

        if not pattern:
            pattern = ''

        sql = """
                select
                    hi.ip ip,
                    i.snmp_community community
                from
                    items i inner join
                    interface hi on (i.hostid=hi.hostid)
                where
                    hi.type=2 and
                    hi.ip !='' and
                    hi.ip !='127.0.0.1' and
                    hi.ip !='0.0.0.0' and
                    hi.ip is not null and
                    i.snmp_oid like '%1.3.6.1.2.1.1.3.0' and
                    hi.ip like '%{}%'
              """.format(pattern)

        self._cur_.execute(sql)
        #import ipdb;ipdb.set_trace()
        if self._cur_.rowcount > 0:
            res = self._cur_.fetchall()
            return res
        else:
            return ()


def main():
    # Обработка аргументов коммандной строки
    import argparse
    from findmac import Switch
    parser = argparse.ArgumentParser(
        description="""Список свичей""")
    parser.add_argument('-c', '--conf', 
        metavar = 'FILE',
        help = 'Фаил конфигурации')
    parser.add_argument('-p', '--pattern', 
        metavar = 'PATTERN',
        help = 'Mysql-шаблон ip-адреса')
    parser.add_argument('-m', '--mac',
        metavar = 'MAC',
        help = 'Mac-адрес для поиска')
    parser.add_argument('-v', '--vlan',
        metavar = 'VLAN',
        help = 'Vlan для поиска mac-адреса')
    params = parser.parse_args()

    # Инициализация
    zabbix = Zabbix(conf = params.conf)
    
    switches = zabbix.switchlist(params.pattern)

    for ip, comm in switches:
        if not params.mac:
            print "switch ip: %s, community %s" % (ip, comm)
        else:
            sw = Switch(host = ip)
            sw.proto = 'snmp'
            sw.vlan = params.vlan
            sw.model = 'A3100'
            sw.community = comm

            port = sw.find_mac(params.mac)

            if port:
                print "MAC '%s' found on %s port %s" % (params.mac, ip, port)
            else:
                print "MAC '%s' not found on %s vlan %s" % (params.mac, ip, sw.vlan)
    

if __name__ == "__main__":
    main()
