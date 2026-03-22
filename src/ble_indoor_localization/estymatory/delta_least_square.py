from typing import Any

import numpy as np

from .estymator import Estimator
from .least_square import least_square_estimation, objective_function


class DLSEstimator(Estimator):
    def __init__(
        self, 
        startx, 
        starty, 
        window_step, 
        df_transmitters, 
        bounds,
        speed = 1.4, 
        func = objective_function,  
        scale_factor=1, 
        distance_factor=1.0
    ):
        self.x = startx
        self.y = starty
        self.v_max = speed
        self.dt = window_step.total_seconds()
        self.scale_factor = scale_factor
        self.func = lambda position, beacons, distances_from_rssi, weights=None: func(position, beacons, distances_from_rssi, weights, distance_factor=distance_factor)
        self.df_transmitters = df_transmitters
        self.bounds = bounds
        
    def estymation(self, df) -> tuple[Any, Any]:
        x1, y1 = least_square_estimation(df,df_transmitters=self.df_transmitters, bounds=self.bounds, func=self.func)
        x0, y0 = self.x, self.y
        max_speed = self.v_max

        dx = x1 - x0
        dy = y1 - y0

        dist = np.sqrt(dx*dx + dy*dy)

       
        max_dist = max_speed * self.dt

        if dist > max_dist:
            scale = max_dist / dist
        else:
            scale = 1.0

        scale *= self.scale_factor

        x = x0 + dx * scale
        y = y0 + dy * scale
        self.x, self.y = x,y
        return x, y

    

 