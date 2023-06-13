# -*- coding: utf-8 -*-
"""
Created on Sun Sep 02 10:57:36 2018

@author: KayAoke
"""
import numpy as np

def gabor(img,nscale,minWaveLength,mult,sigmaOnf):
    rows,cols = np.shape(img)
    filtersum = np.zeros((1,cols))
    
    E0 = []
    ndata = cols
    
    #If there's an odd number of data points, throw away one
    if(np.mod(ndata,2) == 1):
        ndata = ndata-1
    
        
    logGabor = np.zeros((1,ndata))
    result = np.zeros((rows,ndata),dtype = 'complex')
        
    end = np.fix(ndata/2)
    
    radius = np.arange(0,end+0.5,1)/end/2
    radius = np.transpose(radius)
    radius[0] = 1
    radius = np.reshape(radius,(1,np.size(radius)))
    
    wavelength = minWaveLength
    
    for s in range(0,nscale):
        """
        Construct the filer : First Calculate the radial filter component
        """
        f0 = 1.0/wavelength #Centre frequency
        rf0 = f0/0.5        #Normalised radius from centre of frequency plane corresponding to f0 
        
        index = np.arange(ndata/2+1)
        logGabor[:,0:ndata/2+1] = np.exp((-(np.log(radius/f0))**2) / (2 * np.log(sigmaOnf)**2))
        
        logGabor[0][0] = 0
        
        Filter = logGabor
        filtersum = filtersum + Filter
        
        #for each row of the input img, do the convolution, back transform
        for r in range(0,rows):
            signal = img[r,np.arange(ndata)]
            
            imagefft = np.fft.fft(signal)
            
            temp = imagefft*Filter
            temp = np.fft.ifft(temp)
            result[r:,:] = temp
            
        E0.append(result)
        wavelength = wavelength*mult
        
    filtersum = np.fft.fftshift(filtersum)
    Fsum = filtersum
    
    
    return [E0, filtersum]