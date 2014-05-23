#!/usr/bin/python
#*-* coding:utf-8 *-*

import smtplib
import argparse
import logging

parser = argparse.ArgumentParser()

parser.add_argument('-u', '--usuario',
                    help=u'Usuario',
                    required=True,
                    )

parser.add_argument('-p', '--password',
                    help=u'Contraseña. Por defecto utiliza el usuario como contraseña.',
                    )

parser.add_argument('-s', '--server',
                    help='Servidor STMP',
                    # default='mail.server.com'
                    )

parser.add_argument('-o', '--puerto',
                    help=u'Puerto del servidor SMTP',
                    type=int,
                    default=25,
                    )

parser.add_argument('-e', '--enviar-mail',
                    help=u'Envía Mail de Prueba',
                    action="store_true",
                    )


args = parser.parse_args()

args.password = args.password or args.usuario

SENDER = 'test@mail.server.com'
RCPT = 'myaccount@server.com'
MSG = 'Este es un mensaje de prueba\nSepa disculpas las molestias.\nSaludos cordiales.'

logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)

try:
    logging.info(u'Abriendo conexión a ' + args.server + u':' + str(args.puerto))
    srv = smtplib.SMTP(args.server, args.puerto)
    logging.info(u'Intentando login con ' + args.usuario + u' // ' + args.password)
    srv.login(args.usuario, args.password)
    logging.info(u'Enviado comando Helo')
    srv.helo('MailTester')
    if args.enviar_mail:
        logging.info(u'Enviando correo electrónico de prueba')
        srv.sendmail(SENDER, RCPT, MSG)
    logging.info(u'Cerrando conexión')
    srv.quit()
except smtplib.SMTPAuthenticationError:
    logging.info(u'Resultado: LOGIN FALLIDO')
else:
    logging.info(u'Resultado: login exitoso.')
