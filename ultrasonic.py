import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import RPi.GPIO as GPIO
from time import sleep

import robot_data
import robot_data as rd
from utils import parse_config


class Ultrasonic:
    def __init__(self):
        config = parse_config()['ultrasonic']
        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1015(i2c)
        self.ussl = AnalogIn(ads, ADS.P0)
        self.ussc = AnalogIn(ads, ADS.P2)
        self.ussr = AnalogIn(ads, ADS.P1)
        self.ussl_pin = config['ussl_pin']
        self.ussc_pin = config['ussc_pin']
        self.ussr_pin = config['ussr_pin']
        self.clear_distance_c = config['clear_distance_c']
        self.clear_distance_side = config['clear_distance_side']
        self.path_distance = config['path_distance']
        GPIO.setup(self.ussl_pin, GPIO.OUT)
        GPIO.setup(self.ussc_pin, GPIO.OUT)
        GPIO.setup(self.ussr_pin, GPIO.OUT)
        self.ussl_trigger = GPIO.PWM(self.ussl_pin, 20000)
        self.ussc_trigger = GPIO.PWM(self.ussc_pin, 20000)
        self.ussr_trigger = GPIO.PWM(self.ussr_pin, 20000)
        self.distances = [0, 0, 0]

    def start(self):
        while True:
            self.get_distances()
            self.evaluate_distances()

    def evaluate_distances(self):
        rd.l_clear = (self.distances[0] > self.clear_distance_side)
        rd.c_clear = (self.distances[1] > self.clear_distance_c)
        rd.r_clear = (self.distances[2] > self.clear_distance_side)
        rd.l_path = (self.distances[0] > self.path_distance)
        rd.c_path = (self.distances[1] > self.path_distance)
        rd.r_path = (self.distances[2] > self.path_distance)

    def get_distances(self):
        distances = [0, 0, 0]
        self.ussl_trigger.start(100)
        self.ussl_trigger.stop()
        distances[0] = self.convert_voltage(self.ussl.voltage)
        sleep(0.037)
        self.ussc_trigger.start(100)
        self.ussc_trigger.stop()
        distances[1] = self.convert_voltage(self.ussc.voltage)
        sleep(0.037)
        self.ussr_trigger.start(100)
        self.ussr_trigger.stop()
        distances[2] = self.convert_voltage(self.ussr.voltage)
        sleep(0.037)
        robot_data.current_distances = distances

    @staticmethod
    def convert_voltage(voltage):
        # 6.8mV = 1cm
        return round((voltage*1000/4.125), 1)
