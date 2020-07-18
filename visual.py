import robot_data as rd
import picamera
import time
import logging
import numpy as np
import cv2
from utils import parse_config


class Visual():
    def __init__(self):
        config = parse_config()["camera"]
        self.sigma = 0.33
        self.objpoints = np.load(f'config/{config["id"]}_obj.npy')
        self.imgpoints = np.load(f'config/{config["id"]}_img.npy')
        self.sample_image = cv2.imread(f'config/{config["id"]}_sample_image.jpg')
        self.mipi_calibration = tuple()
        self.camera_y = config['camera_y']
        self.camera_x = config['camera_x']
        # todo: Catch other PiCamera resolution roundups
        if self.camera_y == 1080:
            self.camera_y = 1088
        self.framerate = config['framerate']
        self.canny_params = config['canny_params']
        self.hough_params = config['hough_params']
        self.fisheye = config['fisheye']
        self.camera = picamera.PiCamera()
        self.camera.resolution = (self.camera_x, self.camera_y)
        self.camera.framerate = self.framerate
        self.mipi_calibration = self.get_fisheye_calibration(self.objpoints, self.imgpoints)
        self.canny_auto_levels = config['canny_auto_levels']
        self.stream_canny = config['stream_canny']

    def start(self):
        try:
            frequency_counter = 1
            frequency = 0
            f_timer = time.time()
            while True:
                mipi_image = self.frame()
                rd.stream_input.write(mipi_image.tobytes())
                frequency = (time.time() - f_timer) / frequency_counter
                logging.debug(f'VISUAL FREQUENCY: {frequency}')
                frequency_counter += 1
        except Exception as e:
            logging.critical(e)

    def get_fisheye_calibration(self, objp, imgp):
        logging.debug('Loading Camera calibration')
        calibration_flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv2.fisheye.CALIB_CHECK_COND + cv2.fisheye.CALIB_FIX_SKEW
        image = self.sample_image
        grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # By preinitializing camera_matrix&distortions we are pre-populating the fisheye distortion grid
        # with guesses.
        grid_size = len(self.objpoints)
        camera_matrix = np.zeros((3, 3))
        distortions = np.zeros((4, 1))

        # Prepopulate calibration objects
        # Required due to OpenCV bug https://github.com/opencv/opencv/issues/5534#issuecomment-148864862
        rvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(grid_size)]
        tvecs = [np.zeros((1, 1, 3), dtype=np.float64) for i in range(grid_size)]
        h, w = image.shape[:2]

        calibrate_params = (
            objp,
            imgp,
            grey.shape[::-1],
            camera_matrix,
            distortions,
            rvecs,
            tvecs,
            calibration_flags,
            (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1e-6)

        )
        try:
            ret, camera_matrix, distortion, rvecs, tvecs = cv2.fisheye.calibrate(*calibrate_params)
            new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, distortion, (w, h), 0, (w, h))
            logging.debug(f'camera_matrix:\n {camera_matrix}')
            logging.debug(f'new_camera_matrix:\n {new_camera_matrix}')
            logging.debug(f'distortion:\n {distortion}')
            logging.debug(f'region of interest:\n {roi}')
            return camera_matrix, distortion, new_camera_matrix, roi
        except Exception as e:
            logging.critical('Camera get_fisheye_calibration() failed!')
            logging.critical(e)
            exit(1)

    def get_calibration(self, objp, imgp):
        image = self.sample_image
        grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = image.shape[:2]
        ret, camera_matrix, distortion, rvecs, tvecs = cv2.calibrateCamera(objp, imgp, grey.shape[::-1], None, None)
        new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, distortion, (w, h), 0, (w, h))
        logging.info(f'new_camera_matrix:\n {new_camera_matrix}')
        logging.info(f'distortion:\n {distortion}')
        logging.info(f'camera_matrix:\n {camera_matrix}')
        logging.info(f'region of interest:\n {roi}')
        return camera_matrix, distortion, new_camera_matrix, roi

    def get_lines(self, edges):
        try:
            if self.hough_params['probabilistic']:
                lines = cv2.HoughLinesP(image=edges,
                                        rho=1,
                                        theta=np.pi / 180.0,
                                        threshold=5,
                                        minLineLength=self.hough_params['minLineLength'],
                                        maxLineGap=self.hough_params['maxLineGap']
                                        )
            else:
                lines = cv2.HoughLines(image=edges,
                                       rho=1,
                                       theta=np.pi / 180.0,
                                       threshold=5,
                                       )
            return lines
        except Exception as e:
            logging.critical(f'get_lines() {e}')

    def get_edges(self, undistorted_capture):
        try:
            grey = cv2.cvtColor(undistorted_capture, cv2.COLOR_BGR2GRAY)
            if self.canny_auto_levels:
                v = np.median(undistorted_capture)
                lower = int(max(0, (1.0 - self.sigma) * v))
                upper = int(min(255, (1.0 + self.sigma) * v))
            else:
                lower = self.canny_params['lower']
                upper = self.canny_params['upper']
            edges = cv2.Canny(image=grey,
                              threshold1=lower,
                              threshold2=upper,
                              apertureSize=3,
                              L2gradient=False)
            return edges
        except Exception as e:
            logging.critical(e)

    def undistort_image(self, image, camera_matrix, distortion, new_camera_matrix, roi):
        try:
            image = image.reshape((self.camera_y, self.camera_x, 3))
            undistorted_image = cv2.undistort(image, camera_matrix, distortion, new_camera_matrix)
            x, y, w, h = roi
            # Modify the image to a "region of interest"
            undistorted_image = undistorted_image[y:y + h, x:x + w]
            return undistorted_image
        except Exception as e:
            logging.critical(f'undistort_image() {e}')

    def undistort_fisheye_image(self, image, camera_matrix, distortion, new_camera_matrix, roi):
        try:
            image = image.reshape((self.camera_y, self.camera_x, 3))
            map_y, map_x = cv2.fisheye.initUndistortRectifyMap(camera_matrix,
                                                               distortion,
                                                               np.eye(3, 3),
                                                               camera_matrix,
                                                               (self.camera_x, self.camera_y),
                                                               cv2.CV_16SC2
                                                               )
            undistorted_image = cv2.remap(image, map_y, map_x, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
            # Crop the frame symmetrically, Fisheye calibration returns no ROI.
            roi = (40, 40, 560, 400)
            x, y, w, h = roi
            # Modify the image to a region of interest
            undistorted_image = undistorted_image[y:y + h, x:x + w]
            return undistorted_image
        except Exception as e:
            logging.critical(f'undistort_fisheye_image() {e}')

    def process_image(self, image, camera_matrix, distortion, new_camera_matrix=None, roi=None):
        timer = time.time()
        if self.fisheye:
            undistorted_image = self.undistort_fisheye_image(image,
                                                             camera_matrix,
                                                             distortion,
                                                             new_camera_matrix,
                                                             roi
                                                             )
        else:
            undistorted_image = self.undistort_image(image,
                                                     camera_matrix,
                                                     distortion,
                                                     new_camera_matrix,
                                                     roi
                                                     )
        logging.debug(f'Time taken for UNDISTORTION: {time.time() - timer}')
        edges = self.get_edges(undistorted_image)
        lines = self.get_lines(edges)
        if lines is None:
            logging.debug('no houghlines drawn')
            return undistorted_image, edges
        if self.hough_params["probabilistic"]:
            for row in lines:
                for x1, y1, x2, y2 in row:
                    cv2.line(undistorted_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        else:
            for rho, theta in lines[0]:
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 1000 * (-b))
                y1 = int(y0 + 1000 * (a))
                x2 = int(x0 - 1000 * (-b))
                y2 = int(y0 - 1000 * (a))
                cv2.line(undistorted_image, (x1, y1), (x2, y2), (0, 0, 255), 2)
        return undistorted_image, edges

    def frame(self):
        timer = time.time()
        undistorted_image, edges = self.process_image(self.get_image(), *self.mipi_calibration)
        if self.stream_canny:
            res, data = cv2.imencode(ext='.jpg', img=edges)
        else:
            res, data = cv2.imencode(ext='.jpg', img=undistorted_image)
        logging.debug(f'Time taken for MIPI processing: {time.time() - timer}')
        return data

    def get_image(self):
        try:
            timer = time.time()
            image = np.empty((self.camera_y * self.camera_x * 3,), dtype=np.uint8)
            self.camera.capture(image, 'bgr')
            logging.debug(f'Time taken for MIPI IMAGE: {time.time() - timer}')
            return image
        except Exception as e:
            logging.critical(e)

