import cv2
import base64
import urllib.parse
import requests
import json
import timeit
import sys
from multiprocessing import Queue
import threading

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

url = 'http://service.mmlab.uit.edu.vn/checkinService_demo/search_face/post/'
####################################

cascPath = 'haarcascade_frontalface_dataset.xml'  # dataset
faceCascade = cv2.CascadeClassifier(cascPath)

# video_capture = cv2.VideoCapture('rtsp://admin:mmlab123@192.168.16.42:554/live1.264')
# video_capture = cv2.VideoCapture(0)


#  for cctv camera'rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp'
#  example of cctv or rtsp: 'rtsp://mamun:123456@101.134.16.117:554/user=mamun_password=123456_channel=1_stream=0.sdp'

q = Queue()
q.put("Unknow")
response = "Unknow"
t = threading.Thread()
token = get_token()

# def get_info(image_read, q):
#     url = 'http://service.mmlab.uit.edu.vn/checkinService_demo/search_face/post/'
#     _, a_numpy = cv2.imencode('.jpg', image_read)
#     a = a_numpy.tobytes()
#     encoded = base64.encodebytes(a)
#     image_encoded = encoded.decode('utf-8')

#     # ###################################

#     data = {'token': token, 'data': {'image_encoded': image_encoded,
#                                      'class_id': '0', 'model': '0', 'classifier': '0'}}
#     headers = {'Content-type': 'application/json'}
#     data_json = json.dumps(data)
#     response = requests.post(url, data=data_json, headers=headers)
#     # print(response)
#     response = response.json()
#     # print(response)
#     if len(response) > 2:
#         get_name = list(response['data'].values())[6:8]
#         # name = str(get_name[-1])
#         q.put(get_name)
#         print(get_name)
#     else:
#         q.put(["Unknow","Unknow"])
#     return (response)


# def camera_stream():
#     # Capture frame-by-frame
#     global t
#     global q
#     global response
#     ret, frame = video_capture.read()
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     faces = faceCascade.detectMultiScale(
#         gray,
#         scaleFactor=1.1,
#         minNeighbors=5,
#         minSize=(60, 60),
#         flags=cv2.CASCADE_SCALE_IMAGE
#     )
#     info = []
#     # Draw a rectangle around the faces
#     for (x, y, w, h) in faces:
#         cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
#         image_read = frame[y:y+h, x:x+w]
#         # response = api_face(image_read)
#         if not t.isAlive():
#             t = threading.Thread(target=get_info, args=(image_read, q,))
#             info.append(q.get())
#             t.start()
#     return (info, cv2.imencode('.jpg', frame)[1].tobytes())
face = []


def get_info(face, q):
    global token
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
        # print(response)
        response = response.json()
        # print(response)
        if len(response) > 2:
            get_name = list(response['data'].values())
            # name = str(get_name[-1])
            q.put(get_name)
        else:
            q.put(["Unknow","Unknow"])
    # return (response)


def start():
    global face
    global t
    # for index in face:
    #     q.put(index)    
    if not t.isAlive():
        t = threading.Thread(target=get_info, args=(face, q,))
        # info.append(q.get())
        while(not q.empty()):
            print(q.get(),end='')
        print('\n')
        t.start()

def cam():
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
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            image_read = frame[y:y+h, x:x+w]
            # response = api_face(image_read)
            face.append(image_read)
            # q.put(image_read)
            # if not t.isAlive():
            #     t = threading.Thread(target=get_info, args=(image_read, q,))
            #     info.append(q.get())
            #     t.start()
        if len(faces)>0:
            # print(len(faces))
            start()
        cv2.imshow("",frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break
# start()
# cam()