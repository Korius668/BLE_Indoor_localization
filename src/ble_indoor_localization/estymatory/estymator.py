from abc import ABC, abstractmethod

from .extended_kalman_filter import EKFLocalizer
from .least_square import least_square_estimation
from .minimize_log_error import MLEstimator
from .particle_filter import ParticleFilter


class Estimator(ABC):
    @abstractmethod
    def estymation(self, df) -> tuple:
        pass