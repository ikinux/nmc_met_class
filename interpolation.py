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
from scipy import interpolate

#已知一个网格数据，和一个目标网格，将原网格数据插值到目标网格。
#True时表示插值后level,time，dtime，member等信息要用原来的,否则用grid里面的
'''
示例：（测试阶段使用，正式上线需删除）问题是这样的，假设我们有个数据da0  
它的经纬度范围是70-140E 0-60N，分辨率是1*1。时间是2018050108，时效是0，层次是850，
现在将它插值到一个经纬度范围为80-130,  10-50间隔为0.5*0.5，时间，时效，层次时效都为9999的一个网格中，
reserve_other_dim = false时，你想想返回的结果是什么样的
'''
def linear_xy(da0, grid, reserve_other_dim=False):
    # 使用grid的信息
    dat = da0.values
    df = da0.to_dataframe(name="")
    gf = grid.to_dataframe(name="")
    # 分别获取纬度信息
    dslat = float(df.index.get_level_values(4)[0])
    dslat2 = float(df.index.get_level_values(4)[1])
    delat = float(df.index.get_level_values(4)[-1])
    ddlat = dslat2 - dslat
    dnlat = (delat - dslat) / ddlat + 1
    gslat = float(gf.index.get_level_values(4)[0])
    gslat2 = float(gf.index.get_level_values(4)[1])
    gelat = float(gf.index.get_level_values(4)[-1])
    gdlat = gslat2 - gslat
    gnlat = (gelat - gslat) / gdlat + 1
    # 分别获取经度信息
    dslon = float(df.index.get_level_values(5)[0])
    dslon2 = float(df.index.get_level_values(5)[1])
    delon = float(df.index.get_level_values(5)[-1])
    dlon = dslon2 - dslon
    dnlon = (delon - dslon) / dlon + 1
    gslon = float(gf.index.get_level_values(5)[0])
    gslon2 = float(gf.index.get_level_values(5)[1])
    gelon = float(gf.index.get_level_values(5)[-1])
    gdlon = gslon2 - gslon
    gnlon = (gelon - gslon) / dlon + 1
    # 先按照纬度拆分,获取到插值网格对应的点
    nlon_num = (gelon - gslon) / gdlon + 1
    new_start_lat = gslat * nlon_num
    new_end_lat = (gelat + 1) * nlon_num - 1
    data = dat[new_start_lat:new_end_lat]
    # 纬度拆分完毕，对经度进行拆分,算出插值前的原始数据
    data1 = data.reshape(nlon_num, gelat - gslat)
    data2 = data1[gslon - dslon:delon - gelon + 1:1, :]
    # 进行二维线性插值
    tox = np.linspace(0, data2.shape[0] - 1, data2.shape[0])
    toy = np.linspace(0, data2.shape[1] - 1, data2.shape[1])
    x, y = np.meshgrid(tox, toy)
    newfunc = interpolate.interp2d(x, y, data2, kind='cubic')
    nglon_num = int((gelon - gslon) / gdlon + 1)
    xnew = np.linspace(0, data2.shape[0] - 1, nglon_num)  # x
    nglat_num = int((gelat - gslat) / gdlat + 1)
    ynew = np.linspace(0, data2.shape[0] - 1, nglat_num)  # y
    dat = newfunc(xnew, ynew)
    if reserve_other_dim is None:
        nmember = grid.index.get_level_values(0)
        levels = grid.index.get_level_values(1)
        times = grid.index.get_level_values(2)
        dts = grid.index.get_level_values(3)
        lat = grid.index.get_level_values(4)
        lon = grid.index.get_level_values(5)
        da = xr.DataArray(dat, coords={'member': nmember, 'level': levels, 'time': times, 'dt': dts,
                                       'lat': lat, 'lon': lon},
                          dims=['member', 'level', 'time', 'dt', 'lat', 'lon'])
    else:
        nmember = dat.index.get_level_values(0)
        levels = dat.index.get_level_values(1)
        times = dat.index.get_level_values(2)
        dts = dat.index.get_level_values(3)
        lat = dat.index.get_level_values(4)
        lon = dat.index.get_level_values(5)
        da = xr.DataArray(dat, coords={'member': nmember, 'level': levels, 'time': times, 'dt': dts,
                                       'lat': lat, 'lon': lon},
                          dims=['member', 'level', 'time', 'dt', 'lat', 'lon'])
    return da