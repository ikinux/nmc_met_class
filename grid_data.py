#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-
import math
import xarray as xr
import pandas as pd
import numpy as np

#完整网格数据
'''
继承自xarray
约定坐标顺序为: member, times,dhs, level, lat,lon
网格属性可以定义一个 fgrid 结构来存储
添加一个属性grid 来存储网格的范围包括（起始经纬度、格距、起止时间，时间间隔，起止时效，时效间隔，层次列表）
"slon,elon,slat,elat,ladis,stime,etime,tinter,sdhs,edhs,interdhs,leverlist"
grid(glon, glat, gtime = None, gdt = None, dtime_type="hour",levels=None)
'''
class grid:
    def __init__(self):
        'slon,elon,dlon,slat,elat,dlat,stime,dtime, sdt,edt,ddt,dtime_type,levels'
        self.slon = 1
        self.dlon = 1
        self.elon = 1
        self.slat = 1
        self.dlat = 1
        self.elat = 1
        self.stime = 1
        self.dtime = 1
        self.sdt = 1
        self.edt = 1
        self.ddt = 1
        self.dtime_type = 1
        self.levels = 1

    def grid_data_structure(self,grid,member=None,times=None,dhs=None,level=None,lat=None,lon=None):
        return(xr.DataArray(grid, coords={'member': member, 'times': times,'dhs':dhs,'level': level,
                                  'lat': lat, 'lon': lon},
                          dims=['level','time','dhs','member']))