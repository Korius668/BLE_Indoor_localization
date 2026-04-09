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
        self.func = func
        self.df_transmitters = df_transmitters
        self.bounds = bounds
        offset = 3
        self.ls_bounds = ([bounds[0][0]-offset, bounds[0][1]-offset],[bounds[1][0]+offset, bounds[1][1]+offset])
        self.distance_factor = distance_factor
    
    # @Estimator.stay_within_bounds
    def estimation(self, df) -> tuple[Any, Any]:
        target = np.array(least_square_estimation(
            df,
            df_transmitters=self.df_transmitters,
            func=self.func,
            distance_factor=self.distance_factor
        ))

        pos = np.array([self.x, self.y])
        vel = np.array([self.vx, self.vy])

        d = target - pos
        dist = np.linalg.norm(d)

        # Kierunek
        direction = d / dist if dist > 1e-6 else np.zeros(2)

        # Docelowa prędkość
        v_desired = min(self.v_max, dist / self.dt)
        vel_desired = direction * v_desired

        # Ograniczenie przyspieszenia
        dv = vel_desired - vel
        dv_norm = np.linalg.norm(dv)

        max_dv = self.a_max * self.dt
        scale = min(1.0, max_dv / dv_norm) if dv_norm > 0 else 1.0
        scale *= self.scale_factor

        vel += dv * scale

        # Ograniczenie prędkości maksymalnej
        speed = np.linalg.norm(vel)
        if speed > self.v_max:
            vel *= self.v_max / speed

        # Aktualizacja pozycji
        pos += vel * self.dt

        # zapis do obiektu
        self.x, self.y = pos
        self.vx, self.vy = vel

        return self.x, self.y