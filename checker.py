#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
 Rough checker to get warnings when spider.py may fail
"""

import os
HOME = os.getenv('HOME')
here = os.path.dirname(os.path.realpath(__file__))

import logging
import log_help
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)s:%(levelname)s - %(message)s',
                    datefmt='%Y/%m/%d-%H:%M:%S',
                    filename=HOME+'/check.log', filemode='w')
LG = logging.getLogger('main')


import datetime as dt
now = dt.datetime.now()

import sys
try: fol = sys.argv[1]
except IndexError: fol = HOME+'/Documents/WeatherData/' + now.strftime('%Y_%m')


mail_lim = 2*24*60*60  #threshold in seconds to send mail
f_mail = here + '/.last_mail'  # file to store date of last mail
fmt = '%d/%m/%Y %H:%M'


day = now.day
max_lines = day * 24  # data should be hourly

error_report = []
for l in os.popen("wc -l %s/*.csv"%(fol)).read().splitlines()[:-1]:
   n,name = l.split()
   n = int(n)
   if n > max_lines + 25: # extra in case of checking while retrieving new data
      short_name = '/'.join(name.split('/')[-2:])
      msg =  'File: .../%s has %s lines '%(short_name,n)
      msg += '(max %s expected)'%(max_lines)
      error_report.append(msg)

if len(error_report) > 0:
   LG.info('Error in %s files'%(len(error_report)))
   body = '\n'.join(error_report)
   subj = 'ERROR in FORE spyder'
   try:
      last_mail = open(f_mail,'r').read().lstrip().rstrip()
      last_mail = dt.datetime.strptime(last_mail,fmt)
   except FileNotFoundError: last_mail = now - dt.timedelta(days=365)

   T0 = (now - last_mail).total_seconds()
   if T0 > mail_lim:
      LG.debug('Last mail sent %s hours ago'%(T0/3600))
      # dependence on my mailator library, which can be found here:
      # https://github.com/B4dWo1f/bin/blob/master/mailator.py
      from mailator import send_mail
      send_mail(body,subj=subj)
      LG.info('New mail sent')
      with open(f_mail,'w') as f:
         f.write(now.strftime(fmt)+'\n')
   else:
      LG.warning('Last mail was sent only %s hours ago'%(T0/3600))
      with open(HOME+'/FORE.err','w') as f:
         f.write('Report done at' +now.strftime('%d/%m/%Y %H:%M')+'\n')
         f.write(body+'\n\n')
         LG.info('Errors reported via file')
else: LG.info('All files are ok')
