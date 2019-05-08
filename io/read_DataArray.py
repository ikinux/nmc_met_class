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
import lch.nmc_met_class.basicdatatrans as ts
import lch.nmc_met_class.basicdatas as bs

#规范化格点（起始经纬度，间隔经度，格点数）
def grid_ragular(slon,dlon,elon,slat,dlat,elat):
    slon1 = slon
    dlon1 = dlon
    elon1 = elon
    slat1 = slat
    dlat1 = dlat
    elat1 = elat
    nlon = 1 + (elon1 - slon1) / dlon1
    error = abs(round(nlon) - nlon)
    if (error > 0.01):
        nlon1 = math.ceil(nlon)
    else:
        nlon1 = int(round(nlon))
    nlat = 1 + (elat - slat) / dlat
    error = abs(round(nlat) - nlat)
    if (error > 0.01):
        nlat1 = math.ceil(nlat)
    else:
        nlat1 = int(round(nlat))
    return slon1,dlon1,elon1,slat1,dlat1,elat1,nlon1,nlat1

def read_from_micaps4(filename,grid=None):
    try:
        if not os.path.exists(filename):
            print(filename + " is not exist")
            return None
        try:
            file = open(filename,'r')
            str1 = file.read()
            file.close()
        except:
            file = open(filename,'r',encoding='utf-8')
            str1 = file.read()
            file.close()
        strs = str1.split()
        year1 = int(strs[3])
        month = int(strs[4])
        day = int(strs[5])
        hour = int(strs[6])
        dts = str(strs[7])
        levels = float(strs[8])
        y = str(datetime.datetime.now().year)
        year2 = int(y[2:])
        #由于m4只提供年份的后两位，因此，做了个暂时的换算范围在1920-2019年的范围可以匹配成功
        if len(str(year1)) ==4:
            year3 = year1
        else:
            if year2 - year1 >= 0:
                year3 = '20' + str(year1)
            else:
                year3 = '19' + str(year1)
        ymd = year3 + str(month) + str(day) + str(hour) + '0000'
        dlon = float(strs[9])
        dlat = float(strs[10])
        slon = float(strs[11])
        elon = float(strs[12])
        slat = float(strs[13])
        elat = float(strs[14])
        slon1, dlon1, elon1, slat1, dlat1, elat1, nlon1, nlat1 = grid_ragular(slon,dlon,elon,slat,dlat,elat)
        if len(strs) - 22 >= nlon1 * nlat1 :
            #用户没有输入参数信息的时候，使用m4文件自带的信息
            k = 22
            dat = (np.array(strs[k:])).astype(float).reshape((1, 1, 1, 1, nlat1, nlon1))
            lon = np.arange(nlon1) * dlon1 + slon1
            lat = np.arange(nlat1) * dlat1 + slat1
            times = pd.date_range(ymd, periods=1)
            da = xr.DataArray(dat, coords={'member': [1], 'level': levels, 'time': times, 'dt': dts,
                                           'lat': lat, 'lon': lon},
                              dims=['member', 'level', 'time', 'dt', 'lat', 'lon'])
            if grid is None:
                return da
            else:
                da1 = ts.interpolation.linear_xy(da, grid)
                return da1
        else:
            return None
    except:
        print(filename + "'s format is wrong")
        return None

def create_micaps4(micaps_abspath,grid_data):

    """
    输出micaps4格式文件
    :param micaps_abspath:生成文件绝对路径
    :param grid_data:网格数据
    """
    grid = bs.get_grid_of_data(grid_data)
    nlon = grid.nlon
    nlat = grid.nlat
    slon = grid.slon
    slat = grid.slat
    elon = grid.elon
    elat = grid.elat
    dlon = grid.dlon
    dlat = grid.dlat
    stime = grid.stime
    year = stime[0:4]
    month = stime[5:6]
    day = stime[7:8]
    hour = stime[9:10]
    hour_range =grid.sdtimedelta
    values = grid_data.values
    grid_values = np.squeeze(values)
    max_value = math.ceil(max(grid_values.flatten()))
    min_value = math.ceil(min(grid_values.flatten()))
    max_value = str(max_value)
    min_value = str(min_value)

    #第一行标题
    title0 = 'diamond 4 %s\n' %stime
    #第二行标题
    title1 = '%s %s %s %s %s 999 %s %s %s %s %s %s %d %d 4 %s %s 2 0.00' \
             % (year, month, day, hour, hour_range,
                dlon, dlat,
                slon, elon, slat,
                elat, nlon, nlat,max_value,min_value)
    title = title0 + title1
    #二维数组写入micaps文件
    np.savetxt(micaps_abspath, grid_values, delimiter='  ',
               fmt='%4.6f', header=title,comments='')
    print('Create [%s] success'%micaps_abspath)

