#-*- coding: utf-8 -*-
import numpy
import numpy as np
import tesseract
import cv2
import sys
from os import *
import mahotas as mh
from scipy.ndimage import label
from scipy import ndimage
import matplotlib.pyplot as plt
from scipy.spatial import distance
import tesseract
import cv2.cv as cv
import time
import copy
import GlobalCounters
def fix_image(img, blobs):
      ## blobs_img holds 0 for good pixels and 1 for pixels where an overflow occured
    blobs_img = np.zeros(img.dimensions, img.data.dtype)
    cv2.drawContours( blobs_img, blobs, -1, 1, -1) # fill contour
    cv2.drawContours( blobs_img, blobs, -1, 0, 1) # exclude line
    ## cropped_blobs cuts the pixels where an overflow occured out of the original image
    cropped_blobs = blobs_img * img.data
    ## return an image with values rescaled to half its original value and the blob areas lifted up by 2^(depth-1)
    return ((img.data-cropped_blobs)*.5 + blobs_img*img.data*.5+blobs_img*2**(img.depth-1)).astype(img.data.dtype)


def DoG_Filter(grayImage):
    forDoG1 = cv2.GaussianBlur(grayImage,(3,3),0);
    forDoG2 = cv2.GaussianBlur(grayImage,(27,27),0);
    DoG = cv2.subtract(forDoG1,forDoG2);
    return DoG;

def DoG_Filter_for_white(grayImage):
    forDoG1 = cv2.GaussianBlur(grayImage,(3,3),0);
    forDoG1 = 255- forDoG1
    forDoG2 = cv2.GaussianBlur(grayImage,(27,27),0);
    forDoG2 = 255- forDoG2
    DoG = cv2.subtract(forDoG1,forDoG2);
    return DoG;

def Th_(DoG_image):
    ret2,th =cv2.threshold(DoG_image,10,255,cv2.THRESH_BINARY);
    #return 0 or 1 and th --> 0 is no green license plate
    return th;

def getPT(blobs):
    #src = numpy.zeros_like((4,2),dtype="float32")
    #dst = numpy.zeros_like((4,2),dtype="float32")
    minX=10000;
    maxX=0;    
    for i in range(0,len(blobs)):
        x = (blobs[i][1].start+blobs[i][1].stop)/2
        y = (blobs[i][0].start+blobs[i][0].stop)/2
        if(minX>x):
            minX=x
            minIndex=i
        if(maxX<x):
            maxX=x
            maxIndex=i
    minxx = (blobs[minIndex][1].start+blobs[minIndex][1].stop)/2
    minyy = (blobs[minIndex][0].start+blobs[minIndex][0].stop)/2
    maxxx = (blobs[maxIndex][1].start+blobs[maxIndex][1].stop)/2
    maxyy = (blobs[maxIndex][0].start+blobs[maxIndex][0].stop)/2
    bsize_min_y = blobs[minIndex][0].stop-blobs[minIndex][0].start
    bsize_max_y = blobs[maxIndex][0].stop-blobs[maxIndex][0].start
    if len(blobs)>5:
        src = numpy.array([(minxx-bsize_min_y*0.2,minyy-bsize_min_y*0.6),(maxxx+bsize_max_y*0.5,maxyy-bsize_max_y*0.5),(maxxx+bsize_max_y*0.4,maxyy+bsize_max_y*0.6),(minxx-bsize_min_y*0.4,minyy+bsize_min_y*0.5)],dtype="float32")
        dst = numpy.array([(0,0),(maxxx+bsize_max_y*0.5,0),(maxxx+bsize_max_y*0.5,minyy-bsize_min_y*0.5),(0,minyy-bsize_min_y*0.5)],dtype="float32")
    else:
        src = numpy.array([(minxx-bsize_min_y*1,minyy-bsize_min_y*1.5),(maxxx+bsize_max_y*0.8,maxyy-bsize_max_y*1.3),(maxxx+bsize_max_y*0.5,maxyy+bsize_max_y*0.7),(minxx-bsize_min_y*1.2,minyy+bsize_min_y*0.5)],dtype="float32")
        dst = numpy.array([(0,0),(maxxx+bsize_max_y*0.8,0),(maxxx+bsize_max_y*0.8,minyy-bsize_min_y*0.5),(0,minyy-bsize_min_y*0.5)],dtype="float32")
    
    return cv2.getPerspectiveTransform(src,dst),src[1][0],src[3][1],src

def check_help() :
    print "1. set moving pos"
    print "2. set roi"
    print "3. set Sensitive"
    a = input()    
    if a ==1:
        print "Set moving Pos"
        return 1

    if a == 2:
        print "set roi pos"        
        return 2
    if a == 3:
        print "set Moving Sensitive ", GlobalCounters.Moving_Sensitive
        min = input()    
        GlobalCounters.Moving_Sensitive = min
        print "set Stop Sensitive ", GlobalCounters.Stop_Sensitive
        max = input()    
        GlobalCounters.Stop_Sensitive = max
        print "complete set Sensitive"
        
        
def setPos_and_roi(ori,image,input):

    
    GlobalCounters.GlobalImage = image
    GlobalCounters.GlobalImage_Ori = ori
    
    if input==1:        
        clone = image.copy()
        cv2.namedWindow("image")
        cv2.setMouseCallback("image", click_and_moving)
    elif input==2:       
        clone = ori.copy()
        cv2.namedWindow("image")
        cv2.setMouseCallback("image", click_and_crop)
    elif input ==3:
        print "complete set Sensitive"
    else :
        print "reset"
    if input == 1:
        while True :
            cv2.imshow("image",image)
            key =  cv2.waitKey(1) & 0xFF
            #print len(refPt_moving)
            if len(GlobalCounters.refPt_moving) == 4:
                break        
    if input == 2:
        while True :
            cv2.imshow("image",ori)
            key =  cv2.waitKey(1) & 0xFF  
            if len(GlobalCounters.refPt) ==2:
                break

    if len(GlobalCounters.refPt) ==2 and input ==2:
        GlobalCounters.GlobalRoi = clone[GlobalCounters.refPt[0][1]:GlobalCounters.refPt[1][1], GlobalCounters.refPt[0][0]:GlobalCounters.refPt[1][0]]             
        cv2.imshow("ROI",GlobalCounters.GlobalRoi)	
        cv2.waitKey(0)  

    cv2.destroyAllWindows()
    return 0

def click_and_moving(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:       
        #print x,y
        GlobalCounters.cropping = True
    elif event == cv2.EVENT_LBUTTONUP:
        GlobalCounters.refPt_moving.append(copy.deepcopy((x,y)))
        GlobalCounters.cropping = False
        cv2.circle(GlobalCounters.GlobalImage,(GlobalCounters.refPt_moving[len(GlobalCounters.refPt_moving)-1][0],GlobalCounters.refPt_moving[len(GlobalCounters.refPt_moving)-1][1]),2,(0,0,255),-2)        
        cv2.imshow("image",GlobalCounters.GlobalImage)

def click_and_crop(event,x,y,flags,param):    
    if event == cv2.EVENT_LBUTTONDOWN:
        GlobalCounters.refPt = [(x,y)]
        #print x,y
        GlobalCounters.cropping = True
    elif event == cv2.EVENT_LBUTTONUP:
        GlobalCounters.refPt.append((x,y))
        GlobalCounters.cropping = False
        cv2.rectangle(GlobalCounters.GlobalImage_Ori ,GlobalCounters.refPt[0],GlobalCounters.refPt[1],(0,0,255),2)
        cv2.imshow("image",GlobalCounters.GlobalImage_Ori )
