from .estymator import Estimator


def foggy_wrapper(est1: Estimator, est2: Estimator, proportion=0.5):
    def wrapper(df_window):
        x1, y1 = est1.estimation(df_window)
        x2, y2 = est2.estimation(df_window)

        x = proportion * x1 + (1 - proportion) * x2
        y = proportion * y1 + (1 - proportion) * y2

        return x, y
    return wrapper