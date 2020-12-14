from flask import Flask, render_template, request, jsonify

# import cv2
# import numpy as np 
# import tensorflow as tf
# import keras 
# from keras.models import load_model

app = Flask(__name__,template_folder='template',  static_folder='static')




@app.route('/')
def index():
    return render_template('index.html')



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)