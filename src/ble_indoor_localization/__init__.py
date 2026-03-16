"""
BLE Indoor Localization Package

This package provides utilities for indoor localization using BLE beacons.
"""
from datetime import timedelta


from .calculations import (
    distance_between_2_points,
    create_rssi_distance_model,
    calculate_distance_from_rssi,
    objective_function,
    objective_function_normalized,
    prepare_distance_data,
    least_square_estimation,
    value_of_objective_function,
    generate_samples
)

from .plotting import (
    plot_mesurement_position,
    plot_signal_strength_map,
    plot_distance_from_signal,
    plot_area_of_objective_function,
    plot_average_positions,
    plot_estimated_positions,
    plot_boxplots
)

from .estymatory import Estimator

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
    'plot_mesurement_position',
    'plot_signal_strength_map',
    'plot_distance_from_signal',
    'plot_area_of_objective_function',
    'plot_average_positions',
    'plot_estimated_positions',
    'plot_boxplots',
]

