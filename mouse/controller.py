import numpy as np
from scipy.special import erf
import json
from config import Config


class Controller:
    def __init__(self, config=None, Dj=None, muj=None, sigmaj=None, thetasj=None, thetaej=None):
        self.vmax = 1200
        self.vmin = 200
        self.config = config if config else Config()
        self.thetasj = thetasj if thetasj else np.random.uniform(-np.pi, np.pi)
        self.sigmaj = sigmaj if sigmaj else np.random.uniform(0.1, 3)
        self.muj = muj if muj else np.random.uniform(-3, 3)
        self.thetaej = thetaej if thetaej else self.generateThetaEj()
        self.Dj = Dj if Dj else self.generateDj()

    def adjust_velocity(self, t, t0j):
        if not self.config.end:
            vm = self.calculate_v_max(t0j)
            while vm < 300 or vm > 1300:
                self.muj = np.random.uniform(-3, 3)
                vm = self.calculate_v_max(t0j)

    def velocity_profile(self, t, t0j, mu):
        epsilon = 1e-10
        t_adjusted = np.maximum(t - t0j, epsilon)
        return (self.Dj / (t_adjusted * self.sigmaj * np.sqrt(2 * np.pi))) * \
            np.exp(-(np.log(t_adjusted) - mu)**2 / (2 * self.sigmaj**2))

    def calculate_velocity_derivative(self, t, t0j, mu):
        epsilon = 1e-6
        return (self.velocity_profile(t + epsilon, t0j, mu) - self.velocity_profile(t, t0j, mu)) / epsilon

    def calculate_v_max(self, t0j):
        tmax = t0j + np.exp((-np.square(self.sigmaj)) + self.muj)
        return self.velocity_profile(tmax, t0j, self.muj)

    def generateDj(self):
        Dj_list = []
        current_thetasj = self.thetasj  # Start with the initial thetasj
        if self.config.end:
            for i in range(self.config.complexity):
                erf_arg = np.sqrt(
                    2) * (self.muj - np.log(self.config.duration - 0.01)) / (2 * self.sigmaj)
                atan_arg = (self.config.xf[i] * np.tan(current_thetasj / 2) - self.config.yf[i]) / \
                    (self.config.xf[i] + self.config.yf[i]
                     * np.tan(current_thetasj / 2))

                numerator = self.config.xf[i] * (current_thetasj * (erf(erf_arg) - 1) - current_thetasj *
                                                 erf(erf_arg) - current_thetasj - 4 * np.arctan(atan_arg))
                denominator = (np.sin(current_thetasj) + np.sin(2 *
                                                                np.arctan(atan_arg))) * (erf(erf_arg) - 1)
                Dj = numerator / denominator
                Dj_list.append(Dj)

                # Update thetasj for the next stroke to be this stroke's thetaej
                if isinstance(self.thetaej, list):
                    current_thetasj = self.thetaej[i]
                else:
                    current_thetasj = self.thetaej

            return Dj_list
        else:
            return np.random.uniform(100, 1200)

    def generateThetaEj(self):
        thetaej_list = []
        current_thetasj = self.thetasj  # Start with the initial thetasj
        if self.config.end:
            for i in range(self.config.complexity):
                erf_arg = np.sqrt(
                    2) * (self.muj - np.log(self.config.duration - 0.01)) / (2 * self.sigmaj)
                atan_arg = (self.config.xf[i] * np.tan(current_thetasj / 2) - self.config.yf[i]) / \
                    (self.config.xf[i] + self.config.yf[i]
                     * np.tan(current_thetasj / 2))

                numerator = current_thetasj * \
                    erf(erf_arg) + current_thetasj + 4 * np.arctan(atan_arg)
                denominator = erf(erf_arg) - 1

                # Calculate the current stroke's thetaej
                thetaej = numerator / denominator
                thetaej_list.append(thetaej)

                # Update thetasj for the next stroke to be this stroke's thetaej
                current_thetasj = thetaej

            return thetaej_list
        return np.random.uniform(-np.pi, np.pi)

    def dump(self):
        # Convert the attributes to a dictionary
        controller_dict = {
            "vmax": self.vmax,
            "vmin": self.vmin,
            "config": self.config.__dict__,
            "thetasj": self.thetasj,
            "sigmaj": self.sigmaj,
            "muj": self.muj,
            "thetaej": self.thetaej,
            "Dj": self.Dj
        }
        # Convert dictionary to JSON for pretty printing
        controller_json = json.dumps(controller_dict, indent=4)
        print(controller_json)
        return controller_json
