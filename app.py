from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
# from test_cam import camera_stream
from multiprocessing import Queue
import cv2
import base64
import urllib.parse
import requests
import json
import timeit
import sys
from PCN_api import*

import threading
import time
async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# socketio = SocketIO(app)
socketio = SocketIO(app, async_mode=async_mode)


print("Stop")
# socketio = SocketIO(app)

name = ""
mssv = ""
face = ""
info = []
t2 = threading.Thread()
q = Queue()

def send1():
    i = 0
    global name
    global mssv
    global info
    global face
    global q
    token = get_token()
    while True:
        url = 'http://service.mmlab.uit.edu.vn/checkinService_demo/search_face/post/'
        for index in face:
            _, a_numpy = cv2.imencode('.jpg', index)
            a = a_numpy.tobytes()
            encoded = base64.encodebytes(a)
            image_encoded = encoded.decode('utf-8')
            # ###################################
            data = {'token': token, 'data': {'image_encoded': image_encoded,
                                            'class_id': '0', 'model': '0', 'classifier': '0'}}
            headers = {'Content-type': 'application/json'}
            data_json = json.dumps(data)
            response = requests.post(url, data=data_json, headers=headers)
            response = response.json()
            
            if len(response) > 2:
                get = list(response['data'].values())[6:8]
                # name = str(get_name[-1])
                index = [get[0],get[1],image_encoded]
                # q.put([get[0],get[1],image_encoded])
                # print(get)
            else:
                index = ["Unknow","Unknow",image_encoded]
                # q.put(["Unknow","Unknow",image_encoded])
            info.append({
                'name':index[1],
                'mssv':index[0],
                'face_crop':index[2]
            })
        socketio.emit('my_response', info, namespace='/info')
        info = []
        time.sleep(1)


@socketio.on('connect', namespace='/info')
def connect():
    global t2
    if not t2.isAlive():
        print("connect")
        t2 = threading.Thread(
            name='websocket_process_thread_', target=send1, args=())
        t2.start()


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen_frame():
    """Video streaming generator function."""
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
    width = 640
    height = 480
    fps = cap.get(cv2.CAP_PROP_FPS) 

    token = get_token()
    url = 'http://service.mmlab.uit.edu.vn/checkinService_demo/search_face/post/'
    print (width,height)
    while cap.isOpened():
        global t
        global q
        global response
        global face
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
        
        face = []
        ##Call API and draw bbox
        
        for i in range(face_count.value):
            #Call API
            x1 = windows[i].x
            y1 = windows[i].y
            x2 = windows[i].width + windows[i].x 
            y2 = windows[i].width + windows[i].y 
            index = frame[y1:y2,x1:x2].copy()
            face.append(index)
            DrawFace(windows[i],frame,name)
            # DrawPoints(windows[i],frame)
        free_faces(windows)
        end = time.time()
        fps = int(1 / (end - start))
        cv2.putText(frame, str(fps) + "fps", (20, 45), 4, 1, (0, 0, 125))
        yield (b'--frame\r\n Content-Type: image/jpeg\r\n\r\n' + cv2.imencode('.jpg', frame)[1].tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @socketio.on('connect', namespace='/info')
# def connect():
#     socketio.emit('my_response',{'name': str(name), 'mssv': str(mssv)}, namespace='/info',callback=video_feed())


if __name__ == '__main__':
    socketio.run(app, debug=True)
    # app.run(debug=True)
