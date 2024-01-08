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
        return "가"
    if str_char == "na" :
        return "나"
    if str_char == "da" :
        return "다"
    if str_char == "la" :
        return "라"
    if str_char == "ma" :
        return "마"
    if str_char == "gu" :
        return "거"
    if str_char == "nu" :
        return "너"
    if str_char == "du" :
        return "더"
    if str_char == "lu" :
        return "러"
    if str_char == "mu" :
        return "머"
    if str_char == "bu" :
        return "버"
    if str_char == "su" :
        return "서"
    if str_char == "uh" :
        return "어"
    if str_char == "ju" :
        return "저"
    if str_char == "go" :
        return "고"
    if str_char == "no" :
        return "노"
    if str_char == "do" :
        return "도"
    if str_char == "lo" :
        return "로"
    if str_char == "mo" :
        return "모"
    if str_char == "bo" :
        return "보"
    if str_char == "so" :
        return "소"
    if str_char == "oh" :
        return "오"
    if str_char == "jo" :
        return "조"
    if str_char == "nn" :
        return "누"
    if str_char == "gg":
        return "구"
    if str_char == "dd" :
        return "두"
    if str_char == "ll" :
        return "루"
    if str_char == "mm" :
        return "무"
    if str_char == "bb" :
        return "부"
    if str_char == "ss" :
        return "수"
    if str_char == "oo" :
        return "우"
    if str_char == "jj" :
        return "주"
    if str_char == "ah" :
        return "아"
    if str_char == "ba" :
        return "바"
    if str_char == "sa" :
        return "사"
    if str_char == "ja" :
        return "자"
    if str_char == "ha" :
        return "하"
    if str_char == "hu" :
        return "허"
    if str_char == "ho" :
        return "호"
    if str_char == "bt" :
        return "배"
    str_char == "^^"

def transEng(str_char):        
    if str_char == "가" :
        return "ga"
    if str_char == "나" :
        return "na"
    if str_char == "다" :
        return "da"
    if str_char == "라" :
        return "la"
    if str_char == "마" :
        return "ma"
    if str_char == "거" :
        return "gu"
    if str_char == "너" :
        return "nu"
    if str_char == "더" :
        return "du"
    if str_char == "러" :
        return "lu"
    if str_char == "머" :
        return "mu"
    if str_char == "버" :
        return "bu"
    if str_char == "서" :
        return "su"
    if str_char == "어" :
        return "uh"
    if str_char == "저" :
        return "ju"
    if str_char == "고" :
        return "go"
    if str_char == "노" :
        return "no"
    if str_char == "도" :
        return "do"
    if str_char == "로" :
        return "lo"
    if str_char == "모" :
        return "mo"
    if str_char == "보" :
        return "bo"
    if str_char == "소" :
        return "so"
    if str_char == "오" :
        return "oh"
    if str_char == "조" :
        return "jo"
    if str_char == "누" :
        return "nn"
    if str_char == "구":
        return "gg"
    if str_char == "두" :
        return "dd"
    if str_char == "루" :
        return "ll"
    if str_char == "무" :
        return "mm"
    if str_char == "부" :
        return "bb"
    if str_char == "수" :
        return "ss"
    if str_char == "우" :
        return "oo"
    if str_char == "주" :
        return "jj"
    if str_char == "아" :
        return "ah"
    if str_char == "바" :
        return "ba"
    if str_char == "사" :
        return "sa"
    if str_char == "자" :
        return "ja"
    if str_char == "하" :
        return "ha"
    if str_char == "허" :
        return "hu"
    if str_char == "호" :
        return "ho"
    if str_char == "배" :
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


