import threading
from ultrasonic import Ultrasonic
from orientation import Orientation
from driver import Driver
from visual import Visual
from stream import Stream
import logging

ROBOT_NAME = 'Robot'
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s | %(threadName)s | %(message)s')

if __name__ == "__main__":
    ultrasonic = Ultrasonic()
    orientation = Orientation()
    driver = Driver()
    visual = Visual()
    streaming = Stream()
    ultrasonic_thread = threading.Thread(name='Ultrasonic', target=ultrasonic.start, daemon=False)
    orientation_thread = threading.Thread(name='Orientation', target=orientation.start, daemon=False)
    driver_thread = threading.Thread(name='Driver', target=driver.start, daemon=False)
    streaming_thread = threading.Thread(name='Streaming', target=streaming.start, daemon=False)
    visual_thread = threading.Thread(name='Visual', target=visual.start, daemon=False)
    ultrasonic_thread.start()
    orientation_thread.start()
    streaming_thread.start()
    visual_thread.start()
    driver_thread.start()
