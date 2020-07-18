# https://docs.opencv2.rg/trunk/dc/dbb/tutorial_py_calibration.html
import numpy as np
import cv2
import glob
import os
from utils import parse_config
import shutil.copy2

CHESSBOARD = (7, 7)


def read_calibration_images():
    config = parse_config()['camera']

    if config['fisheye']:
        # We need an extra dimensions for the fisheye calibrate method
        objp = np.zeros((1, CHESSBOARD[0] * CHESSBOARD[1], 3), np.float32)
        objp[0, :, :2] = np.mgrid[0:CHESSBOARD[0], 0:CHESSBOARD[1]].T.reshape(-1, 2)
        # termination criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    else:
        objp = np.zeros((CHESSBOARD[0] * CHESSBOARD[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:CHESSBOARD[0], 0:CHESSBOARD[1]].T.reshape(-1, 2)
        # termination criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.

    images = glob.glob('samples/calibration/*.jpg')
    success_c = 0
    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray,
                                                 CHESSBOARD,
                                                 cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE
                                                 )
        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)
            if config['fisheye']:
                refined_corners = cv2.cornerSubPix(gray, corners, (3, 3), (-1, -1), criteria)
            else:
                refined_corners = cv2.cornerSubPix(gray, corners, (int(CHESSBOARD[0] / 2), int(CHESSBOARD[1] / 2)),
                                                   (-1, -1), criteria)
            imgpoints.append(refined_corners)
            # Draw and display the corners
            cv2.drawChessboardCorners(img, (CHESSBOARD[0], CHESSBOARD[1]), refined_corners, ret)
            if cv2.imwrite(f'samples/results/success_{success_c}.jpg', img=img):
                success_c += 1
            print(f'Succeeded! {fname}')
        else:
            print(f'Failed! {fname}')
            os.remove(f'{fname}')

    np.save(f'samples/config/{config["id"]}_obj', objpoints)
    np.save(f'samples/config/{config["id"]}_img', imgpoints)
    shutil.copy2(f'samples/results/success_0.jpg', f'samples/config/{config["id"]}_sample_image.jpg', )


if __name__ == '__main__':
    read_calibration_images()
