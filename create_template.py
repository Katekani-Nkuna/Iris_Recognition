"""
Created on Fri Mar 23 06:55:17 2018

@author: KayAoke
"""
import cv2
import scipy
import numpy as np
from matplotlib import pyplot as plt
from Normalize import normalize
from DIDO import DIDO
from encode import encode
from Hamming_Distance import HD
import sys
import glob

seg = []
mode = sys.argv[13]

print mode
for i in range(0,12):
    seg.append(np.float(sys.argv[i]))

    
xi = np.int(seg[0]); yi = np.int(seg[1]); ri = np.int(seg[2])
xp = np.int(seg[3]); yp = np.int(seg[4]); rp = np.int(seg[5])
a = np.float(seg[6]); b = np.int(seg[7]); c = np.int(seg[8])
a_ = np.float(seg[9]); b_ = np.int(seg[10]); c_ = np.int(seg[11])

print [xi,yi,ri]
print [xp,yp,rp]
print [a,b,c]
imagename = sys.argv[12].split('/')

imagename = imagename[1]

directory = 'Database/'
filename = directory+imagename
img = cv2.imread(filename,0)


r = 10
n = 600
rmin = 50
rmax = 80

"""
Unwrapp Iris Region
"""
    
rows = np.size(img,0)
cols = np.size(img,1)


x0 = yi-2*ri;
n = 3.5*ri;

for i in range(rows):
    for j in range(cols):
        """
        if we are within bounds
        """
        if(j > x0 and j < x0 + n):
            
            Ri = np.power(i-xi,2) + np.power(j-yi,2);
            Rp = np.power(i-xp,2) + np.power(j-yp,2);
            
            if(Ri <= np.power(ri,2) and Rp >= np.power(rp,2)):
                if(i  > a*np.power((j-b),2)+c):
                    if(i <-1*a_*np.power((j-b_),2)+c_):
                        continue
        img[i][j] = 0

"""         
plt.subplot(111)
plt.imshow(img,cmap ='gray')

plt.show
plt.waitforbuttonpress()
"""
    
print [rows, cols]
print 'Normalizing the iris region'
z = normalize(img,yi,xi,ri,yp,xp,rp,20,240)
Normalized_Image = np.uint8(np.array(z[2]))

"""
Store the Normalized Image on the Normalized folder
"""
print 'Encoding the iris region'
filename = 'Normalized/' + imagename

if(mode == "enroll"):
    scipy.misc.imsave(filename, Normalized_Image)

nscale=1;
minWaveLength=18;
mult=1; # not applicable if using nscales = 1
sigmaOnf=0.5;

"""
Use the log Gabor filters to encode the Normalized iris region
"""
template = encode(Normalized_Image,Normalized_Image, nscale, minWaveLength, mult, sigmaOnf)

"""
Store the iris template on th folder Template
"""

filename = 'Template/' + imagename
if(mode == "enroll"):
    scipy.misc.imsave(filename, template)
  


"""
Plotting eyelids
"""

x0 = yi-2*ri;
n = 3.5*ri;
x1 = []
y1 = []
y2 = []

for i in range(rows):
    for j in range(cols):
        if(j > x0 and j < x0 + n):
            x1.append(j)
            y1.append(np.int(a*np.power((j-b),2)+c))
            y2.append(np.int(-1*a_*np.power((j-b_),2)+c_))
  
filename =  directory + imagename
image = cv2.imread(filename)
cv2.circle(image, (yi, xi), ri, (0,255,0), 3)
cv2.circle(image, (yp, xp), rp, (0,255,0), 3)
cv2.circle(image, (yp, xp), 0, (0,255,0), 3)
    
for i in range(len(x1)-1):
    cv2.line(image,(x1[i],y1[i+1]),(x1[i],y1[i+1]),(0,255,0),3)
    cv2.line(image,(x1[i],y2[i+1]),(x1[i],y2[i+1]),(0,255,0),3)


"""
Verification
"""
results = []
if(mode == "verify"):
    
    print "Verifying..."
    template1 = template
    owners = [file for file in glob.glob("Template/*.bmp")]
    template = [cv2.imread(file,0) for file in glob.glob("Template/*.bmp")]
    for template2 in template:
    #template2 = img = cv2.imread(filename,0)
    
        for x in range(np.size(template2,0)):
            for y in range(np.size(template2,1)):
                if template2[x][y] != 0 :
                    template2[x][y] = 1

    
        HD = template1^template2
        HD = float(np.sum(HD))/float(np.size(HD))
        results.append(HD)
        
    results = np.array(results)
    match = np.min(results)
    
    ownerid = 0
        
    print
    print
    print "verifying: ", imagename
    
    if(match < 0.4):
        print "Access granted"
        for i in range(np.size(results)):
            if(match == results[i]):
                ownerid = i
            
        print "Owner: ", owners[ownerid]
    else:
        print "Access denied"
        
    print "Plotting images"
    plt.plot(312)
    plt.imshow(image)
    plt.title(imagename)
    plt.show    
    plt.waitforbuttonpress()
    
  
print
print  
    
"""
Display the Iris/Pupil regions, The normalized image and the iris template
"""

for i in range(rows):
    for j in range(cols):
        """
        if we are within bounds
        """

if(mode == "enroll"):
    print 'Now showing the plots'
        
    plt.subplot(311)
    plt.imshow(image)
    plt.title(imagename)
    
    plt.subplot(312)
    plt.imshow(Normalized_Image,cmap ='gray')
    
    plt.subplot(313)
    plt.imshow(template,cmap ='gray')
    
    plt.show
    plt.waitforbuttonpress()



