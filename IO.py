#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
This library is in charge of loading/saving data as well as particular data
retrieval
"""

import os
HOME = os.getenv('HOME')

import numpy as np
import pandas as pd
import datetime as dt
from scipy.interpolate import interp1d

import geography as geo
## LOG
import logging
import log_help
LG = logging.getLogger(__name__)

## DataFrame parameters
fol_root = HOME+'/Documents/WeatherData/'
fmt = '%d/%m/%Y %H:%M'
parser = lambda date: pd.datetime.strptime(date, fmt)
names = ['date','temperature','wind','wind dir','gust','gust dir',
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
##fname = 'stations.csv'   
##M = pd.read_csv(fname, delimiter=',',names=['ID','lat','lon','url'])
##M = M[['ID','lon','lat']]
##points = [(x,y) for x,y in zip(M['lon'].values,M['lat'].values)]
##ids = M['ID'].values
##dict_stations = dict(zip(ids, points))
##del M,points,ids
#
#def get_stations(fname='stations.csv',url=False):
#   """
#     Returns a pandas dataframe with the sations ID and (lon,lat) position
#   """
#   if url:
#      M = pd.read_csv(fname, delimiter=',',names=['ID','lat','lon','url'])
#      return M[['ID','lon','lat','url']]
#   else:
#      M = pd.read_csv(fname, delimiter=',',names=['ID','lat','lon'])
#      return M[['ID','lon','lat']]
#
#
#def get_data(date,place,prop=None,fol=fol_root,d=1,n=5):
#   """
#     Returns the closest data for that date and place (Interpolation in space
#     and time)
#     d = delta in time
#     n = number of stations to use
#   """
#   ## Fix props to return
#   if prop==None: props = names[1:]
#   elif isinstance(prop,str): props = [prop]
#   else: props = list(prop)
#   ## Find N closest stations
#   stations = get_stations()
#   IDs,dists = [],[]
#   for _, R in stations.iterrows():
#      IDs.append(R['ID'])
#      dists.append(geo.GPSdistance((R['lon'],R['lat']),place))
#   X = stations['lon'].values
#   Y = stations['lat'].values
#   IDs = np.array(IDs)
#   dists = np.array(dists)
#   inds = np.argsort(dists)
#
#   points = []
#   data,i = [],0
#   while len(data) < n and i<len(IDs):
#      ID = IDs[inds[i]]
#      data_station = get_data_from_station(ID,date,props)
#      aux = []
#      for a in data_station:
#         if a == a: aux.append(a)
#         else: aux.append(float('nan'))
#      points.append( (X[inds[i]],Y[inds[i]]) )
#      data.append(aux)
#      i += 1
#   x = [ix[0] for ix in points]
#   y = [ix[1] for ix in points]
#   from scipy.interpolate import CloughTocher2DInterpolator,LinearNDInterpolator
#   #f = CloughTocher2DInterpolator(points,data)
#   interps = []
#   for i in range(len(props)):
#      data_aux = []
#      points_aux = []
#      for ip in range(len(data)):
#         d = data[ip]
#         if d[i]==d[i]:
#            data_aux.append(d[i])
#            points_aux.append(points[ip])
#      interps.append(LinearNDInterpolator(points_aux,data_aux))
#   return [float(f(place)) for f in interps]
#
#def get_data_from_station(ID,date,prop=None,fol=fol_root,d=2):
#   """
#     Retrieve data (specific, or all of them) from a given station for a
#     specific time.
#     This function is equivalent to a interpolation in time for a given station
#     d: number of hours used for the interpolation
#   returning order:
#   temperature,wind,wind dir,gust,gust dir,precipitation,pressure,
#                                                       pressure trend,humidity
#   """
#   if prop==None: props = names[1:]
#   elif isinstance(prop,str): props = [prop]
#   else: props = list(prop)
#   d = dt.timedelta(hours=d)
#   x0 = pd.Timestamp(date).value
#   fname = fol_root+date.strftime('%Y/%m/') + '%s.csv'%(ID)
#   M = aemet_csv(fname,cnvt=False)
#   start = M.index.searchsorted(date-d)
#   end   = M.index.searchsorted(date+d)
#   df = M.ix[start:end]
#   aux = []
#   for prop in props:
#      x = [x.value for x in M.ix[start:end][prop].index]
#      y = M.ix[start:end][prop].values
#      if len(x) >= 2:
#         f = interp1d(x, y)  #TODO implement "kind"
#         a = float(f(x0))
#      else: a = float('nan')
#      aux.append(a)
#   return aux


def ck_folder(f):
   """
     Check if folder f exists and creat it if it doesn't
   """
   if not os.path.isdir(f):
      com = 'mkdir -p %s'%(f)
      LG.warning('Creating folder: %s'%(f))
      os.system(com)
   else: LG.debug('folder %s already existed'%(f))


def aemet_csv(fname,head=True,cnvt=True):
   """
     Wrapper to pandas.read_csv to adapt it to my data format.
     - head: if True use the first line as header names
     - cvnt: if True convert direction for wind/gust to float numbers
   """
   if head:
      M = pd.read_csv(fname, delimiter=',',parse_dates=True,header=0,
                             date_parser=parser)
   else:
      M = pd.read_csv(fname, delimiter=',',parse_dates=True,date_parser=parser,
                             names=names)
   if cnvt:
      nms = ['wind dir', 'gust dir']
      for nm in nms:
         X = [directions[str(x)] for x in M[nm]]
         X = pd.Series(X,name=nm,index=M.index,dtype=float)
         M.update(X)
   M.set_index('date',inplace=True)
   M.index = pd.to_datetime(M.index,format=fmt)
   return M

def save_by_date(DF,folder,station,fmt='%d/%m/%Y %H:%M',head=True,cnvt=False):
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
   ## generate all the dates
   ds = [min(DF.index.date), max(DF.index.date)]
   current = min(ds)
   dates = [current]
   while current < max(ds):
      next_month = (current.month+1)%12
      if next_month < current.month:
         current = current.replace(year=current.year+1)
         current = current.replace(month=(current.month+1)%12)
      else: current = current.replace(month=(current.month+1)%12)
      dates.append(current)

   for d in dates:
      fm = folder + d.strftime('%Y/%m') + '/'
      fname = fm+station+'.csv'
      y,m = d.year,d.month
      ck_folder(fm)
      A = DF.loc[DF.index.year==y]
      A = A[A.index.month==m]
      ## Try to merge with previously existing data
      try: B = aemet_csv(fname,head=head,cnvt=False)
      except OSError: B = pd.DataFrame()
      A = pd.concat([A,B])
      A = A.sort_index()
      A = A.groupby(A.index).mean()
      n,m = A.shape
      LG.info('Saving %s lines to %s'%(n,fm+station+'.csv'))
      A.to_csv(fm+station+'.csv', date_format=fmt,header=True,
                                                         columns=names[1:])
