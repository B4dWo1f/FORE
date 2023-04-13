#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import load
log_level = load.get_log_level()
import IO
import web
import pandas as pd
import datetime as dt
import os
here = os.path.dirname(os.path.realpath(__file__))
HOME = os.getenv('HOME')
is_cron = bool( os.getenv('RUN_BY_CRON') )

#################################################################################
#import logging
#LG = logging.getLogger('main')
#lg_lvls = {'debug':logging.DEBUG, 'info':logging.INFO,
#           'warning':logging.WARNING, 'error':logging.ERROR,
#           'critical':logging.CRITICAL}
#logging.basicConfig(level=lg_lvls[log_level],
#                 format='%(asctime)s %(name)s:%(levelname)s - %(message)s',
#                 datefmt='%Y/%m/%d-%H:%M:%S',
#                 filename=f'{here}/spider.log', filemode='w')
#fmt='%(name)s -%(levelname)s- %(message)s'
#lv = logging.INFO
#sh = logging.StreamHandler()
#sh.setLevel(lv)
#fmt = logging.Formatter(fmt)
#sh.setFormatter(fmt)
#LG.addHandler(sh)
#################################################################################

################################# LOGGING ####################################
import logging
log_name, _ = os.path.splitext(os.path.basename(__file__))
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{log_name}.log')
if is_cron: lv = logging.DEBUG
else: lv = logging.INFO
fmt='%(asctime)s:%(name)s:%(levelname)s: %(message)s'
logging.basicConfig(level=lv, format=fmt, datefmt='%Y/%m/%d-%H:%M:%S',
                              filename = log_file, filemode='w')
LG = logging.getLogger(__name__)
########## Screen Logger (optional) ##########
if not is_cron:                                 #
   sh = logging.StreamHandler()                 #
   sh.setLevel(logging.DEBUG)                    #
   fmt = '%(name)s:%(levelname)s: %(message)s'  #
   fmt = logging.Formatter(fmt)                 #
   sh.setFormatter(fmt)                         #
   LG.addHandler(sh)                            #
##############################################################################
LG.info(f'Starting: {__file__}')


## Config
P = load.setup(f'{here}/config.ini')
folder = P.folder_data
fname_stations = P.stations
IO.ck_folder(folder)
fname = P.stations
fmt = P.fmt

# Get Stations information
LG.info('Updating stations')
stations = web.get_all_stations(P.url_base,write=True)
LG.info(f'Parsing {len(stations)} stations')
stations = web.update_stations(stations, P, fname=fname_stations)
LG.info(f'Parsed stations')


# Download data
LG.info('Downloading data')
for index, row in stations.iterrows():
   LG.debug(f"Doing station: {row['code']}. Updated: {row['date']}")
   RAW_DATA = web.make_request(row['url']).replace('"','').strip()
   if RAW_DATA != None: IO.merge_data(folder,row['code'],RAW_DATA)
LG.info('Done!')
