#!/usr/bin/env python2
# -*- coding: utf_8 -*-

from os import path
from UserDict import UserDict
import ConfigParser
import MySQLdb
import MySQLdb.cursors

from gwman import gwman

class Dbi(UserDict, gwman):
    _params = {'v.vg_id': "id учетной записи",
               'v.tar_id': "номер тарифа",
               'v.id': "id агента",
               'v.login': "логин",
               'v.current_shape': "полоса пропускания",
               'v.archive': "удалена",
               'v.blocked': "статус",
               't.descr': "тариф",
               't.rent': "абонентская плата",
               'agrm.number': "договор",
               'a.name': "абонент",
               }

    _blocked = {0: "активна",
                1: "заблокирована по балансу",
                2: "заблокирована пользователем",
                3: "заблокирована администратором",
                4: "заблокирована по балансу(активная блокировка)",
                5: "достигнут лимит трафика",
                10: "отключена",
                }


    def __init__(self, ip, conf='conf/main.conf'):
        super(Dbi, self).__init__()

        self.ip = ip
        self['ip'] = self.ip

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
        """Подключиться к БД на основе секции [dbi] файла конфигурации
        и задать текущие dbi._db_ и dbi._cursor_"""
        if not self.conf:
            raise ValueError("conf file must be set")

        db_params = self.parse_conf('dbi')
        try:
            self._db_ = MySQLdb.connect(**db_params)
            self._cur_ = self._db_.cursor(MySQLdb.cursors.DictCursor)
            #self._cur_ = self._db_.cursor()
        except MySQLdb.Error, e:
            raise IOError("Error connecting to billing database!")


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


    def field_descr(self, field):
        """Возвращает значение ключа field
        в словаре self._params"""
        result = self._params.get(field) or field
        return result


    def _ipinfo(self, params=None):
        """Заполняет информацию об учетной записи
        с ip-адресом self.ip.
        params - Список полей в таблице vgroups"""
        if not params:
            params = self._params

        if not self.ip:
            raise ValueError("Dbi.ip must be assigned first")

        if not type(params) == type(dict()):
            raise TypeError("'params' must be a dict type")

        args = dict()
        args['ip'] = self.ip
        ## К каждому имени поля добавить префикс 'v.'
        args['fields'] = ", ".join(map(lambda field: "{0} as '{0}'".format(field), params.keys()))
        #args['fields'] = ", ".join(params.keys())
        #print args
        sql = """
                select
                    %(fields)s
                from
                    staff st
                    inner join vgroups v
                    on (st.vg_id = v.vg_id)
                    inner join tarifs t
                    on (v.tar_id = t.tar_id)
                    inner join agreements agrm
                    on (v.agrm_id = agrm.agrm_id)
                    inner join accounts a
                    on (agrm.uid = a.uid)
                where
                    st.segment = inet_aton('%(ip)s')
              """ % args
        #print sql

        self._cur_.execute(sql)
        if self._cur_.rowcount == 0:
            return False
        elif self._cur_.rowcount > 1:
            raise RuntimeError("'%s' belongs to many vgroups O_o... It's impossible!" % self.ip)
        elif self._cur_.rowcount < 0:
            raise RuntimeError("MySQLdb.cursor.execute return value < 0... Is it possible?")
        
        # Here self._cur_.rowcount = 1
        res = self._cur_.fetchall()
        vg = res[0]

        # Конвертация цифрового представления поля blocked в текстовое обозначение
        # TODO: решить проблему с кодировкой
        #vg['v.blocked'] = self._blocked.get(vg.get('v.blocked'))
        #if vg.get('blocked'):
        #    vg['blocked'] = vg['blocked'].decode('utf-8')

        self.data.update(vg)
        return True



def main():
    # Обработка аргументов коммандной строки
    import argparse
    parser = argparse.ArgumentParser(
        description="""Dbi""")
    parser.add_argument('-c', '--conf', 
        metavar = 'FILE',
        help = 'Фаил конфигурации')
    parser.add_argument('-i', '--ip', 
        metavar = 'IP',
        help = 'ip-адрес для поиска информации')
    params = parser.parse_args()

    # Инициализация
    dbi = Dbi(ip = params.ip, conf = params.conf)

    
    if dbi._ipinfo():
        for k, v in dbi.data.items():
            key = dbi.field_descr(k)
            value = v
            print u'%s\t%s' % (key.decode('utf-8'), value)
    else:
        print "not found"
    
if __name__ == "__main__":
    main()
