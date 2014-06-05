#!/usr/bin/env python2
# -*- coding: utf_8 -*-

from os import path
import ConfigParser
import MySQLdb
import MySQLdb.cursors

from gwman import gwman

class dbi(UserDict, gwman):
    
    def __init__(self, ip, conf='conf/main.conf'):
        UserDict.__init__(self)
        gwman.__init__(self)

        self.ip = ip
        self['ip'] = self.ip

        self.conf = conf

        self.open_db()

    def __del__(self):
        self.close_db()
        UserDict.__del__(self)
        gwman.__del__(self)


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
        """Подключиться к БД на основе секции [dbi] файла конфигурации
        и задать текущие dbi._db_ и dbi._cursor_"""
        if not self.conf:
            raise ValueError("conf file must be set")

        db_params = self.parse_conf('dbi')
        self._db_ = MySQLdb.connect(**db_params)
        self._cur_ = self._db_.cursor(MySQLdb.cursors.DictCursor)
        #self._cur_ = self._db_.cursor()

    def close_db(self):
        """Закрыть соединение с dbi._db_"""
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


    def _vgroup(self, params):
        """Заполняет информацию об учетной записи
        с ip-адресом self.ip.
        params - Список полей в таблице vgroups"""
        if not self.ip:
            raise ValueError("dbi.ip must be assigned first")

        if not type(params) == type(list()):
            raise TypeError("'params' must be a list type")

        args = dict()
        args['ip'] = self.ip
        args['fields'] = ", ".join(map(lambda field: "v.{}".format(field), params))
        #print args
        sql = """
                select
                    %(fields)s
                from
                    staff st inner join
                    vgroups v on (st.vg_id = v.vg_id)
                where
                    ip = inet_aton('%(ip)s')
              """ % args
        #print sql

        self._cur_.execute(sql)
        if self._cur_.rowcount == 0:
            return None
        elif self._cur_.rowcount > 1:
            raise RuntimeError("'%s' belongs to many vgroups O_o... It's impossible!")
        elif self._cur_.rowcount < 0:
            raise RuntimeError("MySQLdb.cursor.execute return value < 0... Is it possible?")
        else:
            res = self._cur_.fetchall()



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


# TODO: Переписать тесты под класс dbi
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

    if not params.mac:
        for ip, comm in switches:
            print "switch ip: %s, community %s" % (ip, comm)
    else:
        for ip, comm in switches:
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
