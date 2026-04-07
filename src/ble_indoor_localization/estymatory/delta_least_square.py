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
        self.func = func
        self.df_transmitters = df_transmitters
        self.bounds = bounds
    
    # @Estimator.stay_within_bounds
    def estimation(self, df) -> tuple[Any, Any]:
        x_desired, y_desired = least_square_estimation(
            df,
            df_transmitters=self.df_transmitters, 
            # bounds=self.bounds, 
            func=self.func
        )
        x0, y0 = self.x, self.y
        
        dx = x_desired - x0
        dy = y_desired - y0

        dist = np.sqrt(dx * dx + dy * dy)
            
        max_dist = self.v_max * self.dt

        if dist > max_dist:
            scale = max_dist / dist
        else:
            scale = 1.0

        scale *= self.scale_factor

        x = x0 + dx * scale
        y = y0 + dy * scale
        self.x, self.y = x,y
        return x, y

    

 