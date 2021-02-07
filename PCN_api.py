#!/usr/bin/python3
from ctypes import *
import cv2
import numpy as np
import sys
import os
import time
from ipdb import set_trace as dbg
from enum import IntEnum
import json
import requests
import base64
import imutils

class CPoint(Structure):
    _fields_ = [("x", c_int),
                ("y", c_int)]

FEAT_POINTS = 14
class CWindow(Structure):
    _fields_ = [("x", c_int),
                ("y", c_int),
                ("width", c_int),
                ("angle", c_int),
                ("score", c_float),
                ("points",CPoint*FEAT_POINTS)]

class FeatEnam(IntEnum):
    CHIN_0 = 0
    CHIN_1 = 1
    CHIN_2 = 2
    CHIN_3 = 3
    CHIN_4 = 4
    CHIN_5 = 5
    CHIN_6 = 6
    CHIN_7 = 7
    CHIN_8 = 8
    NOSE = 9
    EYE_LEFT = 10
    EYE_RIGHT = 11
    MOUTH_LEFT = 12
    MOUTH_RIGHT = 13
    FEAT_POINTS = 14

lib = CDLL("/usr/local/lib/libPCN.so")

init_detector = lib.init_detector
#void *init_detector(const char *detection_model_path, 
#            const char *pcn1_proto, const char *pcn2_proto, const char *pcn3_proto, 
#            const char *tracking_model_path, const char *tracking_proto,
#            int min_face_size, float pyramid_scale_factor, float detection_thresh_stage1,
#            float detection_thresh_stage2, float detection_thresh_stage3, int tracking_period,
#            float tracking_thresh, int do_smooth)
init_detector.argtypes = [
        c_char_p, c_char_p, c_char_p, 
        c_char_p, c_char_p, c_char_p,
        c_int,c_float,c_float,c_float,
        c_float,c_int,c_float,c_int]
init_detector.restype = c_void_p

#CWindow* detect_faces(void* pcn, unsigned char* raw_img,size_t rows, size_t cols, int *lwin)
detect_faces = lib.detect_faces
detect_faces.argtypes = [c_void_p, POINTER(c_ubyte),c_size_t,c_size_t,POINTER(c_int)]
detect_faces.restype = POINTER(CWindow)

#CWindow* detect_track_faces(void* pcn, unsigned char* raw_img,size_t rows, size_t cols, int *lwin)
detect_track_faces = lib.detect_track_faces
detect_track_faces.argtypes = [c_void_p, POINTER(c_ubyte),c_size_t,c_size_t,POINTER(c_int)]
detect_track_faces.restype = POINTER(CWindow)

#void free_faces(CWindow* wins)
free_faces = lib.free_faces
free_faces.argtypes= [c_void_p]

# void free_detector(void *pcn)
free_detector = lib.free_detector
free_detector.argtypes= [c_void_p]

CYAN=(255,255,0)
BLUE=(255,0,0)
RED=(0,0,255)
GREEN=(0,255,0)
YELLOW=(0,255,255)

def DrawFace(win,img,name):
    width = 2
    x1 = win.x
    y1 = win.y
    x2 = win.width + win.x - 1
    y2 = win.width + win.y - 1
    centerX = (x1 + x2) / 2
    centerY = (y1 + y2) / 2
    angle = win.angle
    R = cv2.getRotationMatrix2D((centerX,centerY),angle,1)
    pts = np.array([[x1,y1,1],[x1,y2,1],[x2,y2,1],[x2,y1,1]], np.int32)
    pts = (pts @ R.T).astype(int) #Rotate points
    pts = pts.reshape((-1,1,2))
    cv2.putText(img, str(name), (x1, y1-5), 4, 1, (0, 0, 125))
    cv2.polylines(img,[pts],True,CYAN,width)
    cv2.line(img, (pts[0][0][0],pts[0][0][1]), (pts[3][0][0],pts[3][0][1]), BLUE, width)
  
