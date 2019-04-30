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
    dat0 = da0.values
    dat = np.squeeze(dat0)
    df = da0.to_dataframe(name="")
    gslon = grid.slon
    gdlon = grid.dlon
    gslat = grid.slat
    gdlat = grid.dlat
    gelon = grid.elon
    gelat = grid.elat
    gnlon = grid.nlon
    gnlat = grid.nlat
    # 通过起始经纬度和格距计算经纬度格点数
    lon = np.arange(gnlon) * gdlon + gslon
    lat = np.arange(gnlat) * gdlat + gslat
    dslon = float(df.index.get_level_values(5)[0])
    delon = float(df.index.get_level_values(5)[-1])
    # 先按照纬度拆分,获取到插值网格对应的点
    nlon_num = (gelon - gslon) / gdlon + 1
    new_start_lat = gslat * nlon_num
    new_end_lat = (gelat + 1) * nlon_num - 1
    data = dat[new_start_lat:new_end_lat]
    # 纬度拆分完毕，对经度进行拆分,算出插值前的原始数据
    data1 = data.reshape(gelat - gslat,nlon_num)
    data2 = data1[:,gslon - dslon:delon - gelon + 1:1]
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
    #使用grid的信息
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
        data = dat.reshape(nmember,nlevels,ntime,ndt,dat.shape[0],dat.shape[1])
        da = xr.DataArray(data, coords={'member': nmember, 'level': levels, 'time': times, 'dt': dts,
                                       'lat': lat, 'lon': lon},
                          dims=['member', 'level', 'time', 'dt', 'lat', 'lon'])

    else:
        nmember = int(len(da0.coords.variables.get(da0.coords.dims[0])))
        nlevel = int(len(da0.coords.variables.get(da0.coords.dims[1])))
        ntime = int(len(da0.coords.variables.get(da0.coords.dims[2])))
        ndt = int(len(da0.coords.variables.get(da0.coords.dims[3])))
        data = dat.reshape(nmember, nlevel, ntime, ndt, dat.shape[0], dat.shape[1])
        nmember = dat.index.get_level_values(0)
        levels = dat.index.get_level_values(1)
        times = dat.index.get_level_values(2)
        dts = dat.index.get_level_values(3)
        da = xr.DataArray(data, coords={'member': nmember, 'level': levels, 'time': times, 'dt': dts,
                                       'lat': lat, 'lon': lon},
                          dims=['member', 'level', 'time', 'dt', 'lat', 'lon'])
    return da