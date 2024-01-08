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


def transKorea(str_char):        
    if str_char == "ga" :
        return "��"
    if str_char == "na" :
        return "��"
    if str_char == "da" :
        return "��"
    if str_char == "la" :
        return "��"
    if str_char == "ma" :
        return "��"
    if str_char == "gu" :
        return "��"
    if str_char == "nu" :
        return "��"
    if str_char == "du" :
        return "��"
    if str_char == "lu" :
        return "��"
    if str_char == "mu" :
        return "��"
    if str_char == "bu" :
        return "��"
    if str_char == "su" :
        return "��"
    if str_char == "uh" :
        return "��"
    if str_char == "ju" :
        return "��"
    if str_char == "go" :
        return "��"
    if str_char == "no" :
        return "��"
    if str_char == "do" :
        return "��"
    if str_char == "lo" :
        return "��"
    if str_char == "mo" :
        return "��"
    if str_char == "bo" :
        return "��"
    if str_char == "so" :
        return "��"
    if str_char == "oh" :
        return "��"
    if str_char == "jo" :
        return "��"
    if str_char == "nn" :
        return "��"
    if str_char == "gg":
        return "��"
    if str_char == "dd" :
        return "��"
    if str_char == "ll" :
        return "��"
    if str_char == "mm" :
        return "��"
    if str_char == "bb" :
        return "��"
    if str_char == "ss" :
        return "��"
    if str_char == "oo" :
        return "��"
    if str_char == "jj" :
        return "��"
    if str_char == "ah" :
        return "��"
    if str_char == "ba" :
        return "��"
    if str_char == "sa" :
        return "��"
    if str_char == "ja" :
        return "��"
    if str_char == "ha" :
        return "��"
    if str_char == "hu" :
        return "��"
    if str_char == "ho" :
        return "ȣ"
    if str_char == "bt" :
        return "��"
    str_char == "^^"

def transEng(str_char):        
    if str_char == "��" :
        return "ga"
    if str_char == "��" :
        return "na"
    if str_char == "��" :
        return "da"
    if str_char == "��" :
        return "la"
    if str_char == "��" :
        return "ma"
    if str_char == "��" :
        return "gu"
    if str_char == "��" :
        return "nu"
    if str_char == "��" :
        return "du"
    if str_char == "��" :
        return "lu"
    if str_char == "��" :
        return "mu"
    if str_char == "��" :
        return "bu"
    if str_char == "��" :
        return "su"
    if str_char == "��" :
        return "uh"
    if str_char == "��" :
        return "ju"
    if str_char == "��" :
        return "go"
    if str_char == "��" :
        return "no"
    if str_char == "��" :
        return "do"
    if str_char == "��" :
        return "lo"
    if str_char == "��" :
        return "mo"
    if str_char == "��" :
        return "bo"
    if str_char == "��" :
        return "so"
    if str_char == "��" :
        return "oh"
    if str_char == "��" :
        return "jo"
    if str_char == "��" :
        return "nn"
    if str_char == "��":
        return "gg"
    if str_char == "��" :
        return "dd"
    if str_char == "��" :
        return "ll"
    if str_char == "��" :
        return "mm"
    if str_char == "��" :
        return "bb"
    if str_char == "��" :
        return "ss"
    if str_char == "��" :
        return "oo"
    if str_char == "��" :
        return "jj"
    if str_char == "��" :
        return "ah"
    if str_char == "��" :
        return "ba"
    if str_char == "��" :
        return "sa"
    if str_char == "��" :
        return "ja"
    if str_char == "��" :
        return "ha"
    if str_char == "��" :
        return "hu"
    if str_char == "ȣ" :
        return "ho"
    if str_char == "��" :
        return "bt"
    str_char == "^^"

def reshapeText(_num,_char):
    reshaped = ""
    test = "^^"
    try :
        if len(_num) >0:
            for i in range(0,len(_num)):
                #reshaped.append(_text[i][0])
                reshaped=reshaped+_num[i][0]
            if _char == [] :
                reshaped = reshaped[:2]+test+reshaped[2:]
            else :
                char_text = transKorea(_char[0][0][0]+_char[0][0][1])
                reshaped = reshaped[:2]+char_text+reshaped[2:]
        return reshaped
    except :
        return "^^"

def setResult(conf_t,text_t):    
    global result_conf
    result_conf.insert(len(result_conf)-1,conf_t)
    global result_text
    result_text.insert(len(result_text)-1,text_t)

