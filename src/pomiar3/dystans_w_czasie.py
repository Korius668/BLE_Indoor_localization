import re
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.widgets import Slider

from pomiar2.dystans_w_czasie import (compute_transmitter_stats,
                                      load_measurements, plot_interactive_map,
                                      plot_measurement_position,
                                      plot_signal_strength_map, prepare_data,
                                      save_probki_w_czasie_plot)
from pomiar3.pozycje import df_positions
from src.mapa_nadajniki import df_transmitters, plot_map

folder_path = Path("dane/19.09.2025_07/")
WINDOW_STEP = timedelta(seconds=0.5)
WINDOW_WIDTH = timedelta(seconds=2)
df = load_measurements(folder_path)
df = prepare_data(df)


if __name__ == "__main__":
    plot_interactive_map(df, window_width=WINDOW_WIDTH, window_step=WINDOW_STEP)
    save_probki_w_czasie_plot(df, WINDOW_WIDTH, WINDOW_STEP,'wykresy3/probki_w_czasie.png')