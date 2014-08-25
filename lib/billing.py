#!/usr/bin/env python2
# -*- coding: utf_8 -*-

from os import path
from collections import OrderedDict
import ConfigParser
import MySQLdb
import MySQLdb.cursors

from gwman import gwman

class Dbi(gwman):
    _blocked = {0: u"активна",
            1: u"заблокирована по балансу",
            2: u"заблокирована пользователем",
            3: u"заблокирована администратором",
            4: u"заблокирована по балансу(активная блокировка)",
            5: u"достигнут лимит трафика",
            10: u"отключена",
            }

    

    def __init__(self, ip, conf='conf/db.conf', dbi_section='dbi', stat_section='billstat'):
        super(Dbi, self).__init__()
        
        # Instance properties
        # Структура полей из таблицы статистики
        """Каждое запись словаря это структура:
        'идентификатор поля': ('поле в mysql', 'описание поля', включить_в_выборку?, группировать?, сортировать?),
        """
        self._stat_fields = OrderedDict([
            ('dfrom', ["s.timefrom", "время начала сессии", True, True, 1]),
            ('dday', ["day(s.timefrom)", "День", False, False, 0]),
            ('dhour', ["hour(s.timefrom)", "Час", False, False, 0]),
            ('dto', ["s.timeto", "время окончания сессии", False, False, 0]),
            ('lip', ["inet_ntoa(s.ip)", "локальный ip", True, True, 0]),
            ('lport', ["s.ipport", "локальный порт", True, True, 0]),
            ('rip', ["inet_ntoa(s.remote)", "удаленный ip", True, True, 0]),
            ('rport', ["s.remport", "удаленный порт", True, True, 0]),
            ('tin', ["sum(s.cin)", "входящий, байт", True, False, 0]),
            ('tout', ["sum(s.cout)", "исходящий, байт", True, False, 0]),
            ('vgid', ["s.vg_id", "учетная запись", False, False, 0]),
            ('agrmid', ["s.agrm_id", "договор", False, False, 0]),
            ('userid', ["s.uid", "абонент", False, False, 0]),
            ('tarid', ["s.tar_id", "тариф", False, False, 0]),
            ])

        # Параметры ip-адреса, получаемые из 'dbi'
        self._ip_params = OrderedDict([
            ('a.name', "абонент"),
            ('v.login', "логин"),
            ('v.blocked', "статус"),
            ('t.descr', "тариф"),
            ('v.current_shape', "полоса пропускания"),
            ('t.rent', "абонентская плата"),
            ('agrm.number', "договор"),
            ('v.vg_id', "id учетной записи"),
            ('v.tar_id', "номер тарифа"),
            ('v.id', "id агента"),
            ('v.archive', "удалена"),
            ])

        # Имя конфиг-файла
        self.conf = conf

        # Имена секций баз данных биллинга и статистики в конфиге
        self._dbi = dbi_section
        self._stat = stat_section

        # Подключение к БД
        self._db = dict()
        self.open_db(self._dbi)

        # Инициализация информации об ip-адоесе
        self._ipinfo = OrderedDict()
        self.ip = ip
        self._fill_ipinfo()


    def __del__(self):
        for db in self._db.keys():
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
        добавить в словарь self._db текущее подключение и курсор.
        После выполнения данной процедуры будет заполнена структура self._db = 
        {
            'conn': <DB connection>,
            'cursor': <DB cursor>,
            'params': {DB connection params (host, user, etc...},
        }"""
        if not self.conf:
            raise ValueError("conf file must be set")
        
        # Если self._db['db']['cursor'] существует, значит соединение уже установлено
        if self._db.get(db) and self._db['db'].get('cursor'):
            return True

        self._db[db] = dict()
        db_params = self.parse_conf(db)
        try:
            self._db[db]['conn'] = MySQLdb.connect(**db_params)
            self._db[db]['cursor'] = self._db[db]['conn'].cursor(MySQLdb.cursors.DictCursor)
            #self._db[db]['cursor'] = self._db[db]['conn'].cursor()
        except MySQLdb.Error, e:
            raise IOError("Error connecting to database '{0}'!\n{1}".format(db, e))

        return True


    def close_db(self, db):
        """Закрыть соединение с dbi._db_"""
        try:
            self._db[db]['conn'].close()
            del self._db[db]['cursor']
        except:
            return False


    def parse_conf(self, section):
        """ Parse configuration file """
        config = ConfigParser.RawConfigParser()
        config.read(self.conf)
        if config.has_section(section):
            result = dict(config.items(section))
        else:
            raise IOError("Config file '{0}' not contain section '{1}'".format(self.conf, section))

        self._db[section]['params'] = result
        return result


    def field_descr(self, field):
        """Возвращает значение ключа field
        в словаре self._params"""
        result = self._ip_params.get(field) or field
        return result

    
    def _fill_ipinfo(self, params=None):
        """Заполняет информацию об учетной записи
        с ip-адресом self.ip.
        params - Список полей в таблице vgroups"""
        if not params:
            params = self._ip_params

        assert type(params) == type(OrderedDict()), "_fill_ipinfo: 'params' must be a OrderedDict type"
        assert self.ip, "self.ip must be assigned first"
        assert type(self._ipinfo) == type(OrderedDict()), "_fill_ipinfo: 'params' must be a OrderedDict type"

        self._ipinfo['ip'] = self.ip

        args = dict()
        args['ip'] = self.ip
        # Имя поля в формате <имя поля> as '<имя поля>' для корректного поиска по ключу при получении описания поля
        args['fields'] = ", ".join(map(lambda field: "{0} as '{0}'".format(field), params.keys()))
        #print args
        sql = """
                select
                    {fields}
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
                    st.segment = inet_aton('{ip}')
              """.format(**args)
        #print sql

        cur = self._db[self._dbi]['cursor']
        cur.execute(sql)
        if cur.rowcount == 0:
            self._ipinfo = OrderedDict()
            return False
        assert cur.rowcount == 1, "'{0}' belongs to many vgroups or MySQLdb.cursor.rowcount < 0!!! O_o... It's impossible!".format(args['ip'])
        
        # Здесь cur.rowcount = 1
        ipinfo = cur.fetchone()

        # Конвертация цифрового представления поля blocked в текстовое обозначение
        ipinfo['v.blocked'] = self._blocked.get(ipinfo['v.blocked']) or ipinfo['v.blocked']

        # Чтобы сохранить порядок следования полей как в self._ip_params
        self._ipinfo = OrderedDict.fromkeys(self._ip_params)

        self._ipinfo.update(ipinfo)
        return True


    def _tables(self, timefrom='19011213', timeto='20380119', agent=None):
        """Возвращает отсортированный список таблиц.
        Параметры: даты формата YYYYMMDD, включая С исключая ПО,
        agent = id агента"""
        _param_err = """params 'timefrom' and 'timeto' must be string representation of date YYYYMMDD
                        param 'agent' must be string representation of integer with length <= 3"""
        _agent = agent or self._ipinfo['v.id']
        _agent = str(_agent)
        assert type(timefrom) == type(str()) and len(timefrom) == 8, _param_err
        assert type(timeto) == type(str()) and len(timefrom) == 8, _param_err
        assert timefrom.isdigit() and timeto.isdigit(), _param_err
        assert _agent.isdigit() and len(_agent) <= 3, _param_err
        
        # Получение имени БД со статистикой
        _stat = self._db.get(self._stat)
        if not _stat:
            self.open_db(self._stat)
        _db_params = self._db[self._stat].get('params')

        assert type(_db_params) == type(dict()), "_tables: _db_params must be a dictionary"

        db = _db_params['db']

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

        #print "_tables: sql = ", sql
        cur = self._db[self._stat]['cursor']
        cur.execute(sql)
        if cur.rowcount == 0:
            return False
        #TODO: А эта проверка вообще нужна?
        assert cur.rowcount >= 1, "MySQLdb.cursor.rowcount return value < 0... Is it possible?"

        # Here cur.rowcount >= 1
        rows = cur.fetchall()
        result = [row.get('tbl') for row in rows]
        return result

    def _set_detail(self, det='day'):
        """Настройка self._stat_fields в зависимости от типа детализации"""
        # Пример 'dfrom': ["s.timefrom", "время начала сессии", <Отображать>, <Группировать>, <Сортировать>],
        assert type(det) == type(str()), "_detalisation: det must be string type"
        if det == 'day':
            self._stat_fields['dfrom'][0] = 'date(s.timefrom)'
            self._stat_fields['dfrom'][1] = 'Дата'
            self._stat_fields['dfrom'][3] = False
            self._stat_fields['dday'][2] = True
            self._stat_fields['dday'][3] = True
            self._stat_fields['lip'][2] = False
            self._stat_fields['lport'][2] = False
            self._stat_fields['rip'][2] = False
            self._stat_fields['rport'][2] = False
        elif det == 'hour':
            #self._stat_fields['dfrom'][0] = 'hour(s.timefrom)'
            #self._stat_fields['dfrom'][1] = 'Час'
            self._stat_fields['dfrom'][3] = False
            self._stat_fields['dhour'][2] = True
            self._stat_fields['dhour'][3] = True
            self._stat_fields['lip'][2] = False
            self._stat_fields['lport'][2] = False
            self._stat_fields['rip'][2] = False
            self._stat_fields['rport'][2] = False
        elif det == 'day_file':
            self._stat_fields['dfrom'][2] = False
            self._stat_fields['tin'][4] = -1
        elif det == 'session_file':
            self._stat_fields['dfrom'][0] = 's.timefrom'
            self._stat_fields['dfrom'][4] = 1
        else:
            raise ValueError("'{0}' must be in [day|hour|day_file|session_file]".format(det))

        return True


    def _get_stat(self, timefrom='19011213', timeto='20380119', det='day'):
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

        # Установка степени детализации
        self._set_detail(det)

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
                desc = ''
                if v[4] < 0:
                    desc = 'desc'
                sort.append("`{0}` {1}".format(k, desc)) 
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
        cur = self._db[self._stat]['cursor']
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
                row = map(lambda s: str(s), row.values())
                data.append(row)

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
    parser.add_argument('-d', '--det', 
        metavar = 'DET',
        help = 'Уровень детализации')
    params = parser.parse_args()

    # Инициализация
    dbi = Dbi(ip = params.ip, conf = params.conf)

    # Печать информации об ip адресе
    if dbi._ipinfo:
        for k, v in dbi._ipinfo.items():
            key = dbi.field_descr(k)
            value = v
            print u'%s\t%s' % (key.decode('utf-8'), value)
    else:
        sys.exit("not found")

    stat = dbi._get_stat(params.dfrom, params.dto, params.det)
    print stat['header']
    for row in stat['body']:
        print row
    
if __name__ == "__main__":
    main()