def recg_text(image):
    #### you may need to thicken the border in order to make tesseract feel happy to ocr your image #####
    offset=20
    height,width = image.shape
    image1=cv2.copyMakeBorder(image,offset,offset,offset,offset,cv2.BORDER_CONSTANT,value=(255,255,255)) 

    api = tesseract.TessBaseAPI()
    api.Init(".","charOnly",tesseract.OEM_DEFAULT)
    #api.SetPageSegMode(tesseract.PSM_SINGLE_CHAR)
    api.SetPageSegMode(tesseract.PSM_SINGLE_BLOCK)
    #api.SetPageSegMode(tesseract.PSM_AUTO)
    height1,width1=image1.shape
    #print image1.shape
    #print image1.dtype.itemsize
    width_step = width*image1.dtype.itemsize
    #print width_step
    #method 1 
    iplimage = cv.CreateImageHeader((width1,height1), cv.IPL_DEPTH_8U,1)
    cv.SetData(iplimage, image1.tostring(),image1.dtype.itemsize * 1 * (width1))
    tesseract.SetCvImage(iplimage,api)
  #  if (float(width) / float(height) > 0.68) and (float(width) / float(height)) <0.90 :
    text=api.GetUTF8Text()
    conf=api.MeanTextConf()
    image=None
    #print "..............."
    #print "Ocred Text: %s"%text
    #print "Cofidence Level: %d %%"%conf
        

    return conf,text

def recg_number(image0):
    #### you may need to thicken the border in order to make tesseract feel happy to ocr your image #####
    offset=20
    height,width = image0.shape
    image1=cv2.copyMakeBorder(image0,offset,offset,offset,offset,cv2.BORDER_CONSTANT,value=(255,255,255)) 
    #cv2.namedWindow("Test")
    #cv2.imshow("Test", image1)
    #cv2.waitKey(0)
    #cv2.destroyWindow("Test")
    #####################################################################################################
    api = tesseract.TessBaseAPI()
    api.Init(".","number1",tesseract.OEM_DEFAULT)
    #api.SetPageSegMode(tesseract.PSM_SINGLE_CHAR)
    api.SetPageSegMode(tesseract.PSM_SINGLE_BLOCK)
    height1,width1=image1.shape
    #print image1.shape
    #print image1.dtype.itemsize
    width_step = width*image1.dtype.itemsize
    #print width_step
    #method 1 
    
    iplimage = cv.CreateImageHeader((width1,height1), cv.IPL_DEPTH_8U, 1)
    cv.SetData(iplimage, image1.tostring(),image1.dtype.itemsize * 1 * (width1))
    tesseract.SetCvImage(iplimage,api)

    text=api.GetUTF8Text()
    conf=api.MeanTextConf()
    image=None
    #print "..............."
    #print "Ocred Text: %s"%text
   # print "Cofidence Level: %d %%"%conf

    #method 2:
    cvmat_image=cv.fromarray(image1)
    iplimage =cv.GetImage(cvmat_image)
    #print iplimage

    tesseract.SetCvImage(iplimage,api)
    #api.SetImage(m_any,width,height,channel1)
    text=api.GetUTF8Text()
    conf=api.MeanTextConf()
    image=None
    #print "..............."
  #  print "Ocred Text: %s"%text
#    print "Cofidence Level: %d %%"%conf
    api.End()
        

    return conf,text

def recg_all_text(image0):
    #### you may need to thicken the border in order to make tesseract feel happy to ocr your image #####
    offset=20
    height,width = image0.shape
    image1=cv2.copyMakeBorder(image0,offset,offset,offset,offset,cv2.BORDER_CONSTANT,value=(255,255,255)) 
    #cv2.namedWindow("Test")
    #cv2.imshow("Test", image1)
    #cv2.waitKey(0)
    #cv2.destroyWindow("Test")
    #####################################################################################################
    api = tesseract.TessBaseAPI()
    api.Init(".","ultcarplate",tesseract.OEM_DEFAULT)
    #api.SetPageSegMode(tesseract.PSM_SINGLE_CHAR)
    api.SetPageSegMode(tesseract.PSM_AUTO)
    height1,width1=image1.shape
    #print image1.shape
    #print image1.dtype.itemsize
    width_step = width*image1.dtype.itemsize
    #print width_step
    #method 1 
    
    iplimage = cv.CreateImageHeader((width1,height1), cv.IPL_DEPTH_8U, 1)
    cv.SetData(iplimage, image1.tostring(),image1.dtype.itemsize * 1 * (width1))
    tesseract.SetCvImage(iplimage,api)

    text=api.GetUTF8Text()
    conf=api.MeanTextConf()
    image=None
    #print "..............."
    #print "Ocred Text: %s"%text
   # print "Cofidence Level: %d %%"%conf

    #method 2:
    cvmat_image=cv.fromarray(image1)
    iplimage =cv.GetImage(cvmat_image)
    #print iplimage

    tesseract.SetCvImage(iplimage,api)
    #api.SetImage(m_any,width,height,channel1)
    text=api.GetUTF8Text()
    conf=api.MeanTextConf()
    image=None
    #print "..............."
  #  print "Ocred Text: %s"%text
#    print "Cofidence Level: %d %%"%conf
    api.End()
        

    return conf,text


