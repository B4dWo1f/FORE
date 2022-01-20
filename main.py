#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import web

# from urllib.request import Request, urlopen
# from urllib.error import URLError
# from time import sleep
# from random import random

# def make_request(url,maxN=10):
#    """
#      Make http request
#    """
#    # LG.info(f'Getting html from: {url}')
#    print(f'Getting html from: {url}')
#    cont,out = 0,False
#    while not out:
#       print('**',url)
#       headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
#       req = Request(url, headers=headers) #{'User-Agent': 'Mozilla/5.0'})
#       print('**',req)
#       HTMLdoc = urlopen(req)
#       print('**',HTMLdoc)
#       header = HTMLdoc.headers
#       print('**',header)
#       HTMLdoc = HTMLdoc.read()
#       print('**',HTMLdoc)
#       print('---------------')
#       out = True
#       # try:
#       #    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
#       #    req = Request(url, headers=headers)
#       #    HTMLdoc = urlopen(req)
#       #    header = HTMLdoc.headers
#       #    HTMLdoc = HTMLdoc.read()
#       #    out = True
#       # except URLError:
#       #    # LG.debug(f'Download from {url} failed. Retrying')
#       #    print(f'Download from {url} failed. Retrying')
#       #    out = False   # XXX handle specific exceptions
#       #    cont += 1
#       #    t0 = 10*random()
#       #    print(f'Waiting {t0} seconds')
#       #    sleep(t0)
#       if cont >= maxN:
#          # LG.critical(f'Unable to download from {url}')
#          print(f'Unable to download from {url}')
#          out = True
#          # XXX maybe aske if keep trying??
#    HTMLdoc = HTMLdoc.decode(header.get_content_charset())
#    return HTMLdoc

base = 'http://www.aemet.es'
last_data = base+'/es/eltiempo/observacion/ultimosdatos'
html_doc = web.make_request(last_data)
print(html_doc)
