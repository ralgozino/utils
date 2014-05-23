#!/usr/bin/python
#*-* coding:utf-8 *-*

import argparse
import smtplib
import logging
import socket

USRS_SISTEMA = ['EXCHANGE-01$', 'EXFESMTP-03$', 'OWA-01$', 'SYSTEM']


def get_logins(archivo):
    """
    Funcion que escanea archivo de log de EventViewer por logins
    """
    f = open(archivo)
    t = f.read()
    f.close()

    logging.info('Escaneando archivo de logins...')

    usuarios = set()
    for linea in t.split('\r\n'):
        if linea != '' and linea != 'Type\tDate\tTime\tSource\tCategory\tEvent\tUser\tComputer':
            try:
                usuario = linea.split('\t')[6]
                if usuario not in USRS_SISTEMA and usuario != '':
                    usuarios.add(usuario)
            except IndexError:
                logging.DEBUG('No se encontró usuario en la línea:', linea)

    logging.info('Finalizado el escaneo')

    return sorted(usuarios)


def test_SMTP(srv_dir, srv_port, srv_timeout, usr, psw, sender, rcpt, msg, enviar):
    """
    Testea conexión al servidor STMP.
    """
    logging.info(u'Abriendo conexión a ' + srv_dir + u':' + str(srv_port) + u'...')
    try:
        srv = smtplib.SMTP(srv_dir, srv_port, timeout=srv_timeout)
        logging.info('Login con ' + usr + ' // ' + psw)
        srv.login(usr, psw)
        logging.info('Login EXITOSO')
        valida = True
        logging.info('Helo')
        srv.helo('MailTester')
        if enviar:
            logging.info('Enviando test')
            srv.sendmail(sender, rcpt, msg)
        logging.info('Saliendo')
        srv.quit()
    except socket.timeout:
        logging.info('TimeOut al intentar conexión')
        valida = -1
    except smtplib.SMTPAuthenticationError:
        logging.info('Login fallido')
        valida = False
    return valida


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-t',
                        help='Testea los logins encontrados contra el servidor STMP utilizando contraseñas por defecto',
                        action="store_true",
                        )

    parser.add_argument('-s', '--server',
                        help='Especifica el servidor STMP',
                        # default='smtp.server.com'
                        )

    parser.add_argument('-o', '--server-port',
                        help='Especifica el Puerto del servidor SMTP (25 por defecto)',
                        default=25,
                        type=int
                        )

    parser.add_argument('-u', '--usuario',
                        help='Usuario SMTP'
                        )

    parser.add_argument('-p', '--password',
                        help='Password del Usuario SMTP',
                        #default='13245678',
                        )

    parser.add_argument('-r', '--remitente',
                        help='Remitente',
                        # default='test@server.com',
                        )

    parser.add_argument('-d', '--destinatario',
                        help='Destinatario',
                        # default='myaccount@server.com'
                        )

    parser.add_argument('-m', '--mensaje',
                        help='Mensaje de correo',
                        default='Mensaje electrónico de prueba.\nSaludos.'
                        )

    parser.add_argument('-e',
                        help='Enviar mail de prueba',
                        action='store'
                        )

    parser.add_argument('-l', '--debug', '--logging',
                        help='Muestra información adicional por pantalla',
                        action="store_true",
                        )

    parser.add_argument('-i', '--timeout',
                        help='Especifica la cantidad de segundos a esperar por timeout',
                        default=3,
                        type=int
                        )

    parser.add_argument('archivo',
                        help='Escanea el archivo para obtener logins',
                        action='store'
                        )

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s')

    logins = get_logins(args.archivo)

    if args.t:
        logging.info(u'Test de Contraseñas para cada login')
        validados = []
        no_validados = []

        for login in logins:
            valida = test_SMTP(args.server,
                               args.server_port,
                               args.timeout,
                               login or args.usuario,
                               args.password or login,
                               args.remitente,
                               args.destinatario,
                               args.mensaje,
                               args.e,
                               )
            if valida == -1:
                logging.info(u'No se continuará intenando logins')
                break
            elif valida:
                validados.append(login)
            else:
                no_validados.append(login)

        print 'Listado de Usuarios Validados:'
        print '=============================='
        print '\n'.join(sorted(validados))

        print 'Listado de Usuarios NO Validados:'
        print '================================='
        print '\n'.join(sorted(no_validados))

    else:
        print '\n'.join(logins)


if __name__ == '__main__':
    main()
