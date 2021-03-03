#!/usr/bin/python
#*-* coding:utf-8 *-*

import sys

if len(sys.argv) > 1:
    archivo = sys.argv[1]
else:
    archivo = 'logins.log'

f = open(archivo)
t = f.read()
f.close()

usuarios = set()
for linea in t.split('\r\n'):
    if linea != '' and linea != 'Type\tDate\tTime\tSource\tCategory\tEvent\tUser\tComputer':
        try:
            usuarios.add(linea.split('\t')[6])
        except IndexError:
            print 'No se encontró usuario en la línea:',linea

for usuario in sorted(usuarios):
    print usuario
