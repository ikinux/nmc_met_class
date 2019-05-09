#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-

import xarray as xr
import numpy as np
import pandas as pd
import datetime
import lch.nmc_met_class.basicdatas as ts
import re



def put_into(grd_from,grd_to)
    #根据grd_form中的坐标信息,判断grd_to 的坐标系能否覆盖前者
    #如果能：
        #吧 grd_from 中的数据覆盖掉grd_to 中相同的网格部分
    #如果不能：
        #，在grd_to中将坐标范围扩展成能覆盖前者，扩展出来的网格区域先设置为9999
        #，再将grd_from中的值覆盖掉grd_to 中相同的网格部分
        
    return


    

def set_coords(grd0,level = None,time = None,dtime = None, member = None):
    #如果level 不为None，并且grd0 的level维度上size = 1，则将level方向的坐标统一设置为传入的参数level
    #其它参数类似处理
    nmember = int(len(grd0.coords.variables.get(grd0.coords.dims[0])))
    nlevel = int(len(grd0.coords.variables.get(grd0.coords.dims[1])))
    ntime = int(len(grd0.coords.variables.get(grd0.coords.dims[2])))
    ndt = int(len(grd0.coords.variables.get(grd0.coords.dims[3])))
    if (level != None) and (nlevel == 1):
        grd0.coords["level"] = ("level", level)
    #time和dtime的时候兼容一下datetime 和str两种格式
    if (time != None) and (ntime == 1):
        if type(time) == str:
            datetime.datetime.strptime(time, "%Y-%m-%d-%H")
        grd0.coords["time"] = ("time", time)
    if (dtime != None) and (ndt == 1):
        if type(dtime) == str:
            datetime.datetime.strptime(dtime, "%Y-%m-%d-%H")
        grd0.coords["dt"] = ("dt", dtime)
    if (member != None) and (nmember == 1):
        grd0.coords["member"] = ("member", member)
    return grd0

#返回一个DataArray，其维度信息和grid描述一致，数组里面的值为0.
def grid_data(grid,data=None):
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
    if np.all(data == None):
        data = np.zeros((nmember, nlevels, ntime, ndt, nlat, nlon))
    else:
        data = data.reshape(nmember, nlevels, ntime, ndt, nlat, nlon)
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
                stime11 = ''.join([x for x in stime1 if x.isdigit()])
                stime2 = str(xf.index.get_level_values(2)[1])
                stime22 = ''.join([x for x in stime2 if x.isdigit()])
                etime1 = str(xf.index.get_level_values(2)[-1])
                etime11 = ''.join([x for x in etime1 if x.isdigit()])

                stime3 = datetime.datetime.strptime(stime22, "%Y-%m-%d:%H:%M:%S")
                stime = datetime.datetime.strptime(stime11, "%Y-%m-%d:%H:%M:%S")
                dtime = stime3 - stime
                etime = datetime.datetime.strptime(etime11, "%Y-%m-%d:%H:%M:%S")
                gtime = [stime, etime, dtime]
            else:
                gtime = None
        if xr01.coords.dims[i] == 'dt':
            print("存在dt")
            if len_ndt > 1:
                #将gdt时间格式改为"m"分钟的形式。
                sdt1 = str(xf.index.get_level_values(3)[0])
                sdt2 = str(xf.index.get_level_values(3)[1])
                edt = str(xf.index.get_level_values(3)[-1])
                time1 = [sdt1,sdt2,edt]
                for i in range(3):
                    day1 = re.findall(r"\D+", time1[i])
                    day2 = re.findall(r"\d+", time1[i])
                    if day1[0].startswith(' days'):
                        time_list = re.findall(r"\d+", time1[i])
                        minute = int(time_list[0]) * 60 * 24 + int(time_list[1]) * 60 + int(time_list[2])
                        gdt.append(str(minute) + 'm')
                    else:
                        minute01 = int(day2[0]) * 60 + int(day2[1])
                        gdt.append(str(minute01) + 'm')
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

