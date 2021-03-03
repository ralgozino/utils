#!/usr/bin/env python
# *-* coding:utf-8 *-*

"""
Basado en: 
Threaded Python multiple port scanner 
http://exchange.nagios.org/directory/Plugins/Network-Protocols/*-TCP-and-UDP-(Generic)/Threaded-Python-multiple-ports-scanner/details
"""

import threading
import socket
import time
import sys
import logging
import argparse


servers = ['10.70.2.' + str(i) for i in range(100,109)]

warning = 10 # default value
critical = 30 # default value
port = 8080

parser = argparse.ArgumentParser()

parser.add_argument('-l','--debug','--logging',
                    help='Muestra información adicional por pantalla',
                    action="store_true",
                    )

args = parser.parse_args()

if args.debug:
    logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)

def check_port(server,port):
    s = socket.socket()
    if s.connect_ex((server,port)) == 0:
        escuchando.append(server)
        logging.info(server + u':' + str(port) + u' escuchando.')
    else:
        no_escuchando.append(server)
    s.close()


s = time.time()
threads = []
escuchando = []
no_escuchando = []

#servers = servers.split()

for server in servers:
    logging.info(u'Intentando Conexión a ' + server + ':' + str(port))
    t = threading.Thread(target=check_port,args=(server,int(port)))
    t.start()
    threads.append(t)
for t in threads:
    t.join()


time_value = time.time() - s


if no_escuchando:
    msg = u"Servidores que no están escuchando el puerto %s:\n%s."% (port,"\n".join(sorted(no_escuchando)))
    exit_code = 2
else:
    msg = "Todos los servidores online."
    exit_code = 0


if time_value > critical:
    msg += " Time is CRITICAL %s" % (time_value)
    exit_code = 2

if time_value > warning:
    msg += " Time is WARNING %s" % (time_value)
    if exit_code == 0:
        exit_code = 1

print msg
sys.exit(exit_code)

