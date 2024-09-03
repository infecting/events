import numpy as np
import scipy.special
import traceback
import json
from config import Config
from controller import Controller
from synthesizer import Synthesizer

sensors = []
controller = None  # Initialize controller outside the try block

for i in range(10):
    try:
        config = Config(duration=1.2, x0=np.random.uniform(400, 800), y0=np.random.uniform(400, 800),
                        complexity=3, xf=None, yf=None)
        controller = Controller(config, None, None, None, None, None)
        synthesizer = Synthesizer(config, controller)
        t, x, y, v = synthesizer.generate_mouse_data()
        sensors.append(synthesizer.format_mouse_data(x, y, t))
    except Exception as e:
        print(f"Error occurred during sensor data generation: {e}")
        if controller:
            controller.dump()  # Only call dump if controller is initialized
        print(traceback.format_exc())

# print(config.x0, config.y0, config.xf, config.yf)
print(f"window.mactData = {sensors}")
