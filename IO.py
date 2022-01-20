#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
This library is in charge of loading/saving data as well as particular data
retrieval
"""

import os
HOME = os.getenv('HOME')

#import numpy as np
import pandas as pd
from io import StringIO
import datetime as dt
import pytz
#from scipy.interpolate import interp1d
#
#import geography as geo
## LOG
import logging
#import log_help
LG = logging.getLogger(__name__)

### DataFrame parameters
#fol_root = HOME+'/Documents/WeatherData/'
fmt = '%d/%m/%Y %H:%M'
parser = lambda date: pd.datetime.strptime(date, fmt)
names = ['date','temperature','wind','wind dir','gust','gust dir',
         'precipitation','pressure','pressure trend','humidity']
directions = {'Calma':float('nan'), 'nan':float('nan'),
              'Norte':0.0, 'Nordeste':45.0,
              'Este':90.0, 'Sudeste':135.0, 'Sur':180.0, 'Sudoeste':225.0,
              'Oeste':270.0, 'Noroeste':315.0}


def stf_df(data, do_utc_shift=True):
   """ Standard formatting of a DataFrame """
   for k,v in directions.items():
      data = data.replace(k,str(v))
   header = ','.join(names)
   data = '\n'.join(data.splitlines()[4:])
   data = '\n'.join([header,data])
   df = pd.read_csv( StringIO(data) )
   df['date'] = pd.to_datetime(df['date'],format='%d/%m/%Y %H:%M')
   if do_utc_shift: df['date'] = df['date'].apply(shift_date_utc)
   df.set_index('date', inplace=True)
   return df

def read_csv(fname):
   """
   Read csv file converting the dates to datetime and using it as index
   """
   parser = lambda date: pd.datetime.strptime(date, fmt)
   df = pd.read_csv(fname,date_parser=parser)
   df['date'] = pd.to_datetime(df['date'],format='%d/%m/%Y %H:%M')
   df.set_index('date', inplace=True)
   return df

def read_by_date(code,start_date,end_date,folder):
   """
   This function bypasses the folder structure when retrieving data from
   different months/years
   TODO. to be tested
   """
   if start_date.year == end_date.year and start_date.month == end_date.month:
      fname = f"{folder}/{start_date.strftime('%Y/%m')}/{code}.csv"
      return read_csv(fname)
   else:
      dfs = []
      for month in pd.date_range(start_date, end_date, freq='MS').tolist():
         fname = f"{folder}/month.strftime('%Y/%m')/{code}.csv"
         dfs.append(read_csv(fname))
      DF = pd.concat(dfs, axis=0, join="outer",
                          ignore_index=False, keys=None,
                          levels=None, names=None,
                          verify_integrity=False, copy=True)
      return DF

def merge_data(folder,code,new_data):
   """ Merge data with previous files and write changes """
   now = dt.datetime.now()
   ym = now.strftime('%Y/%m')
   fol = f'{folder}/{ym}'
   ck_folder(fol)
   fname = f"{fol}/{code}.csv"
   new = stf_df(new_data)
   try: old = aemet_csv(fname,head=True,cnvt=False) # data stored should already
                                                    # be converted
   # try: old = read_csv(fname)
   except OSError: old = pd.DataFrame()
   DATOS = pd.concat([old,new])
   DATOS = DATOS.drop_duplicates()
   # TODO Break the DF by month and save
   # DATOS.to_csv(fname, date_format=fmt)
   save_by_date(DATOS,folder,code,fmt='%d/%m/%Y %H:%M',head=True,cnvt=False)


def ck_folder(f):
   """
   Check if folder f exists and creat it if it doesn't
   """
   if not os.path.isdir(f):
      com = 'mkdir -p %s'%(f)
      LG.warning('Creating folder: %s'%(f))
      os.system(com)
   else: LG.debug(f'folder {f} already existed')


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
   ds = [min(DF.index.date), max(DF.index.date)] # shame of your ancestors!!!
   ds = [x.replace(day=1) for x in ds]           # TODO Fix this
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
      fm = f"{folder}/{d.strftime('%Y/%m')}"
      fname = f'{fm}/{station}.csv'
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
      LG.info(f'Saving {n} lines to {fname}')
      A.to_csv(fname, date_format=fmt,header=True, columns=names[1:])

###fname = 'stations.csv'   
###M = pd.read_csv(fname, delimiter=',',names=['ID','lat','lon','url'])
###M = M[['ID','lon','lat']]
###points = [(x,y) for x,y in zip(M['lon'].values,M['lat'].values)]
###ids = M['ID'].values
###dict_stations = dict(zip(ids, points))
###del M,points,ids
##
##def get_stations(fname='stations.csv',url=False):
##   """
##     Returns a pandas dataframe with the sations ID and (lon,lat) position
##   """
##   if url:
##      M = pd.read_csv(fname, delimiter=',',names=['ID','lat','lon','url'])
##      return M[['ID','lon','lat','url']]
##   else:
##      M = pd.read_csv(fname, delimiter=',',names=['ID','lat','lon'])
##      return M[['ID','lon','lat']]
##
##
##def get_data(date,place,prop=None,fol=fol_root,d=1,n=5):
##   """
##     Returns the closest data for that date and place (Interpolation in space
##     and time)
##     d = delta in time
##     n = number of stations to use
##   """
##   ## Fix props to return
##   if prop==None: props = names[1:]
##   elif isinstance(prop,str): props = [prop]
##   else: props = list(prop)
##   ## Find N closest stations
##   stations = get_stations()
##   IDs,dists = [],[]
##   for _, R in stations.iterrows():
##      IDs.append(R['ID'])
##      dists.append(geo.GPSdistance((R['lon'],R['lat']),place))
##   X = stations['lon'].values
##   Y = stations['lat'].values
##   IDs = np.array(IDs)
##   dists = np.array(dists)
##   inds = np.argsort(dists)
##
##   points = []
##   data,i = [],0
##   while len(data) < n and i<len(IDs):
##      ID = IDs[inds[i]]
##      data_station = get_data_from_station(ID,date,props)
##      aux = []
##      for a in data_station:
##         if a == a: aux.append(a)
##         else: aux.append(float('nan'))
##      points.append( (X[inds[i]],Y[inds[i]]) )
##      data.append(aux)
##      i += 1
##   x = [ix[0] for ix in points]
##   y = [ix[1] for ix in points]
##   from scipy.interpolate import CloughTocher2DInterpolator,LinearNDInterpolator
##   #f = CloughTocher2DInterpolator(points,data)
##   interps = []
##   for i in range(len(props)):
##      data_aux = []
##      points_aux = []
##      for ip in range(len(data)):
##         d = data[ip]
##         if d[i]==d[i]:
##            data_aux.append(d[i])
##            points_aux.append(points[ip])
##      interps.append(LinearNDInterpolator(points_aux,data_aux))
##   return [float(f(place)) for f in interps]
##
##def get_data_from_station(ID,date,prop=None,fol=fol_root,d=2):
##   """
##     Retrieve data (specific, or all of them) from a given station for a
##     specific time.
##     This function is equivalent to a interpolation in time for a given station
##     d: number of hours used for the interpolation
##   returning order:
##   temperature,wind,wind dir,gust,gust dir,precipitation,pressure,
##                                                       pressure trend,humidity
##   """
##   if prop==None: props = names[1:]
##   elif isinstance(prop,str): props = [prop]
##   else: props = list(prop)
##   d = dt.timedelta(hours=d)
##   x0 = pd.Timestamp(date).value
##   fname = fol_root+date.strftime('%Y/%m/') + '%s.csv'%(ID)
##   M = aemet_csv(fname,cnvt=False)
##   start = M.index.searchsorted(date-d)
##   end   = M.index.searchsorted(date+d)
##   df = M.ix[start:end]
##   aux = []
##   for prop in props:
##      x = [x.value for x in M.ix[start:end][prop].index]
##      y = M.ix[start:end][prop].values
##      if len(x) >= 2:
##         f = interp1d(x, y)  #TODO implement "kind"
##         a = float(f(x0))
##      else: a = float('nan')
##      aux.append(a)
##   return aux




def aemet_csv(fname,head=True,cnvt=False):
   """
     Wrapper to pandas.read_csv to adapt it to my data format.
     - head: if True use the first line as header names
     - cvnt: if True convert direction for wind/gust to float numbers
   """
   if head:
      M = pd.read_csv(fname, delimiter=',',parse_dates=True,header=0,
                             date_parser=parser, engine='python')
   else:
      M = pd.read_csv(fname, delimiter=',',parse_dates=True,date_parser=parser,
                             names=names, engine='python')
   if cnvt:
      nms = ['wind dir', 'gust dir']
      for nm in nms:
         X = [directions[str(x)] for x in M[nm]]
         X = pd.Series(X,name=nm,index=M.index,dtype=float)
         M.update(X)
   M.set_index('date',inplace=True)
   M.index = pd.to_datetime(M.index,format=fmt)
   return M


def UTC_shift(date,zone="Europe/Madrid"):
   """
   get current UTC offset
   """
   # adding a timezone
   timezone = pytz.timezone(zone)
   aware_date = timezone.localize(date)
   return aware_date.utcoffset()

def shift_date_utc(date):
   """
   Returns UTC time for the date-time provided
   """
   return date - UTC_shift(date)
