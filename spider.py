#!/usr/bin/python3
# -*- coding: UTF-8 -*-


import pandas as pd
import datetime as dt
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
#from time import sleep
#from random import random
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


def ck_folder(f):
   """
     Check if folder f exists and creat it if it doesn't
   """
   if not os.path.isdir(f):
      com = 'mkdir -p %s'%(f)
      LG.warning('Creating folder: %s'%(f))
      os.system(com)
   else: LG.debug('folder %s already existed'%(f))


def save_by_date(DF,folder,station,fmt='%d/%m/%Y %H:%M'):
   """
     Save data frame splitting the data as follows:
     folder
       ;-year1
       ;  `-month1
       ;      ;-IND1.dat
       ;      ;-IND2.dat
       ;      `-IND3.dat
       `-year2
          ;-month2
          `-month1
   """
   m = min(DF.index.date)
   min_year = m.year
   min_month = m.month
   m = max(DF.index.date)
   max_year = m.year
   max_month = m.month
   for y in range(min_year,max_year+1):
      fy = folder + str(y) + '/'
      ck_folder(fy)
      for m in range(min_month,max_month+1):
         fm = fy + '%02d/'%(m)
         fname = fm+station+'.csv'
         ck_folder(fm)
         A = DF.loc[DF.index.year==y]
         A = A[A.index.month==m]
         try:
            B = pd.read_csv(fname,delimiter=',', index_col=0,parse_dates=True,
                            header=0,date_parser=parser,names=names)
         except OSError: B = pd.DataFrame()
         A = pd.concat([A,B])
         A = A.sort_index()
         A = A.groupby(A.index).mean()
         #datos = datos.sort_index()
         #datos = datos.groupby(datos.index).mean()
         #datos.to_csv(folder+str(ind)+'.csv',date_format=fmt)
         #save_by_date(DATOS,folder,station,fmt=fmt)
         n,m = A.shape
         LG.debug('Saving %s lines to %s'%(n,fm+station+'.csv'))
         A.to_csv(fm+station+'.csv', date_format=fmt)


## URL params
base = 'http://www.aemet.es'
last_data = base+'/es/eltiempo/observacion/ultimosdatos'

## System setup
folder = HOME+'/Documents/WeatherData1/'
ck_folder(folder)

s = ', '   # delimiter for the csv file
ym = now.strftime('%Y/%m/')


f_stations = open(here+'/stations.csv','w')


## DataFrame parameters
fmt = '%d/%m/%Y %H:%M'
parser = lambda date: pd.datetime.strptime(date, fmt)
names = ['dates','temperature','wind','wind dir','gust','gust dir',
         'precipitation','pressure','pressure trend','humidity']


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
            LG.info(ind+': '+url_download)
            RAW_DATA = make_request(url_download).replace('"','')
            SAVE_DATA = '\n'.join(RAW_DATA.splitlines()[4:])
            with open('/tmp/station.csv','w') as f_out:
               f_out.write(SAVE_DATA+'\n')
            try:
               old = pd.read_csv(folder+ym+str(ind)+'.csv',delimiter=',',
                                 index_col=0,parse_dates=True,header=0,
                                 date_parser=parser,names=names)
            except OSError: old = pd.DataFrame()
            new = pd.read_csv('/tmp/station.csv',delimiter=',',
                              index_col=0,parse_dates=True,header=0,
                              date_parser=parser,names=names)
            DATOS = pd.concat([old,new])
            DATOS = DATOS.sort_index()
            DATOS = DATOS.groupby(DATOS.index).mean()
            #DATOS.to_csv(folder+str(ind)+'.csv',date_format=fmt)
            save_by_date(DATOS,folder,ind,fmt='%d/%m/%Y %H:%M')
            #f_out = open(folder+str(ind)+'.csv','a')
            #f_out.write(SAVE_DATA+'\n')
            #f_out.close()
            #twait = 10*random()
            #sleep(twait)
f_stations.close()
