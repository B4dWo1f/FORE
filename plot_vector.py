#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import datetime as dt
import numpy as np
from scipy.interpolate import CloughTocher2DInterpolator
import geography
import os


time = dt.datetime.now() - dt.timedelta(hours=24)
fmt = '%d/%m/%Y %H:00'
t_search = time.strftime(fmt)
folder = '/home/ngarcia/Documents/WeatherData/2017_10'
tmp_file = '/tmp/data.csv'

#T,W,Wd,B,Bd,P,Pr,Prt,H
prop = 1   # wind

props = {'T':0,'W':1,'G':2,'P':3,'Pr':4,'H':5}

def getGPS(ID_station, stations='stations.csv'):
   st = os.popen('grep %s %s*'%(ID_station, stations)).read()
   gps = tuple(map(float,st.split(',')[1:3]))
   return gps


P0 = 40.480381,-3.845215  # lat,lon


com = 'grep "%s" %s/*.csv'%(t_search,folder)
data = os.popen(com).read().splitlines()
points,M,Md = [],[],[]
LAT,LON,DATA,DATAd = [],[],[],[]
U,V = [],[]
for l in data:
   ID_station = l.split(':')[0].split('/')[-1].replace('.csv','')
   data = l.split(',')[1:]
   try: z,zd = float(data[1]),float(data[2])  # wind, winddir
   except ValueError: continue
   lat,lon = getGPS(ID_station)
   if geography.GPSdistance(P0[::-1],(lon,lat)) < 900:
      LON.append(lon)
      LAT.append(lat)
      DATA.append(z)
      DATAd.append(zd)
      points.append((lon,lat))
      M.append(z)
      Md.append(zd)
      U.append(np.sin(np.radians(zd)))
      V.append(np.cos(np.radians(zd)))

print(len(points),len(M),len(Md))

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
ax.quiver(LON,LAT,U,V,linewidth=.5,alpha=0.7,zorder=10)
ax.scatter(X,Y,c=Z,s=100,edgecolors='none',alpha=0.6,zorder=0)
ax.set_aspect('equal')
plt.show()
