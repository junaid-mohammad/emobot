import pathlib
import numpy as np
import cv2
import os
from keras.preprocessing.image import ImageDataGenerator
import tensorflow as tf
from keras.layers import Activation, Conv2D, MaxPooling2D, Dense, Flatten, Dropout, BatchNormalization
from keras.preprocessing import image
from keras.models import Sequential
import pyscreenshot as ImageGrab
import schedule
import PIL.Image
import time
import matplotlib.pyplot as plt
import scipy

# Using flask for the backend

from flask import Flask, render_template, request

app = Flask(__name__)

# variables
emotions = ['disgusted' 'happy' 'surprised' 'neutral' 'sad' 'angry' 'fearful']
output_class_units = len(emotions)
image_generator = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1. / 255)
emotionsdict = {0: 'disgusted', 1: 'happy', 2: 'surprised', 3: 'neutral', 4: 'sad', 5: 'angry', 6: 'fearful'}
emotionlist = []

# model
model = tf.keras.models.load_model('New_Model.h5')



@app.route('/')
@app.route('/home')
def home():
    return render_template("index.html")


@app.route('/launch')
def launch():
    celsius = request.args.get("celsius", "")
    x = 0
    while (x < 2):
        x = x + 1
        return take_screenshot()



@app.route('/launch', methods=['POST', 'GET'])
def take_screenshot():
    try:
        img = ImageGrab.grab(childprocess=False)
        img.save('Output_screenshot.png')

        take_screenshot()
        image = cv2.imread('Output_screenshot.png')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=3,
            minSize=(30, 30)
        )

        print("[INFO] Found {0} Faces.".format(len(faces)))

        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            roi_color = gray[y:y + h, x:x + w]
            print("[INFO] Object found. Saving locally.")
            path = 'Images' + str(w) + str(h) + '_faces.jpg'
            print(path)
            cv2.imwrite(path, roi_color)
            img = tf.keras.utils.load_img(path, target_size=(227, 227, 3), interpolation="bilinear")
            print(img)
            img = np.array(img)
            print(img.shape)
            img = img.reshape(1, 227, 227, 3)
            img = image_generator.flow(img, batch_size=32, shuffle=True)
            result = model.predict(img)
            result = list(result[0])
            print(result)
            img_index = result.index(max(result))
            emotion = emotionsdict[img_index]
            emotionlist.append(emotion)
            return emotionlist

    except ValueError:
        return "invalid input"


if __name__ == "__main__":
    app.run(debug=True, port=5005)
