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

    """Каждое запись словаря это структура:
    'идентификатор поля': ('имя поля mysql', 'описание поля', включить_в_выборку?, группировать?),
    """
    _stat_fields = {
        'timefrom': ("timefrom", "время начала сессии", True, True),
        'timeto': ("timeto", "время окончания сессии", True, True),
        'ip': ("ip", "локальный ip", True, True),
        'ipport': ("ipport", "локальный порт", True, True),
        'remote': ("remote", "удаленный ip", True, True),
        'remport': ("remport", "удаленный порт", True, True),
        'in': ("sum(cin) as in", "входящий, байт", True, True),
        'out': ("sum(cout) as out", "исходящий, байт", True, True),
        'vg_id': ("vg_id", "учетная запись", False, False),
        'agrm_id': ("agrm_id", "договор", False, False),
        'uid': ("uid", "абонент", False, False),
        'tar_id': ("tar_id", "тариф", False, False),
        }


    def __init__(self, ip, conf='conf/main.conf'):
        super(Dbi, self).__init__()

        self.ip = ip
        self['ip'] = self.ip

        self.conf = conf

        self._dblist_ = list()
        self._db_ = dict()
        self._cur_ = dict()

        self.open_db('dbi')

    def __del__(self):
        self.close_db('dbi')


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

        for db in self._db_.keys():
            self.close_db(db)
            self.open_db(db)


    def open_db(self, db):
        """Подключиться к БД на основе секции [<db>] файла конфигурации.
        добавить в словарь self._db_ текущее подключение и в self._cur_ курсор"""
        if not self.conf:
            raise ValueError("conf file must be set")

        db_params = self.parse_conf(db)
        try:
            self._db_[db] = MySQLdb.connect(**db_params)
            self._cur_[db] = self._db_.cursor(MySQLdb.cursors.DictCursor)
            #self._cur_[db] = self._db_.cursor()
        except MySQLdb.Error, e:
            raise IOError("Error connecting to database '{0}'!".format(db))


    def close_db(self, db):
        """Закрыть соединение с dbi._db_"""
        try:
            self._db_[db].close()
            del self._cur_[db]
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

    def _agent_id(self, ip=''):
        """Возвращает id агента, на котором ip-адрес ip.
        если self['ip'] отличается от ip, то запрос в базу
        иначе вернет self['id']""" 
        _ip = ip and self._check_ip(ip)
        if _ip == self.data.get('ip'):
            result = self.data.get('id')
        else:
            #TODO: получение id агента из БД


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

        cur = self._cur_['dbi']
        cur.execute(sql)
        if cur.rowcount == 0:
            return False
        elif cur.rowcount > 1:
            raise RuntimeError("'%s' belongs to many vgroups O_o... It's impossible!" % self.ip)
        elif cur.rowcount < 0:
            raise RuntimeError("MySQLdb.cursor.execute return value < 0... Is it possible?")
        
        # Here self._cur_.rowcount = 1
        res = cur.fetchall()
        vg = res[0]

        # Конвертация цифрового представления поля blocked в текстовое обозначение
        # TODO: решить проблему с кодировкой
        #vg['v.blocked'] = self._blocked.get(vg.get('v.blocked'))
        #if vg.get('blocked'):
        #    vg['blocked'] = vg['blocked'].decode('utf-8')

        self.data.update(vg)
        return True


    def sum_stat(self, timefrom='1901-12-13', timeto='2038-01-19'):
        """Параметры: условия отбора
        возвращает структуру:
        {'header':
            (имяполя1, имяполя2, имяполя3, ..., имяполяХ),
         'body':
            (
                (поле1, поле2, поле3, ..., полеХ),
                (поле1, поле2, поле3, ..., полеХ),
            ),
         'footer':
            ("", суммаполя2, суммаполя3, ..., пусто)
        }
        """
        if not self.ip:
            raise ValueError("Dbi.ip must be assigned first")


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
