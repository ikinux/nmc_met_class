#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-
import math
from datetime import datetime
'''
约定坐标顺序为: member, times,dhs, level, lat,lon
添加一个grid类来存储网格的范围包括（起始经纬度、格距、起止时间，时间间隔，起止时效，时效间隔，层次列表）
'''

class grid:
    def __init__(self,glon, glat, gtime=None, gdt=None, levels=None):
        'slon,elon,dlon,slat,elat,dlat,stime,dtime,sdt,edt,ddt,dtime_type,levels'
        self.slon = glon[0]
        self.elon = glon[1]
        self.dlon = glon[2]
        self.slat = glat[0]
        self.elat = glat[1]
        self.dlat = glat[2]
        self.gtime = gtime
        if (self.gtime !=None):
            if type(self.gtime[0]) == str:
                self.stime = datetime.strptime(self.gtime[0], '%Y%m%d%H')
                self.etime = datetime.strptime(self.gtime[1], '%Y%m%d%H')
                self.dtime = datetime.strptime(self.gtime[2], '%Y%m%d%H')
            else:
                self.stime = self.gtime[0]
                self.etime = self.gtime[1]
                self.dtime = self.gtime[2]
        self.gdt = gdt
        if (self.gdt !=None):
            if type(self.gdt[0]) == str:
                #将gdt的str数据读出dtime_type类型。然后将数据转换为datetime类型
                # self.sdt = datetime.strptime(self.gdt[0], '%d%H')
                # self.edt = datetime.strptime(self.gdt[1], '%d%H')
                # self.ddt = datetime.strptime(self.gdt[2], '%d%H')
            else:
                self.sdt = self.gdt[0]
                self.edt = self.gdt[1]
                self.ddt = self.gdt[2]
        self.levels = levels
        nlon = 1 + (self.elon - self.slon) / self.dlon
        error = abs(round(nlon) - nlon)
        if (error > 0.01):
            self.nlon = math.ceil(nlon)
        else:
            self.nlon = int(round(nlon))
        self.elon = self.slon + (nlon - 1) * self.dlon
        nlat = 1 + (self.elat - self.slat) / self.dlat
        error = abs(round(nlat) - nlat)
        if (error > 0.01):
            self.nlat = math.ceil(nlat)
        else:
            self.nlat = int(round(nlat))
        self.elat = self.slat + (nlat - 1) * self.dlat