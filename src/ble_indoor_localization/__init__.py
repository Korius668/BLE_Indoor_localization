"""
BLE Indoor Localization Package

This package provides utilities for indoor localization using BLE beacons.
"""
from datetime import timedelta

from .calculations import (calculate_distance_from_rssi,
                           create_rssi_distance_model,
                           distance_between_2_points, generate_samples,
                           objective_function,
                           objective_function_normalized,
                           prepare_distance_data, value_of_objective_function)
from .estymatory import (D2LSEstimator,DLSEstimator, EKFLocalizer, Estimator, MLEstimator, D2LSDEstimator,
least_square_estimation, foggy_wrapper)
from .plotting import (plot_area_of_objective_function, plot_average_positions,
                       plot_boxplots, plot_distance_from_signal,
                       plot_estimated_positions, plot_measurement_positions,
                       plot_signal_strength_map,
                       save_probki_w_czasie_plot, plot_active_measurement_position)

# Constants
WINDOW_STEP = timedelta(seconds=0.5)
WINDOW_WIDTH = timedelta(seconds=2)

__all__ = [
    # Constants
    'id_mapping',
    'transmitter_order',
    'WINDOW_STEP',
    'WINDOW_WIDTH',
    
    # Data loading
    'load_positions',
    'read_pomiar_data',
    'calc_boxplot_data',
    'calculate_euclidean_distance',
    
    # Calculations
    'distance_between_2_points',
    'create_rssi_distance_model',
    'calculate_distance_from_rssi',
    'objective_function',
    'objective_function_normalized',
    'prepare_distance_data',
    'least_square_estimation',
    'value_of_objective_function',
    'generate_samples',
    
    # Plotting
    'plot_measurement_positions',
    'plot_signal_strength_map',
    'plot_distance_from_signal',
    'plot_area_of_objective_function',
    'plot_average_positions',
    'plot_estimated_positions',
    'plot_boxplots',
    "save_probki_w_czasie_plot",
    "plot_active_measurement_position",

    # Estimators
    "D2LSEstimator", 
    "DLSEstimator", 
    "EKFLocalizer", 
    "Estimator", 
    "MLEstimator", 
    "D2LSDEstimator"
]

