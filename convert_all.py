#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import IO
import pandas as pd
import datetime as dt
import os
here = os.path.dirname(os.path.realpath(__file__))
HOME = os.getenv('HOME')
now = dt.datetime.now()

com = 'find /home/ngarcia/Documents/WeatherData/ -iname "*.csv" | cut -d "/" -f 7 | sort | uniq'
all_stations = os.popen(com).read().splitlines()

folder = '/home/ngarcia/ZZZ/'

#fmt = '%d/%m/%Y %H:%M'
#parser = lambda date: pd.datetime.strptime(date, fmt)

## DataFrame parameters
fmt = '%d/%m/%Y %H:%M'
parser = lambda date: pd.datetime.strptime(date, fmt)
#names = ['dates','temperature','wind','wind dir','gust','gust dir',
names = ['temperature','wind','wind dir','gust','gust dir',
         'precipitation','pressure','pressure trend','humidity']

directions = {'Calma':float('nan'), '':float('nan'), 'nan':float('nan'),
              'Norte':0.0, 'Nordeste':45.0,
              'Este':90.0, 'Sudeste':135.0, 'Sur':180.0, 'Sudoeste':225.0,
              'Oeste':270.0, 'Noroeste':315.0}

types = {'dates':dt.datetime,
         'temperature':float,
         'wind':float, 'wind dir':str,
         'gust':float,'gust dir':str,
         'precipitation':float,
         'pressure':float, 'pressure trend':float,
         'humidity':float}



for id_station in all_stations:
   ind = id_station.replace('.csv','')
   com = 'ls /home/ngarcia/Documents/WeatherData/*/%s'%(id_station)
   files = os.popen(com).read().splitlines()

   DATOS = pd.DataFrame()
   for fname in files:
      M = IO.aemet_csv(fname,head=False,cnvt=False)
          #pd.read_csv(fname,delimiter=',',index_col=0,parse_dates=True,
          #            date_parser=parser,names=names)
      print(fname, M.shape)
      DATOS = pd.concat([DATOS,M])
   DATOS = DATOS.sort_index()
   DATOS = DATOS.groupby(DATOS.index).mean()
   IO.save_by_date(DATOS,folder,ind)
