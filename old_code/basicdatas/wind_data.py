# -*- coding:UTF-8 -*-
import numpy as np
from copy import deepcopy
from nmc_met_class.basicdatas.grid import *
from scipy.ndimage import convolve

class wind_data:
    # this class is used to define regular lat-lon grid data
    def __init__(self, grid0):
        self.grid = deepcopy(grid0)
        self.slon = grid0.slon
        self.dlon = grid0.dlon
        self.elon = grid0.elon
        self.slat = grid0.slat
        self.dlat = grid0.dlat
        self.elat = grid0.elat
        self.nlon = grid0.nlon
        self.nlat = grid0.nlat
        self.u = np.zeros([grid0.nlat, grid0.nlon])
        self.v = np.zeros([grid0.nlat, grid0.nlon])

    def tostring(self):
        str1 = self.grid.tostring()
        str2 = "u[0,0]: " + str(self.u[0, 0]) + "\nu[nlat-1,0]: " + str(
            self.u[self.nlat - 1,0]) + "\nu[0,nlon-1]: " + str(
            self.u[0,self.nlon - 1]) + "\nu[nlat-1,nlat-1]: " + str(self.u[self.nlat - 1, self.nlon - 1]) + "\n"
        return str1 + str2

    def copy(self):
        return deepcopy(self)

    def reset(self):
        if (self.dlon > 0 and self.dlat > 0):
            return
        u1 = None
        v1 = None
        if (self.dlat < 0):
            u1 = self.u[::-1, :]
            v1 = self.v[::-1, :]
            tran = self.slat
            self.slat = self.elat
            self.elat = tran
            self.dlat = abs(self.dlat)
            self.u = u1
            self.v = v1
        if (self.dlon < 0):
            u1 = self.u[:, ::-1]
            v1 = self.v[:, ::-1]
            tran = self.slon
            self.slon = self.elon
            self.elon = tran
            self.dlon = abs(self.dlon)
            self.u = u1
            self.v = v1
        self.grid = grid(self.slon, self.dlon, self.elon, self.slat, self.dlat, self.elat)
        return

    def smooth(self, time=1):
        kernel = np.array([[0.0625, 0.125, 0.0625],
                           [0.125, 0.25, 0.125],
                           [0.0625, 0.125, 0.0625]])
        for i in range(time):
            self.u= convolve(self.u, kernel)
            self.v= convolve(self.v, kernel)
        return