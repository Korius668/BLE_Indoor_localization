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
        self.distance_factor = distance_factor

    # # @Estimator.stay_within_bounds
    def estimation(self, df) -> tuple[Any, Any]:
        p_ls = np.array(least_square_estimation(
            df,
            df_transmitters=self.df_transmitters, 
            # bounds=self.ounds, 
            func=self.func,
            distance_factor=self.distance_factor
        ))
        p = np.array([self.x, self.y])
        
        d = p_ls - p
        dist = np.linalg.norm(d)
            
        max_dist = self.v_max * self.dt

        if dist > max_dist:
            scale = max_dist / dist
        else:
            scale = 1.0
        
        p +=  d * scale
        
        self.x, self.y = p
        
        return self.x, self.y
    

 