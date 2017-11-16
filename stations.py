#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import numpy as np
import pandas as pd

fname = 'stations.csv'
M = pd.read_csv(fname, delimiter=',',names=['ID','lat','lon','url'])


p0 = np.array([-3,40])

Ps = [np.array([lo,la]) for lo,la in zip(M['lat'],M['lon'])]

Ds = [np.linalg.norm(p-p0) for p in Ps]

inds = np.argsort(Ds)

inds = inds[0:5]

print(M.iloc[inds,:][['ID','url']])
