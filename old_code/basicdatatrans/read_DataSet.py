from copy import deepcopy
import os
import numpy as np
import netCDF4 as nc
import xarray as xr
import pandas as pd
import datetime
import time
class ctl:
    def __init__(self):
        self.slon = 0
        self.dlon = 1
        self.elon = 0
        self.slat = 0
        self.dlat = 1
        self.elat = 0
        self.nlon = 1
        self.nlat = 1
        self.nlevel = 1
        self.ntime = 1
        self.nvar = 1
        self.nensemble = 1
        self.data_Path = ""
        self.values = []
        self.levels = []
        self.times =[]
    def copy(self):
        return deepcopy(self)

def read_from_grads(filename,ctl0 = None,endian = None):
    if ctl0 is None:
        if os.path.exists(filename):
            ctl0 = read_ctl(filename)
            return read_from_grads(ctl0.data_path,ctl0)
    else:
        if os.path.exists(filename):
            if(endian is None):
                data = np.fromfile(filename, dtype='f')
            else:
                data = np.fromfile(filename, dtype='>f')
            data = data.reshape(ctl0.nvar, ctl0.nensemble, ctl0.ntime,ctl0.nlevel, ctl0.nlat, ctl0.nlon)
            dict0 = {}

            for i in range(len(ctl0.values)):
                value_name = ctl0.values[i]
                dict0[value_name] = (['member','time','level','lat','lon'],data[i,:,:,:,:,:])
            lons = np.arange(ctl0.nlon) * ctl0.dlon + ctl0.slon
            lats = np.arange(ctl0.nlat) * ctl0.dlat + ctl0.slat
            times = ctl0.times
            members = np.arange(ctl0.nensemble)

            ds = xr.Dataset(dict0,coords= {'member':members,'time':times,'level':ctl0.levels,
                                             'lat':lats,'lon':lons})
            return ds
    return None

def read_ctl(ctl_filename):
    time_unit_strs= ['mn','hr','dy','mo','yr']
    if os.path.exists(ctl_filename):
        ctl0 = ctl()
        file = open(ctl_filename, 'r')
        content = file.read()
        file.close()
        lines = content.split("\n")
        nlines = len(lines)
        line = lines[0]
        strs = line.split()
        if strs[1].__contains__('^'):
            ctl0.data_path = os.path.dirname(ctl_filename) +"\\"+ strs[1][1:]
        else:
            ctl0.data_path = strs[1][1:]
        var_name_start_i = 0
        for i in range (1,nlines):
            line = lines[i]
            strs = line.split()
            if(len(strs)>0):
                if strs[0].upper() == "XDEF":
                    ctl0.nlon = int(strs[1])
                    ctl0.slon = float(strs[3])
                    ctl0.dlon = float(strs[4])
                if strs[0].upper() == "YDEF":
                    ctl0.nlat = int(strs[1])
                    ctl0.slat = float(strs[3])
                    ctl0.dlat = float(strs[4])
                if strs[0].upper() == "ZDEF":
                    #ctl0.nlevel = int(strs[1])
                    for i in range(3,len(strs)):
                        ctl0.levels.append(strs[i])
                    ctl0.nlevel = len(ctl0.levels)
                if strs[0].upper() == "TDEF":
                    ctl0.ntime = int(strs[1])
                    start_time = datetime.datetime.strptime(strs[3],"%HZ%d%b%Y")
                    str4 = strs[4][-2:]
                    dt = int(strs[4][:-2])
                    print(str4)
                    print(dt)
                    if str4 == 'mn':
                        dtime = datetime.timedelta(minutes=dt)
                    elif str4 == 'yr':
                        dtime = datetime.timedelta(years=dt)
                    elif str4 == 'dy':
                        dtime = datetime.timedelta(days=dt)
                    elif str4 == 'mo':
                        dtime = datetime.timedelta(months=dt)
                    else:
                        dtime = datetime.timedelta(hours=dt)

                    for i in range(ctl0.ntime):
                        ctl0.times.append(start_time)
                        start_time = start_time + datetime.timedelta(hours=dt)
                if strs[0].upper() == "VARS":
                    ctl0.nvar = int(strs[1])
                    var_name_start_i = i + 1
                if(strs[0].upper() == "EDEF"):
                    ctl0.nensemble = int(strs[1])
        for i in range(var_name_start_i,var_name_start_i + ctl0.nvar):
            line = lines[i]
            strs = line.split()
            ctl0.values.append(strs[0])
        ctl0.elon = ctl0.slon + ctl0.dlon * (ctl0.nlon-1)
        ctl0.elat = ctl0.slat + ctl0.dlat * (ctl0.nlat-1)
        return ctl0
    else:
        return None

