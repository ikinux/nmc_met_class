#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-

import xarray as xr
import numpy as np
import pandas as pd
#返回一个DataArray，其维度信息和grid描述一致，数组里面的值为0.
def grid_data(grid):
    slon = grid.slon
    dlon = grid.dlon
    slat = grid.slat
    dlat = grid.dlat
    nlon = grid.nlon
    nlat = grid.nlat
    # 通过起始经纬度和格距计算经纬度格点数
    lon = np.arange(nlon) * dlon + slon
    lat = np.arange(nlat) * dlat + slat
    stime = grid.stime
    etime = grid.etime
    gtime = grid.gtime
    # 通过开始日期，结束日期以及时间间隔来计算times时间序列和ntime序列个数
    times = pd.date_range(stime, etime, freq=gtime[2])
    ntime = len(times)
    # 根据timedelta的格式，算出ngdt次数和gdts时效列表
    edtimedelta = grid.edtimedelta
    sdtimedelta = grid.sdtimedelta
    ddtimedelta = grid.ddtimedelta
    ndt = int((edtimedelta - sdtimedelta) / ddtimedelta)
    gdt_list = []
    for i in range(ndt + 1):
        gdt_list.append(sdtimedelta + ddtimedelta * i)
    gdts = gdt_list
    #取出nmember数和levels层数
    nmember = grid.nmember
    levels = grid.levels
    nlevels = len(levels)
    data = np.zeros((nmember, nlevels, ntime, ndt, nlat, nlon))
    return (xr.DataArray(data, coords={'levels': levels,'times': times,'dhs':gdts,'member': nmember,
                               'lat': lat, 'lon': lon},
                         dims=['member','times', 'dhs', 'levels','lat', 'lon']))