def read_from_nc(filename,member = None,level = None,time = None,dt = None,lat = None,lon = None):
    ds0 = xr.open_dataset(filename)
    drop_list = []
    ds = xr.Dataset()
    #1判断要素成员member
    if(member is None):
        member = "ensemble"
    if member in list(ds0.coords) or member in list(ds0):
        if member in ds0.coords:
            members = ds0.coords[member]
        else:
            members = ds0[member]
            drop_list.append(member)
        ds.coords["member"] = ("member", members)
        attrs_name = list(members.attrs)
        for key in attrs_name:
            ds.member.attrs[key] = members.attrs[key]
    else:
        ds.coords["member"] = ("member", [0])

    #2判断层次level
    if (level is None):
        if "level" in list(ds0.coords) or "level" in list(ds0):
            level = "level"
        elif "lev" in ds0.coords or "lev" in list(ds0):
            level = "lev"
    if level in ds0.coords or level in list(ds0):
        if level in ds0.coords:
            levels = ds0.coords[level]
        else:
            levels = ds0[level]
            drop_list.append(level)
        ds.coords["level"] = ("level", levels)
        attrs_name = list(levels.attrs)
        for key in attrs_name:
            ds.level.attrs[key] = levels.attrs[key]
    else:
        ds.coords["level"] = ("level", [0])

    # 3判断时间time
    if(time is None):
        if "time" in ds0.coords or "time" in list(ds0):
            time = "time"
        elif "t" in ds0.coords:
            time = "t"
    if time in ds0.coords or time in list(ds0):
        if time in ds0.coords:
            times = ds0.coords[time]
        else:
            times = ds0[time]
        ds.coords["time"] = ("time", times)
        attrs_name = list(times.attrs)
        for key in attrs_name:
            ds.time.attrs[key] = times.attrs[key]
    else:
        ds.coords["time"] = ("time", [0])

    # 4判断时效dt
    if (dt is None):
        dt = "dt"
    if dt in ds0.coords or dt in list(ds0):
        if dt in ds0.coords:
            dts = ds0.coords[dt]
        else:
            dts = ds0[dt]
            drop_list.append(dt)

        ds.coords["dt"] = ("dt", dts)
        attrs_name = list(dts.attrs)
        for key in attrs_name:
            ds.dt.attrs[key] = dts.attrs[key]
    else:
        ds.coords["dt"] = ("dt", [0])

    #5判断纬度lat
    if(lat is None):
        if "latitude" in ds0.coords or "latitude" in list(ds0):
            lat = "latitude"
        elif "lat" in ds0.coords or "lat" in list(ds0):
            lat = "lat"
    if lat in ds0.coords or lat in list(ds0):
        if lat in ds0.coords:
            lats = ds0.coords[lat]
        else:
            lats = ds0[lat]
            drop_list.append(lat)
        dims = lats.dims
        if len(dims) == 1:
            ds.coords["lat"] = ("lat", lats)
        else:
            if "lon" in dims[0].lower() or "x" in dims.lower():
                lats = lats.values.T
            ds.coords["lat"] = (("lat","lon"), lats)
        attrs_name = list(lats.attrs)
        for key in attrs_name:
            ds.lat.attrs[key] = lats.attrs[key]
    else:
        ds.coords["lat"] = ("lat",[0])

    #6判断经度lon
    if(lon is None):
        if "longitude" in ds0.coords or "longitude" in list(ds0):
            lon = "longitude"
        elif "lon" in ds0.coords or "lon" in list(ds0):
            lon = "lon"
    if lon in ds0.coords or lon in list(ds0):
        if lon in ds0.coords:
            lons = ds0.coords[lon]
        else:
            lons = ds0[lon]
            drop_list.append(lon)

        dims = lons.dims
        if len(dims) == 1:
            ds.coords["lon"] = ("lon", lons)
        else:
            if "lon" in dims[0].lower() or "x" in dims.lower():
                lons = lons.values.T
            ds.coords["lon"] = (("lat","lon"), lons)
        attrs_name = list(lons.attrs)
        for key in attrs_name:
            ds.lon.attrs[key] = lons.attrs[key]
    else:
        ds.coords["lon"] = ("lon",[0])
    name_list = list((ds0))
    for name in name_list:
        if name in drop_list: continue
        da = ds0[name]
        shape = da.values.shape
        size = 1
        for i in range(len(shape)):
            size = size * shape[i]
        if size > 1:
            dims = da.dims
            dim_order = {}
            for dim in dims:
                if  "ensemble" in dim.lower():
                    dim_order["member"] = dim
                elif "time" in dim.lower():
                    dim_order["time"] = dim
                elif "dt" in dim.lower():
                    dim_order["dt"] = dim
                elif "lev" in dim.lower():
                    dim_order["level"] = dim
                elif "lat" in dim.lower() or 'y' in dim.lower():
                    dim_order["lat"] = dim
                elif "lon" in dim.lower() or 'x' in dim.lower():
                    dim_order["lon"] = dim
            if "member" not in dim_order.keys():
                dim_order["member"] = "member"
                da = da .expand_dims("member")
            if "time" not in dim_order.keys():
                dim_order["time"] = "time"
                da = da .expand_dims("time")
            if "level" not in dim_order.keys():
                dim_order["level"] = "level"
                da = da .expand_dims("level")
            if "dt" not in dim_order.keys():
                dim_order["dt"] = "dt"
                da = da .expand_dims("dt")
            if "lat" not in dim_order.keys():
                dim_order["lat"] = "lat"
                da = da .expand_dims("lat")
            if "lon" not in dim_order.keys():
                dim_order["lon"] = "lon"
                da = da .expand_dims("lon")
            da = da.transpose(dim_order["member"],dim_order["level"],dim_order["time"],
                              dim_order["dt"],dim_order["lat"],dim_order["lon"])
            ds[name] = (("member","level","time","dt","lat","lon"),da)
            attrs_name = list(da.attrs)
            for key in attrs_name:
                ds[name].attrs[key] = da.attrs[key]
    attrs_name = list(ds0.attrs)
    for key in attrs_name:
        ds.attrs[key] = ds0.attrs[key]
    return ds