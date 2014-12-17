#!/usr/bin/env python

from distutils.core import setup

setup(
    name = 'gwman',
    version = '0.9',
    packages = ['gwman'],
    scripts = [
        'bin/gwman_server',
        'bin/gwman_agent',
    ],

    install_requires = [
        'bottle > 0',
        'daemon > 0',
        'dnet > 0',
        'MySQLdb > 0',
    ],

    author = 'Koloskov Alexey',
    author_email = 'koloskov@flexline.ru',
    description = 'Gateway manager',
    url = 'http://redmine.flexline.ru/projects/gw_manager',
)
