#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-

import xarray as xr
import numpy as np
import pandas as pd
import datetime
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
    # 根据timedelta的格式，算出ndt次数和gds时效列表
    edtimedelta = grid.edtimedelta
    sdtimedelta = grid.sdtimedelta
    ddtimedelta = grid.ddtimedelta
    ndt = int((edtimedelta - sdtimedelta) / ddtimedelta)
    gdt_list = []
    for i in range(ndt + 1):
        gdt_list.append(sdtimedelta + ddtimedelta * i)
    dts = gdt_list
    #取出nmember数和levels层数
    nmember = grid.nmember
    levels = grid.levels
    nlevels = len(levels)
    data = np.zeros((nmember, nlevels, ntime, ndt, nlat, nlon))
    return (xr.DataArray(data, coords={'nmember': np.arange(nmember),'levels': levels,'times': times,'dt':dts,
                               'lat': lat, 'lon': lon},
                         dims=['nmember', 'levels','times', 'dt','lat', 'lon']))
# 根据grid_data 生成 grid的函数,输入一个 DataArray，返回一个grid类数据
def get_grid_of_data(xr01):
    #grid类 glon, glat, gtime=None, gdt=None,gdtime_type=None,levels=None,nmember = 1
    grid = []
    for i in range(len(xr01.coords)):
        if xr01.coords.dims[i] == 'nmember':
            print("存在nmember")
            print(len(xr01.coords.variables.get(xr01.coords.dims[i])))  # 获取nmember维度个数
            nmember = len(xr01.coords.variables.get(xr01.coords.dims[i]))
            grid.append(nmember)
        if xr01.coords.dims[i] == 'levels':
            print("存在levels")
            print(len(xr01.coords.variables.get('levels')))  # 获取levels维度个数
            levels = xr01.coords.variables.get('levels')
            grid.append(levels)
        if xr01.coords.dims[i] == 'times':
            print("存在times")
            nums = len(xr01.coords.variables.get('times'))
            if nums > 1:
                stime1 = str(xr01.coords.variables.get('times')[0])
                stime2 = str(xr01.coords.variables.get('times')[1])
                etime1 = str(xr01.coords.variables.get('times')[-1])
                stime3 = datetime.datetime.strptime(stime2, "%Y-%m-%d:%H:%M:%S")
                stime = datetime.datetime.strptime(stime1, "%Y-%m-%d:%H:%M:%S")
                dtime = stime3 - stime
                etime = datetime.datetime.strptime(etime1, "%Y-%m-%d:%H:%M:%S")
                print(stime, etime, dtime)
                dtime = [stime, etime, dtime]
                grid.append(dtime)
            else:
                dtime = xr01.coords.variables.get('times')
                grid.append(dtime)
        if xr01.coords.dims[i] == 'dt':
            print("存在dt")
            nums = len(xr01.coords.variables.get('dt'))
            if nums > 1:
                sdt1 = str(xr01.coords.variables.get('dt')[0])
                sdt2 = str(xr01.coords.variables.get('dt')[1])
                edt = str(xr01.coords.variables.get('dt')[-1])
                # 时效间隔
                ddt = sdt2 - sdt1
                gdt = [sdt1, edt, ddt]
                grid.append(gdt)
            else:
                gdt = xr01.coords.variables.get('dt')
                grid.append(gdt)
        if xr01.coords.dims[i] == 'lat':
            print("存在lat")
            slat = float(xr01.coords.variables.get('lat')[0])
            slat2 = float(xr01.coords.variables.get('lat')[1])
            elat = float(xr01.coords.variables.get('lat')[-1])
            # lat格距
            dlat = slat2 - slat
            glat = [slat, elat, dlat]
            grid.append(glat)
        if xr01.coords.dims[i] == 'lon':
            print("存在lon")
            slon = float(xr01.coords.variables.get('lon')[0])
            slon2 = float(xr01.coords.variables.get('lon')[1])
            elon = float(xr01.coords.variables.get('lon')[-1])
            # lon格距
            dlon = slon2 - slon
            glon = [slon, elon, dlon]
            grid.append(glon)

    return grid

