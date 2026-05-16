import csv
import os
from datetime import timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.widgets import Slider
import matplotlib.patches as mpatches
from tqdm import tqdm

from ble_indoor_localization.estymatory.least_square import (calculate_distance_from_rssi)
from .dystans_w_czasie import (WINDOW_STEP, WINDOW_WIDTH,
                                    df,
                                      )
WINDOW_WIDTH = timedelta(seconds=15)


def plot_window_shape(df):
    fig, ax = plt.subplots(figsize=(15, 10))
    distance = calculate_distance_from_rssi(df['znormalizowana moc sygnalu'])
    
    unique_ids = sorted(df['id nadajnika'].unique())
    
    # Map each ID to a color
    color_map = {uid: f'C{i % 10}' for i, uid in enumerate(unique_ids)}  # Cycle through default colors
    
    # Apply colors to the dataframe
    colors = df['id nadajnika'].map(color_map)
    time = (df['data'] - df['data'].min()).dt.total_seconds()
    time_position = 20

    # Plot bars with colors (time on x, signal on y)
    ax.bar(time, distance, color=colors, width=0.1, alpha=0.5)
    ax.axvline(x=time_position, color='red', linestyle='--', linewidth=2)

    handles = [mpatches.Patch(color=color_map[uid], label=f'ID {uid}') for uid in unique_ids]

    window_start = max(0.0, time_position - WINDOW_WIDTH.total_seconds())

    triangle = mpatches.Polygon(
        [[window_start, 0.0], [time_position, 1.0], [time_position, 0.0]],
        closed=True,
        color='orange',
        alpha=0.25,
        zorder=5,
        transform=ax.get_xaxis_transform()
    )
    ax.add_patch(triangle)

    ax.set_xlabel("Czas w sekundach")
    ax.set_ylabel("Odległość (obliczona z RSSI)")

    handles.append(mpatches.Patch(color='orange', alpha=0.25, label='weight window'))
    ax.legend(handles=handles, title='ID nadajnika')
    ax.set_xlim(0, 22)
    ax.set_title(f"Kształt okna czasowego o szerokości {WINDOW_WIDTH.total_seconds()} sekund")
    ax.grid()

    ax2 = ax.twinx()
    triangle_x = [window_start, time_position, time_position]
    triangle_y = [0.0, 1.0, 0.0]
    ax2.fill_between(triangle_x, triangle_y, color='orange', alpha=0.25)
    ax2.set_ylabel("Waga %")
    ax2.set_ylim(0, 100)
    plt.show()

if __name__ == "__main__":
    plot_window_shape(df)