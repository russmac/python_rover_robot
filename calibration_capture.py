import picamera
import robot_data as rd
import numpy as np
import cv2
import time
from sys import argv
RESOLUTION = (argv[1], argv[2])
CAPTURE_LIMIT = argv[3]
CAPTURE_INTERVAL = argv[4]


def capture():
    with picamera.PiCamera() as camera:
        camera.resolution = (RESOLUTION[0], RESOLUTION[1])
        camera.framerate = 90
        time.sleep(CAPTURE_INTERVAL)
        c = 0
        limit = CAPTURE_LIMIT
        while c < limit:
            timer = time.time()
            camera.capture(f'calibration/{c}.jpg')
            print(f'Time taken for RPI photo: {time.time() - timer}')
            image = cv2.imread(f'calibration/{c}.jpg')
            c += 1
            rd.stream_input.write(image.tobytes())


if __name__ == '__main__':
    if len(argv) < 5:
        print('Help:')
        print('./calibration_capture.py [RESOLUTION_X] [RESOLUTION_Y] [CAPTURE_COUNT] [CAPTURE_INTERVAL]')
        print('./calibration_capture.py 640 480 100 3')
    capture()
