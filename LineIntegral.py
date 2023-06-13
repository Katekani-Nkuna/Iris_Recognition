# -*- coding: utf-8 -*-
"""
Created on Mon Aug 06 11:07:53 2018

@author: KayAoke
"""
import numpy as np
"""
This function computes the normalised line integral of a circular contour
The circular region is approximated by a polygon of a large number of sides (n)
The pixels at the contour are summed to approximate the line integral
img     : Is the gray image to be processed
C(x,y)  : Is the current centre that we are trying
n       : iS tge number of sisdes approximating countiour
r       : circumfrancial radius we are currently trying out   
part    : The eye region we are trying to find (Iris or Pupil)
"""


def LineIntegral(img,C,r,n,part):
    
    """
    These section Extracts the pixels at the circle contour approximated by n sides
    """

    #Ange subtended at the centre by the sides of polygon    
    theta = (2*np.pi)/n  
    
    
    size = np.shape(img)
    rows = size[0]
    cols = size[1]
    #angle = np.arange(0,2*np.pi,theta)
    angle = np.linspace(theta, 2*np.pi, num=n)
    
    x = np.round(C[0] - r*np.sin(angle))
    y = np.round(C[1] + r*np.cos(angle))
    
    #for any circle that exceeds the image's outer bounds return, there's no iris there
    if(any(i >=rows for i in x) or any(j >= cols for j in y) or any(j <= 0 for j in y) or any(i <= 0 for i in x)):
        return []
        
    #When we are searching for the pupil region        
    if(part == 'pupil'):
        L = 0
        for i in range(0,n):
            pixelIntensity = img[x[i]][y[i]]
            L = L + pixelIntensity
            
        return L/n
    else:   
    #When we are searching for the Iris region, compute lateral line integral o prevent
    #occlussin affecting results)
        L = 0
        for i in range(0,n/8):
            pixelIntensity = img[x[i]][y[i]]
            L = L+pixelIntensity
        
        for i in range((3*n)/8,(5*n)/8):
            pixelIntensity = img[x[i]][y[i]]
            L = L+pixelIntensity

        for i in range((7*n)/8,n):
            pixelIntensity = img[x[i]][y[i]]
            L = L+pixelIntensity
        
        return (2*L)/n
        
    