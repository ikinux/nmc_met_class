#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-
import numpy as np
import os
import nmc_met.api.DataBlock_pb2 as DataBlock_pb2
import nmc_met.api.GDS_data_service as GDS_data_service
import struct
import math
import xarray as xr
import pandas as pd
import datetime

#已知一个网格数据，和一个目标网格，将原网格数据插值到目标网格。
#True时表示插值后level,time，dtime，member等信息要用原来的,否则用grid里面的
def linear_xy(da0,grid,reserve_other_dim = False):
    if reserve_other_dim == False:
        dat = da0.values
        slon = grid.slon
        dlon = grid.dlon
        slat = grid.slat
        dlat = grid.dlat
        nlon = grid.nlon
        nlat = grid.nlat
        # 通过起始经纬度和格距计算经纬度格点数
        lon = np.arange(nlon) * dlon + slon
        lat = np.arange(nlat) * dlat + slat
        gtime = grid.gtime
        if (gtime != None):
            stime = grid.stime
            etime = grid.etime
            gtime = grid.gtime
            # 通过开始日期，结束日期以及时间间隔来计算times时间序列和ntime序列个数
            times = pd.date_range(stime, etime, freq=gtime[2])
            ntime = len(times)
        else:
            times = 9999
            ntime = 1
        gdt = grid.gdt
        if (gdt != None):
            # 根据timedelta的格式，算出ndt次数和gds时效列表
            edtimedelta = grid.edtimedelta
            sdtimedelta = grid.sdtimedelta
            ddtimedelta = grid.ddtimedelta
            ndt = int((edtimedelta - sdtimedelta) / ddtimedelta)
            gdt_list = []
            for i in range(ndt + 1):
                gdt_list.append(sdtimedelta + ddtimedelta * i)
            dts = gdt_list
        else:
            ndt = 1
            dts = 9999
        levels = grid.levels
        if (levels != None):
            levels = grid.levels
            nlevels = len(levels)
        else:
            nlevels = 1
        # 取出nmember数和levels层数
        nmember = grid.nmember
        da = xr.DataArray(dat, coords={'member': np.arange(nmember), 'level': levels, 'time': times, 'dt': dts,
                                       'lat': lat, 'lon': lon},
                          dims=['member', 'level', 'time', 'dt', 'lat', 'lon'])
    else:
        dat = da0.values
        slon = grid.slon
        dlon = grid.dlon
        slat = grid.slat
        dlat = grid.dlat
        nlon = grid.nlon
        nlat = grid.nlat
        # 通过起始经纬度和格距计算经纬度格点数
        lon = np.arange(nlon) * dlon + slon
        lat = np.arange(nlat) * dlat + slat
        nmember = dat.index.get_level_values(0)
        levels = dat.index.get_level_values(1)
        times = dat.index.get_level_values(2)
        dts = dat.index.get_level_values(3)
        da = xr.DataArray(dat, coords={'member': nmember, 'level': levels, 'time': times, 'dt': dts,
                                       'lat': lat, 'lon': lon},
                          dims=['member', 'level', 'time', 'dt', 'lat', 'lon'])
    return da
