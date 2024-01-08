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
import plate_recog
import preprocessing
import Plate_detector
import blob_recog



def drawlines (image, pts0, pts1, color):
    for pt0, pt1 in zip(pts0, pts1):
        cv2.line(image,(pt0[0],pt0[1]),(pt1[0],pt1[1]),color,thickness=2);

def calcFlowLib (prev, curr, points):
    #OPTICAL FLOW USING OPENCV IMPLEMENTATION
    currpts = np.reshape(points,(-1,1,2));
    lk_params = dict(winSize=(41,41), maxLevel=0, criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,10,0.03));
    nextpts, stat, err = cv2.calcOpticalFlowPyrLK(prev,curr,currpts,None,**lk_params);
    nextpts = np.reshape(nextpts,(-1,2));
    return nextpts;

def calcFlow (im1, im2, points, halfwin=(10,10)):
    #MY OWN IMPLEMENTATION
    pts = np.copy(points)
    npts = points.shape[0]

    i_x = np.zeros(im1.shape)
    i_y = np.zeros(im1.shape)
    i_t = np.zeros(im1.shape)
    i_x[1:-1, 1:-1] = (im1[1:-1, 2:] - im1[1:-1, :-2]) / 2
    i_y[1:-1, 1:-1] = (im1[2:, 1:-1] - im1[:-2, 1:-1]) / 2
    i_t[1:-1, 1:-1] = im2[1:-1, 1:-1] - im1[1:-1, 1:-1]


    for i in xrange(0,npts,1):
        p = np.reshape(pts[i],(2,1))

        ix = i_x[p[1]-halfwin[1]:p[1]+halfwin[1]+1,p[0]-halfwin[0]:p[0]+halfwin[0]+1]
        iy = i_y[p[1]-halfwin[1]:p[1]+halfwin[1]+1,p[0]-halfwin[0]:p[0]+halfwin[0]+1]            
        it = i_t[p[1]-halfwin[1]:p[1]+halfwin[1]+1,p[0]-halfwin[0]:p[0]+halfwin[0]+1]

        ixx = ix*ix
        iyy = iy*iy
        ixy = ix*iy
        ixt = ix*it
        iyt = iy*it

        G = np.array([[np.sum(ixx),np.sum(ixy)],[np.sum(ixy),np.sum(iyy)]],dtype=np.float32)
        B = np.array([[np.sum(ixy)],[np.sum(iyt)]],dtype=np.float32)
        vel = np.linalg.lstsq(G,B)[0]
        pts[i] = pts[i] + np.ravel(vel)        

    return pts

def motion_detection(cap,image_ori) :
    if len(GlobalCounters.refPt_moving) ==4:
        prevpts0 = np.array([[GlobalCounters.refPt_moving[1][0],GlobalCounters.refPt_moving[1][1]],[GlobalCounters.refPt_moving[0][0],GlobalCounters.refPt_moving[0][1]]],dtype=np.float32)
        prevpts1 = np.array([[GlobalCounters.refPt_moving[3][0],GlobalCounters.refPt_moving[3][1]],[GlobalCounters.refPt_moving[2][0],GlobalCounters.refPt_moving[2][1]]],dtype=np.float32)
    else :
        prevpts0 = np.array([[580,150],[450,100]],dtype=np.float32)
        prevpts1 = np.array([[500,200],[300,150]],dtype=np.float32)
     
    frame = cap;
    if GlobalCounters.startCar ==1:
            GlobalCounters.startCarNext += 1
            #print GlobalCounters.startCarNext
                 
  
    frame_resize = cv2.resize(frame,(640,360))
    GlobalCounters.currgray = cv2.cvtColor(frame_resize,cv2.COLOR_BGR2GRAY)

    if(GlobalCounters.prevgray is not None):
           # print GlobalCounters.startCarNext     
        currpts0 = calcFlowLib(GlobalCounters.prevgray,GlobalCounters.currgray,prevpts0)
        drawlines(frame_resize,prevpts0,currpts0,(0,255,0)) 
        currpts1 = calcFlowLib(GlobalCounters.prevgray,GlobalCounters.currgray,prevpts1)   
        
        if np.abs(currpts1[0][0] - prevpts1[0][0]) > GlobalCounters.Moving_Sensitive and np.abs(currpts1[0][1] - prevpts1[0][1]) >GlobalCounters.Moving_Sensitive  and np.abs(currpts1[1][0] - prevpts1[1][0]) > 0.51  and np.abs(currpts1[1][1] - prevpts1[1][1]) > GlobalCounters.Moving_Sensitive and np.abs(currpts0[0][0] - prevpts0[0][0]) > GlobalCounters.Moving_Sensitive and np.abs(currpts0[0][1] - prevpts0[0][1]) > 0.51 and np.abs(currpts0[1][0] - prevpts0[1][0]) > GlobalCounters.Moving_Sensitive and np.abs(currpts0[1][1] - prevpts0[1][1]) > GlobalCounters.Moving_Sensitive and GlobalCounters.startCar ==0:                                 
            GlobalCounters.carCondition = 1            
            GlobalCounters.startCar = 1            
            print "start car"
            GlobalCounters.Temp_StartFrame = image_ori;
            #cv2.imwrite(str(np.abs(currpts1[0][0] - prevpts1[0][0]))+'.png',image_ori)
            #cv2.imshow("capture",image_ori)
            return 1 ,image_ori;          
        #print np.abs(currpts1[0][0] - prevpts1[0][0]) 
        if GlobalCounters.carCondition ==1 and np.abs(currpts1[0][0] - prevpts1[0][0]) < GlobalCounters.Stop_Sensitive and np.abs(currpts1[0][1] - prevpts1[0][1]) <GlobalCounters.Stop_Sensitive and np.abs(currpts1[1][0] - prevpts1[1][0]) < GlobalCounters.Stop_Sensitive and np.abs(currpts1[1][1] - prevpts1[1][1]) <GlobalCounters.Stop_Sensitive and np.abs(currpts0[0][0] - prevpts0[0][0]) <GlobalCounters.Stop_Sensitive and np.abs(currpts0[0][1] - prevpts0[0][1]) <GlobalCounters.Stop_Sensitive and np.abs(currpts0[1][0] - prevpts0[1][0]) <GlobalCounters.Stop_Sensitive and np.abs(currpts0[1][1] - prevpts0[1][1]) <GlobalCounters.Stop_Sensitive:                    
            if GlobalCounters.startCarNext > 10:
                  GlobalCounters.startCarNext =0
                  GlobalCounters.startCar =0
                  GlobalCounters.carCondition = 0                       
                  GlobalCounters.carSituation == 1
                  GlobalCounters.carCount +=1
                  print "end car"
                  return 3, image_ori
            return 2, image_ori;  

        drawlines(frame_resize,prevpts1,currpts1,(0,0,255))
        prevpts0 = np.copy(currpts0) 
        prevpts1 = np.copy(currpts1)                
    GlobalCounters.prevgray = np.copy(GlobalCounters.currgray)
    cv2.imshow("ttttt",frame_resize)
    if GlobalCounters.startCar ==1 :
        return 1,image_ori
    return 0,0

