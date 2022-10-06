#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from configparser import ConfigParser, ExtendedInterpolation
from os.path import expanduser
import os
here = os.path.dirname(os.path.realpath(__file__))
## LOG
import logging
# import log_help
LG = logging.getLogger(__name__)



class params(object):
   def __init__(self,folder_data,stations,fmt,url_root,url_base):
      if folder_data[-1] == '/': self.folder_data = folder_data[:-1]
      else: self.folder_data = folder_data
      if stations[-1] == '/': self.stations = stations[:-1]
      else: self.stations = stations
      self.folder_data = os.path.abspath(self.folder_data)
      self.stations = os.path.abspath(self.stations)
      self.fmt = fmt
      self.url_root = url_root
      self.url_base = url_base
   def __str__(self):
      txt =''
      for k,v in self.__dict__.items():
         txt += f'{k}: {v}\n'
      return txt.strip()

def path_setter(path):
   """
   Returns the full path of a given file/folder according to the following
   criteria:
     - if the provided path is absolute (ie, starts with /), it's left as is
     - Otherwise it is considered a relative path and it would be converted
     to absolute
   """
   LG.debug(f'Getting absolute path for {path}')
   if os.path.isabs(path): pass
   else: path = f'{here}/{path}'
   return path

def setup(fname='config.ini'):
   """
    Parse an ini file returning the parameter classes
    TODO: Log this function
          try/except for format errors
   """
   config = ConfigParser(inline_comment_prefixes='#')
   config._interpolation = ExtendedInterpolation()
   config.read(fname)

   fmt = config['config']['fmt']
   folder_data = expanduser( config['sys']['folder_data'] )
   if folder_data[0] != '/': folder_data = f'{here}/{folder_data}'
   stations = expanduser( config['sys']['stations'] )
   stations = path_setter(stations)
   # if stations[0] != '/': stations = f'{here}/{stations}'
   url_root = config['aemet']['url_root']
   url_base = config['aemet']['url_base']
   return params(folder_data,stations,fmt,url_root,url_base)

def get_log_level(fname='config.ini'):
   """
    Parse just the log level from the config file
    Not elegant but functional
   """
   config = ConfigParser(inline_comment_prefixes='#')
   config._interpolation = ExtendedInterpolation()
   config.read(fname)
   return config['config']['log_level']


if __name__ == '__main__':
   P = setup(fname='config.ini')
   print(P)
