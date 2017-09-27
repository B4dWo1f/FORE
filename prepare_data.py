#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import datetime as dt
import numpy as np
import os
HOME = os.getenv('HOME')
here = os.path.dirname(os.path.realpath(__file__))

fol = HOME + '/Documents/WeatherData/'
stations = here + 'stations.csv'
fmt = '%d/%m/%Y %H:%M'


## Let's build an interpolator for a given space-time coordinate
T0 = dt.datetime.now() - dt.timedelta(hours=8)
T0 = T0 - dt.timedelta(hours=1)
T0 = T0.replace(minute=0,second=0,microsecond=0)
P0 = 40.951132, -4.323730, T0


# Folder to use
fols_months = os.popen('ls %s'%(fol)).read().splitlines()
months = [dt.datetime.strptime(x, '%Y_%m') for x in fols_months]

now = dt.datetime.now() - dt.timedelta(hours=8)
dist = [(now-x).total_seconds() for x in months]
ind = np.argmin(dist)

folder = fol + fols_months[ind]

com = 'grep "%s" %s/*.csv'%(P0[2].strftime(fmt),folder)
print(com)
resp = os.popen(com).read().splitlines()
f = open('/tmp/fore.csv','w')
for l in resp:
   ll = l.split(':')
   id_station = ll[0].split('/')[-1].replace('.csv','')
   data = ':'.join(ll[1:])
   com = 'grep %s stations.csv'%(id_station)
   gps = os.popen(com).read()
   gps = list(map(float,gps.split(',')[1:3]))
   lat,lon = gps
   f.write(str(lat)+','+str(lon)+','+data+'\n')
f.close()

def parse_ST(fname = '/tmp/fore.csv'):
   print(fname)
   ## Read floats
   Lat,Lon,T,W,dW,G,Gd,P,Pr,Prt,H = np.genfromtxt(fname, usecols=(0,1,3,4,5,6,7,8,9,10,11),
                                                   delimiter=',',unpack=True)
   return Lat,Lon,T,W,dW,G,Gd,P,Pr,Prt,H


lat,lon,T,w,wd,g,gd,p,pr,prt,h = parse_ST()

points,M = [],[]
for i in range(len(T)):
   t = T[i]
   la = lat[i]
   lo = lon[i]
   if t==t :   # Not nan
      points.append((lo,la))
      M.append(t)

from scipy.interpolate import CloughTocher2DInterpolator

TEMPERATURE = CloughTocher2DInterpolator(points,M)
print( TEMPERATURE((P0[1],P0[0])) )





exit()
#files = os.popen('ls %s/*.csv'%(folder)).read().splitlines()


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
