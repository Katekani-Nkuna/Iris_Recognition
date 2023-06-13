# -*- coding: utf-8 -*-
"""
Created on Mon Sep 03 18:27:38 2018

@author: KayAoke
"""
import numpy as np
from gabor import gabor

def encode(polar_array,noise_array, nscales, minWaveLength, mult, sigmaOnf):
    
    E0, filtersum = gabor(polar_array, nscales, minWaveLength, mult, sigmaOnf)
    
    length = np.size(polar_array,1)*2*nscales
    
    template = np.zeros((np.size(polar_array,0), length),dtype = 'int')
    
    length2 = np.size(polar_array,1)
    h = np.arange(0,np.size(polar_array,0))
    h = np.reshape(h,(1,np.size(h)))
    
    """
    create the iris template
    """

    
    mask = np.zeros(np.size(template))
    
    for k in range(0,nscales):
        E1 = E0[k]
        
        """
        Phase Quantisation
        """
        H1 = np.real(E1) > 0
        H2 = np.imag(E1) > 0

        """
        If amplitude is close to zero then the phase data is not useful
        So mark of in the noise mask
        """
        H3 = np.abs(E1) < 0.0001
        
        for i in range(-1,length2-1):
            
            ja = np.double(2*nscales*(i+1))
            
            """
            construct the biometric template
            """
            template[h,ja+(2*(k))]  =   H1[h,i+1]
            template[h,ja+(2*(k))+1]    =   H2[h,i+1]
    
            
            """
            Create noise mask
            """
            mask = template
            
    
    return template