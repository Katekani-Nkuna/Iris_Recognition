"""
Created on Fri Mar 23 06:55:17 2018

@author: KayAoke
"""
import cv2
import scipy
import numpy as np
from matplotlib import pyplot as plt
from scipy import ndimage
import sys




imagename = sys.argv[0].split('/')

imagename = imagename[1]

directory = 'Database/'
filename = directory+imagename


 
# Threshold.
# Set values equal to or above 220 to 0.
# Set values below 220 to 255.


im_in = cv2.imread(filename, cv2.IMREAD_GRAYSCALE);
im_in = cv2.GaussianBlur(im_in,(5,5),0)


im_in = cv2.normalize(im_in.astype('float'), None, 0.0, 1.0, cv2.NORM_MINMAX,dtype=cv2.CV_32F)

th, im_th = cv2.threshold(im_in, 0.05, 255, cv2.THRESH_BINARY_INV);


# Copy the thresholded image.
im_th = np.uint8(im_th)


out = ndimage.binary_fill_holes(im_th)

print "filled holes"
print "Now filling holes"
out = np.array(out)
out = np.uint8(out)

for i in range(np.size(out,0)):
    for j in range(np.size(out,1)):
        if(out[i][j] == 1):
            out[i][j] = 0
        else:
            out[i][j] = 255
            
#out = cv2.bitwise_not(out)
filename = 'Binary/' + imagename
scipy.misc.imsave(filename, out)

print "image Saved"