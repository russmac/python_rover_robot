from motor import Motor
from utils import parse_config


class Driver:
    def __init__(self):
        motors = parse_config()['motors']
        self.motor_left = Motor(en_pin=motors['en_pin'],
                                slew_pin=motors['slew_pin'],
                                pwm_pin=motors['left']['pwm_pin'],
                                forward_pin=motors['left']['forward_pin'],
                                reverse_pin=motors['left']['reverse_pin'],
                                sf_pin=motors['left']['state_flag_pin'],
                                name='left')
        self.motor_right = Motor(en_pin=motors['en_pin'],
                                 slew_pin=motors['slew_pin'],
                                 pwm_pin=motors['right']['pwm_pin'],
                                 forward_pin=motors['right']['forward_pin'],
                                 reverse_pin=motors['right']['reverse_pin'],
                                 sf_pin=motors['right']['state_flag_pin'],
                                 name='right')
        self.motor_left.disable()
        self.motor_right.disable()


driver = Driver()
