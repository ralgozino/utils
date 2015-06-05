#!/bin/bash

# Este script genera un archivo de configuración para NetworkManager, para que
# se active / desactive la placa WiFi cuando se desconecta / conecta el cable 
# de la placa eth.
#
# Este archivo debería estar junto a uno llamado 99-wlan usado como template.
# 
# ERRORES CONOCIDOS:
# Si la placa ethernet se llama distinto a ethX, dónde X es un número, el script
# genera mal el archivo configuración. Para solucionarlo, reemplazar el nombre de
# la placa ethernet en el archivo /etc/NetworkManager/dispatcher.d/99-wlan
#
# Autor: Ramiro Algozino <ralgozino@ascentio.com.ar>
# Fecha: Junio de 2015
# Versión: 1.0



function version_gt() { test "$(echo "$@" | tr " " "\n" | sort -V | tail -n 1)" == "$1"; }

export PLACA="$(nmcli device status | awk '{ print $1 }' | egrep 'eth')"

export VERSION="$(nmcli --version | grep -Eo "([0-9]{1,}\.)+[0-9]{1,}")"


if version_gt $VERSION '0.9.10.0'; then
    COMANDO="radio"
else
    COMANDO="nm"
fi

cp 99-wlan /etc/NetworkManager/dispatcher.d/
chmod +x /etc/NetworkManager/dispatcher.d/99-wlan

sed -i s/COMANDO/$COMANDO/g /etc/NetworkManager/dispatcher.d/99-wlan

sed -i s/PLACA/$PLACA/g /etc/NetworkManager/dispatcher.d/99-wlan
