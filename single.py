#!/usr/bin/python3
# -*- coding: UTF-8 -*-

"""
 prepare data for a single station to anticipate the nan's
"""

from process import parse_csv

fname = '/home/ngarcia/Documents/WeatherData/2017_09/5906X.csv'

D,T,W,Wd,B,Bd,P,Pr,Prt,H = parse_csv(fname)

n = 48
f = open('datos.dat','w')
for i in range(T.shape[0]-n):
   if T[i] != T[i]: continue
   ts = [T[j] for j in range(i+1,i+n+1)]
   for l in ts:
      f.write(str(l)+'   ')
   f.write(str(T[i])+'\n')
f.close()
