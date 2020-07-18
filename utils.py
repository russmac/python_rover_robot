import instance.config


def parse_config():
    motors = instance.config.motor_configuration
    camera = instance.config.camera_configurations[f'{instance.config.camera_selection}']
    ultrasonic = instance.config.ultrasonic_configuration
    return {'motors': motors,
            'camera': camera,
            'ultrasonic': ultrasonic
            }
