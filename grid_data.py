#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-

import xarray as xr
import numpy as np
import pandas as pd
import datetime
import lch.test_data_struct.data_structure as ts
import re

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
    #取出nmember数和levels层数
    nmember = grid.nmember
    data = np.zeros((nmember, nlevels, ntime, ndt, nlat, nlon))
    return (xr.DataArray(data, coords={'member': np.arange(nmember),'level': levels,'time': times,'dt':dts,
                               'lat': lat, 'lon': lon},
                         dims=['member', 'level','time', 'dt','lat', 'lon']))

# 根据grid_data 生成 grid的函数,输入一个 DataArray，返回一个grid类数据
def get_grid_of_data(xr01):
    glon = []
    glat = []
    gtime = []
    gdt = []
    levels = []
    nmember = 1
    len_nmember = len(xr01.coords.variables.get(xr01.coords.dims[0]))
    len_nlevel = len(xr01.coords.variables.get(xr01.coords.dims[1]))
    len_ntime = len(xr01.coords.variables.get(xr01.coords.dims[2]))
    len_ndt = len(xr01.coords.variables.get(xr01.coords.dims[3]))
    len_nlat = len(xr01.coords.variables.get(xr01.coords.dims[4]))
    len_nlon = len(xr01.coords.variables.get(xr01.coords.dims[5]))
    xf = xr01.to_dataframe(name="")
    count_num = int(len_nmember*len_nlevel*len_ntime*len_ndt*len_nlat*len_nlon)
    for i in range(len(xr01.coords)):
        if xr01.coords.dims[i] == 'member':
            print("存在member")
            print(len(xr01.coords.variables.get(xr01.coords.dims[i])))  # 获取nmember维度个数
            nmember = int(len_nmember)
        if xr01.coords.dims[i] == 'level':
            print("存在level")
            print(len(xr01.coords.variables.get('level')))  # 获取levels维度个数
            levels = xr01.coords.variables.get('level')
            for j in range(len_nlevel):
                num = count_num / len_nlevel
                nlevel = int(xf.index.get_level_values(0)[j*num])
                levels.append(nlevel)
        if xr01.coords.dims[i] == 'time':
            print("存在time")
            if len_ntime > 1:
                stime1 = str(xf.index.get_level_values(2)[0])
                stime2 = str(xf.index.get_level_values(2)[1])
                etime1 = str(xf.index.get_level_values(2)[-1])
                stime3 = datetime.datetime.strptime(stime2, "%Y-%m-%d:%H:%M:%S")
                stime = datetime.datetime.strptime(stime1, "%Y-%m-%d:%H:%M:%S")
                dtime = stime3 - stime
                etime = datetime.datetime.strptime(etime1, "%Y-%m-%d:%H:%M:%S")
                gtime = [stime, etime, dtime]
            else:
                gtime = None
        if xr01.coords.dims[i] == 'dt':
            print("存在dt")
            if len_ndt > 1:
                sdt1 = str(xf.index.get_level_values(3)[0])
                sdt2 = str(xf.index.get_level_values(3)[1])
                edt = str(xf.index.get_level_values(3)[-1])
                # 时效间隔(暂定格式)
                # self.dtimes = re.findall(r"\d+", edt)[0]
                # dtime_type = re.findall(r"\D+", edt)[0]
                ddt = sdt2 - sdt1
                gdt = [sdt1, edt, ddt]
            else:
                gdt = None
        if xr01.coords.dims[i] == 'lat':
            print("存在lat")
            slat = float(xf.index.get_level_values(4)[0])
            slat2 = float(xf.index.get_level_values(4)[1])
            elat = float(xf.index.get_level_values(4)[-1])
            # lat格距
            dlat = slat2 - slat
            glat = [slat, elat, dlat]
        if xr01.coords.dims[i] == 'lon':
            print("存在lon")
            slon = float(xf.index.get_level_values(5)[0])
            slon2 = float(xf.index.get_level_values(5)[1])
            elon = float(xf.index.get_level_values(5)[-1])
            # lon格距
            dlon = slon2 - slon
            glon = [slon, elon, dlon]
    grid01 = ts.grid(glon, glat, gtime, gdt,levels,nmember)
    return grid01

