"""
Created on Fri Mar 23 06:55:17 2018

@author: KayAoke
"""
import cv2
import scipy
import numpy as np
from matplotlib import pyplot as plt
from scipy import ndimage


imagename = 'masl5.bmp'
directory = 'Database/'
filename = directory+imagename
#img = cv2.imread(filename,0)

# Read image
im_in = cv2.imread(filename, cv2.IMREAD_GRAYSCALE);
 
# Threshold.
# Set values equal to or above 220 to 0.
# Set values below 220 to 255.


im_in = cv2.normalize(im_in.astype('float'), None, 0.0, 1.0, cv2.NORM_MINMAX,dtype=cv2.CV_32F)

th, im_th = cv2.threshold(im_in, 0.1, 255, cv2.THRESH_BINARY_INV);


# Copy the thresholded image.
im_th = np.uint8(im_th)

im_floodfill = im_th.copy()


out = ndimage.binary_fill_holes(im_th)

filled = out
out = np.uint8(out)

out = cv2.bitwise_not(out)

plt.imshow(filled,cmap ='gray')
plt.show
cv2.imshow(out)
cv2.wait(0);
