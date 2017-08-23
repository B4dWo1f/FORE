#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import datetime as dt
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from time import sleep
from random import random
import numpy as np
import os
here = os.path.dirname(os.path.realpath(__file__))
HOME = os.getenv('HOME')



def make_request(url):
   req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
   html_doc = urlopen(req)
   html_doc = html_doc.read().decode(html_doc.headers.get_content_charset())
   return html_doc

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


base = 'http://www.aemet.es'
last_data = base+'/es/eltiempo/observacion/ultimosdatos'
folder = HOME+'/Documents/WeatherData/'


f_stations = open(here+'/stations.csv','w')

html_doc = make_request(last_data)
S = BeautifulSoup(html_doc, 'html.parser')
## This loop runs over each comunidad autonoma
for a in S.find_all('ul',class_="oculta_enlaces"):
   for link in a.find_all('a', href=True):
      base_url = 'http://www.aemet.es/es/eltiempo/observacion/'
      com_url = base_url+link['href']
      #print('Doing:',com_url)
      html_doc = make_request(com_url)
      S_region = BeautifulSoup(html_doc, 'html.parser')
      for dato in S_region.find_all('a',class_="estacion_dato"):
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
            f_stations.write(str(ind)+','+str(lat)+','+str(lon))
            f_stations.write(url_download+'\n')
            RAW_DATA = make_request(url_download).replace('"','')
            SAVE_DATA = '\n'.join(RAW_DATA.splitlines()[4:])
            f_out = open(folder+str(ind)+'.csv','a')
            f_out.write(SAVE_DATA+'\n')
            f_out.close()
            twait = 10*random()
            sleep(twait)
f_stations.close()
