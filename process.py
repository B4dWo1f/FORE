#!/usr/bin/python3
# -*- coding: UTF-8 -*-


import numpy as np
import datetime as dt
import os
HOME = os.getenv('HOME')
here = os.path.dirname(os.path.realpath(__file__))
import logging
LG = logging.getLogger(__name__)


def parse_csv(fname):
   """
     This function returns arrays for the properties in the following order:
   date, temperature, wind, wind-dir, burst, burst-dir, Precip, Press, 
                                                          Press-tend, Humidity
   """
   LG.info('Loading file: %s'%(fname))
   directions = {'Calma':float('nan'), '':float('nan'),
                 'Norte':0.0, 'Nordeste':45.0,
                 'Este':90.0, 'Sudeste':135.0, 'Sur':180.0, 'Sudoeste':225.0,
                 'Oeste':270.0, 'Noroeste':315.0}

   ## Read floats
   T,W,B,P,Pr,Prt,H = np.genfromtxt(fname, usecols=(1,2,4,6,7,8,9),
                                                    delimiter=',',unpack=True)
   ## Read Strings/dates
   D,Wd,Bd = np.genfromtxt(fname, usecols=(0,3,5), dtype=bytes,
                                                    delimiter=',',unpack=True)
   # Clean dates
   D = [dt.datetime.strptime(str(x,'utf-8'),'%d/%m/%Y %H:%M') for x in D]
   D = np.array(D)
   
   # Clean wind/burst
   aux = []
   for x in Wd:
      try: aux.append( directions[str(x,'utf-8')] )  # to allow new and
      except: aux.append( float(str(x,'utf-8')) )    # previously corrected data
   Wd = np.array(aux)
   aux = []
   for x in Bd:
      try: aux.append( directions[str(x,'utf-8')] )  # to allow new and
      except: aux.append( float(str(x,'utf-8')) )    # previously corrected data
   Bd = np.array(aux)
   if T.shape == W.shape == B.shape == P.shape == Pr.shape == Prt.shape ==\
      H.shape == D.shape == Wd.shape == Bd.shape:
      LG.debug('loaded %s data'%(T.shape[0]))
   else: LG.warning('Different length in data.')
   return D,T,W,Wd,B,Bd,P,Pr,Prt,H 



if __name__ == '__main__':
   import logging
   import log_help
   logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)s:%(levelname)s - %(message)s',
                    datefmt='%Y/%m/%d-%H:%M:%S',
                    filename=HOME+'/FORE.log', filemode='w')
   LG = logging.getLogger('main')
   log_help.screen_handler(LG)
   now = dt.datetime.now()

   import sys
   try:
      folder = sys.argv[1]
   except IndexError:
      folder = HOME+'/Documents/WeatherData/' + now.strftime('%Y_%m')
   LG.info('Destination folder: %s'%(folder))

   #print(folder)
   fmt = '%d/%m/%Y %H:%M'
   tmp = '/tmp/weather.csv'
   s = ','

   files = os.popen('ls %s/*.csv'%(folder)).read()
   files = files.splitlines()
   #files = ['/home/ngarcia/Documents/WeatherData/2017_10/0061X.csv']
   LG.debug('%s files to be processed'%(len(files)))

   for fname in files:
      ## Simple sort and uniq to minimize the later operations
      com = 'sort %s | uniq | tac > %s'%(fname,tmp)
      os.system(com)
      LG.info('Processing file: .../%s'%('/'.join(fname.split('/')[-2:])))
   
   
      ## Parse temporary file
      D,T,W,Wd,B,Bd,P,Pr,Prt,H = parse_csv(tmp)
      D_uniq = np.flipud( np.unique(D) )
      LG.debug('%s data to be reduced to %s'%(D.shape[0],D_uniq.shape[0]))
   
   
      ## Clean repeated/substitute data
      #print('Correcting:',fname,' (%s)'%(D_uniq.shape[0]))
      f = open(fname,'w')
      for i in range(D_uniq.shape[0]):
         ind = D_uniq[i]
         mask = D==ind
         d = D[mask][0]
         t = np.nanmean(T[mask])
         w = np.nanmean(W[mask])
         wd = np.nanmean(Wd[mask])
         b = np.nanmean(B[mask])
         bd = np.nanmean(Bd[mask])
         p = np.nanmean(P[mask])
         pr = np.nanmean(Pr[mask])
         prt = np.nanmean(Prt[mask])
         h = np.nanmean(H[mask])
         l = d.strftime(fmt)+s+str(t)+s+str(w)+s+str(wd)+s+str(b)+s+str(bd)
         l += s+str(p)+s+str(pr)+s+str(prt)+s+str(h)
         f.write(l+'\n')
         #print(i,d,t,w,wd,b,bd,p,pr,prt,h)
         #print(l)
      f.close()
      os.system("sed -i 's/nan//g' %s"%(fname))   # test to remove nan
      #print('')
