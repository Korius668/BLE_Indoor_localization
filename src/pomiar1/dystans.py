from typing import Any, Callable


import matplotlib.pyplot as plt

from ble_indoor_localization import (
    calculate_distance_from_rssi, 
    plot_distance_from_signal
)
from pomiar import df_transmitters, plot_map

from .boxplot import dfs
from .regresja_liniowa import model


if __name__ == "__main__":
    for measurement_name, df_measurement in dfs.items():
        fig, ax = plt.subplots(figsize=(8, 8))
        ax= plot_map()
        func: Callable[..., Any] = lambda rssi: calculate_distance_from_rssi(rssi, model)
        plot_distance_from_signal(measurement_name, df_measurement, df_transmitters, calculate_distance_func=func,  ax=ax)
        ax.set_ylim(-10, 42)
        ax.set_xlim(-20, 20)
        ax.set_xlabel('Oś X (m)')
        ax.set_ylabel('Oś Y (m)')
    plt.show()