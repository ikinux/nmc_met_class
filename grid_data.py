#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-

import xarray as xr
import numpy as np

#返回一个DataArray，其维度信息和grid描述一致，数组里面的值为0.
def grid_data(grid):
    slon = grid.slon
    elon = grid.elon
    dlon = grid.dlon
    slat = grid.slat
    elat = grid.elat
    dlat = grid.dlat
    levels = grid.levels
    gtime = grid.gtime
    member_count = grid.member_count
    stime = grid.stime
    etime = grid.etime
    dtimes = grid.dtimes
    dtime_type = grid.dtime_type
    dtimedelta = grid.dtimedelta
    gdt = grid.gdt
    sdt = grid.sdt
    edt = grid.edt
    ddt = grid.ddt
    gdtime_type = grid.gdtime_type
    sdtimedelta = grid.sdtimedelta
    edtimedelta = grid.edtimedelta
    ddtimedelta = grid.ddtimedelta
    nlon = grid.nlon
    nlat = grid.nlat
    lon = np.arange(nlon) * dlon + slon
    lat = np.arange(nlat) * dlat + slat
    dat = (np.array(levels,gtime,dtime_type,member_count,lon,lat)).astype(float)
    return (xr.DataArray(dat, coords={'levels': levels,'times': gtime,'dhs':dtime_type,'member': member_count,
                               'lat': lat, 'lon': lon},
                         dims=['level', 'time', 'dhs', 'member', 'lat', 'lon']))

