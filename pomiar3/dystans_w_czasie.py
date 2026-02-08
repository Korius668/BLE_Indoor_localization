from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import re
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.lines import Line2D

from pomiar3.pozycje import df_positions
from mapa_nadajniki import plot_map, df_transmitters
from pomiar2.dystans_w_czasie import (
    compute_transmitter_stats,  plot_signal_strength_map, 
    load_measurements, prepare_data, plot_mesurement_position,
    plot_interactive_map, save_probki_w_czasie_plot
    )

folder_path = Path("dane/19.09.2025_07/")
WINDOW_STEP = timedelta(seconds=0.5)
WINDOW_WIDTH = timedelta(seconds=2)
df = load_measurements(folder_path)
df = prepare_data(df)


if __name__ == "__main__":
    plot_interactive_map(df, window_width=WINDOW_WIDTH, window_step=WINDOW_STEP)
    save_probki_w_czasie_plot(df, WINDOW_WIDTH, WINDOW_STEP,'wykresy3/probki_w_czasie.png')