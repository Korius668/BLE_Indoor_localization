from abc import ABC, abstractmethod
import functools

from .extended_kalman_filter import EKFLocalizer
from .least_square import least_square_estimation
from .minimize_log_error import MLEstimator
from .particle_filter import ParticleFilter


class Estimator(ABC):
    @abstractmethod
    def estimation(self, df) -> tuple:
        pass
    
    # def stay_within_bounds(self, x, y):
    #     x_min, y_min = self.bounds[0]
    #     x_max, y_max = self.bounds[1]
    #     x = max(x_min, min(x, x_max))
    #     y = max(y_min, min(y, y_max))
    #     return x, y
    
    @staticmethod
    def stay_within_bounds(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            x, y = func(self, *args, **kwargs)
            x_min, y_min = self.bounds[0]
            x_max, y_max = self.bounds[1]
            x = max(x_min, min(x, x_max))
            y = max(y_min, min(y, y_max))
            return x, y
        return wrapper