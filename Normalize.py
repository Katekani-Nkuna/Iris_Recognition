# -*- coding: utf-8 -*-
"""
Created on Mon Aug 27 16:12:13 2018

@author: KayAoke
"""
import numpy as np
from scipy import interpolate

def normalize(img, x_iris, y_iris, r_iris,x_pupil,y_pupil,r_pupil,radpixels,angulardiv):
    radiuspixels = radpixels+2
    angledivisions = angulardiv-1
    
    r = np.arange(0,radiuspixels)
    step = 2*np.pi/angledivisions
    theta = np.arange(0,2*np.pi+step/2,step)
    
    x_iris = np.double(x_iris)
    y_iris = np.double(y_iris)
    r_iris = np.double(r_iris)
    
    x_pupil = np.double(x_pupil)
    y_pupil = np.double(y_pupil)
    r_pupil = np.double(r_pupil)
    
    """
    Calculate displacement of pupil center from the iris center
    """
    
    ox = x_pupil-x_iris
    oy = y_pupil-y_iris
    
    if(ox <= 0):
        sgn = -1
    elif(ox > 0):
        sgn = 1
        
    if(ox == 0 and oy > 0):
        sgn = 1
    
    r = np.double(r)
    theta = np.double(theta)
    
    
    a = np.ones((1,angledivisions+1))*(ox**2 + oy**2)
    
    if(ox == 0):
        phi = np.pi/2
    else:
        phi = np.arctan(oy/ox)
        
    b = sgn*np.cos(np.pi - phi - theta)
    
    
    """
    Calculate radius around the iris as a function of the angle
    """
    r = (np.sqrt(a)*b) + (np.sqrt(a*(b**2) - (a -(r_iris**2))))
    
    r = r - r_pupil

    rmat = np.ones((1,radiuspixels))
    rmat = (rmat.T)*r
    
    step = 1.0/(radiuspixels-1)
    rmat = rmat*((np.ones((angledivisions+1,1)))*(np.arange(0,1+step/2,step))).T
    
    rmat = rmat + r_pupil
    
    """
    Exclude values at the boundary of the pupil iris border, and the iris sclera border
    as these may not correspond to areas in the iris region and will introduce noise
    i.e don't take the outside rings as iris data
    """
    
    rmat = rmat[1:(radiuspixels-1), :]
    
    """
    Calculate the cartesian location of each data point around the circular iris region
    """
    xcosmat = np.ones((radiuspixels-2,1))*np.cos(theta)
    xsinmat = np.ones((radiuspixels-2,1))*np.sin(theta)
    
    x0 = rmat*xcosmat
    y0 = rmat*xsinmat
    
    x0 = x_pupil+x0
    y0 = y_pupil-y0
    
    """
    Extract intensity values into the normalised polar representation through interpolation
    """
    
    x , y = np.meshgrid(np.arange(0,np.size(img,1)),np.arange(0,np.size(img,0)))
    #img[y][x] = 0
  
    A = np.ravel(x)
    B = np.ravel(y)
    C = np.double(np.ravel(img))
    D = np.ravel(x0)
    E = np.ravel(y0)
    
    polar_array = interpolate.griddata((A,B),C,(D,E), method = 'nearest')
    polar_array = np.reshape(polar_array,(radpixels,angulardiv))
    
    normalized = polar_array
    
    x = A
    y = B
    
    """
    Start diagnostics, writing out eye image with rings overlayed
    Get rid of outlying points in order to write out the circular pattern    
    """
    polar_array = polar_array/255
    
    coords = np.where(x0 >= np.size(img,1))
    x0[coords] = np.size(img,1)
    coords = np.where(x0 <= 0)
    x0[coords] = 0

    coords = np.where(y0 >= np.size(img,0))
    y0[coords] = np.size(img,0)
    coords = np.where(y0 <= 0)
    y0[coords] = 0 
    
    x0 = np.round(x0)
    y0 = np.round(y0)
    
    x0 = np.int32(x0)
    y0 = np.int32(y0)
    
    
    return [x,y,normalized]
    