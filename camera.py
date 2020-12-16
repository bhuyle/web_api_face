import cv2
import base64
import urllib.parse
import requests
import json
import timeit
import sys

url = 'http://service.mmlab.uit.edu.vn/checkinService_demo/user_login/post/'
#url = 'http://192.168.28.73:81/user_login/post/'
#------------------------------------
data ={'user_name':'tester1', 'password': 'tester1'}
headers = {'Content-type': 'application/json'}
data_json = json.dumps(data)
response = requests.post(url, data = data_json, headers=headers)
# print(response)
response = response.json()
# print(response['token'])
token = response['token']

url = 'http://service.mmlab.uit.edu.vn/checkinService_demo/search_face/post/'
####################################

cascPath = 'haarcascade_frontalface_dataset.xml'  # dataset
faceCascade = cv2.CascadeClassifier(cascPath)

video_capture = cv2.VideoCapture(0)
#  for cctv camera'rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp'
#  example of cctv or rtsp: 'rtsp://mamun:123456@101.134.16.117:554/user=mamun_password=123456_channel=1_stream=0.sdp'




def camera_stream():
     # Capture frame-by-frame
    ret, frame = video_capture.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        image_read = frame[y:y+h , x:x+w]
        _, a_numpy = cv2.imencode('.jpg', image_read)
        a = a_numpy.tobytes()
        encoded = base64.encodebytes(a)
        image_encoded = encoded.decode('utf-8')

        # ###################################

        data ={'token': token, 'data':{'image_encoded': image_encoded, 'class_id': '0', 'model': '0', 'classifier': '0'}}
        headers = {'Content-type': 'application/json'}
        data_json = json.dumps(data)
        response = requests.post(url, data = data_json, headers=headers)
        # print(response)
        response = response.json()
        # print(response)
        if len(response)>2: 
            data = list(response['data'].values())[3:]
            name = str(data[-1])
            
            font = cv2.FONT_HERSHEY_DUPLEX
            # font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.rectangle(frame, (x, y+h), (x+w,y+h+15), (0, 0, 255), cv2.FILLED)
            cv2.putText(frame, str(data[-2])+' '+data[-1], (x + 3, y+h + 12), font, 0.5, (255, 255, 255), 2)

        # print(response)
    # Display the resulting frame in browser
    return (cv2.imencode('.jpg', frame)[1].tobytes())

