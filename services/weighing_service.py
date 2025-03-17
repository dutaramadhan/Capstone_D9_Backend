# import random
# import time

# def generate_weight():
#     return round(random.uniform(0, 1000), 2)

# def get_weight_data():
#     return {
#         'weight': generate_weight(),
#         'timestamp': time.time()
#     }

import serial
import time
from config import Config

SERIAL_PORT = Config.SERIAL_PORT
BAUD_RATE = 9600

def get_weight_data():
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, bytesize=serial.SEVENBITS, 
                           parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1) as ser:
            if ser.in_waiting > 0:
                weight_data = ser.readline().decode('utf-8', errors='ignore').strip()
                
                try:
                    weight_value = float(weight_data)
                except ValueError:
                    weight_value = 0.0

                return {
                    'weight': weight_value,
                    'timestamp': time.time()
                }
    except serial.SerialException as e:
        print(f"Serial connection error: {e}")
        return {
            'weight': None,
            'timestamp': time.time(),
            'error': f"Serial connection error: {e}"
        }
    
    except Exception as e:
        print(f"Unexpected error in get_weight_data: {e}")
        return {
            'weight': None,
            'timestamp': time.time(),
            'error': str(e)
        }