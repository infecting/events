import numpy as np
from scipy.special import erf
from config import Config
from controller import Controller


class Synthesizer:
    def __init__(self, config=None, controller=None):
        self.controller = controller if controller else Controller()
        self.config = config if config else Config()

    def angle(self, t, t0j, stroke_index):
        epsilon = 1e-10
        t_adjusted = np.maximum(t - t0j, epsilon)

        log_term = (np.log(t_adjusted) - self.controller.muj) / \
            (self.controller.sigmaj * np.sqrt(2))
        thetae = self.controller.thetaej[stroke_index] if isinstance(
            self.controller.thetaej, list) else self.controller.thetaej
        return self.controller.thetasj + (thetae - self.controller.thetasj) / 2 * (1 + erf(log_term))

    def position(self, t, t0j, stroke_index):
        x = np.zeros_like(t)
        y = np.zeros_like(t)
        phi = self.angle(t, t0j, stroke_index)

        # Handle both array and scalar cases for thetaej
        if isinstance(self.controller.thetaej, (list, np.ndarray)):
            thetae = self.controller.thetaej[stroke_index]
        else:
            thetae = self.controller.thetaej

        # Handle both array and scalar cases for Dj
        if isinstance(self.controller.Dj, (list, np.ndarray)):
            Dje = self.controller.Dj[stroke_index]
        else:
            Dje = self.controller.Dj

        x += Dje * (np.sin(phi) - np.sin(self.controller.thetasj)) / \
            (thetae - self.controller.thetasj)
        y += Dje * (-np.cos(phi) + np.cos(self.controller.thetasj)) / \
            (thetae - self.controller.thetasj)
        return x, y

    def generate_non_uniform_time_array(self, initial_freq, min_freq=50, max_freq=140):
        t_total = []
        t = 0
        current_freq = initial_freq
        while t < self.config.duration:
            current_freq = np.random.uniform(min_freq, max_freq)
            time_step = 1.0 / current_freq
            t += time_step
            if t <= self.config.duration:
                t_total.append(t)
        return np.array(t_total)

    def calculate_power(self, x, y):
        x_power = np.sum(np.square(x)) / len(x)
        y_power = np.sum(np.square(y)) / len(y)
        nx = x_power / self.config.snr
        ny = y_power / self.config.snr
        return nx, ny

    def generate_scale_factor(self, nx, ny, dt):
        gaussian_noise = np.random.uniform(0, 1)
        scale_factor_x = np.sqrt(nx / dt) * gaussian_noise
        scale_factor_y = np.sqrt(ny / dt) * gaussian_noise
        return scale_factor_x, scale_factor_y

    def generate_mouse_data(self):
        t_total = self.generate_non_uniform_time_array(
            self.config.freq, 50, 140)
        x_total = np.zeros_like(t_total)
        y_total = np.zeros_like(t_total)

        stroke_duration = self.config.duration / self.config.complexity
        x_offset, y_offset = 0, 0

        for i in range(self.config.complexity):
            t_start = i * stroke_duration
            t_end = (i + 1) * stroke_duration
            t_stroke = t_total[(t_total >= t_start) & (t_total < t_end)]

            # Adjust the controller's velocity based on the stroke
            self.controller.adjust_velocity(stroke_duration, t_start)

            # Generate positions for this stroke
            if not self.config.end:
                self.controller = Controller(self.config)
            x_stroke, y_stroke = self.position(t_stroke, t_start, i)
            # Apply offset
            x_stroke += x_offset
            y_stroke += y_offset

            # Assign stroke data to the overall trajectory
            x_total[(t_total >= t_start) & (t_total < t_end)] = x_stroke
            y_total[(t_total >= t_start) & (t_total < t_end)] = y_stroke

            # Update offset for the next stroke
            x_offset = x_stroke[-1]
            y_offset = y_stroke[-1]

        # Signal and noise calculations
        signal_power_x = np.mean(x_total**2)
        signal_power_y = np.mean(y_total ** 2)
        noise_power_x = signal_power_x / (self.config.snr)
        noise_power_y = signal_power_y / (self.config.snr)

        noise_x = np.random.normal(
            0, 1, len(x_total)) * (np.sqrt(noise_power_x/self.config.duration) * .01)
        noise_y = np.random.normal(
            0, 1, len(y_total)) * (np.sqrt(noise_power_y/self.config.duration)*.01)

        # x_total += noise_x
        # y_total += noise_y

        # Final adjustments and clipping
        x_total += self.config.x0
        y_total += self.config.y0

        x_total = np.clip(x_total, 0, self.config.screen_size_x)
        y_total = np.clip(y_total, 0, self.config.screen_size_y)

        # Calculate velocities
        vx = np.gradient(x_total, t_total)
        vy = np.gradient(y_total, t_total)
        v = np.sqrt(vx**2 + vy**2)

        return t_total, x_total, y_total, v

    def format_mouse_data(self, x, y, t):
        formatted_data = []
        for i in range(len(x)):
            formatted_data.append(
                f"{int(i)},3,{int(t[i]*1000)},{int(x[i])},{int(y[i])},-1")
        return ";".join(formatted_data)
