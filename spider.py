#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import IO
import pandas as pd
import datetime as dt
from time import sleep
from random import random
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import numpy as np
import os
here = os.path.dirname(os.path.realpath(__file__))
HOME = os.getenv('HOME')
now = dt.datetime.now()

import logging
LG = logging.getLogger('main')
logging.basicConfig(level=logging.DEBUG,
                 format='%(asctime)s %(name)s:%(levelname)s - %(message)s',
                 datefmt='%Y/%m/%d-%H:%M:%S',
                 filename=HOME+'/spider.log', filemode='w')


def make_request(url):
   """
     Make http request
   """
   req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
   html_doc = urlopen(req)
   html_doc = html_doc.read().decode(html_doc.headers.get_content_charset())
   return html_doc

## OBSOLETE
def parse_data(RAW_DATA,tmp='/tmp/data.txt'):
   ## Remove header
   DATA = '\n'.join(RAW_DATA.splitlines()[4:])
   f = open(tmp,'w')
   f.write(DATA)
   f.close()
   ## Data
   M = np.genfromtxt(tmp,delimiter=',',usecols=tuple(range(1,10)))
   ## Date-Time
   N = np.genfromtxt(tmp,delimiter=',',dtype=str,usecols=(0,))
   N = np.array([dt.datetime.strptime(x, '%d/%m/%Y %H:%M') for x in N])
   N = np.reshape(N,(N.shape[0],1))
   os.system('rm %s'%(tmp))
   return np.hstack([N,M])


## URL params
base = 'http://www.aemet.es'
last_data = base+'/es/eltiempo/observacion/ultimosdatos'

## System setup
folder = HOME + '/Documents/WeatherData2/'
IO.ck_folder(folder)

s = ','   # delimiter for the csv file
ym = now.strftime('%Y/%m/')
t0 = 0


f_stations = open(here+'/stations.csv','w')
f_stations.write('ID,lat,lon,url\n')


## DataFrame parameters
fmt = '%d/%m/%Y %H:%M'
parser = lambda date: pd.datetime.strptime(date, fmt)
names = ['date','temperature','wind','wind dir','gust','gust dir',
         'precipitation','pressure','pressure trend','humidity']

directions = {'Calma':float('nan'), '':float('nan'), 'nan':float('nan'),
              'Norte':0.0, 'Nordeste':45.0,
              'Este':90.0, 'Sudeste':135.0, 'Sur':180.0, 'Sudoeste':225.0,
              'Oeste':270.0, 'Noroeste':315.0}


html_doc = make_request(last_data) # Main web site
S = BeautifulSoup(html_doc, 'html.parser')
## This loop runs over each comunidad autonoma
for a in S.find_all('ul',class_="oculta_enlaces"):
   for link in a.find_all('a', href=True):
      LG.info('Doing : %s'%(link.text))
      base_url = 'http://www.aemet.es/es/eltiempo/observacion/'
      com_url = base_url+link['href']
      #print('Doing:',com_url)
      html_doc = make_request(com_url)
      S_region = BeautifulSoup(html_doc, 'html.parser')
      for dato in S_region.find_all('a',class_="estacion_dato"):
         #LG.info(dato.text.lstrip().rstrip())
         url = dato['xlink:href'].replace('img','det')
         if '&'.join(com_url.split('&')[0:-1]).replace(base,'') in url:
            # To stop from rest of links
            url_dow = base+dato['xlink:href'].replace('img','det')
            for f in url_dow.split('&'):
               if 'l=' in f:
                  ind = f.replace('l=','')
                  break
            html_doc = make_request(url_dow)
            S_down = BeautifulSoup(html_doc, 'html.parser')
            ## Download link
            aux = 'enlace_csv inline_block'
            for down in S_down.find_all('div', class_=aux):
               for dato in down.find_all('a',href=True):
                  url_download = base+dato['href']
            ## Geographic information
            for geo in S_down.find_all('span',class_='geo'):
               for lat in S_down.find_all('abbr',class_='latitude'):
                  lat = float(lat['title'])
               for lon in S_down.find_all('abbr',class_='longitude'):
                  lon = float(lon['title'])
            #print(ind,lat,lon,'',url_download)
            LG.info('station: %s  (%.3f, %.3f)'%(ind,lat,lon))
            f_stations.write(str(ind)+s+str(lat)+s+str(lon))
            f_stations.write(s+url_download+'\n')
            try: old = IO.aemet_csv(folder+ym+str(ind)+'.csv',cnvt=False)
            except OSError: old = pd.DataFrame()
            LG.info(ind+': '+url_download)
            RAW_DATA = make_request(url_download).replace('"','')
            SAVE_DATA = '\n'.join(RAW_DATA.splitlines()[4:])
            tmp_sta_fil = '/tmp/station1.csv'
            with open(tmp_sta_fil,'w') as f_out:
               f_out.write(','.join(names)+'\n')
               f_out.write(SAVE_DATA+'\n')
            new = IO.aemet_csv(tmp_sta_fil,head=True,cnvt=True)
            DATOS = pd.concat([old,new])
            DATOS = DATOS.sort_index()
            DATOS = DATOS.groupby(DATOS.index).mean()
            IO.save_by_date(DATOS,folder,ind,fmt='%d/%m/%Y %H:%M')
            sleep(t0*random())
f_stations.close()
LG.debug('Done')
