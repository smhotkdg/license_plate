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

def getMedian(pos_ori,x):
    pos = []
    if len(pos_ori) ==0:
        return -1
    for i in range(0,len(pos_ori)):
        if x==1 :
            pos.append(pos_ori[i][0])
        else :
            pos.append(pos_ori[i][1])
    pos.sort()   
    return pos[len(pos)/2]          

def eraseBlobs(blobs,pos,b_size,distance):    
    removelist=[]
    x_mid, y_mid = 0,0
    for i in range(0,len(blobs)):
        if distance[i] > 50:
            removelist.append(i)
            
    for i in range(len(removelist),0,-1):
        blobs.pop(removelist[i-1])
        pos.pop(removelist[i-1])
        b_size.pop(removelist[i-1])
        distance.pop(removelist[i-1])
    # true false cheak
    removelist=[]
    x_mid = getMedian(pos,1)
    y_mid = getMedian(pos,0)

    if (x_mid !=-1) and (y_mid != -1):
        for i in range(0,len(blobs)):
            if (numpy.abs(pos[i][1]-y_mid)> 30) or (numpy.abs(pos[i][0]-x_mid)>300):
                removelist.append(i)
    for i in range(len(removelist),0,-1):
        blobs.pop(removelist[i-1])
        pos.pop(removelist[i-1])
        b_size.pop(removelist[i-1])
        distance.pop(removelist[i-1])
    return blobs

def getEuclidean(a,b):
    return distance.euclidean(a,b)

def getBSize(blobs):
    bsize = []
    for i in range(0,len(blobs)):
        bsize.append(((blobs[i][1].stop-blobs[i][1].start),(blobs[i][0].stop-blobs[i][0].start)))
    return bsize

def getPos(blobs):
    pos = []
    for i in range(0,len(blobs)):
        pos.append((((blobs[i][1].start+blobs[i][1].stop)/2),((blobs[i][0].start+blobs[i][0].stop)/2)))
    return pos

def getDistance(pos):
    distances = []
    for i in range(0,len(pos)):
        min_distance = 10000
        for j in range(0,len(pos)):
            if j==i:
                continue
            distance_euclidean = getEuclidean(pos[i],pos[j])
            if distance_euclidean < min_distance :
                min_distance = distance_euclidean
        distances.append(min_distance)
    return distances

def segment_on_dt_green(img):      
    lbl, ncc = label(img)
    NumberCount = 0
    blobs = ndimage.find_objects(lbl)
    
    savelist = []
    for i,j in enumerate(blobs):    
        
        rows = lbl[j].shape[0]
        cols = lbl[j].shape[1]
        #cnt = sum(sum(lbl[j]))
        cnt = (lbl[j]!=0).sum()
        #for y in range(0,rows):
        #    for x in range(0,cols):
        #        cnt = cnt + lbl[j][y][x]
       # print "i rows , cols ", i, rows, cols
        #if rows >20 and rows < 60:
        if cnt>100 and cnt<800:
            if rows >20 and rows < 60:
                if float(cols)/rows < 1.0:
                    NumberCount += 1
                    #plt.imsave('ablob'+str(i)+'.png',lbl[j])
                    #cv2.waitKey(0)
                    savelist.append(j)
                    #lbl[j]를 새이미지로 복사

                    #cv2.rectangle(lbl,(j[1].start,j[0].start),(j[1].stop,j[0].stop),(255,255,255),1)

    if len(savelist) >=4 :
        for i in range(0,len(savelist)):
            #plt.imsave('blob'+str(i)+'.png',lbl[savelist[i]])
            x = (savelist[i][1].start+savelist[i][1].stop-1)/2
            y = (savelist[i][0].start+savelist[i][1].stop-1)/2
            #cv2.rectangle(img,(savelist[i][1].start,savelist[i][0].start),(savelist[i][1].stop,savelist[i][0].stop),(255,0,0),1)
            
            #print x, y
    lbl[lbl!=0]=255
    lbl = lbl.astype(numpy.uint8)    
    #print "number of lables :" ,ncc
    return  lbl ,NumberCount,savelist

def segment_on_dt(img):           
    lbl, ncc = label(img)    
    NumberCount = 0
    blobs = ndimage.find_objects(lbl)
    savelist = []
    for i,j in enumerate(blobs):                
        rows = lbl[j].shape[0]
        cols = lbl[j].shape[1]
       # print "i rows , cols ", i, rows, cols
        if rows >20 and rows < 60 :
            if float(cols)/rows < 1.0:
                NumberCount += 1
                #plt.imsave('blob'+str(i)+'.png',lbl[j])
                savelist.append(j)

    if len(savelist) >=4 :
        for i in range(0,len(savelist)):
            #plt.imsave('blob'+str(i)+'.png',lbl[savelist[i]])
            x = (savelist[i][1].start+savelist[i][1].stop-1)/2
            y = (savelist[i][0].start+savelist[i][1].stop-1)/2
            #cv2.rectangle(img,(savelist[i][1].start,savelist[i][0].start),(savelist[i][1].stop,savelist[i][0].stop),(255,0,0),1)
            
            #print x, y
            
    
    lbl = lbl.astype(numpy.uint8)    
    #print "number of lables :" ,ncc
    return  lbl ,NumberCount,savelist

