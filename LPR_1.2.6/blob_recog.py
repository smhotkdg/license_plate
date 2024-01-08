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
import os
import time
import copy
import plate_recog
import GlobalCounters
import LPRClient
def segment_on_number(img,carSituation):          
    lbl, ncc = label(img)
    NumberCount = 0
    blobs = ndimage.find_objects(lbl)
    global result_conf
    global result_text

    savelist = []
    
    for i,j in enumerate(blobs):                
        rows = lbl[j].shape[0]
        cols = lbl[j].shape[1]
        if float(cols)/rows < 1.0 and cols* rows > 300:
            #plt.imsave('blob'+str(i)+'.png',lbl[j])
            NumberCount += 1
            savelist.append(j)
    
    # Using white plate detection    
    savelist.sort()
    result_list = []
    blob_list = []
    tmep_list = []
    text_input = []
    rect_list = []
    times = time.clock()
    if len(savelist) >6 and len(savelist) < 9 :        
        for i in range(0,len(savelist)):                                                     
            x = (savelist[i][1].start+savelist[i][1].stop-1)/2
            y = (savelist[i][0].start+savelist[i][1].stop-1)/2                  
            #cv2.rectangle(img,(savelist[i][1].start,savelist[i][0].start),(savelist[i][1].stop,savelist[i][0].stop),(255,255,255),1)
            if i+1 < len(savelist) :
                #if savelist[i][1].start > savelist[i+1][0].stop or savelist[i][0].start > savelist[i+1][1].stop:                    
                rect = (min(savelist[i][1].start,savelist[i+1][1].stop),min(savelist[i][0].start,savelist[i+1][0].stop),abs(savelist[i][1].start-savelist[i+1][1].stop),abs(savelist[i][0].start-savelist[i+1][0].stop))                            
                    #text_input.append(roi)
                    #if rect[0] -rect[3] > 40 and rect[0] -rect[3]  < 60 :
                        #cv2.rectangle(img,(min(savelist[i][1].start,savelist[i+1][1].stop),min(savelist[i][0].start,savelist[i+1][0].stop)),(abs(savelist[i][1].start-savelist[i+1][1].stop),abs(savelist[i][0].start-savelist[i+1][0].stop)),(255,255,255))
                roi = img[rect[1]:rect[1]+rect[3], rect[0]:rect[0]+rect[2]]
                #cv2.imwrite('blob'+str(rect[0]-rect[3])+'.png',roi)     
                rect_list.append(rect)                                             
            th_text_input = []
            temp = lbl[savelist[i]].astype(numpy.uint8)    
            ret2,th =cv2.threshold(temp,0,255,cv2.THRESH_BINARY);              
            th = 255-th
            blob_list.append((x,th))
            #cv2.imwrite('blob'+str(times)+'.png',th)                 
            if len(blob_list) >6 and len(blob_list) < 9:                                         
                blob_list.sort(key=lambda x:x[0])           
                #for i  in range(0,len(blob_list)):
                    #cv2.imwrite('blob'+str(i)+'.png',blob_list[i][1])      
                for i in range(0,len(blob_list)):                    
                         temp_conf,temp_text = 0,0
                         temp_text_conf,temp_text_text = 0,0
                         if i !=2:
                            temp_conf,temp_text = plate_recog.recg_number(blob_list[i][1]) 
                         #if temp_conf > 10:                             
                            GlobalCounters.conf.append(temp_conf)
                            GlobalCounters.text.append(temp_text)                      

                if len(savelist) ==7 :        
                        temp_text_conf , temp_text_text = plate_recog.recg_text(blob_list[2][1])      
                        #cv2.imwrite('blob'+str(times)+'.png',blob_list[2][1])      
                        if temp_text_conf > 10:
                            GlobalCounters.text_conf.append(temp_text_conf)
                            GlobalCounters.text_text.append(temp_text_text)  
                else:
                    for i in range(0,len(rect_list)):                                          
                        temp_input = img.copy()  
                        roi = temp_input[rect_list[i][1]:rect_list[i][1]+rect_list[i][3], rect_list[i][0]:rect_list[i][0]+rect_list[i][2]]                        
                        no_rows = roi.shape[0];
                        no_cols = roi.shape[1];
                        if no_cols > 0 and no_rows > 0:                           
                            if no_cols < 50 and no_cols > 20  :
                                ret2,th =cv2.threshold(roi,0,255,cv2.THRESH_BINARY);                                                        
                                th = 255-th
                                th_text_input.append(th)          
                                #text write                  
                                #cv2.imwrite('blob'+str(times)+'.png',th)      
                                #cv2.imshow("test",th)

                    for j in range(0,len(th_text_input)):
                        temp_text_conf , temp_text_text = plate_recog.recg_text(th_text_input[j])
                        if temp_text_conf > 10:
                            GlobalCounters.text_conf.append(temp_text_conf)
                            GlobalCounters.text_text.append(temp_text_text)  
               
                
                
                _result_text =[]
                _result_conf=[]
                _result_char_text= []
                _result_char_conf=[]
                if len(GlobalCounters.conf) ==6 and len(GlobalCounters.text) ==6:
                    GlobalCounters.result_conf.append(copy.deepcopy(GlobalCounters.conf))                
                    GlobalCounters.result_text.append(copy.deepcopy(GlobalCounters.text))

                if len(GlobalCounters.text_conf)==1 and len(GlobalCounters.text_text) ==1:
                    GlobalCounters.result_char.append(copy.deepcopy(GlobalCounters.text_text))
                    GlobalCounters.result_char_conf.append(copy.deepcopy(GlobalCounters.text_conf))

                if carSituation ==1:
                    for i in range(0,len(GlobalCounters.result_conf)):
                        #print len(result_conf[i])
                        if len(GlobalCounters.result_conf[i]) == 6 :
                            for j in range(0,len(GlobalCounters.result_conf[i])):      
                                if i ==0:                          
                                    _result_conf.append(copy.deepcopy(GlobalCounters.result_conf[i][j]))
                                    _result_text.append(copy.deepcopy(GlobalCounters.result_text[i][j]))
                                if len(_result_conf) ==6:                                
                                    if _result_conf[j] < GlobalCounters.result_conf[i][j] :
                                        _result_conf[j] = GlobalCounters.result_conf[i][j]
                                        _result_text[j] = GlobalCounters.result_text[i][j]

                    for i in range(0,len(GlobalCounters.result_char_conf)):
                        if not GlobalCounters.result_char_conf[0]:
                            GlobalCounters.result_char_conf.pop(0)
                            GlobalCounters.result_char.pop(0)

                    for i in range(0,len(GlobalCounters.result_char_conf)):
                       if i ==0 :
                           _result_char_conf.append(copy.deepcopy(GlobalCounters.result_char_conf[i]))
                           _result_char_text.append(copy.deepcopy(GlobalCounters.result_char[i]))
                       if _result_char_conf[0] < GlobalCounters.result_char_conf[i] :
                            _result_char_conf[0] = GlobalCounters.result_char_conf[i]
                            _result_char_text[0] = GlobalCounters.result_char[i]
                        

                    
                    if len(_result_conf) >0: 
                        tasser_1char_conf =None
                        tasser_1char_char = None
                        if len(GlobalCounters.tasseract_1char_conf) >0:
                            for i in range(0,len(GlobalCounters.tasseract_1char_conf)):
                                if i ==0:
                                    tasser_1char_conf = GlobalCounters.tasseract_1char_conf[i]
                                    tasser_1char_char = GlobalCounters.tasseract_1char_text[i]
                                else :
                                    if tasser_1char_conf < GlobalCounters.tasseract_1char_conf[i]:
                                        tasser_1char_conf = GlobalCounters.tasseract_1char_conf[i]
                                        tasser_1char_char = GlobalCounters.tasseract_1char_text[i]

                        #print tasser_1char_conf , tasser_1char_char
                        #print _result_char_conf                
                        eng_char = plate_recog.transEng(tasser_1char_char)
                        #print eng_char                
                        #print len(_result_char_conf)
                        if len(_result_char_conf ) > 0 :
                            if _result_char_conf[0][0] < 85 :
                                if tasser_1char_conf > 45:
                                     text_set =  eng_char + '\n\n'
                                     _result_char_text = [[text_set]]       
                        #    if _result_char_conf[0][0] < 60 :
                        #        if tasser_1char_conf > 60:
                        #            text_set =  eng_char + '\n\n'
                        #            _result_char_text = [[text_set]]       
                        #    if _result_char_conf[0][0] < 70 :
                        #        if tasser_1char_conf > 75:
                        #            text_set =  eng_char + '\n\n'
                        #            _result_char_text = [[text_set]]       
                        #    if _result_char_conf[0][0] < 60 :
                        #        if tasser_1char_conf > 65:
                        #            text_set =  eng_char + '\n\n'
                        #            _result_char_text = [[text_set]]       
                        #    if _result_char_conf[0][0] < 45 :
                        #        if tasser_1char_conf > 50:
                        #            text_set =  eng_char + '\n\n'
                        #            _result_char_text = [[text_set]]       
                        #    if _result_char_conf[0][0] < 50 :
                        #        if tasser_1char_conf > 55:
                        #            text_set =  eng_char + '\n\n'
                        #            _result_char_text = [[text_set]]       
                        elif len(_result_char_conf) ==0:
                              if tasser_1char_conf > 45:
                                text_set =  eng_char + '\n\n'
                                _result_char_text = [[text_set]]                                                  
                        test = plate_recog.reshapeText(_result_text,_result_char_text)                        
                        number_str =0
                        img = 255-img
                        cv2.imwrite(str(GlobalCounters.carCount)+str("-") + str(test)+'.png',img)
                        #print test                    
            
                        
                del GlobalCounters.text_conf[:]
                del GlobalCounters.text_text[:]                
                del GlobalCounters.conf[:]
                del GlobalCounters.text[:]
                #cv2.waitKey(0)
                #         
            
            #cv2.imshow('test',th);
            #cv2.waitKey(0)

    
    
    lbl = lbl.astype(numpy.uint8)    
    #print "number of lables :" ,ncc
    return  lbl ,NumberCount,savelist

