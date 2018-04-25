import cv2
from darkflow.net.build import TFNet
import numpy as np
import time
import tensorflow as tf
from vrep_main_python import vRep
import sys, getopt
import vrep
import math

_DEFAULT_LEFT_MOTOR = 0.2
_DEFAULT_RIGHT_MOTOR = 0.0

def print_help():
    print('cv2_vrep.py -l <left_motor> -r <right_motor>')


def main():
    left_motor = None
    right_motor = None

    opts = ""

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'l:r:', ['left_motor=', 'right_motor='])
    except getopt.GetoptError:
        print_help()
        exit(2)

    left_motor = ""
    right_motor = ""

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print_help()
            sys.exit(2)
        elif opt in ("-l", "--left_motor"):
            left_motor = float(arg)
        elif opt in ("-r", "--right_motor"):
            right_motor = float(arg)
        else:
            print("Unrecognised option {0}".format(opt))
            print_help()
            sys.exit(2)

    if left_motor is None:
        left_motor = _DEFAULT_LEFT_MOTOR
    elif right_motor is None:
        right_motor = _DEFAULT_RIGHT_MOTOR

    options = {
        'model': 'cfg/yolo.cfg',
        'load': 'bin/yolo.weights',
        'threshold': 0.2,
        'gpu': 0.8
    }

    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    session = tf.Session(config=config)

    resolution = 724

    tfnet = TFNet(options)
    colors = [tuple(255 * np.random.rand(3)) for _ in range(10)]

    vrep.simxFinish(-1)  # just in case, close all opened connections
    clientID = vrep.simxStart('127.0.0.1', 19999, True, True, 5000, 5)  # Connect to V-REP

    if clientID != -1:
        print("Connected to remote API server")

        while True:
            stime = time.time()
            frame = vRep.stream_vision_sensor('ePuck_camera', clientID, left_motor, right_motor)
            results = tfnet.return_predict(frame)
            # print(results)
            # if ret:
            for color, result in zip(colors, results):
                tl = (result['topleft']['x'], result['topleft']['y'])
                br = (result['bottomright']['x'], result['bottomright']['y'])
                label = result['label']
                confidence = result['confidence']
                # print('We have the following objects: {}: {:.2f}%'.format(label, confidence * 100))
                text = '{}: {:.0f}%'.format(label, confidence * 100)
                frame = cv2.rectangle(frame, tl, br, color, 5)
                frame = cv2.putText(
                    frame, text, tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2)
                cv2.imshow('image', frame)

                dist = math.hypot(tl[0] - br[0], tl[1] - br[1])
                print(dist)

                if tl[0] <256 and br[0] > 256:
                    if dist >= 0.8 * resolution:
                        vRep.stream_vision_sensor('ePuck_camera', clientID, left_motor, 0)
                    elif dist >= 0.6 * resolution:
                        vRep.stream_vision_sensor('ePuck_camera', clientID, left_motor + 0.5, right_motor)
                    elif dist >= 0.5 * resolution:
                        vRep.stream_vision_sensor('ePuck_camera', clientID, left_motor, right_motor)
                    elif dist >= 0.4 * resolution:
                        vRep.stream_vision_sensor('ePuck_camera', clientID, left_motor, right_motor)

                elif tl[0] > 256:
                    if dist >= 0.8 * resolution:
                        vRep.stream_vision_sensor('ePuck_camera', clientID, left_motor, 0)
                    elif dist >= 0.6 * resolution:
                        vRep.stream_vision_sensor('ePuck_camera', clientID, left_motor + 0.2, right_motor)
                    elif dist >= 0.5 * resolution:
                        vRep.stream_vision_sensor('ePuck_camera', clientID, left_motor, right_motor + 0.3)
                    elif dist >= 0.4 * resolution:
                        vRep.stream_vision_sensor('ePuck_camera', clientID, left_motor, right_motor + 0.2)

                elif br[0] <256:
                    if dist >= 0.8 * resolution:
                        vRep.stream_vision_sensor('ePuck_camera', clientID, 0, right_motor)
                    elif dist >= 0.6 * resolution:
                        vRep.stream_vision_sensor('ePuck_camera', clientID, left_motor, right_motor + 0.2)
                    elif dist >= 0.5 * resolution:
                        vRep.stream_vision_sensor('ePuck_camera', clientID, left_motor + 0.3, right_motor)
                    elif dist >= 0.4 * resolution:
                        vRep.stream_vision_sensor('ePuck_camera', clientID, left_motor + 0.2, right_motor)



            # print('FPS {:.1f}'.format(1 / (time.time() - stime)))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()

    else:
        print("Connection not succesful")
        sys.exit("Could not connect")


if __name__ == "__main__":
    main()

