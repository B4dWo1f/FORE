#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from math import sin, cos, atan2, sqrt, radians,floor
from shapely.geometry import Point

class GPSpoint(object):
   def __init__(self,lat,lon,dodms=False):
      """
        This class can receive the lat,lon information in 2 ways:
          - 2 float/integer numbers. Ex: (41.8, -8.1)
          - 2 tuples containing (degrees,minutes,seconds,direction)
                [degrees]: integer         [seconds]: float
                [minutes]: integer         [direction]: str
                Ex: [(41,51,44.8,'N'), (8,6,23.8,'W')]
      """
      try: LA,LO = tuple(map(float,[lat,lon]))
      except TypeError:
         if isinstance(lat[-1],str) and isinstance(lon[-1],str):
            LA,LO = dmsd2dd(*lat), dmsd2dd(*lon)
         else:
            LA,LO = dms2dd(*lat), dms2dd(*lon)
      self.lat = LA
      self.lon = LO
      self.gps = (LA,LO)
      self.dd = self.gps
      if dodms: self.to_dms()
   def to_dms(self): self.dms = (dd2dms(self.lat),dd2dms(self.lon))
   def in_region(self,region):
      """ region must be a shapely.geometry.Polygon """
      return region.contains(Point(self.lon,self.lat))
   def __sub__(self,other):
      """ Calculates the distance between 2 GPS points """
      return GPSdistance(self.gps[::-1],other.gps[::-1])
   def __str__(self):
      return 'GPS point (lat,lon): (%s,%s)'%(self.lat,self.lon)



def dms2dd(deg,minu,sec):
   """ Converts degree (with sign), minute, second to decimal """
   s = deg/abs(deg)
   return s*(abs(deg) + minu/60. + sec/3600.)

def dmsd2dd(deg,minu,sec,d):
   """ Same as deg2dec including direction {'N','E','S','W'} """
   NSEW = {'E':1, 'N':1, 'S':-1, 'W':-1}   # North-East-South-West sign
   value = dms2dd(deg,minu,sec)
   sign = NSEW[d]
   return sign * value

def dd2dms(dd):   #XXX  check
   """ Returns the defrees,minute,second (with sign) """
   deg = int(dd)
   mi = int((dd-deg)*60)
   sec = ((dd-deg)*60) - mi
   return deg,mi,sec


def GPSdistance(start, end, R0=6371):
   """
    Calculate distance (in kilometers) between two points given as
    (long, latt) pairs based on Haversine formula:
          http://en.wikipedia.org/wiki/Haversine_formula
    R0 = 6371km is the radious of the earth
   """
   ## Degrees to Radians
   start_long = radians(start[0])  # Start point
   start_latt = radians(start[1])  #
   end_long = radians(end[0])  # End point
   end_latt = radians(end[1])  #
   d_long = end_long - start_long
   d_latt = end_latt - start_latt
   a = sin(d_latt/2)**2 + cos(start_latt) * cos(end_latt) * sin(d_long/2)**2
   c = 2 * atan2(sqrt(a), sqrt(1-a))
   return R0 * c


def get_border(fname,ret_poly=True):
   """
     Returns either the border points of the interest region or the polygon
     containing the interest region
   """
   Xb,Yb = np.loadtxt(fname,unpack=True)
   if Xb[0] != Xb[-1]:
      Xb = np.append(Xb,Xb[0])
      Yb = np.append(Yb,Yb[0])
   points = [(x,y) for x,y in zip(Xb,Yb)]
   if ret_poly: 
      from shapely.geometry.polygon import Polygon
      return Polygon(points)
   else: return points


if __name__ == '__main__':
   ## For testing porpouses
   P = GPSpoint(41.556776, -8.401534)
   Q = GPSpoint(40.639432, -8.647119)
   print(P)
   print(Q)
   print(P-Q)
