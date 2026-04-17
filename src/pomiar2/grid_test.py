import csv

from tqdm import tqdm

from .pozycja_w_czasie import precompute_trajectory, START_POS
from .dystans_w_czasie import (WINDOW_STEP, WINDOW_WIDTH,
                                    df,
                                      )
from .pozycje import df_positions
from ble_indoor_localization import (DLSEstimator, 
                                     D2LSEstimator,
                                     D2LSDEstimator,
                                     EKFLocalizer,
                                     Estimator, 
                                     MLEstimator,
                                     least_square_estimation                               
                                     )
from pomiar import bounds, df_transmitters
import numpy as np


if __name__ == "__main__":
  # for distance_factor in tqdm([1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0], desc="Testing LS with different parameters"):
  #   func = lambda df: least_square_estimation(df, df_transmitters, bounds=None, distance_factor=distance_factor)
  #   trajectory = precompute_trajectory(
  #   df=df,
  #   df_positions=df_positions,
  #   func = func,
  #   window_width=WINDOW_WIDTH,
  #   window_step=WINDOW_STEP
  #   # output_file=f"trajectory_{distance_factor}_{speed}_{acceleration}.csv"
  #   )
  #   cumulative_error = round(trajectory["blad"].sum(), 2)
  #   with open("tables/LS_test_results.csv", "a", newline="") as f:
  #     writer = csv.writer(f)
  #     writer.writerow([ "LS", "-",  "-", distance_factor, cumulative_error ])
  # for acceleration in tqdm([1.05, 1.06, 1.07, 1.08, 1.09,1.1,1.12,1.13,1.14,1.15], desc="Testing D2LS with different parameters"):
  #   for distance_factor in [0.61,0.62,0.63,0.64,0.65,0.66,0.67,0.68,0.69,0.71]:
  #     for speed in [0.90,0.91,0.92,0.93,0.94,0.95,0.96,0.97,0.98,0.99]:
  #       d2ls = D2LSEstimator(*START_POS, window_step=WINDOW_STEP,df_transmitters=df_transmitters,bounds=bounds,distance_factor=distance_factor,speed=speed, acceleration=acceleration)
  #       trajectory = precompute_trajectory(
  #       df=df,
  #       df_positions=df_positions,
  #       func =  d2ls.estimation,
  #       window_width=WINDOW_WIDTH,
  #       window_step=WINDOW_STEP
  #       # output_file=f"trajectory_{distance_factor}_{speed}_{acceleration}.csv"
  #       )
  #       cumulative_error = round(trajectory["blad"].sum(), 2)
  #       with open("tables/D2LS_test_results.csv", "a", newline="") as f:
  #         writer = csv.writer(f)
  #         writer.writerow([ "D2LS_v2", acceleration, speed, distance_factor, cumulative_error ])
  
  # for distance_factor in tqdm(np.arange(0.7, 0.71, 0.01), desc="Testing DLS with different parameters"):
  #   for speed in np.arange(0.85, 1.0, 0.01):
  #     dls = DLSEstimator(*START_POS, window_step=WINDOW_STEP,df_transmitters=df_transmitters,bounds=bounds,distance_factor=distance_factor,speed=speed)
  #     trajectory = precompute_trajectory(
  #     df=df,
  #     df_positions=df_positions,
  #     func =  dls.estimation,
  #     window_width=WINDOW_WIDTH,
  #     window_step=WINDOW_STEP
  #     # output_file=f"trajectory_{distance_factor}_{speed}_{acceleration}.csv"
  #     )
  #     cumulative_error = round(trajectory["blad"].sum(), 2)
  #     with open("tables/DLS_test_results.csv", "a", newline="") as f:
  #         writer = csv.writer(f)
  #         writer.writerow([ "DLS", "-", speed, distance_factor, cumulative_error ])
    acceleration, speed, distance_factor = 1.05, 0.9, 0.71
    for damping_factor in tqdm([-1], desc="Testing D2LSD with different parameters"):
      for acceleration in tqdm(np.arange(1.9, 2.3, 0.01), desc="Testing D2LSD with different parameters"):
        acceleration = round(acceleration, 2)
        d2lsd = D2LSDEstimator(*START_POS, window_step=WINDOW_STEP,df_transmitters=df_transmitters,bounds=bounds,distance_factor=distance_factor,speed=speed, acceleration=acceleration, damping_factor=damping_factor)
        trajectory = precompute_trajectory(
        df=df,
        df_positions=df_positions,
        func =  d2lsd.estimation,
        window_width=WINDOW_WIDTH,
        window_step=WINDOW_STEP
        # output_file=f"trajectory_{distance_factor}_{speed}_{acceleration}.csv"
        )
        cumulative_error = round(trajectory["blad"].sum(), 2)
        with open("tables/D2LSD_test_results.csv", "a", newline="") as f:
          writer = csv.writer(f)
          writer.writerow([ "D2LSD", acceleration, speed, distance_factor, damping_factor,cumulative_error ])