def DrawPoints(win,img):
    width = 2
    f = FeatEnam.NOSE
    cv2.circle(img,(win.points[f].x,win.points[f].y),width,GREEN,-1)
    f = FeatEnam.EYE_LEFT
    cv2.circle(img,(win.points[f].x,win.points[f].y),width,YELLOW,-1)
    f = FeatEnam.EYE_RIGHT
    cv2.circle(img,(win.points[f].x,win.points[f].y),width,YELLOW,-1)
    f = FeatEnam.MOUTH_LEFT
    cv2.circle(img,(win.points[f].x,win.points[f].y),width,RED,-1)
    f = FeatEnam.MOUTH_RIGHT
    cv2.circle(img,(win.points[f].x,win.points[f].y),width,RED,-1)
    for i in range(8):
        cv2.circle(img,(win.points[i].x,win.points[i].y),width,BLUE,-1)

def SetThreadCount(threads):
    os.environ['OMP_NUM_THREADS'] = str(threads)

def c_str(str_in):
    return c_char_p(str_in.encode('utf-8'))

def get_token():
    url = 'http://service.mmlab.uit.edu.vn/checkinService_demo/user_login/post/'
    #url = 'http://192.168.28.73:81/user_login/post/'
    # ------------------------------------
    data = {'user_name': 'tester1', 'password': 'tester1'}
    headers = {'Content-type': 'application/json'}
    data_json = json.dumps(data)
    response = requests.post(url, data=data_json, headers=headers)
    # print(response)
    response = response.json()
    # print(response['token'])
    token = response['token']
    return token


video_flag = 1

if __name__=="__main__":

    SetThreadCount(1)
    path = 'model/'
    detection_model_path = c_str(path + "PCN.caffemodel")
    pcn1_proto = c_str(path + "PCN-1.prototxt")
    pcn2_proto = c_str(path + "PCN-2.prototxt")
    pcn3_proto = c_str(path + "PCN-3.prototxt")
    tracking_model_path = c_str(path + "PCN-Tracking.caffemodel")
    tracking_proto = c_str(path + "PCN-Tracking.prototxt")
    ##Load Webcam
    cap = cv2.VideoCapture(0)
    detector = init_detector(detection_model_path,pcn1_proto,pcn2_proto,pcn3_proto,
            tracking_model_path,tracking_proto, 
            40,1.45,0.5,0.5,0.98,30,0.9,1)
    # width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    # height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    # width = cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
    # height = cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
    width = 640
    height = 480
    fps = cap.get(cv2.CAP_PROP_FPS) 

    token = get_token()
    url = 'http://service.mmlab.uit.edu.vn/checkinService_demo/search_face/post/'
    print (width,height)
    while cap.isOpened():
        ret, frame = cap.read()
        frame = imutils.resize(frame, width=640)
        if ret == False:
            break
        start = time.time()
        face_count = c_int(0)
        raw_data = frame.ctypes.data_as(POINTER(c_ubyte))
        windows = detect_track_faces(detector, raw_data, 
                int(height), int(width),
                pointer(face_count))
        
        name = ""

        ##Call API and draw bbox
        
        for i in range(face_count.value):
            ##Call API
            # x1 = windows[i].x
            # y1 = windows[i].y
            # x2 = windows[i].width + windows[i].x - 1
            # y2 = windows[i].width + windows[i].y - 1
            # index = frame[y1:y2,x1:x2]
            # _, a_numpy = cv2.imencode('.jpg', index)
            # a = a_numpy.tobytes()
            # encoded = base64.encodebytes(a)
            # image_encoded = encoded.decode('utf-8')
            # # ###################################
            # data = {'token': token, 'data': {'image_encoded': image_encoded,
            #                                 'class_id': '0', 'model': '0', 'classifier': '0'}}
            # headers = {'Content-type': 'application/json'}
            # data_json = json.dumps(data)
            # response = requests.post(url, data=data_json, headers=headers)
            # response = response.json()
            # if len(response) > 2:
            #     get = list(response['data'].values())[6:8]
            #     name = str(get[-1])
            # else:
            #     name = "Unknow"
            DrawFace(windows[i],frame,name)
            DrawPoints(windows[i],frame)
        free_faces(windows)
        end = time.time()
        fps = int(1 / (end - start))
        cv2.putText(frame, str(fps) + "fps", (20, 45), 4, 1, (0, 0, 125))
        cv2.imshow('PCN', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    free_detector(detector)

