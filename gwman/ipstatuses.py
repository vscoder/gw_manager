#!/usr/bin/env python2
# -*- coding: utf_8 -*-

import re
import subprocess
from distutils import spawn

from gwman import gwman

class Ipstatuses(gwman):
    """Установка состоояния клиентских ip-адресов в соответствии с биллингом"""

    def __init__(self, host='127.0.0.1', hops='8'):
        gwman.__init__(self)

        self.ipstatuses = "/root/billing/scripts/ips_status.sh"

        #self.timeout = 0


    def set_statuses(self):
        """Выполнить /root/billing/scripts/ips_status.sh"""
        cmd = [self.ipstatuses]
        PIPE = subprocess.PIPE
        ipstatuses = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output = ipstatuses.stdout.read()
        retcode = ipstatuses.poll()
        return (retcode, output)


def main():
    # Обработка аргументов коммандной строки
    import argparse
    parser = argparse.ArgumentParser(
        description="""run script /root/billing/scripts/ips_status.sh""")
    params = parser.parse_args()

    ipstatuses = Ipstatuses()
    result = ipstatuses.set_statuses()

    print "returncode: %s\n%s" % result


if __name__ == "__main__":
    main()
