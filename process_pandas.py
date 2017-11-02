#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
HOME = os.getenv('HOME')
here = os.path.dirname(os.path.realpath(__file__))
import datetime as dt
now = dt.datetime.now()

import pandas as pd

folder = HOME+'/Documents/WeatherData/'

ids = os.popen("ls %s*/*.csv | cut -d '/' -f 7 | sort | uniq"%(folder)).read()
ids = ids.splitlines()
folder_out = HOME+'/Documents/WeatherData_pandas/'


fmt = '%d/%m/%Y %H:%M'
parser = lambda date: pd.datetime.strptime(date, fmt)
names = ['dates','temperature','wind','wind dir','gust','gust dir',
         'precipitation','pressure','pressure trend','humidity']

DT_month = dt.timedelta(days=30)
last_year = now.year
last_month = now.month
for station in ids:
   print(station)
   DATOS = pd.DataFrame()
   files = os.popen('ls %s*/%s'%(folder,station)).read().splitlines()
   for fname in files:
      M = pd.read_csv(fname,delimiter=',',index_col=0,parse_dates=True,
                      date_parser=parser,names=names)
      DATOS = pd.concat([DATOS,M])
   DATOS = DATOS.groupby(DATOS.index).mean()  # Delete hourly duplicates
   m = min(DATOS.index.date)
   min_year = m.year
   min_month = m.month
   for y in range(min_year,last_year+1):
      fy = folder_out + str(y) + '/'
      com = 'mkdir -p %s'%(fy)
      os.system(com)
      for m in range(min_month,last_month+1):
         fm = fy + str(m) + '/'
         com = 'mkdir -p %s'%(fm)
         os.system(com)
         A = DATOS.loc[DATOS.index.year==y]
         A = A[A.index.month==m]
         A.to_csv(fm+station, date_format=fmt)
