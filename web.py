#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# from random import shuffle
from urllib.request import Request, urlopen
from urllib.error import URLError
from bs4 import BeautifulSoup
import datetime as dt
import pandas as pd
## LOG
import logging
# import log_help
LG = logging.getLogger(__name__)

# url_root = f'https://www.aemet.es'
# url_base = f'{url_root}/es/eltiempo/observacion/ultimosdatos'

def make_request(url, maxN=10):
   """
   Make http request, trying maxN times
   """
   LG.debug(f'Getting html from: {url}')
   HTMLdoc = None
   cont,out = 0,False
   while not out:
      try:
         req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
         HTMLdoc = urlopen(req)
         header = HTMLdoc.headers
         HTMLdoc = HTMLdoc.read()
         out = True
      except URLError:
         LG.warning(f'Download from {url} failed. Retrying')
         out = False       # TODO handle specific exceptions
         cont += 1
      #HTMLdoc = HTMLdoc.decode(header.get_content_charset())
      try:
         HTMLdoc = HTMLdoc.decode(header.get_content_charset(), errors='ignore')
      except TypeError: HTMLdoc = HTMLdoc.decode()
      except: pass #HTMLdoc = HTMLdoc.decode()
      if cont >= maxN:
         LG.critical(f'Unable to download from {url} after {cont} attempts')
         out = True
         # raise
   return HTMLdoc


def get_all_stations(url_base,write=True):
   """
   This function returns a list of all the available stations starting at 
   El Tiempo > Observacion > Hoy y ultimos dias
     https://www.aemet.es/es/eltiempo/observacion/ultimosdatos
   """
   LG.info('Getting all the comunidades')
   html_doc = make_request(url_base) # Main web site
   # print(html_doc)
   S = BeautifulSoup(html_doc, 'html.parser')
   # Look for all the provinces in the Comunidad Autonoma menu
   # (at the bottom of the page)
   ccaas = S.find('select',{'id':'ccaa_selector'})
   comunidades = []
   for ccaa in ccaas.findAll('option'):
      if ccaa.text == 'Todas': continue
      else:
         LG.debug(ccaa.text)
         comunidades.append( (ccaa['value'], ccaa.text) )
   LG.debug(f'{len(comunidades)} Comunidades')
   # Get all the stations
   LG.info('Retrieving stations')
   # shuffle(comunidades)
   stations = []
   from tqdm import tqdm
   for abbre,name in tqdm(comunidades):
      stations += get_stations_ccaa(abbre, url_base)
      LG.debug(f'{len(stations)} stations from {name}')
   return stations  #XXX

def get_stations_ccaa(ccaa,url_base,debug=False):
   """
   This function returns a list of all the available stations in a given ccaa
   """
   LG.info(f'Getting stations from {ccaa}')
   url = f'{url_base}?k={ccaa}&w=0'
   html_doc = make_request(url) # Main web site
   S = BeautifulSoup(html_doc, 'html.parser')
   menu_stations = S.find('select',{'id':'estacion'})
   stations = []
   for station in menu_stations.findAll('option'):
      if station['value'] != '':
         stations.append( (ccaa,station['value'],station.text) )
   LG.debug(f'Found {len(stations)} stations in {ccaa}')
   return stations  #XXX

def update_stations(stations,config_params,fname='stations.csv'):
   """
   Downloads the data from all the stations
   """
   fmt = '%d/%m/%Y-%H:%M'
   f_stations = open(fname,'w')
   header = ','.join(['code','lat','lon','alt','date','ccaa','muni','url'])
   f_stations.write(header+'\n')
   months = {'enero':'Jan',       'febrero':'Feb',
             'marzo':'Mar',       'abril':'Apr',
             'mayo':'May',        'junio':'Jun',
             'julio':'Jul',       'agosto':'aug',
             'septiembre':'Sep',  'octubre':'Oct',
             'noviembre':'Nov',   'december':'Dec'}
   LG.info('Getting the data')
   url_downloads = []
   for ccaa,code,name in stations:
      url = f'{config_params.url_base}?k={ccaa}&l={code}&w=0&datos=det'
      LG.debug(f'station: {url}')
      html_doc = make_request(url) # Main web site
      S = BeautifulSoup(html_doc, 'html.parser')
      info = S.findAll('div',{'class':'notas_tabla'})[1]
      loc = info.find('span',{'class':'geo'})
      lat = float(loc.find('abbr',{'class':'latitude'})['title'])
      lon = float(loc.find('abbr',{'class':'longitude'})['title'])
      for line in info.text.splitlines():
         if 'Actualizado:' in line:
            date = ':'.join(line.split(':')[1:]).strip().split()[1:-2]
            date = ' '.join(date)
            for k,v in months.items():
               date = date.replace(k,v)
            date.replace('a las','')
            date = dt.datetime.strptime(date,'%d %b %Y a las %H:%M')
         elif 'Municipio:' in line:
            muni = line.split(':')[1].split('-')[0].strip().replace(',','')
         elif 'Altitud (m):' in line:
            alti = int(line.split(':')[1])
      # Get Download link
      download = S.find('div',{'class':'enlace_csv inline_block'})
      url_download = config_params.url_root + download.find('a')['href']
      url_downloads.append(url_download)
      # Insert in DataFrame
      inp = [code,str(lat),str(lon),str(alti),date.strftime(fmt),ccaa,muni,
             url_download]
      inp = ','.join(inp)
      f_stations.write(inp+'\n')
      f_stations.flush()
      LG.debug(f'Added: {code}')
   f_stations.close()
   return pd.read_csv(fname)
