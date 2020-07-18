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
    "en_pin": 17,
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
