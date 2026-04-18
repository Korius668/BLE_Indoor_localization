import csv
from datetime import timedelta

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

def LS_grid_search():
  for distance_factor in tqdm(np.arange(4,10,1), desc="Testing LS with different parameters"):
    for window_width_seconds in np.arange(3, 5, 5):
      distance_factor = round(distance_factor,3)
      window_width_seconds = round(window_width_seconds,3)
      window_width = timedelta(seconds=int(window_width_seconds))
      func = lambda df: least_square_estimation(df, df_transmitters, bounds=None, distance_factor=distance_factor)
      trajectory = precompute_trajectory(
      df=df,
      df_positions=df_positions,
      func = func,
      window_width=window_width,
      window_step=WINDOW_STEP
      # output_file=f"trajectory_{distance_factor}_{speed}_{acceleration}.csv"
      )
      cumulative_error = round(trajectory["blad"].sum(), 2)
      with open("tables/LS_test_results.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([ "LS", "-",  "-", distance_factor, window_width_seconds, cumulative_error ])

def DLS_grid_search():
  window_width_seconds = 3
  window_width = timedelta(seconds=window_width_seconds)
  for distance_factor in tqdm(np.arange(0, 2.5, 0.05), desc="Testing DLS with different parameters"):
    for speed in np.arange(0.5, 1.2, 0.05):
      distance_factor = round(distance_factor,3)
      speed = round(speed,3)
      dls = DLSEstimator(*START_POS, window_step=WINDOW_STEP,df_transmitters=df_transmitters,bounds=bounds,distance_factor=distance_factor,speed=speed)
      trajectory = precompute_trajectory(
      df=df,
      df_positions=df_positions,
      func =  dls.estimation,
      window_width=window_width,
      window_step=WINDOW_STEP
      # output_file=f"trajectory_{distance_factor}_{speed}_{acceleration}.csv"
      )
      cumulative_error = round(trajectory["blad"].sum(), 2)
      with open("tables/DLS_test_results.csv", "a", newline="") as f:
          writer = csv.writer(f)
          writer.writerow([ "DLS", "-", speed, distance_factor, window_width_seconds, cumulative_error ])
        
def D2LS_grid_search():
  window_width_seconds = 3
  window_width = timedelta(seconds=window_width_seconds)
  speed = 0
  for acceleration in tqdm(np.arange( 1.5,2, 0.05), desc="Testing D2LS with different parameters"):
    for distance_factor in np.arange(0.5, 3, 0.05):
        distance_factor = round(distance_factor,3)
        d2ls = D2LSEstimator(*START_POS, window_step=WINDOW_STEP,df_transmitters=df_transmitters,bounds=bounds,distance_factor=distance_factor,speed=speed, acceleration=acceleration)
        trajectory = precompute_trajectory(
        df=df,
        df_positions=df_positions,
        func =  d2ls.estimation,
        window_width=window_width,
        window_step=WINDOW_STEP
        # output_file=f"trajectory_{distance_factor}_{speed}_{acceleration}.csv"
        )
        cumulative_error = round(trajectory["blad"].sum(), 2)
        with open("tables/D2LS_test_results.csv", "a", newline="") as f:
          writer = csv.writer(f)
          writer.writerow([ "D2LS", acceleration, "-", distance_factor,window_width_seconds, cumulative_error ])
          
def D2LSD_grid_search(): 
  window_width_seconds = 3
  window_width = timedelta(seconds=window_width_seconds)
  acceleration, speed, distance_factor = 1.05, 0.9, 0.71
  for acceleration in tqdm(np.arange(0, 1.5, 0.2), desc="Testing D2LS with different parameters"):
    for distance_factor in np.arange(0, 2.5, 0.2):
      for damping_factor in tqdm(np.arange( -1, 2, 0.2), desc="Testing D2LSD with different parameters"):
        acceleration = round(acceleration, 3)
        distance_factor = round(distance_factor,3)
        d2lsd = D2LSDEstimator(*START_POS, window_step=WINDOW_STEP,df_transmitters=df_transmitters,bounds=bounds,distance_factor=distance_factor,speed=speed, acceleration=acceleration, damping_factor=damping_factor)
        trajectory = precompute_trajectory(
        df=df,
        df_positions=df_positions,
        func =  d2lsd.estimation,
        window_width=window_width,
        window_step=WINDOW_STEP
        # output_file=f"trajectory_{distance_factor}_{speed}_{acceleration}.csv"
        )
        cumulative_error = round(trajectory["blad"].sum(), 2)
        with open("tables/D2LSD_test_results.csv", "a", newline="") as f:
          writer = csv.writer(f)
          writer.writerow([ "D2LSD", acceleration, "-", distance_factor, damping_factor,window_width_seconds,cumulative_error ])
          
        
if __name__ == "__main__":
  LS_grid_search()
  # DLS_grid_search()
  # D2LS_grid_search()
  # D2LSD_grid_search()
