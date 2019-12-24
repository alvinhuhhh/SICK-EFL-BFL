import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

#Load image
img = cv.imread('/home/pi/Documents/foo5.jpg', 0)
#Denoise image
dst = cv.fastNlMeansDenoising(img)

plt.hist(dst.ravel(), 256, [0, 256])
plt.show()
