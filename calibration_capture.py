import cv2
import numpy as np
import picamera2
import time
from sys import argv
import sys


def capture():
    camera = picamera2.Picamera2()
    # https://picamera.readthedocs.io/en/release-1.13/_images/sensor_area_2.png
    still_config = camera.create_still_configuration(main={"size": (1640, 1232)})
    camera.configure(still_config)
    camera.start()
    time.sleep(2)
    capture_count = 0
    while capture_count < capture_limit:
        print(f"Capturing image calibration_{capture_count}.jpg")
        image = camera.capture_array(name="main")
        resized_image = cv2.resize(image, (640, 480))
        cv2.imwrite(f"calibration/calibration_{capture_count}.jpg", resized_image)
        time.sleep(0.2)
        capture_count += 1


if __name__ == '__main__':
    if len(argv) < 4:
        print('Help:')
        print('python3 calibration_capture.py [RESOLUTION_X] [RESOLUTION_Y] [CAPTURE_COUNT]')
        print('python3 calibration_capture.py 640 480 100')
        sys.exit(3)
    resolution = (int(argv[1]), int(argv[2]))
    capture_limit = int(argv[3])
    capture()
