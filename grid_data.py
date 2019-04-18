#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-

import xarray as xr

class grid_data:
    def __init__(self, grid,gtime = None, gdt = None,levels=None):
        self.gtime = gtime
        self.gdt = gdt
        self.levels = levels
        xr.DataArray(grid, coords={'member': [0], 'times': gtime,'dhs':[0],'levels': levels,
                                  'lat': [0], 'lon': [0]},
                            dims=['level','time','dhs','member','lat','lon'])