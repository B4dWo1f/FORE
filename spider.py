#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import load
import IO
import web
import pandas as pd
import datetime as dt
import os
here = os.path.dirname(os.path.realpath(__file__))
HOME = os.getenv('HOME')

#################################################################################
import logging
LG = logging.getLogger('main')
logging.basicConfig(level=logging.INFO,
                 format='%(asctime)s %(name)s:%(levelname)s - %(message)s',
                 datefmt='%Y/%m/%d-%H:%M:%S',
                 filename=f'{here}/spider.log', filemode='w')
fmt='%(name)s -%(levelname)s- %(message)s'
lv = logging.INFO
sh = logging.StreamHandler()
sh.setLevel(lv)
fmt = logging.Formatter(fmt)
sh.setFormatter(fmt)
LG.addHandler(sh)
#################################################################################


## Config
P = load.setup(f'{here}/config.ini')
folder = P.folder_data
IO.ck_folder(folder)
fname = P.stations
fmt = P.fmt


# Stations
# try:
#    stations = pd.read_csv(fname)
#    LG.info(f'{fname} not found')
# except FileNotFoundError:
#    LG.info('Updating stations')
#    stations = web.get_all_stations(P.url_base,write=True)
#    LG.info(f'Parsing {len(stations)} stations')
#    stations = web.update_stations(stations)
LG.info('Updating stations')
stations = web.get_all_stations(P.url_base,write=True)
LG.info(f'Parsing {len(stations)} stations')
stations = web.update_stations(stations, P)



LG.info('Downloading data')
for index, row in stations.iterrows(),total=stations.shape[0]:
   LG.debug(f"Doing station: {row['code']}. Updated: {row['date']}")
   RAW_DATA = web.make_request(row['url']).replace('"','').strip()
   IO.merge_data(folder,row['code'],RAW_DATA)
LG.info('Done!')
