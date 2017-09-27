#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import datetime as dt
import numpy as np
import os
HOME = os.getenv('HOME')

fol = HOME + '/Documents/WeatherData/'

fols_months = os.popen('ls %s'%(fol)).read().splitlines()
months = [dt.datetime.strptime(x, '%Y_%m') for x in fols_months]

now = dt.datetime.now() - dt.timedelta(hours=8)
dist = [(now-x).total_seconds() for x in months]
ind = np.argmin(dist)

folder = fol + fols_months[ind]
#files = os.popen('ls %s/*.csv'%(folder)).read().splitlines()

fmt = '%d/%m/%Y %H:%M'

t_forecast = now.replace(minute=0,second=0,microsecond=0)
n = 3  #number of previous hours as input

print('Forecast for:',t_forecast)
print('Inputs')
for i in range(1,n+1):
   t = t_forecast - dt.timedelta(hours=i)
   com = 'grep "%s" %s/*.csv'%(t.strftime(fmt),folder)
   print(com)
   data = os.popen(com).read().splitlines()
   #data = [':'.join(x.split(':')[1:]) for x in data]
   for l in data:
      id_station = l.split(':')[0].split('/')[-1].replace('.csv','')
      com = 'grep %s stations.csv'%(id_station)
      gps = os.popen(com).read()
      gps = list(map(float,gps.split(',')[1:3]))
      lat,lon = gps
      print('',id_station,lat,lon,':'.join(l.split(':')[1:]))
