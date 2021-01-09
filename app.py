from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
# from test_cam import camera_stream
from test_cam import get_token
from multiprocessing import Queue
import cv2
import base64
import urllib.parse
import requests
import json
import timeit
import sys

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
        # while (not q.empty()):
        #     index = q.get()
        #     info.append({
        #         'name':index[1],
        #         'mssv':index[0],
        #         'face_crop':index[2]
        #     }) 

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
    return render_template('index_2.html')


def gen_frame():
    """Video streaming generator function."""
    cascPath = 'haarcascade_frontalface_dataset.xml'  # dataset
    faceCascade = cv2.CascadeClassifier(cascPath)

    # video_capture = cv2.VideoCapture('rtsp://admin:mmlab123@192.168.16.42:554/live1.264')
    video_capture = cv2.VideoCapture(0)
    while True:
        global t
        global q
        global response
        global face
        ret, frame = video_capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        info = []
        face = []
        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            image_read = frame[y:y+h, x:x+w]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            face.append(image_read)
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
