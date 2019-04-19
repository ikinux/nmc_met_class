#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-
import math
from datetime import datetime
import re
'''
约定坐标顺序为: member, times,dhs, level, lat,lon
添加一个grid类来存储网格的范围包括（起始经纬度、格距、起止时间，时间间隔，起止时效，时效间隔，层次列表）
'''

class grid:
    def __init__(self,glon, glat, gtime=None, gdt=None,dtime_type =None,levels=None):
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
                self.dtime = re.findall(r"\D+", gtime[2])[0]
            else:
                self.stime = self.gtime[0]
                self.etime = self.gtime[1]
                self.dtime = re.findall(r"\D+", gtime[2])[0]
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
                    dtime_type = "hour"
                elif TIME_type == 'd':
                    dtime_type = "day"
        self.dtime_type = dtime_type
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