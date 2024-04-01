import adafruit_bno055
from busio import I2C
from board import SDA, SCL
import robot_data as rd
import json
from time import sleep
from micropython import const
import logging

SENSOR_MODES ={
    "NDOF": const(0x0C),
    "CONFIG": const(0x00)
}

CALIBRATION_REGISTERS = {
    "GYR_OFFSET_X_LSB": const(0x61),
    "GYR_OFFSET_X_MSB": const(0x62),
    "GYR_OFFSET_Y_LSB": const(0x63),
    "GYR_OFFSET_Y_MSB": const(0x64),
    "GYR_OFFSET_Z_LSB": const(0x65),
    "GYR_OFFSET_Z_MSB": const(0x66),
    "MAG_OFFSET_X_LSB": const(0x5B),
    "MAG_OFFSET_X_MSB": const(0x5C),
    "MAG_OFFSET_Y_LSB": const(0X5D),
    "MAG_OFFSET_Y_MSB": const(0x5E),
    "MAG_OFFSET_Z_LSB": const(0x5F),
    "MAG_OFFSET_Z_MSB": const(0x60),
    "ACC_OFFSET_X_LSB": const(0x55),
    "ACC_OFFSET_X_MSB": const(0x56),
    "ACC_OFFSET_Y_LSB": const(0x57),
    "ACC_OFFSET_Y_MSB": const(0x58),
    "ACC_OFFSET_Z_LSB": const(0x59),
    "ACC_OFFSET_Z_MSB": const(0x5A),
    "ACC_RADIUS_LSB": const(0x67),
    "ACC_RADIUS_MSB": const(0x68),
    "MAG_RADIUS_LSB": const(0x69),
    "MAG_RADIUS_MSB": const(0x6A)
}


class Orientation():
    def __init__(self, frequency: int = 1):
        i2c = I2C(SCL, SDA)
        self.sensor = adafruit_bno055.BNO055_I2C(i2c)
        self.sensor.mode = SENSOR_MODES['NDOF']
        self.frequency = frequency
        self.calibration_cache = dict()
        self.acceleration_log = list()

    def check_calibration(self):
        c = self.sensor.calibration_status
        if sum(c) == 12:
            return True
        return False

    def start(self):
        # Check for calibration and attempt to load if none.
        if not self.check_calibration():
            if not self.load_stored_calibration():
                logging.warning("Could not load calibration")
        if self.sensor.calibrated and self.check_calibration():
            logging.info('Fully calibrated')
        else:
            logging.info('Calibrate now!')
            while True:
                logging.info(f'\nGyroscope: {self.sensor.calibration_status[1]}\n'
                             f'Accelerometer: {self.sensor.calibration_status[2]}\n'
                             f'Magnetometer: {self.sensor.calibration_status[3]}\n')
                sleep(1)
                if self.check_calibration():
                    logging.info('Fully calibrated')
                    self.save_current_calibration()
                    break
        while True:
            heading = self.orientation()['euler'][0]
            if heading is not None:
                rd.current_heading = heading

    def load_stored_calibration(self):
        try:
            calibration_file = open('config/calibration.json', 'r')
            self.calibration_cache = json.loads(calibration_file.read())
            if self.calibration_cache:
                calibration_file.close()
                logging.info('Loaded calibration cache from disk')
        except FileNotFoundError as e:
            logging.error(f'File not found!: \n {e}')
            return False
        except Exception as e:
            logging.warning(e)
            return False
        for reg_name, reg_value in self.calibration_cache.items():
            self.sensor.mode = SENSOR_MODES['CONFIG']
            # Write to the corresponding reg location the reg value loaded from cache
            self.sensor._write_register(CALIBRATION_REGISTERS[reg_name], reg_value)
        self.sensor.mode = SENSOR_MODES['NDOF']
        return True

    def save_current_calibration(self):
        logging.info("Switching to config mode")
        self.sensor.mode = SENSOR_MODES['CONFIG']
        for reg_name, reg_location in CALIBRATION_REGISTERS.items():
            logging.info(f'Saving to cache: {reg_name}')
            current_offset = self.sensor._read_register(reg_location)
            logging.info(current_offset)
            if current_offset > 0:
                self.calibration_cache[reg_name] = self.sensor._read_register(reg_location)
        logging.info('Configured calibration cache')
        try:
            calibration_file = open('config/calibration.json', 'w')
            content = json.dumps(self.calibration_cache)
            if calibration_file.writelines(content):
                logging.info('Wrote calibration cache to disk')
                calibration_file.close()
                return True
            calibration_file.close()
            logging.info("Switching back to NDOF mode")
            self.sensor.mode = SENSOR_MODES['NDOF']
            return True
        except Exception as e:
            logging.critical(e)

    def orientation(self):
        result = {
            "euler": self.sensor.euler,
        }
        return result


if __name__ == '__main__':
    o = Orientation()
    o.start()


