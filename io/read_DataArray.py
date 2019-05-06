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

def create_micaps4(micaps_abspath, grid_values, label,year,month,day,begin_hour,hour_range,
                   lon_precision,lat_precision,lon_start,lon_end,lat_start,lat_end):

    """
    输出micaps4格式文件
    :param micaps_abspath:生成文件绝对路径
    :param grid_values:格点数组
    :param label: micaps文件标签
    :param year:两位年或四位年
    :param month:两位月
    :param day:两位日
    :param begin_hour:起报时
    :param hour_range:预报时效
    :param lon_precision:经度精确度
    :param lat_precision:纬度精确度
    :param lon_start:起始经度
    :param lon_end:结束经度
    :param lat_start:起始纬度
    :param lat_end:结束纬度
    :return:
    """

    x_grid_num = (lon_end - lon_start) / lon_precision + 1
    y_grid_num = (lat_end - lat_start) / lat_precision + 1
    max_value = math.ceil(max(grid_values.flatten()))
    min_value = math.ceil(min(grid_values.flatten()))
    max_value = str(max_value)
    min_value = str(min_value)
    #第一行标题
    title0 = 'diamond 4 %s\n' %label
    #第二行标题
    title1 = '%s %s %s %s %s 999 %s %s %s %s %s %s %d %d 4 %s %s 2 0.00' \
             % (year, month, day, begin_hour, hour_range,
                lon_precision, lat_precision,
                lon_start, lon_end, lat_start,
                lat_end, x_grid_num, y_grid_num,max_value,min_value)
    title = title0 + title1
    #二维数组写入micaps文件
    np.savetxt(micaps_abspath, grid_values, delimiter='  ',
               fmt='%4.6f', header=title,comments='')
    print('Create [%s] success'%micaps_abspath)