def read_from_nc(filename,ensemble = None,time = None,level = None,latitude = None,longitude = None):
    ds0 = xr.open_dataset(filename)
    print(ds0)
    drop_list = []
    ds = xr.Dataset()
    if(ensemble is None):
        ensemble = "ensemble"
    if ensemble in ds0.coords or ensemble in list(ds0):
        if ensemble in ds0.coords:
            ensembles = ds0.coords[ensemble]
        else:
            ensembles = ds0[ensemble]
            drop_list.append(ensemble)

        ds.coords["ensemble"] = ("ensemble", ensembles)
        attrs_name = list(ensembles.attrs)
        for key in attrs_name:
            ds.ensemble.attrs[key] = ensembles.attrs[key]
    else:
        ds.coords["ensemble"] = ("ensemble", [0])


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


    if(level is None):
        if "level" in ds0.coords or "level" in list(ds0):
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


    if(latitude is None):
        if "latitude" in ds0.coords or "latitude" in list(ds0):
            latitude = "latitude"
        elif "lat" in ds0.coords or "lat" in list(ds0):
            latitude = "lat"
    if latitude in ds0.coords or latitude in list(ds0):
        if latitude in ds0.coords:
            latitudes = ds0.coords[latitude]
        else:
            latitudes = ds0[latitude]
            drop_list.append(latitude)
        dims = latitudes.dims
        if len(dims) == 1:
            ds.coords["latitude"] = ("latitude", latitudes)
        else:
            if "lon" in dims[0].lower() or "x" in dims.lower():
                latitudes = latitudes.values.T
            ds.coords["latitude"] = (("latitude","longitude"), latitudes)
        attrs_name = list(latitudes.attrs)
        for key in attrs_name:
            ds.latitude.attrs[key] = latitudes.attrs[key]
    else:
        ds.coords["latitude"] = ("latitude",[0])


    longitudes = [0]
    if(longitude is None):
        if "longitude" in ds0.coords or "longitude" in list(ds0):
            longitude = "longitude"
        elif "lon" in ds0.coords or "lon" in list(ds0):
            longitude = "lon"
    if longitude in ds0.coords or longitude in list(ds0):
        if longitude in ds0.coords:
            longitudes = ds0.coords[longitude]
        else:
            longitudes = ds0[longitude]
            drop_list.append(longitude)

        dims = longitudes.dims
        if len(dims) == 1:
            ds.coords["longitude"] = ("longitude", longitudes)
        else:
            if "lon" in dims[0].lower() or "x" in dims.lower():
                longitudes = longitudes.values.T
            ds.coords["longitude"] = (("latitude","longitude"), longitudes)
        attrs_name = list(longitudes.attrs)
        for key in attrs_name:
            ds.longitude.attrs[key] = longitudes.attrs[key]
    else:
        ds.coords["longitude"] = ("longitude",[0])



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
                if  "ens" in dim.lower():
                    dim_order["ensemble"] = dim
                elif "time" in dim.lower():
                    dim_order["time"] = dim
                elif "lev" in dim.lower():
                    dim_order["level"] = dim
                elif "lat" in dim.lower() or 'y' in dim.lower():
                    dim_order["latitude"] = dim
                elif "lon" in dim.lower() or 'x' in dim.lower():
                    dim_order["longitude"] = dim
            if "ensemble" not in dim_order.keys():
                dim_order["ensemble"] = "ensemble"
                da = da .expand_dims("ensemble")
            if "time" not in dim_order.keys():
                dim_order["time"] = "time"
                da = da .expand_dims("time")
            if "level" not in dim_order.keys():
                dim_order["level"] = "level"
                da = da .expand_dims("level")
            if "latitude" not in dim_order.keys():
                dim_order["latitude"] = "latitude"
                da = da .expand_dims("latitude")
            if "longitude" not in dim_order.keys():
                dim_order["longitude"] = "longitude"
                da = da .expand_dims("longitude")
            da = da.transpose(dim_order["ensemble"],dim_order["time"],dim_order["level"],
                              dim_order["latitude"],dim_order["longitude"])
            ds[name] = (("ensemble","time","level","latitude","longitude"),da)
            attrs_name = list(da.attrs)
            for key in attrs_name:
                ds[name].attrs[key] = da.attrs[key]
    attrs_name = list(ds0.attrs)
    for key in attrs_name:
        ds.attrs[key] = ds0.attrs[key]
    print(ds)




