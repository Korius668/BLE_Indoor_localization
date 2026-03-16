from abc import ABC, abstractmethod



from .least_square import least_square_estimation
from .extended_kalman_filter import EKFLocalizer
from .particle_filter import ParticleFilter
from .minimize_log_error import MLEstimator


class Estimator(ABC):
    @abstractmethod
    def estymation(self, df) -> tuple:
        pass

    @staticmethod
    def universal_position_estimator(df_window, method, state_obj=None, window_step=None, df_transmitters=None):
        """
        method: 'LS', 'DLS','EKF', 'PF', 'MLE'
        """

        if method == "LS":
            return least_square_estimation(df_window, df_transmitters, bounds=(-100, 100))
        elif method == "DLS":
            if state_obj is None:
                raise ValueError("DLS method requires state_obj (DLSEstimator instance)")
            return state_obj.estimation(df_window)

        elif method == "EKF":
            if state_obj is None:
                raise ValueError("EKF method requires state_obj (EKFLocalizer instance)")
            return state_obj.estimation(df_window, state_obj, window_step)

        elif method == "PF":
            if state_obj is None:
                raise ValueError("PF method requires state_obj (ParticleFilter instance)")
            return state_obj.estimation(df_window, state_obj)

        elif method == "MLE":
            if state_obj is None:
                raise ValueError("MLE method requires state_obj (MLEstimator instance)")
            else:
                return state_obj.estimation(df_window)
     