def segment_result(carSituation,detect_frame):
       _result_text =[]
       _result_conf=[]
       _result_char_text= []
       _result_char_conf=[]

       #GlobalCounters.result_conf.append(copy.deepcopy(GlobalCounters.conf))                
       #GlobalCounters.result_text.append(copy.deepcopy(GlobalCounters.text))
       #GlobalCounters.result_char.append(copy.deepcopy(GlobalCounters.text_text))
       #GlobalCounters.result_char_conf.append(copy.deepcopy(GlobalCounters.text_conf))
       if carSituation ==1:
            index_list = []
            #for i in range(0,len(GlobalCounters.result_conf)):
            #     if len(GlobalCounters.result_conf[i]) != 6 :
            #         index_list.append(i)
            #for i in range(0,len(index_list)-1):
            #    GlobalCounters.result_conf.pop(index_list[i])
            #    GlobalCounters.result_text.pop(index_list[i])
            for i in range(0,len(GlobalCounters.result_conf)):
                #print len(result_conf[i])
                if len(GlobalCounters.result_conf[i]) == 6 :
                    for j in range(0,len(GlobalCounters.result_conf[i])):      
                        if i ==0:                          
                            _result_conf.append(copy.deepcopy(GlobalCounters.result_conf[i][j]))
                            _result_text.append(copy.deepcopy(GlobalCounters.result_text[i][j]))
                        if len(_result_conf) ==6:                                
                            if _result_conf[j] < GlobalCounters.result_conf[i][j] :
                                _result_conf[j] = GlobalCounters.result_conf[i][j]
                                _result_text[j] = GlobalCounters.result_text[i][j]

            for i in range(0,len(GlobalCounters.result_char_conf)):
                if not GlobalCounters.result_char_conf[0]:
                    GlobalCounters.result_char_conf.pop(0)
                    GlobalCounters.result_char.pop(0)

            for i in range(0,len(GlobalCounters.result_char_conf)):
                if i ==0 :
                    _result_char_conf.append(copy.deepcopy(GlobalCounters.result_char_conf[i]))
                    _result_char_text.append(copy.deepcopy(GlobalCounters.result_char[i]))
                if _result_char_conf[0] < GlobalCounters.result_char_conf[i] :
                    _result_char_conf[0] = GlobalCounters.result_char_conf[i]
                    _result_char_text[0] = GlobalCounters.result_char[i]
                        

                    
            if len(_result_conf) >0:                                                
                tasser_1char_conf =None
                tasser_1char_char = None
                if len(GlobalCounters.tasseract_1char_conf) >0:
                    for i in range(0,len(GlobalCounters.tasseract_1char_conf)):
                        if i ==0:
                            tasser_1char_conf = GlobalCounters.tasseract_1char_conf[i]
                            tasser_1char_char = GlobalCounters.tasseract_1char_text[i]
                        else :
                            if tasser_1char_conf < GlobalCounters.tasseract_1char_conf[i]:
                                tasser_1char_conf = GlobalCounters.tasseract_1char_conf[i]
                                tasser_1char_char = GlobalCounters.tasseract_1char_text[i]

                #print tasser_1char_conf , tasser_1char_char
                #print _result_char_conf                
                eng_char = plate_recog.transEng(tasser_1char_char)
                #print eng_char                
                #print len(_result_char_conf)
                if len(_result_char_conf ) > 0 :
                    if _result_char_conf[0][0] < 80 :
                        if tasser_1char_conf > 45:
                             text_set =  eng_char + '\n\n'
                             _result_char_text = [[text_set]]       
                #    if _result_char_conf[0][0] < 60 :
                #        if tasser_1char_conf > 60:
                #            text_set =  eng_char + '\n\n'
                #            _result_char_text = [[text_set]]       
                #    if _result_char_conf[0][0] < 70 :
                #        if tasser_1char_conf > 75:
                #            text_set =  eng_char + '\n\n'
                #            _result_char_text = [[text_set]]       
                #    if _result_char_conf[0][0] < 60 :
                #        if tasser_1char_conf > 65:
                #            text_set =  eng_char + '\n\n'
                #            _result_char_text = [[text_set]]       
                #    if _result_char_conf[0][0] < 45 :
                #        if tasser_1char_conf > 50:
                #            text_set =  eng_char + '\n\n'
                #            _result_char_text = [[text_set]]       
                #    if _result_char_conf[0][0] < 50 :
                #        if tasser_1char_conf > 55:
                #            text_set =  eng_char + '\n\n'
                #            _result_char_text = [[text_set]]       
                elif len(_result_char_conf) ==0:
                      if tasser_1char_conf > 45:
                        text_set =  eng_char + '\n\n'
                        _result_char_text = [[text_set]]                                  
                   
                #print tt_result
                test = plate_recog.reshapeText(_result_text,_result_char_text)                        
                number_str =0
                #os.mkdir('C:/Users/yang/Desktop/car/'+str(test))                
                cv2.imwrite(str(GlobalCounters.carCount) +str("-")+ str(test) +'.png',GlobalCounters.Temp_StartFrame)
                #print _result_conf
                #print _result_char_conf
                del GlobalCounters.text_conf[:]
                del GlobalCounters.text_text[:]                
                del GlobalCounters.conf[:]
                del GlobalCounters.text[:]
                if len(test) != 0:
                    LPRClient.sendMessage(test)
                print test                            
                return 1
            
                        
                del GlobalCounters.text_conf[:]
                del GlobalCounters.text_text[:]                
                del GlobalCounters.conf[:]
                del GlobalCounters.text[:]
       else :
             return 0

