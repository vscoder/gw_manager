#!/usr/bin/env python

from distutils.core import setup
from glob import glob

setup(
    name = 'gwman',
    version = '0.9.0',
    packages = ['gwman'],
    scripts = [
        'bin/gwman_server',
        'bin/gwman_agent',
    ],

    data_files = [
        ('etc/gwman', glob('conf/*.sample')),
        ('www/gwman/conf',  glob('www/conf/*.conf') +
                            glob('www/conf/*.sample')),
        ('www/gwman/views', glob('www/views/*.tpl')),
        ('www/gwman/static/css', glob('www/static/css/*.css')),
        ('www/gwman/static/pict', glob('www/static/pict/*.png')),
        ('www/gwman/log', glob('www/log/.*')),
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
