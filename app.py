from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
from test_cam import camera_stream
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


def send1():
    i = 0
    global name
    global mssv
    global info
    while True:
        # i += 1
        # print("emit1", i)
        # socketio.emit('my_response', {'name': str(name), 'mssv': str(mssv)}, namespace='/info')
        socketio.emit('my_response', info, namespace='/info')
        info = []
        time.sleep(2)


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
    global name
    global mssv
    global face
    global info
    while True:
        data, frame = camera_stream()
        if data != []:
            name = ""
            mssv = ""
            info = []
            for index in data:
                info.append({
                    'name':index[1],
                    'mssv':index[0]
                }) 
        else:
            name = 'Unknow'
            mssv = 'Unknow'
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


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
