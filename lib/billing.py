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

        self._dblist_ = list()
        self._db_ = dict()
        self._cur_ = dict()

        self.open_db('dbi')

        # Instance properties
        """Каждое запись словаря это структура:
        'идентификатор поля': ('поле в mysql', 'описание поля', включить_в_выборку?, группировать?, сортировать?),
        """
        _stat_fields = {
            'dfrom': ["s.timefrom", "время начала сессии", True, True, False],
            'dto': ["s.timeto", "время окончания сессии", False, False, False],
            'lip': ["inet_ntoa(s.ip)", "локальный ip", True, True, False],
            'lport': ["s.ipport", "локальный порт", True, True, False],
            'rip': ["inet_ntoa(s.remote)", "удаленный ip", True, True, False],
            'rport': ["s.remport", "удаленный порт", True, True, False],
            'tin': ["sum(s.cin)", "входящий, байт", True, False, False],
            'tout': ["sum(s.cout)", "исходящий, байт", True, False, False],
            'vgid': ["s.vg_id", "учетная запись", False, False, False],
            'agrmid': ["s.agrm_id", "договор", False, False, False],
            'userid': ["s.uid", "абонент", False, False, False],
            'tarid': ["s.tar_id", "тариф", False, False, False],
            }

    def __del__(self):
        for db in self._db_.keys():
            self.close_db(db)


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

        #if type(self._db_) == type(list()):
        #    for db in self._db_.keys():
        #        self.close_db(db)
        #        self.open_db(db)


    def open_db(self, db):
        """Подключиться к БД на основе секции [<db>] файла конфигурации.
        добавить в словарь self._db_ текущее подключение и в self._cur_ курсор"""
        if not self.conf:
            raise ValueError("conf file must be set")

        db_params = self.parse_conf(db)
        try:
            self._db_[db] = MySQLdb.connect(**db_params)
            self._cur_[db] = self._db_[db].cursor(MySQLdb.cursors.DictCursor)
            #self._cur_[db] = self._db_.cursor()
        except MySQLdb.Error, e:
            raise IOError("Error connecting to database '{0}'!\n{1}".format(db, e))


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
            result = dict(config.items(section))

        if not self.data.get('dbconf'):
            self.data['dbconf'] = dict()

        self.data['dbconf'][section] = result
        return result


    def field_descr(self, field):
        """Возвращает значение ключа field
        в словаре self._params"""
        result = self._params.get(field) or field
        return result

    def _agent_id(self, ip=''):
        """Возвращает id агента, на котором ip-адрес ip.
        если self['ip'] отличается от ip, то запрос в базу
        иначе вернет self['id']""" 
        # Если параметр ip задан и проходит проверку, то _ip = ip,
        # иначе _ip = self.data.get('ip') иначе ip = None
        _ip = ip and self._check_ip(ip) or self.data.get('ip')
        if not _ip:
            raise ValueError("_agent_id(ip): ip or self['ip'] must be set!")
        if _ip == self.data.get('ip'):
            result = self.data.get('v.id')
        else:
            sql = """
                select
                    s.id as id
                from
                    staff st inner join segments s
                    on (st.segment_id = s.record_id)
                where
                    st.segment = inet_aton('{0}')
                """.format(_ip)

            cur = self._cur_['dbi']
            cur.execute(sql)
            if cur.rowcount == 0:
                return False
            elif cur.rowcount > 1:
                raise RuntimeError("'{0}' belongs to many segments O_o... It's impossible!".format(ip))
            elif cur.rowcount < 0:
                raise RuntimeError("MySQLdb.cursor.rowcount return value < 0... Is it possible?")

            # Here cur.rowcount = 1
            row = cur.fetchone()
            result = res['id']

        return str(result)


    def _tables(self, timefrom='19011213', timeto='20380119', agent=None):
        """Возвращает отсортированный список таблиц.
        Параметры: даты формата YYYYMMDD, включая С исключая ПО,
        agent = id агента"""
        _param_err = """params 'timefrom' and 'timeto' must be string representation of date YYYYMMDD
                        param 'agent' must be string representation of integer with length <= 3"""
        _agent = agent or self._agent_id()
        assert type(timefrom) == type(str()) and len(timefrom) == 8, _param_err
        assert type(timeto) == type(str()) and len(timefrom) == 8, _param_err
        assert timefrom.isdigit() and timeto.isdigit(), _param_err
        assert _agent.isdigit() and len(_agent) <= 3, _param_err
        
        # Получение имени БД со статистикой
        _dbconf = self.data.get('dbconf')
        assert type(_dbconf) == type(dict()), "self['dbconf'] must be a dictionary"
        if not _dbconf.get('billstat'):
            self.open_db('billstat')
        db = _dbconf['billstat']['db']

        _agent = "{:03d}".format(int(_agent))
        prefix = "user{0}".format(_agent)
        
        sql = """
                select
                    t.TABLE_NAME as tbl
                from
                    information_schema.TABLES t
                where
                    t.TABLE_SCHEMA = '{db}'
                    and t.TABLE_NAME like '{prefix}%'
                    and substr(TABLE_NAME,8) between '{dfrom}' and '{dto}'
                order by
                    t.TABLE_NAME
              """.format(prefix = prefix, dfrom = timefrom, dto = str(int(timeto)-1), db = db)

        cur = self._cur_['billstat']
        cur.execute(sql)
        if cur.rowcount == 0:
            return False
        #TODO: А эта проверка вообще нужна?
        assert cur.rowcount >= 0, "MySQLdb.cursor.rowcount return value < 0... Is it possible?"

        # Here cur.rowcount >= 1
        rows = cur.fetchall()
        result = [row.get('tbl') for row in rows]
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

        cur = self._cur_['dbi']
        cur.execute(sql)
        if cur.rowcount == 0:
            return False
        elif cur.rowcount > 1:
            raise RuntimeError("'%s' belongs to many vgroups O_o... It's impossible!" % self.ip)
        elif cur.rowcount < 0:
            raise RuntimeError("MySQLdb.cursor.execute return value < 0... Is it possible?")
        
        # Here cur.rowcount = 1
        res = cur.fetchall()
        vg = res[0]

        # Конвертация цифрового представления поля blocked в текстовое обозначение
        # TODO: решить проблему с кодировкой
        #vg['v.blocked'] = self._blocked.get(vg.get('v.blocked'))
        #if vg.get('blocked'):
        #    vg['blocked'] = vg['blocked'].decode('utf-8')

        self.data.update(vg)
        return True


    def _stat(self, timefrom='19011213', timeto='20380119', sort='dfrom'):
        """Параметры: условия отбора
        возвращает структуру:
        {'header':
            (имяполя1, имяполя2, имяполя3, ..., имяполяХ),
         'body':
            (
                (поле1, поле2, поле3, ..., полеХ),
                (поле1, поле2, поле3, ..., полеХ),
            ),
        }
        """
        if not self.ip:
            raise ValueError("Dbi.ip must be assigned first")

        try:
            self._stat_fields[sort][4] = True
        except KeyError, e:
            raise KeyError("key '{}' not found in self._stat_fields".format(sort))

        #self._stat_fields['dfrom'][0] = 'day(s.timefrom)'

        # Формиррование параметров запроса
        # Поля для выборки и группировка с сортировкой
        header = list()
        fields = list()
        group = list()
        sort = list()
        for k, v in self._stat_fields.items():
            # Если поле не включать в отбор, то переходим к следующему
            if not v[2]:
                continue
            # Добавляем заголовок столбца в header
            header.append(v[1])
            # Если группировка или сортировка по полю, добавляем в соответствующий список
            if v[3]:
                group.append("`{}`".format(k)) 
            if v[4]:
                sort.append("`{}`".format(k)) 
            fields.append("{0} as '{1}'".format(v[0], k))
        cond = "ip = inet_aton('{ip}')".format(ip = self.ip)
        
        params = {'fields': ", ".join(fields),
                  'cond': cond,
                  'group': ", ".join(group),
                  'sort': ", ".join(sort),
                 }

        # Из каждой таблицы получаем статистику
        data = list()
        tables = self._tables(timefrom, timeto)
        cur = self._cur_['billstat']
        for table in tables:
            params['table'] = table
            sql = """
                    select {fields}
                    from {table} s
                    where {cond}
                    group by {group}
                    order by {sort}
                  """.format(**params)
            #print "_stat: sql -- ", sql
            cur.execute(sql)
            for row in cur.fetchall():
                data.append(row.values())

        stat = {'header': header,
                'body': data,
                }

        return stat



def main():
    # Обработка аргументов коммандной строки
    import argparse
    import sys
    parser = argparse.ArgumentParser(
        description="""Dbi""")
    parser.add_argument('-c', '--conf', 
        metavar = 'FILE',
        help = 'Фаил конфигурации')
    parser.add_argument('-i', '--ip', 
        metavar = 'IP',
        help = 'ip-адрес для поиска информации')
    parser.add_argument('-f', '--dfrom', 
        metavar = 'YYYYMMDD',
        help = 'Начальная дата статистики')
    parser.add_argument('-t', '--dto', 
        metavar = 'YYYYMMDD',
        help = 'Конечная дата статистики (исключая)')
    params = parser.parse_args()

    # Инициализация
    dbi = Dbi(ip = params.ip, conf = params.conf)

    
    if dbi._ipinfo():
        for k, v in dbi.data.items():
            key = dbi.field_descr(k)
            value = v
            print u'%s\t%s' % (key.decode('utf-8'), value)
    else:
        sys.exit("not found")

    stat = dbi._stat(params.dfrom, params.dto, 'dfrom')
    print stat['header']
    for row in stat['body']:
        print row
    
if __name__ == "__main__":
    main()
