# -*- coding: utf-8 -*-
"""
Created on Mon Aug 06 16:32:07 2018

@author: KayAoke
"""
import numpy as np
from PartialDerivative import *

"""
This function searches for the pupil of the eye, on fixed subset of the image
with a given radius range [rmin-rmax] around a 10*10 neighbourhood
of the point x,y given as input
"""

def SearchPupil(img,rmin,rmax,x,y,option):
    size = np.shape(img)
    rows = size[0]
    cols = size[1]
    
    sigma = 0.5 #standard deviation for the Gaussian filter
    R = np.arange(rmin,rmax+1,1)
    maxrad = np.zeros((rows,cols))
    maxb = np.zeros((rows,cols))
    
    for i in range(x-5,x+5):
        for j in range(y-5,y+5):
            Max = PartialDerivative(img,[i,j],rmin,rmax,sigma,600,'iris')
            maxrad[i][j] = Max[1]
            maxb[i][j] = Max[0]

    centre = np.argwhere(maxb.max() == maxb)
    
    X = centre[0][0]
    Y = centre[0][1]
    
    radius = maxrad[X][Y]
    
    return [X,Y,radius]   #centre point and radius has been found