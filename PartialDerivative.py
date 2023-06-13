# -*- coding: utf-8 -*-
"""
Created on Mon Aug 06 11:35:51 2018

@author: KayAoke
"""
import cv2
import numpy as np
from LineIntegral import *
"""
This function computes the partial derivatives of the countour line Integrals adjacent to each other
While increasing the radius from rimin to rmax until on a centre pixel

"""


def PartialDerivative(img,C,rmin,rmax,sigma,n,part):
    
    L =[]
    R = np.arange(rmin,rmax,1)
    for i in range(0,len(R)):
        l = LineIntegral(img,C,R[i],n,part)
        
        if(l == []):
            break
        L.append(l)
        
    D = np.diff(L)
    D = np.append([0],D)       #The derivetive vector is goin to be 1 element shorter, thus add one element in the beginning
    
    if(sigma == 'inf'):
        f = np.ones((1,7))/7
        
    else:
        #Generate a 5 member 1-D gaussian
        f = cv2.getGaussianKernel(5,sigma)
        f = f.T
        
    #Smooth the Derivative Vector by 1-D gaussian
    f = np.ravel(f)
    
    blur = np.convolve(D,f,'same')
    
    blur = np.abs(blur)
    
    i = np.argmax(blur) # get index of the the maximum blur
    
    r = R[i]            # get radius at which maximum blur occurs
    b = blur[i]         # get the maximum blur
    
    return [b,r,blur]
    
    
    
    
       
    
    

            
            
    
    
    