import csv

from tqdm import tqdm

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



if __name__ == "__main__":
  # with open("tables/grid_test_results.csv", "w", newline="") as f: 
  #   writer = csv.writer(f) 
  #   writer.writerow(["Estymator","przyspieszenie", "predkosc","wspolczynnik odleglosci","blad" ])
  # func = lambda df: least_square_estimation(df, df_transmitters, bounds=None, distance_factor=distance_factor)
  # trajectory = precompute_trajectory(
  # df=df,
  # df_positions=df_positions,
  # func = func,
  # window_width=WINDOW_WIDTH,
  # window_step=WINDOW_STEP
  # # output_file=f"trajectory_{distance_factor}_{speed}_{acceleration}.csv"
  # )
  # cumulative_error = round(trajectory["blad"].sum(), 2)
  # with open("tables/grid_test_results.csv", "a", newline="") as f:
  #   writer = csv.writer(f)
  #   writer.writerow([ "LS", "-",  "-", distance_factor, cumulative_error ])
  for acceleration in tqdm([1.1,1.2,1.3,1.4,1.5], desc="Testing D2LS with different parameters"):
    for distance_factor in [0, -0.05, -0.1, -0.15, -0.2]:
      for speed in [0.9,0.95,1,1.1,1.15]:
        d2ls = D2LSEstimator(*START_POS, window_step=WINDOW_STEP,df_transmitters=df_transmitters,bounds=bounds,distance_factor=distance_factor,speed=speed, acceleration=acceleration)
        trajectory = precompute_trajectory(
        df=df,
        df_positions=df_positions,
        func =  d2ls.estimation,
        window_width=WINDOW_WIDTH,
        window_step=WINDOW_STEP
        # output_file=f"trajectory_{distance_factor}_{speed}_{acceleration}.csv"
        )
        cumulative_error = round(trajectory["blad"].sum(), 2)
        with open("tables/grid_test_results.csv", "a", newline="") as f:
          writer = csv.writer(f)
          writer.writerow([ "D2LS", acceleration, speed, distance_factor, cumulative_error ])
  
    # for distance_factor in tqdm([-0.2,-0.3,-0.4,-0.5,-0.6], desc="Testing DLS with different parameters"):
    #   for speed in [0.95,1,1.1]:
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
    #     with open("tables/grid_test_results.csv", "a", newline="") as f:
    #       writer = csv.writer(f)
    #       writer.writerow([ "DLS", "-", speed, distance_factor, cumulative_error ])

