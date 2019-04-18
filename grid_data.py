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
    def __init__(self,slon,dlon,elon,slat,dlat,elat,stime,dtime,sdt,edt,ddt,dtime_type,level):
        'slon,elon,dlon,slat,elat,dlat,stime,dtime,sdt,edt,ddt,dtime_type,levels'
        self.slon = slon
        self.dlon = dlon
        self.elon = elon
        self.slat = slat
        self.dlat = dlat
        self.elat = elat
        self.stime = stime
        self.dtime = dtime
        self.sdt = sdt
        self.edt = edt
        self.ddt = ddt
        self.dtime_type =dtime_type
        self.levels = level
        nlon = 1 + (elon - slon) / dlon
        error = abs(round(nlon) - nlon)
        if (error > 0.01):
            self.nlon = math.ceil(nlon)
        else:
            self.nlon = int(round(nlon))
        self.elon = self.slon + (nlon - 1) * dlon
        nlat = 1 + (elat - slat) / dlat
        error = abs(round(nlat) - nlat)
        if (error > 0.01):
            self.nlat = math.ceil(nlat)
        else:
            self.nlat = int(round(nlat))
        self.elat = self.slat + (nlat - 1) * dlat

    def grid(self,slon, elon, dlon, slat, elat, dlat):

        return ([slon, elon, dlon], [slat, elat, dlat])

    def grid_data_structure(self,grid):
        return(xr.DataArray(grid, coords={'member': [0], 'times': [0],'dhs':[0],'level': [0],
                                  'lat': [0], 'lon': [0]},
                            dims=['level','time','dhs','member','lat','lon']))