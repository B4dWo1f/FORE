#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
import numpy as np
import pandas as pd
import datetime as dt
## LOG
import logging
import log_help
LG = logging.getLogger(__name__)

## DataFrame parameters
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
         ## Try to merge with previously existing data
         try: B = aemet_csv(fname,head=head,cnvt=False)
         except OSError: B = pd.DataFrame()
         A = pd.concat([A,B])
         A = A.sort_index()
         A = A.groupby(A.index).mean()
         n,m = A.shape
         LG.info('Saving %s lines to %s'%(n,fm+station+'.csv'))
         A.to_csv(fm+station+'.csv', date_format=fmt)
