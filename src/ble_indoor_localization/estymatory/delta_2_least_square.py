from typing import Any

import numpy as np

from .estymator import Estimator
from .least_square import least_square_estimation, objective_function


class D2LSEstimator(Estimator):
    def __init__(self, startx, starty, window_step, df_transmitters, bounds,speed = 0, maxspeed = 1.4,acceleration = 0.1, func = objective_function,  scale_factor=1, distance_factor=1.0):
        self.maxspeed = maxspeed
        self.speed = speed
        self.acceleration = acceleration
        self.x = startx
        self.y = starty
        self.dt = window_step.total_seconds()
        self.scale_factor = scale_factor
        self.func = lambda position, beacons, distances_from_rssi, weights=None: func(position, beacons, distances_from_rssi, weights, distance_factor=distance_factor)
        self.df_transmitters = df_transmitters
        self.bounds = bounds
        
    def estymation(self, df) -> tuple[Any, Any]:
        x1, y1 = least_square_estimation(df,df_transmitters=self.df_transmitters, bounds=self.bounds, func=self.func)
        x0, y0 = self.x, self.y

        self.speed = min(self.speed + self.acceleration * self.dt, self.maxspeed)

        dx = x1 - x0
        dy = y1 - y0

        max_dist = np.sqrt(dx*dx + dy*dy)
        
        # Avoid division by zero and overflow
        if max_dist > 1e-7:
            dist = min(max_dist, self.speed * self.dt)
            scale = dist / max_dist
        else:
            scale = 0

        scale *= self.scale_factor

        x = x0 + dx * scale
        y = y0 + dy * scale
        self.x, self.y = x, y
        return x, y

    

 