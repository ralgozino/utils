#!/bin/env python
# -*- coding: utf8 -*-


import json
import urllib
import urllib2
import os
import argparse
import logging
import sys
from cgi import escape
from key import KEY

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--separador',
                    help='Separador de campos. TAB por defecto.',
                    default='\t',
                    )
parser.add_argument('-c', '--columna',
                    help='Número de la columna principal. Se usará para buscar las imágenes.',
                    default=0,
                    type=int,
                    )
parser.add_argument('-o', '--salida',
                    help='Nombre del archivo de salida.',
                    )
parser.add_argument('-d', '--debug',
                    help='Mostrar información de DEBUG.',
                    action="store_true",
                    )
parser.add_argument('-g', '--google',
                    help='Usar Google Image Search en vez de Bing.',
                    action="store_true",
                    )
parser.add_argument('-a', '--append',
                    help='Agregar texto al final de la query',
                    )
parser.add_argument('-i', '--skip',
                    help='Saltear los primeros n elementos',
                    default=0,
                    type=int,
                    )
parser.add_argument('-t', '--txt',
                    help='Generar archivo txt además de html.',
                    action="store_true",
                    default=False,
                    )
parser.add_argument('-n', '--no-search',
                    help='No realiza las búsquedas.',
                    action="store_true",
                    default=False,
                    )
parser.add_argument('archivo',
                    help='Archivo a parsear.'
                    )

args = parser.parse_args()

if args.debug:
    logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
else:
    logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

logging.debug('Iniciando programa')


def gimg(name=None):

    if args.append:
        name += ' ' + args.append

    gurl = 'https://ajax.googleapis.com/ajax/services/search/images?'
    gvalues = {'v': '1.0', 'q': name}

    gdata = urllib.urlencode(gvalues)

    greq = urllib2.Request(gurl + gdata)
    gresponse = urllib2.urlopen(greq)
    the_page = gresponse.read()

    jdata = json.loads(the_page)
    try:
        img_url = jdata['responseData']['results'][0]['url'].encode('utf-8')
        logging.debug('Encontrada imagen para ' + name + ': ' + img_url)
    except IndexError:
        img_url = 'SIN IMAGEN'
        logging.debug('No se encuentra imagen para ' + name)
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        img_url = 'SIN IMAGEN'
        logging.debug('No se encuentra imagen para ' + name)
        logging.error('Error no esperado: ' + str(exc_type) + str(exc_value))
        logging.debug('Respuesta de Google: ' + str(jdata))
    return urllib.unquote(img_url)


def bimg(query=None):
    user_agent = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; FDM; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 1.1.4322)'
    key = KEY
    creds = (':%s' % key).encode('base64')[:-1]
    auth = 'Basic %s' % creds

    if args.append:
        query += ' ' + args.append

    encoded_query = urllib.quote_plus(query)
    request = urllib2.Request('https://api.datamarket.azure.com/Data.ashx/Bing/Search/Image?Query=%27' +
                              encoded_query +
                              '%27&$top=1&$format=json')
    request.add_header('Authorization', auth)
    request.add_header('User-Agent', user_agent)

    requestor = urllib2.build_opener()
    result = requestor.open(request)
    jdata = json.loads(result.read())
    try:
        img_url = jdata['d']['results'][0]['MediaUrl'].encode('utf-8')
        img_title = jdata['d']['results'][0]['Title'].encode('utf-8')
        logging.debug('Encontrada imagen para ' + query + ': ' + img_url)
    except IndexError:
        img_url = 'SIN IMAGEN'
        logging.debug('No se encuentra imagen para ' + query)
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        img_url = 'SIN IMAGEN'
        logging.debug('No se encuentra imagen para ' + query)
        logging.error('Error no esperado: ' + str(exc_type) + str(exc_value))
        logging.debug('Respuesta de Bing: ' + str(jdata))
    return urllib.unquote(img_url)

def file_len(full_path):
  """ Count number of lines in a file."""
  f = open(full_path)
  nr_of_lines = sum(1 for line in f if line)
  f.close()
  return nr_of_lines

def main():
    logging.debug('Comenzando a escanear ' + args.archivo)
    total_items = file_len(args.archivo)
    items = open(args.archivo)
    logging.debug(args.archivo + ' tiene ' + str(total_items) + ' items.')
    items_con_foto_html = open(args.salida or os.path.splitext(args.archivo)[0] + '.html', 'w')
    logging.info('Guardando resultado a ' + items_con_foto_html.name)
    if args.txt:
        items_con_foto_txt = open(args.salida or os.path.splitext(args.archivo)[0] + '_procesado.txt', 'w')
        logging.info('Generando archivo txt adicional: ' + items_con_foto_txt.name)
    items_con_foto_html.write('<html><head><meta http-equiv="Content-Type" content="text/html;charset=utf-8"><title>Items con imagen</title></head><body style="background:#DADADA; font-family: \'Rock Salt\', \'Cantarell\', \'Ubuntu\', \'Liberation Sans\', sans-serif;">\n')

    if args.google:
        motor = 'Google'
    else:
        motor = 'Bing'
    logging.debug('Comenzando las búsquedas en ' + motor)

    if args.append:
        logging.debug('Agregando "' + args.append + '" a las búsquedas.')

    for i, linea in enumerate(items):
        if i < args.skip:
            logging.debug('Salteando item %s' % (i + 1))
            continue
        linea = linea.rstrip('\r\n')
        try:
            item = linea.split(args.separador)[args.columna]
            otros_items = linea.split(args.separador)[:args.columna] + linea.split(args.separador)[args.columna+1:]
            logging.debug('Procesando item %s: "%s"' % (i + 1, item))
        except IndexError:
            item = ''
            logging.debug('Error al tratar de obtener la columna ' + args.columna + 'de la linea ' + linea)
        if item:
            if not args.no_search:
                logging.info('Buscando imagen para ' + item)
                if args.google:
                    item_img = gimg(item)
                else:
                    item_img = bimg(item)
                if args.txt:
                    items_con_foto_txt.write(item + '\t' + item_img + '\t' + '\t'.join(otros_items))
                if item_img == 'SIN IMAGEN':
                    item_img = 'http://bancos.tictucumansistemas.net/images/sin_.png'
                items_con_foto_html.write('<div style="\
                                          display:inline-block;\
                                          margin:10px;\
                                          background-color:white;\
                                          border: 5px white solid;\
                                          box-shadow: 1px 1px 3px #888888;\
                                          ">\
                                          <p style="padding:0px;;margin:0px;">\
                                          <a href=https://www.google.com.ar/search?' + urllib.urlencode({'tbm': 'isch', 'q': item}) + '>' + escape(item) +
                                          '</a></p>' +
                                          '<p style="padding:0px;margin:0px;">' + escape(' '.join(otros_items)) + '</p>' +
                                          '<a href="' + item_img + '"><img style="display:block;margin-left:auto;margin-right:auto;max-width:250px;" src="' + item_img + '"/></a></div>'
                                          )
        logging.info('Completado %%%2.2f' % ((i + 1) / float(total_items) * 100.0))
    logging.debug('Finalizado el escaneo.')
    items_con_foto_html.write('</body></html>')
    items_con_foto_html.close()
    if args.txt:
        items_con_foto_txt.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.debug('Programa cancelado por el usuario.')
