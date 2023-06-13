# -*- coding: utf-8 -*-
"""
Created on Mon Aug 06 16:59:53 2018

@author: KayAoke
"""

import cv2
import numpy as np
from PartialDerivative import *
from SearchPupil import *
from scipy.misc import imresize

"""
This is Daugman's Integro Differential Operator application
We are now using it to search for the pupil
then from that we find the pupil
"""

def DIDO(img,rmin,rmax,scale):
    
    #scaling factor
    rmin = rmin*scale
    rmax = rmax*scale
    
    """
    Rescale the image for faster performance
    ...
    """
    
    #img = imresize(img,5)
    img2 = img
    img = imresize(img,scale)
    
    img = np.array(img)
    
    """
    Because of Specular Reflections, we have to fill in those holes with imfill()
    ...
    """
    
    """
    Normalize the image such that Pixel values are between [0,1] im2double()
    """
    
    I = cv2.normalize(img.astype('float'), None, 0.0, 1.0, cv2.NORM_MINMAX,dtype=cv2.CV_32F)

    """
    Binarize the image and extract only the black Pixels
    ...
    """
    X, Y = np.where(I < 0.5)
    
    """
    From the black pixels try to localise the pupil search by eliminating pixels that 
    are surrounded by white pixels, leaving only local minimum pixels    
    ...
    """  
    size = np.shape(img)
    rows = size[0]
    cols = size[1]
    
    X.setflags(write=1)
    Y.setflags(write=1)
    
    for k in range(0,np.size(X)):
        if(((X[k] > rmin) and (Y[k] > rmin)) and (X[k] <= (rows-rmin)) and (Y[k] <(cols-rmin))):
            A = I[(X[k]-1) : (X[k]+1), (Y[k]-1) : (Y[k]+1)]
            Min = np.min(A)
            
            if(I[X[k]][Y[k]] != Min):
                X[k] = -1
                Y[k] = -1

    v = np.where(X == -1)
    X = np.delete(X,v)
    Y = np.delete(Y,v)       
            
    """
    Also remove all Pixels that are so close to the boarder, as the obviously can't be the pupil
    ...
    """
    v = np.where(X <= rmin)
    
    a = np.where(Y <= rmin)
    v = np.append(v,a)
    
    a = np.where(X > (rows-rmin))
    v = np.append(v,a)
    
    a = np.where(Y > (rows-rmin))
    v = np.append(v,a)   
    
    X = np.delete(X,v)
    Y = np.delete(Y,v)
    
    """
    Now apply Daugman's Integro Differential Operator
    LineIntegral -> PartialDerivatives
    """
    
    N = np.size(X)
    maxb = np.zeros((rows,cols))
    maxrad = np.zeros((rows,cols))
    
    
    #On this areas that have possible centres, we shall search for the iris centre
    print 'Searching for iris centre'
    for j in range(0,N):
        #Coarse search
        pd = PartialDerivative(I,[X[j],Y[j]],rmin,rmax,'inf',600,'iris')
        maxb[X[j]][Y[j]] = pd[0]
        maxrad[X[j]][Y[j]] = pd[1]
        
    x, y = np.where(maxb == np.max(maxb))
    
    print 'Searching for iris boundaries'
    """
    Fine search of the iris on the possible centre
    """
    ci = SearchPupil(I,rmin,rmax,x,y,'iris')
    ci = np.array(ci)/scale
    
    print 'Searching for Pupil boundaries'
    """
    Fine search of the pupil on the Iris centre
    """
    
    r = ci[2]
    rmin = round(0.1*r)
    rmax = round(0.8*r)
    x = int(round(ci[0]*scale))
    y = int(round(ci[1]*scale))
    
    cp = SearchPupil(I,rmin,rmax,x,y,'pupil')
    
    
    cp = np.array(cp)/scale
    
    return[ci,cp]
    
    
    
  