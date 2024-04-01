import picamera2
import robot_data as rd
import numpy as np
import cv2
import time
from sys import argv
resolution = (int(argv[1]), int(argv[2]))
capture_limit = int(argv[3])

def capture():
    camera = picamera2.Picamera2()
    camera.create_still_configuration(main={"size": (resolution[0], resolution[1])})
    camera.start_and_capture_files(name="calibration/calib{:03d}.jpg", num_files=capture_limit, delay=1, show_preview=False)
    

if __name__ == '__main__':
    if len(argv) < 5:
        print('Help:')
        print('python3 calibration_capture.py [RESOLUTION_X] [RESOLUTION_Y] [CAPTURE_COUNT]')
        print('python3 calibration_capture.py 480 640 100 1')
    capture()
