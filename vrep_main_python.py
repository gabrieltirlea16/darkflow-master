import vrep
import numpy as np
import cv2


class vRep:
    def stream_vision_sensor(vision_sensor_name, clientID, left_motor, right_motor):
        errorCode, left_motor_handle = vrep.simxGetObjectHandle(clientID, 'ePuck_leftJoint',
                                                                vrep.simx_opmode_oneshot_wait)
        errorCode, right_motor_handle = vrep.simxGetObjectHandle(clientID, 'ePuck_rightJoint',
                                                                 vrep.simx_opmode_oneshot_wait)

        errorCode = vrep.simxSetJointTargetVelocity(clientID, left_motor_handle, left_motor, vrep.simx_opmode_streaming)
        errorCode = vrep.simxSetJointTargetVelocity(clientID, right_motor_handle, right_motor, vrep.simx_opmode_streaming)

        # print('Vision Sensor object handling')

        res, v1 = vrep.simxGetObjectHandle(clientID, vision_sensor_name, vrep.simx_opmode_oneshot_wait)

        # print('Getting first image')

        err, resolution, image = vrep.simxGetVisionSensorImage(clientID, v1, 0, vrep.simx_opmode_streaming)
        while vrep.simxGetConnectionId(clientID) != -1:
            err, resolution, image = vrep.simxGetVisionSensorImage(clientID, v1, 0, vrep.simx_opmode_buffer)
            if err == vrep.simx_return_ok:
                img = np.array(image, dtype=np.uint8)
                img.resize([resolution[1], resolution[0], 3])
                cv2.flip(img, 0, img)
                cv2.imshow('image', img)
                return img
            elif err == vrep.simx_return_novalue_flag:
                pass
            else:
                print(err)


# if __name__ == '__main__':
#     vrep.simxFinish(-1) # just in case, close all opened connections
#     clientID = vrep.simxStart('127.0.0.1', 19999, True, True, 5000, 5) # Connect to V-REP
#
#     if clientID != -1:
#         print("Connected to remote API server")
#         while True:
#             capture = (vRep.stream_vision_sensor('ePuck_camera', clientID, 0.0001))
#             print(capture)
#             cv2.flip(capture, 0, capture)
#             cv2.imshow('image', capture)
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break
#
#     else:
#         print("Connection not succesful")
#         sys.exit("Could not connect")
