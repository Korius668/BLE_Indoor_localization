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
WINDOW_WIDTH = timedelta(seconds=3)


def plot_window_shape(df):
    fig, ax = plt.subplots(figsize=(7, 5))
    distance = calculate_distance_from_rssi(df['znormalizowana moc sygnalu'])
    
    unique_ids = sorted(df['id nadajnika'].unique())
    
    time_position = 17
    window_start = max(0.0, time_position - WINDOW_WIDTH.total_seconds())
    triangle = mpatches.Polygon(
        [[window_start, 0.0], [time_position, 0.66], [time_position, 0.0]],
        closed=True,
        color='orange',
        alpha=0.25,
        zorder=5,
        transform=ax.get_xaxis_transform()
    )
    ax.add_patch(triangle)
    cmap = plt.cm.get_cmap("gnuplot2", len(unique_ids))

    color_map = {uid: cmap(i) for i, uid in enumerate(unique_ids)}
    # Apply colors to the dataframe
    colors = df['id nadajnika'].map(color_map)
    time = (df['data'] - df['data'].min()).dt.total_seconds()
  

    # Plot bars with colors (time on x, signal on y)
    ax.bar(time, distance, color=colors, width=0.1, alpha=1)
    ax.axvline(x=time_position, color='red', linestyle='--', linewidth=2, label='Aktualny czas')

    handles = [mpatches.Patch(color=color_map[uid], label=f'{uid}') for uid in unique_ids]   
    handles.append(plt.Line2D([0], [0], color='red', linestyle='--', lw=2,  label='Aktualny czas'))

    ax.set_xlabel("Czas w sekundach")
    ax.set_ylabel("Odległość (obliczona z RSSI)")

    handles.append(mpatches.Patch(color='orange', alpha=0.25, label='Waga'))
    ax.legend(handles=handles, title='ID nadajnika')
    ax.set_xlim(12, 20)
    ax.set_ylim(0, 50)
    ax.set_title(f"Kształt okna czasowego o szerokości {WINDOW_WIDTH.total_seconds()} sekund")
    ax.grid()

    ax2 = ax.twinx()
    ax2.set_ylabel("Waga %")
    ax2.set_ylim(0, 150)
    ax2.set_yticks([0, 20, 40, 60, 80, 100])

    plt.show()

if __name__ == "__main__":
    plot_window_shape(df)