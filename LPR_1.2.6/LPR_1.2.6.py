#-*- coding: utf-8 -*-
import LPRClient
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
import motion_detector



def main_image():
    # insert image and convert 
    image = cv2.imread("1.png")    
    
    main_Process(image)    
    
    cv2.waitKey(0)

def main_video():
    # insert video and convert 
    #cap = cv2.VideoCapture('rtsp://192.168.100.236:554/PSIA/Streaming/channels/0')
    cap = cv2.VideoCapture('C:/Users/yang/Desktop/green3.avi')
    GlobalCounters.carCount = 0
    while(cap.isOpened()):
        ret, image = cap.read()
        main_Process(image)
        key = cv2.waitKey(1) & 0xFF        
        if key == ord("h"):
            input = preprocessing.check_help()
            image_temp = cv2.resize(image,(640,360))
            if len(GlobalCounters.refPt) > 0 and input ==2:
                del GlobalCounters.refPt[:]
                GlobalCounters.GlobalRoi = None
            if len(GlobalCounters.refPt_moving)>0 and input ==1:
                del GlobalCounters.refPt_moving[:]
                del GlobalCounters.movingPos[:]
            preprocessing.setPos_and_roi(image,image_temp,input)            
            GlobalCounters.cropping = False             
            GlobalCounters.GlobalImage = None

    cap.release()
    cv2.destroyAllWindows()

def main_Process(image):
    
    no_rows = image.shape[0];
    no_cols = image.shape[1];
    image_ori = image.copy()
   #image = image[no_rows/6:no_cols/3, no_rows/2:no_cols]
    image = cv2.resize(image,(640,360))
    #cv2.rectangle(img,(savelist[i][1].start,savelist[i][0].start),(savelist[i][1].stop,savelist[i][0].stop),(255,0,0),1)
    
    motion ,detect_frame = motion_detector.motion_detection(image,image_ori)        
    #print motion
    #print motion
    if motion :               
        if motion ==3:
            blob_recog.segment_result(1,detect_frame)                  
            del GlobalCounters.previe_posList[:]
            del GlobalCounters.result_conf[:]
            del GlobalCounters.result_text[:]                       
            del GlobalCounters.result_char [:]
            del GlobalCounters.result_char_conf [:]        
            del GlobalCounters.tasseract_1char_conf[:]
            del GlobalCounters.tasseract_1char_text[:]              
            blob_recog.segment_green_result()
            del GlobalCounters.green_f_text [:]
            del GlobalCounters.green_f_conf  [:]
            del GlobalCounters.green_f_number_text  [:]
            del GlobalCounters.green_f_number_conf  [:]

            del GlobalCounters.green_s_number_text   [:]
            del GlobalCounters.green_s_number_conf   [:]
            del GlobalCounters.green_number_conf [:]
            del GlobalCounters.green_number_text [:]
        times = time.clock()
        # ROI 
        if len(GlobalCounters.refPt) >0 :
            detect_frame = detect_frame[GlobalCounters.refPt[0][1]:GlobalCounters.refPt[1][1], GlobalCounters.refPt[0][0]:GlobalCounters.refPt[1][0]]             
        else :
            detect_frame = detect_frame[no_rows/6:no_cols/3, no_rows/2:no_cols]        
        cv2.imshow("test",detect_frame)
        #cv2.imwrite('detect_frame'+str(times)+'.png',detect_frame) 
        grayImage = cv2.cvtColor(detect_frame,cv2.COLOR_RGB2GRAY)
    
        #input image row,cols
        no_rows = detect_frame.shape[0]
        no_cols = detect_frame.shape[1]
    
        DoG = preprocessing.DoG_Filter_for_white(grayImage)
        th2 = preprocessing.Th_(DoG)
        DoG_green = preprocessing.DoG_Filter(grayImage)
        #th2_gg = preprocessing.Th_(DoG_green)
        #cv2.imshow("DOG",th2)
        #cv2.imshow("DOG_Green",th2_gg)
        result,countNumber,blobs = Plate_detector.segment_on_dt(th2)
        pos = Plate_detector.getPos(blobs)
        bsize = Plate_detector.getBSize(blobs)
        distances = Plate_detector.getDistance(pos)
        blobs = Plate_detector.eraseBlobs(blobs,pos,bsize,distances)

        if len(blobs) < 4 or len(blobs) > 10:                        
            lower_green = np.array([0,15,0])
            upper_green = np.array([25,60,15])
            mask = cv2.inRange(detect_frame, lower_green, upper_green)

            #res = cv2.bitwise_and(img,img, mask= mask)
            ori = detect_frame.copy()
            Plate_detector.sement_on_dt_greenresult(mask,ori)
            #cv2.imshow("mask",mask)
            #여기 초록색

        if len(blobs) >= 4 and len(blobs) <=10:   
           m,maxWidth,maxHeight,src_t = preprocessing.getPT(blobs)          
           ratio = maxWidth/maxHeight              
           if ratio <= 5 and ratio >= 2:   
                warp = cv2.warpPerspective(result,m,(maxWidth,maxHeight))        
                GlobalCounters.previe_posList.append(src_t[0][0])                 
                ret2,th =cv2.threshold(warp,10,255,cv2.THRESH_BINARY); 
                kernel = np.ones((3,3),np.uint8)
                erosion = cv2.erode(th,kernel,iterations = 1)
                kernel = np.ones((5,5),np.uint8)
                dilation = cv2.dilate(erosion,kernel,iterations = 1)
                th = 255 -dilation                
                result,countNumber,blobs = blob_recog.segment_on_number(dilation,1)     
                blob_recog.segment_all(dilation)                
                #conf_t ,text_t = plate_recog.recg_all_text(th)
                #print text_t                
                cv2.imshow("warp",th)              

    #cv2.imshow("ori",image_ori)  
    #GlobalCounters.carSituation == 0

if __name__ == '__main__':
    #main_image()
    LPRClient.connectServer()
    main_video()
    LPRClient.closeServer()
    #test()
