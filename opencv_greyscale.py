import numpy as np
import cv2 as cv

#######################
#***IMAGE THRESHOLD***#
#######################
#Lower and upper bounds
##lower = 55
##upper = 105

##################
#Global Variables#
##################
##load = '/home/pi/Documents/LightOffSample.jpg'
resolution = [1024, 768]
leftBound = 0
rightBound = 1023
topBound = 0
botBound = 767

#############################
#Image loading and denoising#
#############################
###Load image
##img = cv.imread(load, 0)
###Denoise image
##dst = cv.fastNlMeansDenoising(img)
###Isolating pixels
##mask = cv.inRange(dst, lower, upper)
##res = cv.bitwise_and(dst, dst, mask = mask)

################
#Image cropping#
################
def CropROI(image):
    for i in range(resolution[1]):
        currentRow = image[i]
        prevRow = image[i-1]
        if currentRow.any() and not prevRow.any():
            topBound = i
            break

    for i in range(resolution[1]-2, 0, -1):
        currentRow = image[i]
        prevRow = image[i+1]
        if currentRow.any() and not prevRow.any():
            botBound = i
            break

    rotateCCW = np.rot90(image)
    for i in range(resolution[0]):
        currentRow = rotateCCW[i]
        prevRow = rotateCCW[i-1]
        if currentRow.any() and not prevRow.any():
            rightBound = resolution[0]-i
            break

    for i in range(resolution[0]-2, 0, -1):
        currentRow = rotateCCW[i]
        prevRow = rotateCCW[i+1]
        if currentRow.any() and not prevRow.any():
            leftBound = resolution[0]-i
            break

    cropped = image[topBound:botBound, leftBound:rightBound]

    return cropped

####################
#Measuring diameter#
####################
def CalcAvgDiameter(file, lower, upper):
    #Load image
    img = cv.imread(file, 0)
    #Denoise image
    dst = cv.fastNlMeansDenoising(img)
    #Isolating pixels
    mask = cv.inRange(dst, lower, upper)
    res = cv.bitwise_and(dst, dst, mask = mask)

    result = CropROI(res)
    
    return (result.shape[0]+result.shape[1])/2

def CalcHorizontalDiameter(file, lower, upper):
    #Load image
    img = cv.imread(file, 0)
    #Denoise image
    dst = cv.fastNlMeansDenoising(img)
    #Isolating pixels
    mask = cv.inRange(dst, lower, upper)
    res = cv.bitwise_and(dst, dst, mask = mask)
    
    return CropROI(res).shape[1]

def CalcVerticalDiameter(file, lower, upper):
    #Load image
    img = cv.imread(file, 0)
    #Denoise image
    dst = cv.fastNlMeansDenoising(img)
    #Isolating pixels
    mask = cv.inRange(dst, lower, upper)
    res = cv.bitwise_and(dst, dst, mask = mask)
    
    return CropROI(res).shape[0]

#############################
#Calculating center position#
#############################
def CalcCentrePosition(file, lower, upper):
    #Load image
    img = cv.imread(file, 0)
    #Denoise image
    dst = cv.fastNlMeansDenoising(img)
    #Isolating pixels
    mask = cv.inRange(dst, lower, upper)
    res = cv.bitwise_and(dst, dst, mask = mask)
    
    for i in range(resolution[1]):
        currentRow = res[i]
        prevRow = res[i-1]
        if currentRow.any() and not prevRow.any():
            topBound = i
            break

    for i in range(resolution[1]-2, 0, -1):
        currentRow = res[i]
        prevRow = res[i+1]
        if currentRow.any() and not prevRow.any():
            botBound = i
            break

    rotateCCW = np.rot90(res)
    for i in range(resolution[0]):
        currentRow = rotateCCW[i]
        prevRow = rotateCCW[i-1]
        if currentRow.any() and not prevRow.any():
            rightBound = resolution[0]-i
            break

    for i in range(resolution[0]-2, 0, -1):
        currentRow = rotateCCW[i]
        prevRow = rotateCCW[i+1]
        if currentRow.any() and not prevRow.any():
            leftBound = resolution[0]-i
            break
        
    xCentre = leftBound + (rightBound-leftBound)/2
    yCentre = topBound + (botBound-topBound)/2
    
    return (int(xCentre), int(yCentre))

#######
#Tests#
#######
#Original image
##cv.imshow('original', img)
#Denoised imaged
##cv.imshow('denoise', dst)
#Processed image
##cv.imshow('processed', res)
#Cropped image
##cv.imshow('cropped', CropROI(res))

#Horizontal Diameter
##print('Horizontal Diameter: ', CalcHorizontalDiameter(res))
#Vertical Diameter
##print('Vertical Diameter: ', CalcVerticalDiameter(res))

#Center Position
##print('Centre Position: ', CalcCentrePosition(res))

#Draw circle
##res = cv.circle(res, CalcCentrePosition(res), 1, 255, -1)
##cv.imshow('centre', res)
##
##cv.waitKey(0)
##cv.destroyAllWindows()
