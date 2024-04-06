# Python Rover Robot
This is a Python Rover project which currently uses 3 ultrasonic sensors and a magnetometer to navigate. Its a fairly specific thing I used as a learning tool perhaps someone may find as a useful example. 

It is capable of streaming basic OpenCV image processing done onboard at roughly 700ms frequency (very slow), helper scripts are included to calibrate a lens for image processing. 

It does not navigate by the houghline detection it performs due to the capability being limited by the visual frequency. Of roughly 2.5fps which would be impacted further by additional processing. 

![Robot](/doc/robot.png)

## Supported OS.
Raspbian Stable/Raspberry Pi OS stable

## Instructions
Install everything in Linuxfile with apt
```
for package in `cat Linuxfile`; do
apt -y install $package
done
```

Create a venv for the files, The drivers used require root access.
```python
cd ~
git clone https://github.com/russmac/python_rover robot
cd robot && python3 -m venv venv
. venv/bin/activate
pip3 install -r requirements.txt
```
Edit instance/config.py
```
camera_selection = "picamera_v2_vga"

camera_configurations = {
    "picamera_v2_vga": {
        "id": "picamera_v2_vga",
        "fisheye": True,
        "canny_auto_levels": True,
        "stream_canny": False,
        "camera_x": 640,
        "camera_y": 480,
        "framerate": 90,
        "canny_params": {"upper": 160,
                         "lower": 40},
        "hough_params": {"minLineLength": 100,
                         "maxLineGap": 5,
                         "probabilistic": True},
    },
}

motor_configuration = {
    "enable_pin": 17,
    "slew_pin": 27,
    "left": {
        "pwm_pin": 13,
        "forward_pin": 6,
        "reverse_pin": 5,
        "state_flag_pin": 11,
    },
    "right": {
        "pwm_pin": 12,
        "forward_pin": 20,
        "reverse_pin": 16,
        "state_flag_pin": 26,
    },
}

ultrasonic_configuration = {
    "ussl_pin": 7,
    "ussc_pin": 8,
    "ussr_pin": 25,
    # How many cm is considered clear from center sensor
    "clear_distance_c": 18,
    # How many cm is considered clear from side sensors
    "clear_distance_side": 30,
    # What cm is a clear path.
    "path_distance": 38,
}

```
And to start up
```python
python3 threaded.py
```

The app looks for a camera calibration in ./config matching the camera id in instance/config.py , The same config is used in the calibration helper scripts so the files should be correctly named.

The robot will concurrently look for a locally saved Bosch BNO055 calibration, Whichever parts are present will be used, You will be prompted to calibrate the rest. 

https://www.youtube.com/watch?v=Bw0WuAyGsnY

```
root@media-desktop:/robot/python_rover_robot# python3 threaded.py 
WARNING | Orientation | Expecting value: line 1 column 1 (char 0)
INFO | Orientation | Calibrate now!
INFO | Orientation | 
Gyroscope: 0
Acceleromter: 0
Magnetometer: 0

...

Follow calibration video instructions

...

INFO | Orientation | 
Gyroscope: 3
Acceleromter: 1
Magnetometer: 3

INFO | Orientation | Fully calibrated
INFO | Orientation | Switching to config mode
INFO | Orientation | Saving to cache: GYR_OFFSET_X_LSB
INFO | Orientation | 0
INFO | Orientation | Saving to cache: GYR_OFFSET_X_MSB
INFO | Orientation | 0
INFO | Orientation | Saving to cache: GYR_OFFSET_Y_LSB
INFO | Orientation | 3
INFO | Orientation | Saving to cache: GYR_OFFSET_Y_MSB
INFO | Orientation | 0
INFO | Orientation | Saving to cache: GYR_OFFSET_Z_LSB
INFO | Orientation | 0
INFO | Orientation | Saving to cache: GYR_OFFSET_Z_MSB
INFO | Orientation | 0
INFO | Orientation | Saving to cache: MAG_OFFSET_X_LSB
INFO | Orientation | 24
INFO | Orientation | Saving to cache: MAG_OFFSET_X_MSB
INFO | Orientation | 0
INFO | Orientation | Saving to cache: MAG_OFFSET_Y_LSB
INFO | Orientation | 86
INFO | Orientation | Saving to cache: MAG_OFFSET_Y_MSB
INFO | Orientation | 0
INFO | Orientation | Saving to cache: MAG_OFFSET_Z_LSB
INFO | Orientation | 215
INFO | Orientation | Saving to cache: MAG_OFFSET_Z_MSB
INFO | Orientation | 0
INFO | Orientation | Saving to cache: ACC_OFFSET_X_LSB
INFO | Orientation | 200
INFO | Orientation | Saving to cache: ACC_OFFSET_X_MSB
INFO | Orientation | 255
INFO | Orientation | Saving to cache: ACC_OFFSET_Y_LSB
INFO | Orientation | 22
INFO | Orientation | Saving to cache: ACC_OFFSET_Y_MSB
INFO | Orientation | 0
INFO | Orientation | Saving to cache: ACC_OFFSET_Z_LSB
INFO | Orientation | 227
INFO | Orientation | Saving to cache: ACC_OFFSET_Z_MSB
INFO | Orientation | 255
INFO | Orientation | Saving to cache: ACC_RADIUS_LSB
INFO | Orientation | 232
INFO | Orientation | Saving to cache: ACC_RADIUS_MSB
INFO | Orientation | 3
INFO | Orientation | Saving to cache: MAG_RADIUS_LSB
INFO | Orientation | 189
INFO | Orientation | Saving to cache: MAG_RADIUS_MSB
INFO | Orientation | 2
INFO | Orientation | Configured calibration cache
INFO | Orientation | Switching back to NDOF mode
INFO | Driver | Sensor data populated
WARNING | Driver | I think its clear... driving
```


## Using the calibration tools 
https://docs.opencv.org/2.4/doc/tutorials/calib3d/camera_calibration/camera_calibration.html#

1. Run ./calibration_capture.py on your Rpi and take your captures, This process is really important to get right as without an undistorted image machine vision algorithms are ineffective.
2. You need to rsync or scp ~/robot/calibration to ~/samples/calibration on your local machine when you're done.
3. You then run calibrate.py and it will show you progress as it attempts to find chessboard corners.
4. Succesfully chessboarded calibration images will be saved (and drawn on) under samples/results , Failures will be deleted from samples/calibration.
5. Numpy binary arrays will be saved under samples/config , You need to SCP or Rsync these to ~/robot/config (including sample_image.jpg).

## Viewing the camera feed
Navigate to http://robot:8000 where robot is your robots IP address.

## Hardware list
##### Microcontroller
- Raspberry Pi 4B (used in my project)

Other options; 
- Raspberry Pi 3B
- Nvidia Jetson Developer kit
- Nvidia Xavier NX

##### Platform
- DFRobot "Devastator" platform (any two motor rover will do)
- Polulu Dual MC33926 Motor Driver

##### Navigation

- 3x DFRobot URM37 v5.0 Ultrasonic rangefinders.
- Adafruit ADS 1015 12 bit ADC
- DFRobot 10DOF AHRS (Bosch BNO055 & BMP280)

##### Vision
- PiCamera V2

##### Power
- Adafruit PowerBoost 1000 Charger 5v 1A
- Polymer Lithium Ion Battery (LiPo) 3.7V 6000mAh 

