import numpy as np
from scipy.special import erf


class Config:
    def __init__(self, duration=None, freq=50, snr=.98, complexity=3, screen_size_x=1920, screen_size_y=1080, x0=0, y0=0, xf=None, yf=None):
        if duration:
            self.duration = duration
        else:
            raise Exception("Duration needed")

        self.freq = freq
        self.snr = snr
        self.complexity = complexity
        self.screen_size_x = screen_size_x
        self.screen_size_y = screen_size_y
        self.x0 = x0
        self.y0 = y0

        if xf is not None and yf is not None:
            self.end = True
            if isinstance(xf, list) and isinstance(yf, list):
                if len(xf) != complexity or len(yf) != complexity:
                    raise ValueError(
                        "Length of xf and yf lists must match the complexity")
                # Store original endpoints
                self.original_xf = xf
                self.original_yf = yf
                # Adjust each endpoint relative to the starting position
                self.xf = []
                self.yf = []
                x00 = x0
                y00 = y0
                for x in xf:
                    print("x00", x00)
                    self.xf.append(x-x00)
                    x00 = x - (x-x00)
                for y in yf:
                    print("y00", y00)
                    self.yf.append(y-y00)
                    y00 = y - (y-y00)
            else:
                # Single endpoint, repeat for all strokes
                self.original_xf = [xf] * complexity
                self.original_yf = [yf] * complexity
                self.xf = [xf - x0] * complexity
                self.yf = [yf - y0] * complexity
        else:
            self.end = False
            self.xf = None
            self.yf = None

        self.current_stroke = 0

    def update_positions(self):
        if self.end and self.current_stroke < self.complexity - 1:
            self.current_stroke += 1
            self.x0 = self.original_xf[self.current_stroke - 1]
            self.y0 = self.original_yf[self.current_stroke - 1]
            # Adjust remaining endpoints relative to new starting position
            for i in range(self.current_stroke, self.complexity):
                self.xf[i] = self.original_xf[i] - self.x0
                self.yf[i] = self.original_yf[i] - self.y0
