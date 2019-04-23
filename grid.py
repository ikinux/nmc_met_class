#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-
import math
from datetime import datetime
from datetime import timedelta
import re
from copy import deepcopy
import time
import pandas as pd
'''
约定坐标顺序为: member, times,dhs, level, lat,lon
添加一个grid类来存储网格的范围包括（起始经纬度、格距、起止时间，时间间隔，起止时效，时效间隔，层次列表，数据成员）
'''

class grid:
    def __init__(self,glon, glat, gtime=None, gdt=None,gdtime_type=None,levels=None,nmember = 1):
        'slon,elon,dlon,slat,elat,dlat,stime,dtime,sdt,edt,ddt,dtime_type,levels'
        self.slon = glon[0]
        self.elon = glon[1]
        self.dlon = glon[2]
        self.slat = glat[0]
        self.elat = glat[1]
        self.dlat = glat[2]
        self.gtime = gtime
        if (self.gtime !=None):
            num1 =[]
            if type(self.gtime[0]) == str:
                for i in range (0,2):
                    num = ''.join([x for x in gtime[i] if x.isdigit()])
                    #用户输入2019041910十位字符，后面补全加0000，为14位统一处理
                    if len(num) == 4:
                        num1.append(num + "0101000000")
                    elif len(num) == 6:
                        num1.append(num + "01000000")
                    elif len(num) == 8:
                        num1.append(num + "000000")
                    elif len(num) == 10:
                        num1.append(num + "0000")
                    elif len(num) == 12:
                        num1.append(num + "00")
                    elif len(num) == 14:
                        num1.append(num)
                    else:
                        print("输入日期有误，请检查！")
                    #统一将日期变为datetime类型
                self.stime = datetime.strptime(num1[0], '%Y%m%d%H%M%S')
                self.etime = datetime.strptime(num1[1], '%Y%m%d%H%M%S')
            else:
                self.stime = self.gtime[0]
                self.etime = self.gtime[1]
            self.dtimes = re.findall(r"\d+", gtime[2])[0]
            dtime_type = re.findall(r"\D+", gtime[2])[0]
            if dtime_type == 'h':
                self.dtime_type ="hour"
                self.dtimedelta = datetime.timedelta(hours=int(self.dtimes))
            elif dtime_type == 'd':
                self.dtime_type ="day"
                self.dtimedelta = datetime.timedelta(days=int(self.dtimes))
            elif dtime_type == 'm':
                self.dtime_type ="minute"
                self.dtimedelta = datetime.timedelta(minutes=int(self.dtimes))
        self.gdt = gdt
        if (self.gdt !=None):
            num2 = []
            if type(self.gdt[0]) == str:
                for i in range(0, 3):
                    gdt_num = ''.join([x for x in gdt[i] if x.isdigit()])
                    num2.append(gdt_num)
                self.sdt = num2[0]
                self.edt = num2[1]
                self.ddt = num2[2]
                #提取出dtime_type类型
                TIME_type = re.findall(r"\D+", gdt[2])[0]
                if TIME_type == 'h':
                    gdtime_type = "hour"
                    self.sdtimedelta = datetime.timedelta(hours=num2[0])
                    self.edtimedelta = datetime.timedelta(hours=num2[1])
                    self.ddtimedelta = datetime.timedelta(hours=num2[2])
                elif TIME_type == 'd':
                    gdtime_type = "day"
                    self.sdtimedelta = datetime.timedelta(days=num2[0])
                    self.edtimedelta = datetime.timedelta(days=num2[1])
                    self.ddtimedelta = datetime.timedelta(days=num2[2])
                elif TIME_type == 'm':
                    gdtime_type = "minute"
                    self.sdtimedelta = datetime.timedelta(minutes=num2[0])
                    self.edtimedelta = datetime.timedelta(minutes=num2[1])
                    self.ddtimedelta = datetime.timedelta(minutes=num2[2])
                self.gdtime_type = gdtime_type
        self.levels = levels
        self.nmember = nmember
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

    #tostring 的作用是重置系统自动的函数，在print(grid) 的时候可以很整齐的看到所有信息
    def tostring(self):
        if (self.gtime != None):
            if (self.gdt != None):
                if (self.levels != None):
                    #gtime,gdt,levels都存在
                    str1 = "nlon: " + str(self.nlon) + "    nlat: " + str(self.nlat) + \
                           "\nslon: " + str(self.slon) + "    dlon: " + str(self.dlon) + "    elon: " + str(self.elon) + \
                           "\nslat: " + str(self.slat) + "    dlat: " + str(self.dlat) + "    elat: " + str(self.elat) + \
                           "\nstime: " + str(self.stime) + "    etime: " + str(self.etime) + "    dtime: " + str(self.dtime) + \
                           "\ndtime_type: " + str(self.dtime_type) + "    dtimedelta: " + str(self.dtimedelta) + \
                           "\nsdt: " + str(self.sdt) + "    edt: " + str(self.edt) + "    ddt: " + str(self.ddt) + \
                           "\ngdtime_type: " + str(self.gdtime_type) + "    sdtimedelta: " + str(self.sdtimedelta) + "    edtimedelta: " + str(self.edtimedelta) + "    ddtimedelta: " + str(self.ddtimedelta) + \
                           "\nlevels: " + str(self.levels) + \
                           "\nmember_count: " + str(self.member_count) + "\n"
                else:
                    #gtime,gdt存在,levels不存在
                    str1 = "nlon: " + str(self.nlon) + "    nlat: " + str(self.nlat) + \
                           '\nslon: ' + str(self.slon) + "    dlon: " + str(self.dlon) + "    elon: " + str(self.elon) + \
                           "\nslat: " + str(self.slat) + "    dlat: " + str(self.dlat) + "    elat: " + str(self.elat) + \
                           "\nstime: " + str(self.stime) + "    etime: " + str(self.etime) + "    dtime: " + str(self.dtime) + \
                           "\ndtime_type: " + str(self.dtime_type) + "    dtimedelta: " + str(self.dtimedelta) + \
                           "\nsdt: " + str(self.sdt) + "    edt: " + str(self.edt) + "    ddt: " + str(self.ddt) + \
                           "\ngdtime_type: " + str(self.gdtime_type) + "    sdtimedelta: " + str(self.sdtimedelta) + "    edtimedelta: " + str(self.edtimedelta) + "    ddtimedelta: " + str(self.ddtimedelta) + \
                           "\nmember_count: " + str(self.member_count) + "\n"
            else:
                if (self.levels != None):
                    # gtime，levels存在，gdt不存在
                    str1 = "nlon: " + str(self.nlon) + "    nlat: " + str(self.nlat) + \
                           "\nslon: " + str(self.slon) + "    dlon: " + str(self.dlon) + "    elon: " + str(self.elon) + \
                           "\nslat: " + str(self.slat) + "    dlat: " + str(self.dlat) + "    elat: " + str(self.elat) + \
                           "\nstime: " + str(self.stime) + "    etime: " + str(self.etime) + "    dtime: " + str(self.dtime) + \
                           "\ndtime_type: " + str(self.dtime_type) + "    dtimedelta: " + str(self.dtimedelta) + \
                           "\nlevels: " + str(self.levels) + \
                           "\nmember_count: " + str(self.member_count) + "\n"

                else:
                    #gtime存在，levels，gdt不存在
                    str1 = "nlon: " + str(self.nlon) + "    nlat: " + str(self.nlat) + \
                           "\nslon: " + str(self.slon) + "    dlon: " + str(self.dlon) + "    elon: " + str(self.elon) + \
                           "\nslat: " + str(self.slat) + "    dlat: " + str(self.dlat) + "    elat: " + str(self.elat) + \
                           "\nstime: " + str(self.stime) + "    etime: " + str(self.etime) + "    dtime: " + str(self.dtime) + \
                           "\ndtime_type: " + str(self.dtime_type) + "    dtimedelta: " + str(self.dtimedelta) + \
                           "\nmember_count: " + str(self.member_count) + "\n"
        else:

            if (self.gdt != None):
                if (self.levels != None):
                    # gtime不存在，levels,gdt存在
                    str1 = "nlon: " + str(self.nlon) + "    nlat: " + str(self.nlat) + \
                           "\nslon: " + str(self.slon) + "    dlon: " + str(self.dlon) + "    elon: " + str(self.elon) + \
                           "\nslat: " + str(self.slat) + "    dlat: " + str(self.dlat) + "    elat: " + str(self.elat) + \
                           "\nsdt: " + str(self.sdt) + "    edt: " + str(self.edt) + "    ddt: " + str(self.ddt) + \
                           "\ngdtime_type: " + str(self.gdtime_type) + "    sdtimedelta: " + str(self.sdtimedelta) + "    edtimedelta: " + str(self.edtimedelta) + "    ddtimedelta: " + str(self.ddtimedelta) + \
                           "\nlevels: " + str(self.levels) + \
                           "\nmember_count: " + str(self.member_count) + "\n"
                else:
                    #gtime,levels不存在,gdt存在
                    str1 = "nlon: " + str(self.nlon) + "    nlat: " + str(self.nlat) + \
                           "\nslon: " + str(self.slon) + "    dlon: " + str(self.dlon) + "    elon: " + str(self.elon) + \
                           "\nslat: " + str(self.slat) + "    dlat: " + str(self.dlat) + "    elat: " + str(self.elat) + \
                           "\nsdt: " + str(self.sdt) + "    edt: " + str(self.edt) + "    ddt: " + str(self.ddt) + \
                           "\ngdtime_type: " + str(self.gdtime_type) + "    sdtimedelta: " + str(self.sdtimedelta) + "    edtimedelta: " + str(self.edtimedelta) + "    ddtimedelta: " + str(self.ddtimedelta) + \
                           "\nmember_count: " + str(self.member_count) + "\n"
            else:
                #gtime,gdt不存在,levels存在
                if (self.levels != None):
                    str1 = "nlon: " + str(self.nlon) + "    nlat: " + str(self.nlat) + \
                           "\nslon: " + str(self.slon) + "    dlon: " + str(self.dlon) + "    elon: " + str(self.elon) + \
                           "\nslat: " + str(self.slat) + "    dlat: " + str(self.dlat) + "    elat: " + str(self.elat) + \
                           "\nlevels: " + str(self.levels) + \
                           "\nmember_count: " + str(self.member_count) + "\n"
                else:
                    #gtime,gdt,levels都不存在
                    str1 = "nlon: " + str(self.nlon) + "    nlat: " + str(self.nlat) + \
                           "\nslon: " + str(self.slon) + "    dlon: " + str(self.dlon) + "    elon: " + str(self.elon) + \
                           "\nslat: " + str(self.slat) + "    dlat: " + str(self.dlat) + "    elat: " + str(self.elat) + \
                           "\nmember_count: " + str(self.member_count) + "\n"
        return str1

    def copy(self):
        return deepcopy(self)

    #reset的作用是把网格的坐标间隔统一为正数。
    def reset(self):
        if (self.dlon > 0 and self.dlat > 0):
            pass
        if (self.dlat < 0):
            tran = self.slat
            self.slat = self.elat
            self.elat = tran
            self.dlat = abs(self.dlat)
        if (self.dlon < 0):
            tran = self.slon
            self.slon = self.elon
            self.elon = tran
            self.dlon = abs(self.dlon)
        return