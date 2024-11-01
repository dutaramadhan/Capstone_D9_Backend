import random
import time

def generate_weight():
    return round(random.uniform(0, 100), 2)

def get_weight_data():
    return {
        'weight': generate_weight(),
        'timestamp': time.time()
    }
