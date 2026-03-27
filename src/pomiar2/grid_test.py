from .pozycja_w_czasie import precompute_trajectory, START_POS
from .dystans_w_czasie import (WINDOW_STEP, WINDOW_WIDTH,
                                    df,
                                      )
from .pozycje import df_positions
from ble_indoor_localization import (DLSEstimator, 
                                     D2LSEstimator,
                                     EKFLocalizer,
                                     Estimator, 
                                     MLEstimator,
                                     least_square_estimation                               
                                     )
from pomiar import bounds, df_transmitters



if __name__ is "__main__":
    distance_factor=0.1
    d2ls = D2LSEstimator(*START_POS, window_step=WINDOW_STEP,df_transmitters=df_transmitters,bounds=bounds,distance_factor=0.5, acceleration=0.30)
    trajectory = precompute_trajectory(
    df=df,
    df_positions=df_positions,
    func =  d2ls.estimation,
    window_width=WINDOW_WIDTH,
    window_step=WINDOW_STEP
    )
