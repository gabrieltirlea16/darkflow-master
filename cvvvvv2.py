import cv2
from darkflow.net.build import TFNet
import numpy as np
import time
import tensorflow as tf
from serial_koala import serialKoala
import math

options = {
    'model': 'cfg/yolo.cfg',
    'load': 'bin/yolo.weights',
    'threshold': 0.2,
    'gpu': 0.8
}

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.Session(config=config)

tfnet = TFNet(options)
colors = [tuple(255 * np.random.rand(3)) for _ in range(10)]

capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 512)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 512)

resolution = 724

while True:
    stime = time.time()
    ret, frame = capture.read()
    results = tfnet.return_predict(frame)
    if ret:
        for color, result in zip(colors, results):
            tl = (result['topleft']['x'], result['topleft']['y'])
            br = (result['bottomright']['x'], result['bottomright']['y'])
            label = result['label']
            confidence = result['confidence']
            print('We have the following objects: {}: {:.2f}%'.format(label, confidence * 100))
            text = '{}: {:.0f}%'.format(label, confidence * 100)
            frame = cv2.rectangle(frame, tl, br, color, 5)
            frame = cv2.putText(
                frame, text, tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
        cv2.imshow('frame', frame)
        # print('FPS {:.1f}'.format(1 / (time.time() - stime)))
        dist = math.hypot(tl[0] - br[0], tl[1] - br[1])
        print(dist)

        if tl[0] < 256 and br[0] > 256:
            if dist >= 0.8 * resolution:
                serialKoala.koala('D,10,0')
            elif dist >= 0.6 * resolution:
                serialKoala.koala('D,15,10')
            elif dist >= 0.5 * resolution:
                serialKoala.koala('D,10,10')
            elif dist >= 0.4 * resolution:
                serialKoala.koala('D,10,10')

        elif tl[0] > 256:
            if dist >= 0.8 * resolution:
                serialKoala.koala('D,10,0')
            elif dist >= 0.6 * resolution:
                serialKoala.koala('D,12,10')
            elif dist >= 0.5 * resolution:
                serialKoala.koala('D,10,13')
            elif dist >= 0.4 * resolution:
                serialKoala.koala('D,10,12')

        elif br[0] < 256:
            if dist >= 0.8 * resolution:
                serialKoala.koala('D,0,10')
            elif dist >= 0.6 * resolution:
                serialKoala.koala('D,10,12')
            elif dist >= 0.5 * resolution:
                serialKoala.koala('D,13,10')
            elif dist >= 0.4 * resolution:
                serialKoala.koala('D,12,10')

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()