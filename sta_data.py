#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-
import pandas as pd
import numpy as np
import xarray as xr


# #设定参数
# def set_para(dframe, time = None,dtime = None, dtime_type = None, level = None):
#     time,dtime,dtime_type,level
#     return 0

#纬度完整的站点数
'''
继承自DataFrame
第一层index为level,第二层Index为站号，第三层index为时间，第四层index为时效,
数据内容的第一列为经度、第二列为纬度、第三列为高度、第4为要素值，如果列数大于4，则第4列开始为要素值的集合成员值。
列名称约定记为’lon’, ’lat’, ‘alt’,’data0’,’data1’,…
多层索引可以切片，但是：
1.外层标签必须是经过排序的；
2.每个索引的外层标签第一个字母必须得一致，要么全是大写，要么全是小写
'''
#level_type='surface'dtime_type=None

def sta_data(dframe,level=None,level_type=None,sta_num=None,time=None,dtime=None,dtime_type = "hour"):
    #传过来的参数为列表
    columns = ['lon','lat','alt']
    level_type,dtime_type
    data_num = dframe.shape[1] - 2
    for i in range(0,data_num):
        data = data + str(i)
        columns.append(data)
    # columns = [0, 1, column_num]
    #     # sta_num = ['a', 'a', 'b', 'b']
    #     # time = [1,2,3,4]
    #     # prescription = ['w', 'x', 'y', 'z']
    return pd.DataFrame(dframe.ix[:,dframe.shape[1]].values,
                        index=[level,time,dtime,sta_num],
                        columns = columns)
