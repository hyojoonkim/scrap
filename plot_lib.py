#################################################
# Copyright 2014 Hyojoon Kim
# All Rights Reserved 
# 
# email: deepwater82@gmail.com
#################################################

import operator
import string
import pickle
import sys
import re
import time
import os
import sqlite3 as db
import shlex, subprocess
import hashlib
import xml.etree.ElementTree as ET
from multiprocessing import Process
from multiprocessing import Pool
from collections import namedtuple
from datetime import datetime
import tarfile
import matplotlib as mpl
mpl.use('PS')
#mpl.use('pdf')
#mpl.use('AGG')
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from numpy.random import normal
import numpy as np
from optparse import OptionParser
from matplotlib.patches import ConnectionPatch
import struct
from socket import *


mpl.rc('text', usetex=True)
mpl.rc('font', **{'family':'serif', 'sans-serif': ['Times'], 'size': 9})
mpl.rc('figure', figsize=(3.33, 2.06))
mpl.rc('axes', linewidth=0.5)
mpl.rc('patch', linewidth=0.5)
mpl.rc('lines', linewidth=0.5)
mpl.rc('grid', linewidth=0.25)



def plot_distribution(x_ax, y_map, output_dir, filename, title):
    fig = plt.figure(dpi=700)
    ax = fig.add_subplot(111)
    colors = ['r-+','k-*','g-^','c-h','r-.']
    pl = []
    #  ax.set_yscale('log')
  #    ax.xaxis.grid(True, which='major')
    ax.yaxis.grid(True, which='major')
  
    nflows_median = []
    nflows_maxerr = []
    nflows_minerr = []
    instances_list = y_map.keys()
    nflows_len = len(y_map[instances_list[0]])

    for i in range(nflows_len):
        this_flow_list = []
        for idx2,y in enumerate(y_map):
            this_flow_list.append(y_map[y][i])
        nflows_median.append(np.median(this_flow_list))
        nflows_maxerr.append(np.max(this_flow_list) - np.median(this_flow_list))
        nflows_minerr.append(np.median(this_flow_list) - np.min(this_flow_list))

    pl.append(plt.errorbar(x_ax, nflows_median, yerr=[nflows_minerr, nflows_maxerr], fmt='r-o',markersize=1.5))

  
    ff = plt.gcf()
    ff.subplots_adjust(bottom=0.20)
    ff.subplots_adjust(left=0.15)
    plt.title(title)
    plt.xlabel('Number of flows')
    plt.ylabel('Delay (seconds)', rotation=90)
    
    plt.savefig(output_dir + str(filename), dpi=700)


def plot_multiline_diff(xa_list, ya_list, output_dir, filename, title, xlabel, ylabel,xlim,ylim, markersize):

  fig = plt.figure(dpi=700)
  ax = fig.add_subplot(111)
#  colors = ['r-+','k-*','g-^','c-h','r-.']
  colors = ['r:','k--','g-','c:','r...']
  pl = []
#  ax.set_xscale('log')
#    ax.xaxis.grid(True, which='major')
  ax.yaxis.grid(True, which='major')

  #  ind = np.arange(len(ya))
  idx = 0
  for x,y, in zip(xa_list,ya_list):
    cidx = idx%len(colors)
    pl.append( plt.plot(x, y, '%s' %(colors[cidx]), label="",markersize=markersize,linewidth=0.7,) )
    idx = idx+1

  
  # xlabels = ['0', '10', '20', '30', '40', '50', '60']
  #  majorind = np.arange(len(ya),step=99)
  #  plt.xticks(majorind,xlabels)
 
  plt.xlim(xlim[0],xlim[1])
  plt.ylim(ylim[0],ylim[1])

  ff = plt.gcf()
  ff.subplots_adjust(bottom=0.20)
  ff.subplots_adjust(left=0.15)
  plt.title(title)
  plt.xlabel(xlabel)
  plt.ylabel(ylabel, rotation=90)

  l = plt.legend([pl[0][0],pl[1][0],pl[2][0]], ['Maintenance','Outage','Total'], bbox_to_anchor=(0.5, 1.15), loc='upper center',ncol=3, fancybox=True, shadow=False, prop={'size':7.0})    
  

  plt.savefig(output_dir + str(filename), dpi=700)


def plot_multiline(x_ax, y_map, output_dir, filename, title, xlabel, ylabel,xlim,ylim, markersize):

  fig = plt.figure(dpi=700)
  ax = fig.add_subplot(111)
  colors = ['r-+','k-*','g-^','c-h','r-.']
  pl = []
  #  ax.set_yscale('log')
#    ax.xaxis.grid(True, which='major')
  ax.yaxis.grid(True, which='major')

  #  ind = np.arange(len(ya))

  keys = sorted(y_map.keys())

  for idx,y in enumerate(keys):
    y_ax = y_map[y]
    cidx = idx%len(colors)
    pl.append( plt.plot(map(str,x_ax), y_ax, '%s' %(colors[cidx]), label="",markersize=markersize,linewidth=2.0) )
  
  xlabels = ['2008','2009','2010','2011','2012','2013']
#  majorind = np.arange(len(x_ax),step=1)
#  print majorind
  locs, labels = plt.xticks()
  plt.xticks(locs,xlabels)
 
  plt.xlim(xlim[0],xlim[1])
  plt.ylim(ylim[0],ylim[1])

  ff = plt.gcf()
  ff.subplots_adjust(bottom=0.20)
  ff.subplots_adjust(left=0.15)
  plt.title(title)
  plt.xlabel(xlabel)
  plt.ylabel(ylabel, rotation=90)

  l = plt.legend([pl[0][0],pl[1][0],pl[2][0]], ['Maintenance','Outage','Total'], bbox_to_anchor=(0.5, 1.1), loc='upper center',ncol=3, fancybox=True, shadow=False, prop={'size':7.0})    
  
  plt.savefig(output_dir + str(filename), dpi=700)



def get_cdf2(arr):
  '''
      Fn to get CDF of an array
      Input: unsorted array with values
      Output: 2 arrays - x and y axes values
  '''
  sarr = np.sort(arr)
  l = len(sarr)
  x = []
  y = []
  for i in range(0,l):
    x.append(sarr[i])
    y.append(float(i+1)/l)

  return x,y
