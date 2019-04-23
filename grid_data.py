#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-

import xarray as xr
import numpy as np

#返回一个DataArray，其维度信息和grid描述一致，数组里面的值为0.
def grid_data(grid):
    slon = grid.slon
    dlon = grid.dlon
    slat = grid.slat
    dlat = grid.dlat
    nmember_count = grid.member_count
    ngdt = grid.ngdt
    gdts = grid.gdts
    nlon = grid.nlon
    nlat = grid.nlat
    levels = grid.levels
    nlevels = len(levels)
    ntime = grid.ntime
    times = grid.times
    lon = np.arange(nlon) * dlon + slon
    lat = np.arange(nlat) * dlat + slat
    data = np.zeros((nmember_count, nlevels, ntime, ngdt, nlat, nlon))
    return (xr.DataArray(data, coords={'levels': levels,'times': times,'dhs':gdts,'member': nmember_count,
                               'lat': lat, 'lon': lon},
                         dims=['member','times', 'dhs', 'levels','lat', 'lon']))