def sement_on_dt_greenresult(img,ori):
    lbl, ncc = label(img)
    NumberCount = 0
    blobs = ndimage.find_objects(lbl)
    
    savelist = []
    for i,j in enumerate(blobs):            
        rows = lbl[j].shape[0]
        cols = lbl[j].shape[1]
        cnt = sum(sum(lbl[j]))
        cnt = (lbl[j]!=0).sum()
        NumberCount += 1
        
        if rows * cols > 8000  and float(cols)/rows >1 and cnt > 7000 :            
            #cv2.imwrite(str(cnt)+"blobTest.png",lbl[j])
            savelist.append(j)

    if len(savelist) ==1 :
        #for i in range(0,len(savelist)):
        x = (savelist[0][1].start+savelist[0][1].stop-1)/2
        y = (savelist[0][0].start+savelist[0][1].stop-1)/2    
        lbl = lbl.astype(numpy.uint8)    
        ori = ori[savelist[0][0].start:savelist[0][0].stop, savelist[0][1].start:savelist[0][1].stop]     
        #cv2.imshow("ori",ori)
        grayImage = cv2.cvtColor(ori,cv2.COLOR_RGB2GRAY)
        forDoG1 = cv2.GaussianBlur(grayImage,(3,3),0);
        forDoG2 = cv2.GaussianBlur(grayImage,(27,27),0);
        DoG = cv2.subtract(forDoG1,forDoG2);
        ret2,th =cv2.threshold(DoG,0,255,cv2.THRESH_BINARY);
        #plt.imsave('ablobth'+str(x+y)+'.png',th)    
        cv2.imshow("test",th)
        find_blob_green(th)
    lbl[lbl!=0]=255

def find_blob_green(img):
    lbl, ncc = label(img)
    NumberCount = 0
    blobs = ndimage.find_objects(lbl)
    save_blob = []
    for i,j in enumerate(blobs):            
        rows = lbl[j].shape[0]
        cols = lbl[j].shape[1]
        #cnt = sum(sum(lbl[j])) 
        cnt = (lbl[j]!=0).sum()
        if rows * cols > 300  and float(cols)/rows >0.2 and float(cols)/rows <  1.2 and cnt > 200 and  rows < 60 and cols < 40:
            NumberCount += 1                
            temp = lbl[j].astype(numpy.uint8)    
            ret2,th =cv2.threshold(temp,0,255,cv2.THRESH_BINARY);              
            th = 255-th            
            save_blob.append(th)
            
    #if len(save_blob) >7:
    #    del save_blob[:]
    #    for i,j in enumerate(blobs):            
    #        rows = lbl[j].shape[0]
    #        cols = lbl[j].shape[1]
    #        cnt = sum(sum(lbl[j])) 
    #        cnt = (lbl[j]!=0).sum()
    #        if rows * cols > 300  and float(cols)/rows >0.2 and float(cols)/rows <  1.2 and cnt > 150 and  rows < 60 and cols < 40 and cnt > 400:
    #            NumberCount += 1                
    #            temp = lbl[j].astype(numpy.uint8)    
    #            ret2,th =cv2.threshold(temp,0,255,cv2.THRESH_BINARY);              
    #            th = 255-th
    #            cv2.imwrite(str(cnt)+'.png',th)
    #            save_blob.append(th)
    result= []
    if len(save_blob) ==7:
        for i in range(0,len(save_blob)):
            if i ==0 or i ==1:                
                conf,text  = plate_recog.recg_number(save_blob[i])                                
                if len(GlobalCounters.green_f_number_conf) <2:
                    GlobalCounters.green_f_number_text.append(text)
                    GlobalCounters.green_f_number_conf.append(conf)       
                else :                    
                    if GlobalCounters.green_f_number_conf[i] < conf:
                        GlobalCounters.green_f_number_conf[i] = conf
                        GlobalCounters.green_f_number_text[i] = text
            if i ==2:
                conf,text  = plate_recog.recg_text(save_blob[i])                                
                if len(GlobalCounters.green_f_conf) ==0:
                    GlobalCounters.green_f_text.append(text)
                    GlobalCounters.green_f_conf.append(conf)
                else :                                        
                    if GlobalCounters.green_f_conf[0] < conf:
                        GlobalCounters.green_f_conf[0] = conf
                        GlobalCounters.green_f_text[0] = text
            if i ==3 or i ==4 or i == 5 or i==6 :
                conf, text = plate_recog.recg_number(save_blob[i])
                if len(GlobalCounters.green_s_number_conf) <4:
                    GlobalCounters.green_s_number_text.append(text)
                    GlobalCounters.green_s_number_conf.append(conf)
                else :                    
                    k = i -3;
                    if GlobalCounters.green_s_number_conf[k] < conf:
                        GlobalCounters.green_s_number_conf[k] = conf
                        GlobalCounters.green_s_number_text[k] = text
    

    if len(save_blob) ==4:
        for i in range(0,4):
            conf, text = plate_recog.recg_number(save_blob[i])
            if len(GlobalCounters.green_number_conf) <4:
                    GlobalCounters.green_number_text.append(text)
                    GlobalCounters.green_number_conf.append(conf)
            else :                                        
                if GlobalCounters.green_number_conf[i] < conf:
                    GlobalCounters.green_number_conf[i] = conf
                    GlobalCounters.green_number_text[i] = text           
      
        