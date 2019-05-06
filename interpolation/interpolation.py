#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-
import numpy as np
import os
import nmc_met.api.DataBlock_pb2 as DataBlock_pb2
import nmc_met.api.GDS_data_service as GDS_data_service
import lch.nmc_met_class.basicdatas as ts
import struct
import math
import xarray as xr
import pandas as pd
import datetime
from scipy import interpolate
import time

#已知一个网格数据，和一个目标网格，将原网格数据插值到目标网格。
#True时表示插值后level,time，dtime，member等信息要用原来的,否则用grid里面的
'''
示例：（测试阶段使用，正式上线需删除）问题是这样的，假设我们有个数据da0  
它的经纬度范围是70-140E 0-60N，分辨率是1*1。时间是2018050108，时效是0，层次是850，
现在将它插值到一个经纬度范围为80-130,  10-50间隔为0.5*0.5，时间，时效，层次时效都为9999的一个网格中，
reserve_other_dim = false时，你想想返回的结果是什么样的
'''


def linear_xy(da0, grid, reserve_other_dim=False):
    dat0 = da0.values
    # 六维转换为二维的值
    dat = np.squeeze(dat0)
    df = da0.to_dataframe(name="")
    dslat = float(df.index.get_level_values(4)[0])
    dslat2 = float(df.index.get_level_values(4)[int(dat.shape[1]) + 1])
    delat = float(df.index.get_level_values(4)[-1])
    ddlat = dslat2 - dslat
    dnlat = (delat - dslat) / ddlat + 1
    dslon = float(df.index.get_level_values(5)[0])
    dslon2 = float(df.index.get_level_values(5)[1])
    delon = float(df.index.get_level_values(5)[-1])
    ddlon = dslon2 - dslon
    dnlon = (delon - dslon) / ddlon + 1
    gslon = grid.slon
    gdlon = grid.dlon
    gslat = grid.slat
    gdlat = grid.dlat
    gelon = grid.elon
    gelat = grid.elat
    gnlon = grid.nlon
    gnlat = grid.nlat
    lat = np.arange(gslat, gelat + gdlat, gdlat)
    lon = np.arange(gslon, gelon + gdlon, gdlon)
    if (da0 is None):
        return None
    if (dslon * ddlon >= 360):
        grd1 = ts.grid_data(ts.grid([dslon, delon, ddlon], [dslat, delat, ddlat]))
        grd2 = np.squeeze(grd1)
        grd2[:, 0:-1] = dat[:, :]
        grd2[:, dnlon] = dat[:, 0]
    # 对插值范围进行判定
    if (gelon > delon or gslon < dslon or gelat > delat or gslat < dslat):
        print("object grid is out range of original grid")
        return
    x = ((np.arange(gnlon) * gdlon + gslon - dslon) / ddlon)  # 经度
    ig = x[:].astype(dtype='int16')  # 整数部分
    dx = x - ig  # 小数部分
    y = (np.arange(gnlat) * gdlat + gslat - dslat) / ddlat  # 纬度
    jg = y[:].astype(dtype='int16')  # 整数部分
    dy = y[:] - jg  # 小数部分
    ii, jj = np.meshgrid(ig, jg)  # 整数部分网格
    ii1 = np.minimum(ii + 1, dnlon - 1)
    jj1 = np.minimum(jj + 1, dnlat - 1)
    ii2 = ii1.astype(dtype='int16')
    jj2 = jj1.astype(dtype='int16')
    ddx, ddy = np.meshgrid(dx, dy)  # 小数部分网格
    c00 = (1 - ddx) * (1 - ddy)
    c01 = ddx * (1 - ddy)
    c10 = (1 - ddx) * ddy
    c11 = ddx * ddy
    # 一行代码进行循环计算
    datt = (c00 * dat[jj, ii] + c10 * dat[jj2, ii] + c01 * dat[jj, ii2] + c11 * dat[jj2, ii2])
    # 最终的结果需要转换为一个六维的数组。
    if reserve_other_dim is False:
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
        data = datt.reshape(nmember, nlevels, ntime, ndt, datt.shape[0], datt.shape[1])
        da = xr.DataArray(data, coords={'member': nmember, 'level': levels, 'time': times, 'dt': dts,
                                        'lat': lat, 'lon': lon},
                          dims=['nmember', 'levels', 'times', 'dts', 'lat', 'lon'])

    else:
        nmember = int(len(da0.coords.variables.get(da0.coords.dims[0])))
        nlevel = int(len(da0.coords.variables.get(da0.coords.dims[1])))
        ntime = int(len(da0.coords.variables.get(da0.coords.dims[2])))
        ndt = int(len(da0.coords.variables.get(da0.coords.dims[3])))
        data = datt.reshape(nmember, nlevel, ntime, ndt, datt.shape[0], datt.shape[1])
        nmember = datt.index.get_level_values(0)
        levels = datt.index.get_level_values(1)
        times = datt.index.get_level_values(2)
        dts = datt.index.get_level_values(3)
        da = xr.DataArray(data, coords={'member': nmember, 'level': levels, 'time': times, 'dt': dts,
                                        'lat': lat, 'lon': lon},
                          dims=['nmember', 'levels', 'times', 'dts', 'lat', 'lon'])
    return da