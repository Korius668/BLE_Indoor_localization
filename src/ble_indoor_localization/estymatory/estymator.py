from abc import ABC, abstractmethod
import functools

class Estimator(ABC):
    @abstractmethod
    def estimation(self, df) -> tuple:
        pass
    
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