#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
here = os.path.dirname(os.path.realpath(__file__))
import IO
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
try: plt.style.use('mystyle')
except: pass
from matplotlib import gridspec
import matplotlib.dates as mdates


def dew_point(T,RH):
   """
   Calculates the dew point from the temperature (T) and the relative
   humidity (RH)
   Temperature is assumed in Celsius
   """
   TD = 243.04*(np.log(RH/100)+((17.625*T)/(243.04+T)))/(17.625-np.log(RH/100)-((17.625*T)/(243.04+T)))
   return TD


def plot(folder, code, start_date, end_date, stations=f'{here}/stations.csv',
                                             fig=None):
   """
   Plot any data from the station `code` between `start_date` and `end_date`
   """
   all_stations = pd.read_csv(stations)
   station_info = all_stations[all_stations['code'] == code]
   name = station_info['muni'].values[0]
   altitude = station_info['alt'].values[0]
   latitude  = round(station_info['lat'].values[0], 2)
   longitude = round(station_info['lon'].values[0], 2)
   title = f"{name}\n({latitude},{longitude}), {altitude}m"
   
   # df = IO.read_csv(f'{folder}/{station}')
   df = IO.read_by_date(code,start_date,end_date,folder)
   

   # Extract properties     XXX probably inefficient?
   X = df.index.values
   T = df['temperature'].values
   RH = df['humidity'].values
   DwP = dew_point(T,RH)   # derived
   wind = df['wind'].values
   winddir = np.radians(df[f'wind dir'].values)
   gust = df['gust'].values
   gustdir = np.radians(df[f'gust dir'].values)
   rain = df['precipitation'].values
   P = df['pressure'].values
   Pt = df['pressure trend'].values

   
   if fig == None: fig = plt.figure(figsize=(8, 16))
   gs = gridspec.GridSpec(5, 1, height_ratios=[1,1,.5,.5,.5], hspace=0.)
   fig.subplots_adjust() #wspace=0.1,hspace=0.1)
   ax0 = plt.subplot(gs[0,0])
   ax1 = plt.subplot(gs[1,0], sharex=ax0)
   ax2 = plt.subplot(gs[2,0], sharex=ax0)
   ax3 = plt.subplot(gs[3,0], sharex=ax0)
   ax4 = plt.subplot(gs[4,0], sharex=ax0)
   axs = [ax0,ax1,ax2,ax3,ax4]
   
   # Title
   ax0.set_title(title)
   
   # Temperature
   ax0.plot(X, T, 'C3o-', label='temperature')
   ax0.plot(X, DwP, 'C0o-', label='dewpoint')
   ax0.legend()
   ax0.set_ylabel('T (°C)')
   
   # Wind
   ax1.plot(X,wind, 'o-', label='wind')
   ax1.barbs(X,wind,-wind*np.sin(winddir),-gust*np.cos(winddir), pivot='middle')
   ax1.plot(X,gust, 'o-', label='gust')
   ax1.barbs(X,gust,-gust*np.sin(gustdir),-gust*np.cos(gustdir), pivot='middle')
   # ax1.set_ylim(bottom=0)
   ax1.legend()
   ax1.set_ylabel('Wind (km/h)')
   
   # precipitation
   ax2.plot(X,rain, 'o-', label='precipitation')
   ax2.set_ylim(bottom=0)
   ax2.legend()
   ax2.set_ylabel('rain (mm)')
   
   # Humid
   ax3.plot(X,RH, 'o-', label='humidity')
   ax3.set_ylim(0,100)
   ax3.legend()
   ax3.set_ylabel('H (%)')
   
   # Pressure
   ax4.plot(X,P, 'o-', label='Pressure')
   ax4_2 = ax4.twinx()
   ax4_2.plot(X,Pt,'C1o-', label='Pres. Tend.')
   ax4_2.tick_params(axis='y', labelcolor='C1')
   ax4.set_ylabel('P (hPa)')
   ax4.legend()
   ax4_2.legend()
   
   # General settings
   fig.autofmt_xdate()
   axs[-1].fmt_xdata = mdates.DateFormatter('%d/%m-%H:%M')
   axs[-1].tick_params(axis='x', rotation=15)
   axs[-1].set_xlim(left=start_date, right=end_date)
   for ax in axs[:-1]:
      ax.spines['bottom'].set_linewidth(2)
   
   fig.tight_layout()
   plt.show()


if __name__ == '__main__':
   folder = '~/Documents/WeatherData'
   end_date = dt.datetime.utcnow()
   start_date = end_date - dt.timedelta(hours=24)

   from random import choice
   Xstation = choice(os.popen(f'ls ~/Documents/WeatherData/2023/04').read().strip().split())
   #station = 'C929I.csv'
   code = Xstation.replace('.csv','')
   print('Doing',code)

   plot(folder,code,start_date,end_date)
