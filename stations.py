#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull




fname = 'stations.csv'

M = pd.read_csv(fname, delimiter=',',names=['ID','lat','lon','url'])

X = M['lon'].values
Y = M['lat'].values

Xb,Yb = np.loadtxt('border.gps',unpack=True)
if Xb[0] != Xb[-1]:
   Xb = np.append(Xb,Xb[0])
   Yb = np.append(Yb,Yb[0])
points = [(x,y) for x,y in zip(Xb,Yb)]
from shapely.geometry.polygon import Polygon
region = Polygon(points)


#hull = ConvexHull(points)

#def in_hull(p, hull):
#    """
#      Test if points in `p` are in `hull`
#      `p` should be a `NxK` coordinates of `N` points in `K` dimensions
#      `hull` is either a scipy.spatial.Delaunay object or the `MxK` array of
#      the coordinates of `M` points in `K`dimensions for which Delaunay
#      triangulation will be computed
#    """
#    #if not isinstance(hull,Delaunay): hull = Delaunay(hull)
#    return hull.find_simplex(p)>=0
def in_hull(point, hull, tol=1e-12):
   return all( (np.dot(eq[:-1], point) + eq[-1]<=tol) for eq in hull.equations)


x,y = [],[]
from shapely.geometry import Point
for ix,iy in zip(X,Y):
   if  region.contains(Point(ix,iy)):
      x.append(ix)
      y.append(iy)

import matplotlib.pyplot as plt
fig, ax = plt.subplots()
#ax.scatter(X,Y,c='g',s=100,edgecolors='none')
ax.scatter(x,y,c='r',edgecolors='none')
ax.plot(Xb,Yb,'-')
ax.set_xlim([-10,5])
ax.set_ylim([35,44])
plt.show()




exit()






p0 = np.array([-3.29046,40.3297])
p1 = np.array([3.967,39.1406])

Ps = [np.array([x,y]) for x,y in zip(X,Y)]
Ds = np.array([np.linalg.norm(p-p1) for p in Ps])
Balear_Ds = np.array([np.linalg.norm(p-p1) for p in Ps])

import matplotlib.pyplot as plt
fig, ax = plt.subplots()
l=17
lb = 2.7
x = X[Ds<l]
y = Y[Ds<l]
bd = Balear_Ds[Ds<l]




xx,yy = x[bd>lb],y[bd>lb]
points = [(x,y) for x,y in zip(xx,yy)]

hull = ConvexHull(points)




Vx,Vy = [],[]
for ind in hull.vertices:
   print(points[ind][0],points[ind][1])
   Vx.append(points[ind][0])
   Vy.append(points[ind][1])

Vx.append(points[hull.vertices[0]][0])
Vy.append(points[hull.vertices[0]][1])




ax.scatter(xx,yy)
ax.plot(Vx,Vy)
ax.set_xlim([-10,5])
ax.set_ylim([35,44])
plt.show()

exit()

p0 = np.array([-3,40])

Ps = [np.array([lo,la]) for lo,la in zip(M['lat'],M['lon'])]
Ds = [np.linalg.norm(p-p0) for p in Ps]

inds = np.argsort(Ds)

inds = inds[0:5]

print(M.iloc[inds,:][['ID','url']])