def segment_all(img):
    lbl, ncc = label(img)
    NumberCount = 0
    blobs = ndimage.find_objects(lbl)
    #global result_conf
    #global result_text

    savelist = []
    charlist = []
    for i,j in enumerate(blobs):                
        rows = lbl[j].shape[0]
        cols = lbl[j].shape[1]
        if float(cols)/rows < 1.0 and cols* rows > 300:
            #plt.imsave('blob'+str(i)+'.png',lbl[j])
            NumberCount += 1
            savelist.append(j)
   # print len(savelist)    

    _tasseract_8char_conf = []
    _tasseract_8char_text = []
    if len(savelist) >6 and len(savelist) < 9 :    
        ret2,th =cv2.threshold(img,10,255,cv2.THRESH_BINARY); 
        th = 255 -th    
        #cv2.imshow("tttst",th)
        _tasseract_8char_conf , _tasseract_8char_text = plate_recog.recg_all_text(th)        
        #print "conf ", _tasseract_8char_conf
        
        #_tasseract_8char_text
        if len(_tasseract_8char_text) >7:
            #print _tasseract_8char_text
            str = _tasseract_8char_text[2:4]
            result_str = plate_recog.transKorea(str)
            if result_str != "^^" and result_str !=None:                
                #print result_str
                #print _tasseract_8char_conf
                GlobalCounters.tasseract_1char_text.append(result_str)
                GlobalCounters.tasseract_1char_conf.append(_tasseract_8char_conf)
                
def segment_green(img,ori):
    lbl, ncc = label(img)
    NumberCount = 0
    blobs = ndimage.find_objects(lbl)
    #global result_conf
    #global result_text

    savelist = []
    charlist = []
    for i,j in enumerate(blobs):                
        rows = lbl[j].shape[0]
        cols = lbl[j].shape[1]

def segment_green_result():
     str = []
     number = []
     if len(GlobalCounters.green_f_number_text) !=0:
         number += GlobalCounters.green_f_number_text 
         #print GlobalCounters.green_f_number_text ,   GlobalCounters.green_f_number_conf
         str.append(GlobalCounters.green_f_text)
        #print GlobalCounters.green_f_text , GlobalCounters.green_f_conf
     else :
         number += GlobalCounters.green_number_text
     if len(GlobalCounters.green_s_number_text) !=0:
         number += GlobalCounters.green_s_number_text
         #print   GlobalCounters.green_s_number_text ,   GlobalCounters.green_s_number_conf
     tt = plate_recog.reshapeText(number,str)
     print len(tt)
     if len(tt) != 0:
        LPRClient.sendMessage(tt)
     print tt
