#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import IO
import geography as geo
import pandas as pd
import numpy as np
import datetime as dt
from scipy.interpolate import interp1d
from scipy.interpolate import CloughTocher2DInterpolator,LinearNDInterpolator
## Sys params
import os
HOME = os.getenv('HOME')


## DataFrame parameters
fol_root = HOME+'/Documents/WeatherData/'
fmt = '%d/%m/%Y %H:%M'
parser = lambda date: pd.datetime.strptime(date, fmt)
names = ['date','temperature','wind','wind dir','gust','gust dir',
         'precipitation','pressure','pressure trend','humidity']


def get_stations(fname='stations.csv',url=False):
   """
     Returns a pandas dataframe with the sations ID and (lon,lat) position
   """
   M = pd.read_csv(fname, delimiter=',',header=0)
   if url: return M[['ID','lon','lat','url']]
   else: return M[['ID','lon','lat']]

def get_N_stations(p0,N=5,fname='stations.csv',url=False):
   """
     Returns a generator with the stations ordered by distance to p0
   """
   ## Find N closest stations
   stations = get_stations()
   IDs,dists = [],[]
   for _, R in stations.iterrows():
      IDs.append(R['ID'])
      dists.append(geo.GPSdistance((R['lon'],R['lat']),p0))
   X = stations['lon'].values
   Y = stations['lat'].values
   IDs = np.array(IDs)
   dists = np.array(dists)
   inds = np.argsort(dists)
   for ID in IDs[inds]:
      yield ID
   #return IDs[inds[:N]]


def get_data(date,place,prop=None,fol=fol_root,d=1,n=5,kind='cubic'):
   """
     Returns the closest data for that date and place (Interpolation in space
     and time)
     d: delta in time
     n: number of stations to use
   """
   ## Fix parameters
   # properties to return
   if prop==None: props = names[1:]
   elif isinstance(prop,str): props = [prop]
   else: props = list(prop)
   # interpolation kind
   if kind == 'linear': interp2d = LinearNDInterpolator
   else: interp2d = CloughTocher2DInterpolator
   ## Find N closest stations
   stations = get_stations()
   IDs,dists = [],[]
   for _, R in stations.iterrows():
      IDs.append(R['ID'])
      dists.append(geo.GPSdistance((R['lon'],R['lat']),place))
   X = stations['lon'].values
   Y = stations['lat'].values
   IDs = np.array(IDs)
   dists = np.array(dists)
   inds = np.argsort(dists)

   points = []
   data,i = [],0
   while len(data) < n and i<len(IDs):
      ID = IDs[inds[i]]
      data_station = get_data_from_station(ID,date,props,kind=kind)
      aux = []
      for a in data_station:
         if a == a: aux.append(a)
         else: aux.append(float('nan'))
      points.append( (X[inds[i]],Y[inds[i]]) )
      data.append(aux)
      i += 1
   x = [ix[0] for ix in points]
   y = [ix[1] for ix in points]
   interps = []
   for i in range(len(props)):
      data_aux = []
      points_aux = []
      for ip in range(len(data)):
         d = data[ip]
         if d[i]==d[i]:
            data_aux.append(d[i])
            points_aux.append(points[ip])
      interps.append(LinearNDInterpolator(points_aux,data_aux))
   return [float(f(place)) for f in interps]


def get_data_from_station(ID,date,prop=None,fol=fol_root,d=2,kind='cubic'):
   """
     Retrieve data (specific, or all of them) from a given station for a
     specific time.
     This function is equivalent to a interpolation in time for a given station
     ID: ID of the station
     date: datetime for which to retrieve the data
     fol: root folder containing all the data
     d: number of hours used for the interpolation
     prop: properties to return. If None ==> return all the properties
   returning order:
   temperature,wind,wind dir,gust,gust dir,precipitation,pressure,
                                                      pressure trend,humidity
   """
   ## Fix parameters
   # properties to return
   if prop == None: props = names[1:]
   elif isinstance(prop,str): props = [prop]
   else: props = list(prop)
   d = dt.timedelta(hours=d)
   x0 = pd.Timestamp(date).value
   fname = fol_root+date.strftime('%Y/%m/') + '%s.csv'%(ID)
   M = IO.aemet_csv(fname,cnvt=False)
   start = M.index.searchsorted(date-d)
   end   = M.index.searchsorted(date+d)
   df = M.ix[start:end]
   aux = []
   for prop in props:
      x = [x.value for x in M.ix[start:end][prop].index]
      y = M.ix[start:end][prop].values
      if len(x) >= 2:
         f = interp1d(x, y, kind=kind)
         a = float(f(x0))
      else: a = float('nan')
      aux.append(a)
   return aux
