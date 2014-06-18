#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import os
import sys

# Установка текущей рабочей директории
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
cwd = os.getcwd()

import ConfigParser
import xmlrpclib

from ast import literal_eval

from collections import OrderedDict

import logging
logging.basicConfig(filename='log/bottle.log', format='%(asctime)s %(message)s', level=logging.DEBUG)

from bottle import route
from bottle import request
from bottle import template
from bottle import static_file
from bottle import run
from bottle import Bottle

gwman = Bottle()

#sys.path.insert(0, "%s/lib" % cwd)
#from server_functions import GwManServerFunctions

@gwman.route('/whoami')
def whoami():
    logging.info("%s?%s" % (request.path, request.query_string))
    login = os.getlogin()
    ip = gwman.request.environ.get('REMOTE_ADDR')
    tmpl_str = "I am a '{{login}}'<br>\
                my ip is '{{ip}}'"
    out = template(tmpl_str, login=login, ip=ip)
    return out


@gwman.route('/')
def index():
    logging.info("bottle index: %s?%s" % (request.path, request.query_string))
    forms = get_forms("%s/conf/forms.conf" % cwd)
    return template('index.tpl', forms=forms)


@gwman.route('/action/<action>')
def action(action):
    logging.info("bottle action: %s?%s" % (request.path, request.query_string))
    forms = get_forms("%s/conf/forms.conf" % cwd)

    rpcserver = request.params.get('rpcserver') or '127.0.0.1'
    logging.debug("bottle action: rpcserver = '{0}'".format(rpcserver))
    conn_str = 'http://{0}:1237'.format(rpcserver)
    params = dict(request.params)
    params = {k: v.strip() for k, v in params.iteritems()}
    try:
        del params['rpcserver']
    except:
        pass
    result = xmlrpcrequest(conn_str, action, params)
    

    return template('index.tpl', forms=forms, data=result)


@gwman.route('/static/<filepath:path>')
def static(filepath):
    logging.info("%s?%s" % (request.path, request.query_string))
    return static_file(filepath, root="%s/static" % cwd)

def get_forms(conf_file):
    """Возвращает список словарей form,
    имеющих структуру, считанную из секций conf/main.conf,
    начинающихся с form_.
    Каждый параметр секции обрабатывается ast.literal_eval(),
    строковые значения должны быть в кавычках"""
    logging.debug("get_forms file:\t%s" % str(conf_file))
    forms = list()
    config = ConfigParser.RawConfigParser()
    config.read(conf_file)
    sections = config.sections()
    forms_list = [s for s in sections if s.find("form_") >= 0]
    for form_name in forms_list:
        form = dict()
        for k, v in config.items(form_name):
            form[k] = literal_eval(config.get(form_name, k))
        forms.append(form)
        #name = config.get(form_name, 'name')
        #caption = config.get(form_name, 'caption')
        #fields = literal_eval(config.get(form_name, 'fields'))
        #forms.append({'caption': caption, 'fields': fields})

    return forms


def xmlrpcrequest(conn_str, func, params):
    """Выполняет xmlrpc запрос к серверу conn_str.
    Возвращает результат выполнения функции func
    с параметрами params"""
    logging.info("xmlrpcrequest call:\t%s" % str((conn_str, func, params)))

    server = xmlrpclib.ServerProxy(conn_str)
    #logging.debug("xmlrpcrequest server:\t%s" % server)

    methods = server.system.listMethods()
    logging.debug("xmlrpcrequest methods:\t%s" % methods)
    if not func in methods:
        raise ValueError("%s not implemented in server_functions" % func)

    method = getattr(server, func)
    #logging.debug("xmlrpcrequest:\ttype of 'method' is %s" % type(method))

    result = method(params)
    return result


if __name__ == "__main__":
    #run(host='localhost', port=8001, server='cherrypy', debug=True)
    gwman.run(host='0.0.0.0', port=8000, debug=True, reloader=True)
