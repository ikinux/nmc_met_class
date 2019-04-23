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
    nmember_count = grid.member_count
    stime = grid.stime
    etime = grid.etime
    dtimes = grid.dtimes
    dtimedelta = grid.dtimedelta
    sdt = grid.sdt
    edt = grid.edt
    ddt = grid.ddt
    gdtime_type = grid.gdtime_type
    sdtimedelta = grid.sdtimedelta
    edtimedelta = grid.edtimedelta
    ddtimedelta = grid.ddtimedelta
    gdt = grid.gdt
    ngdt = len(gdt)
    nlon = grid.nlon
    nlat = grid.nlat
    levels = grid.levels
    nlevels = len(levels)
    gtime = grid.gtime
    ntime = len(gtime)
    dtime_type = grid.dtime_type
    ndtime_type = len(dtime_type)
    lon = np.arange(nlon) * dlon + slon
    lat = np.arange(nlat) * dlat + slat
    data = np.zeros((nmember_count, nlevels, ntime, ngdt, nlat, nlon))
    return (xr.DataArray(data, coords={'levels': levels,'times': gtime,'dhs':gdt,'member': nmember_count,
                               'lat': lat, 'lon': lon},
                         dims=['member','times', 'dhs', 'levels','lat', 'lon']))

