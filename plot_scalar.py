#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
 Library with tools to plot weather conditions for a given time
"""


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt

now = dt.datetime.now()
today = now.date()



## DataFrame parameters
fmt = '%d/%m/%Y %H:%M'
parser = lambda date: pd.datetime.strptime(date, fmt)
names = ['dates','temperature','wind','wind dir','gust','gust dir',
         'precipitation','pressure','pressure trend','humidity']
fig, ax = plt.subplots()

import IO
import os
files = os.popen('ls /home/ngarcia/Documents/WeatherData2/2017/11/*.csv').read().splitlines()
from random import shuffle

shuffle(files)
for fname in files:
   print(fname)
   print('')
   os.system('head %s'%(fname))
   print('')
   print(len(names))
   M = IO.aemet_csv(fname,cnvt=False)
   X = M.index
   Y = M['temperature']

   ax.plot(X,Y)

plt.show()
exit()
import datetime as dt
import numpy as np
from scipy.interpolate import CloughTocher2DInterpolator
import geography
import os

props = {'temperature':0, 't':0, 'temp':0,
         'wind':1, 'w':1,
         'gust':2, 'g':2,
         'precipitation':3, 'p':3, 'precip':3,
         'pressure':4, 'pr':4, 'press':4,
         'humidity':5, 'hum':5, 'H':5}
import sys
try: prop = props[sys.argv[1].lower()]
except KeyError:
   print('Unkown property:',sys.argv[1])
   print('The availabe properties are:')
   vals = [v for v in props.values()]
   uniq_vals = list(sorted(set(vals)))
   keys = [[] for _ in uniq_vals]
   for k,v in props.items():
      keys[uniq_vals.index(v)].append(k)
   keys = [sorted(x,key=lambda y:len(y),reverse=True) for x in keys]
   for k,v in zip(keys,uniq_vals):
      print('  -',', '.join(k))
   exit()
except IndexError:
   print('File not specified')
   exit()


time = dt.datetime.now() - dt.timedelta(hours=24)
fmt = '%d/%m/%Y %H:00'
t_search = time.strftime(fmt)
folder = '/home/ngarcia/Documents/WeatherData/2017_10'
tmp_file = '/tmp/data.csv'

#T,W,Wd,B,Bd,P,Pr,Prt,H
prop = 0   # Temperature


def getGPS(ID_station, stations='stations.csv'):
   st = os.popen('grep %s %s*'%(ID_station, stations)).read()
   gps = tuple(map(float,st.split(',')[1:3]))
   return gps


P0 = 40.480381,-3.845215  # lat,lon


com = 'grep "%s" %s/*.csv'%(t_search,folder)
data = os.popen(com).read().splitlines()
points,M = [],[]
LAT,LON,DATA = [],[],[]
for l in data:
   ID_station = l.split(':')[0].split('/')[-1].replace('.csv','')
   data = l.split(',')[1:]
   try: z = float(data[prop])
   except ValueError: continue
   lat,lon = getGPS(ID_station)
   if geography.GPSdistance(P0[::-1],(lon,lat)) < 900:
      LON.append(lon)
      LAT.append(lat)
      DATA.append(z)
      points.append((lon,lat))
      M.append(z)


aux = CloughTocher2DInterpolator(points,M)
x = np.linspace(min(LON),max(LON),100)
y = np.linspace(min(LAT),max(LAT),100)
X,Y,Z = [],[],[]
for ix in x:
   for iy in y:
      X.append(ix)
      Y.append(iy)
      Z.append( aux(ix,iy) )


import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.scatter(X,Y,c=Z,s=100,edgecolors='none')
ax.set_aspect('equal')
plt.show()
