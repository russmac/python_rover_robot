import wiringpi


class Motor:
    def __init__(self,
                 en_pin: int,
                 slew_pin: int,
                 pwm_pin: int,
                 forward_pin: int,
                 reverse_pin: int,
                 sf_pin: int,
                 name: str = 'Motor'
                 ):
        self.pwm_pin = pwm_pin
        self.forward_pin = forward_pin
        self.reverse_pin = reverse_pin
        self.en_pin = en_pin
        self.slew_pin = slew_pin
        self.sf_pin = sf_pin
        self.max_speed = 480
        wiringpi.wiringPiSetupGpio()
        wiringpi.pinMode(12, wiringpi.GPIO.PWM_OUTPUT)
        wiringpi.pinMode(13, wiringpi.GPIO.PWM_OUTPUT)
        wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)
        wiringpi.pwmSetRange(self.max_speed)
        wiringpi.pwmSetClock(2)
        wiringpi.pinMode(self.forward_pin,  wiringpi.GPIO.OUTPUT)
        wiringpi.pinMode(self.reverse_pin,  wiringpi.GPIO.OUTPUT)
        wiringpi.pinMode(self.en_pin,  wiringpi.GPIO.OUTPUT)
        wiringpi.pinMode(self.slew_pin,  wiringpi.GPIO.OUTPUT)
        wiringpi.pinMode(self.sf_pin,  wiringpi.GPIO.INPUT)

    def enable(self):
        wiringpi.digitalWrite(self.en_pin, 1)
        wiringpi.digitalWrite(self.slew_pin, 1)

    def disable(self):
        wiringpi.digitalWrite(self.en_pin, 0)
        wiringpi.digitalWrite(self.slew_pin, 0)
        wiringpi.pwmWrite(self.pwm_pin, 0)

    def move(self, direction: int, speed: int = 480):
        if speed > self.max_speed:
            speed = self.max_speed
        if direction is 1:
            self.enable()
            wiringpi.digitalWrite(self.reverse_pin, 0)
            wiringpi.digitalWrite(self.forward_pin, 1)
            wiringpi.pwmWrite(self.pwm_pin, speed)
        elif direction is 0:
            self.enable()
            wiringpi.digitalWrite(self.forward_pin, 0)
            wiringpi.digitalWrite(self.reverse_pin, 1)
            wiringpi.pwmWrite(self.pwm_pin, speed)
