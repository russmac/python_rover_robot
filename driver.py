from motor import Motor
from time import time, sleep
import robot_data as rd
from random import choice
import logging
import time
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
        self.travel_memory = list()
        self.turn_a = 22.5
        self.turn_limit = 180 / self.turn_a
        self.last_turn = None
        self.turns = 0
        self.turn_speed = 440
        self.opposites = {"left": "right", "right": "left"}

    def start(self):
        self.motor_left.disable()
        self.motor_right.disable()
        while not rd.current_heading or not rd.current_distances:
            logging.debug("Waiting for sensor data")
            logging.debug(rd.current_heading)
            logging.debug(rd.current_distances)
            sleep(1)
        logging.info('Sensor data populated')
        self.navigate()

    def navigate(self):
        while True:
            # If its clear ahead left and right continue forwards.
            if rd.c_clear and rd.l_clear and rd.r_clear:
                logging.info(f'I think its clear... heading: {rd.current_heading}')
                self.drive()
                # todo: Use travel_memory to map previous movement
                self.travel_memory.append([rd.current_heading, int(time.time())])
                self.turns = 0
            else:
                # Evaluate turn options
                decision = self.evaluate_turn()
                logging.info(f'Decided to turn {decision}')
                self.turn(decision)

    def evaluate_turn(self):
        logging.warning(f"c_clear: {rd.c_clear} l_clear: {rd.l_clear} r_clear: {rd.r_clear}")
        # If we just drove here, Use USS to determine turn.
        if (self.last_turn is None and rd.l_clear) or (rd.c_clear and rd.l_clear):
            turn_choice = 'left'
        elif (self.last_turn is None and rd.r_clear) or (rd.c_clear and rd.r_clear):
            turn_choice = 'right'
        # Turn in the same direction until we find a gap
        elif self.turns <= self.turn_limit and self.last_turn is not None:
            turn_choice = self.last_turn
        # If we turn 180 degrees we go back the other way. (prevent erroneous physical navigation loop)
        elif self.turns >= self.turn_limit:
            turn_choice = self.opposites[self.last_turn]
            # Double the turn limit to turn back the other way.
            logging.info(f'Negating turn count: {self.turns}')
            self.turns = (0 - self.turn_limit)
        else:
            # Its the first turn at this position
            turn_choice = choice(['left', 'right'])

        if turn_choice == 'left':
            self.last_turn = turn_choice
            return -self.turn_a
        elif turn_choice == 'right':
            self.last_turn = turn_choice
            return self.turn_a
        else:
            self.last_turn = self.opposites[self.last_turn]
            return -180

    # Drive in a straight(ish) line
    def drive(self, distance_cm: int = 10, direction: str = "forwards"):
        self.last_turn = None
        self.turns = 0
        logging.info(f'Driving {distance_cm} centimeters {direction}')
        initial_distance = rd.current_distances[1]
        initial_time = time.time()
        motors_on = False
        while True:
            if not (rd.c_clear and rd.l_clear and rd.r_clear):
                # Something got in the way
                return False
            # We only drive for 1000ms or 10cm whichever is first. # todo: Check accelerometer we are actually moving
            if time.time() > initial_time + 1:
                return True
            if not rd.current_heading or not rd.current_distances:
                self.motor_left.disable()
                self.motor_right.disable()
                logging.error('Lost navigation data')
                continue
            # todo: discard outliers in ultrasonic thread.
            # If we have driven the distance_cm we return to parent loop
            if rd.current_distances[1] <= (initial_distance - distance_cm):
                self.motor_left.disable()
                self.motor_right.disable()
                return True
            # We were not currently driving so we drive.
            if not motors_on:
                self.motor_left.move("forwards")
                self.motor_right.move("forwards")
                motors_on = True

    @staticmethod
    def heading_calc(angle, initial_heading):
        if initial_heading + angle > 360:
            desired_heading = (initial_heading + angle) - 360
        elif initial_heading + angle < 0:
            desired_heading = (initial_heading + angle) + 360
        else:
            desired_heading = rd.current_heading + angle
        return desired_heading

    def turn(self, angle: int = 0, hard: bool = False):
        if angle == 0:
            logging.error('I cant turn 0 degrees!')
            return False
        self.turns += 1
        initial_heading = rd.current_heading
        # If we lose magnetometer heading we wait
        while initial_heading is None:
            logging.warning('Waiting for heading')
            initial_heading = rd.current_heading
        desired_heading = self.heading_calc(angle, initial_heading)
        logging.debug(f'Desired Heading: {desired_heading}')
        driving = False
        logging.debug(f'Initial heading: {initial_heading}')
        while True:
            # If we lose magnetometer heading mid-turn we return to navigation loop.
            if not rd.current_heading:
                logging.warning(f'Current_heading is {type(rd.current_heading)}')
                return False
            # If a path clears mid turn return to navigation loop
            if rd.c_path and rd.l_clear and rd.r_clear:
                self.motor_left.disable()
                self.motor_right.disable()
                return True
            if self.approximate_angle(desired_heading, rd.current_heading):
                logging.debug(f'Current Heading: {rd.current_heading}')
                logging.debug(f"{angle} Turn complete attempting to disable motors")
                self.motor_left.disable()
                self.motor_right.disable()
                return True
            if driving is not True:
                if angle > 0: # Left
                    self.motor_left.move("backwards", speed=self.turn_speed)
                    self.motor_right.move("forwards", speed=self.turn_speed)
                elif angle < 0: # Right
                    self.motor_left.move("forwards", speed=self.turn_speed)
                    self.motor_right.move("backwards", speed=self.turn_speed)
                driving = True

    def abort(self):
        logging.debug('Aborting')
        self.motor_left.disable()
        self.motor_right.disable()

    @staticmethod
    def approximate_angle(desired, current):
        try:
            fuzzy = 5
            if (desired - fuzzy) <= current <= (desired + fuzzy):
                return True
            else:
                return False
        except TypeError as e:
            logging.debug('Exception caught attempting None comparison')
