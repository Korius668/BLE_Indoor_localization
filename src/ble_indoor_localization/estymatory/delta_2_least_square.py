from typing import Any

import numpy as np

from .estymator import Estimator
from .least_square import least_square_estimation, objective_function


class D2LSEstimator(Estimator):
    def __init__(
        self,
        startx,
        starty,
        window_step,
        df_transmitters,
        bounds,
        speed=1.4,
        acceleration=1.0,
        func=objective_function,
        scale_factor=1,
        distance_factor=1.0
    ):
        self.x = startx
        self.y = starty

        self.vx = 0.0
        self.vy = 0.0

        self.dt = window_step.total_seconds()

        self.v_max = speed
        self.a_max = acceleration

        self.scale_factor = scale_factor
        self.func = lambda position, beacons, distances_from_rssi, weights=None: func(position, beacons, distances_from_rssi, weights, distance_factor=distance_factor)
        self.df_transmitters = df_transmitters
        self.bounds = bounds
        offset = 3
        self.ls_bounds = ([bounds[0][0]-offset, bounds[0][1]-offset],[bounds[1][0]+offset, bounds[1][1]+offset])
   
    @Estimator.stay_within_bounds
    def estymation(self, df) -> tuple[Any, Any]:

        x_desired, y_desired  = least_square_estimation(
            df,
            df_transmitters=self.df_transmitters,
            # bounds=self.ls_bounds,
            func=self.func,
        )
        x0, y0 = self.x, self.y

        dx = x_desired - x0
        dy = y_desired - y0

        dist = np.sqrt(dx * dx + dy * dy)

        if dist > 1e-6:
            dir_x = dx / dist
            dir_y = dy / dist
        else:
            dir_x, dir_y = 0.0, 0.0

        v_desired = min(self.v_max, dist / self.dt)
        vx_desired = dir_x * v_desired
        vy_desired = dir_y * v_desired

        dvx_desired = vx_desired - self.vx
        dvy_desired = vy_desired - self.vy

        dv_desired = np.sqrt(dvx_desired * dvx_desired + dvy_desired * dvy_desired)

        max_dv = self.a_max * self.dt

        if dv_desired > max_dv:
            scale = max_dv / dv_desired
        else:
            scale = 1.0

        scale *= self.scale_factor

        self.vx += dvx_desired * scale
        self.vy += dvy_desired * scale

        v = np.sqrt(self.vx * self.vx + self.vy * self.vy)
        if v > self.v_max:
            s = self.v_max / v
            self.vx *= s
            self.vy *= s

        self.x += self.vx * self.dt
        self.y += self.vy * self.dt
        return self.x, self.y