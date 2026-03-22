import re
import os
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.widgets import Slider

from ble_indoor_localization import (
    calculate_distance_from_rssi, 
    plot_distance_from_signal, 
    plot_active_measurement_position, 
    save_probki_w_czasie_plot
    )
from ble_indoor_localization.plotting import plot_distance_from_signal
from .pozycje import df_positions, pomiar2_data_path
from pomiar import df_transmitters, plot_map, id_mapping
from pomiar1 import model


WINDOW_STEP = timedelta(seconds=0.5)
WINDOW_WIDTH = timedelta(seconds=2)

def read_timestamps(file_path):
    timestamps = []
    with open(file_path) as f:
        for line in f:
            ts_str = line.split(",")[0].strip()
            timestamps.append(datetime.fromisoformat(ts_str))
    return timestamps

def time_range(start, end, step):
    current = start
    while current <= end:
        yield current
        current += step
        
def parse_filename(filename: str):
    """
    Przykłady:
    1_10.txt       -> position=1,  motion="stoi"
    2_manual.txt  -> position=2,  motion="ruch"
    """
    match = re.match(r"(\d+)_([a-zA-Z0-9]+)\.txt", filename)
    if not match:
        raise ValueError(f"Nieznany format nazwy pliku: {filename}")

    position = int(match.group(1))
    mode = match.group(2)

    motion = "ruch" if mode == "manual" else "stoi"

    return position, motion

def load_measurements(folder: Path):

    if not folder.exists():
        raise FileNotFoundError(f"Folder does not exist: {folder}")
    
    df = pd.DataFrame()

    for file in folder.glob("*.txt"):
        if file.name in ["pozycje.txt", "nadajniki.txt"]:
            continue
        position, motion = parse_filename(filename=file.name)

        df_temp = pd.read_csv(
            file,
            names=['data', 'id nadajnika', 'wzmocnienie', 'moc sygnalu'],
            parse_dates=["data"]
        )
        df_temp["data"] = pd.to_datetime(df_temp['data'])
        df_temp["position"] = position
        df_temp["motion"] = motion
        df_temp["source_file"] = file.name
        df_temp["id nadajnika"] = df_temp["id nadajnika"].map(id_mapping).astype(int)

        df_temp['znormalizowana moc sygnalu'] = df_temp['moc sygnalu'] - df_temp['wzmocnienie']

        tx_coords = df_transmitters.set_index("Id")[["x", "y"]]
        df_temp["x"] = df_temp["id nadajnika"].map(tx_coords["x"])
        df_temp["y"] = df_temp["id nadajnika"].map(tx_coords["y"])
        df_temp = df_temp.sort_values("data").reset_index(drop=True)
        df = pd.concat([df, df_temp], ignore_index=True)
    return df

def compute_transmitter_stats(df_window, df_transmitters):
  
    if df_window.empty:
        return df_window, pd.DataFrame(
            columns=["id nadajnika", 'average_signal_strength', 'sample_count']
        )

    transmitter_stats = (
        df_window
        .groupby("id nadajnika")
        .agg(
            average_signal_strength=('znormalizowana moc sygnalu', 'mean'),
            sample_count=('znormalizowana moc sygnalu', 'count')
        )
        .reset_index()
    )

    return transmitter_stats


def plot_interactive_map(df, window_width=WINDOW_WIDTH, window_step=WINDOW_STEP):
    fig, ax = plt.subplots(figsize=(6, 10))
    ax = plot_map(ax=ax)
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    func = lambda rssi: calculate_distance_from_rssi(rssi, model)
    c_flag = True
    def redraw_base_map():
        ax.clear()
        plot_map(ax=ax)   
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

    def update(val):
        nonlocal c_flag
        center_time = t0 + timedelta(seconds=slider.val)
        df_window = df[
            (df["data"] >= center_time - window_width/2) &
            (df["data"] <= center_time + window_width/2)
        ]

        active_position = (
            df_window["position"].mode().iloc[0] if not df_window.empty else None
        )

        redraw_base_map()
        plot_active_measurement_position(ax=ax, df_positions=df_positions, active_position=active_position)
        if active_position is not None:
            plot_distance_from_signal(f"Position {active_position}",
                df_measurement=df_window,
                df_transmitters=df_transmitters,
                calculate_distance_func=func,
                ax=ax,
                fig=fig,
                c_flag=c_flag
            )
        c_flag = False
        fig.canvas.draw_idle()
        
   
    
    ax_slider = plt.axes([0.15, 0.05, 0.7, 0.03])
    t0 = df["data"].min()
    times_sec = (df["data"] - t0).dt.total_seconds()

    slider = Slider(
        ax_slider,
        "czas [s]",
        times_sec.min(),
        times_sec.max(),
        valinit=0,
        valstep=window_step.total_seconds()
    )

    slider.on_changed(update)

    redraw_base_map()
    update(0)
   
    plt.show() 

folder_path = Path(pomiar2_data_path)
df = load_measurements(folder_path)


if __name__ == "__main__":
    plot_interactive_map(df, window_width=WINDOW_WIDTH, window_step=WINDOW_STEP)
    save_probki_w_czasie_plot(df, WINDOW_WIDTH, WINDOW_STEP, save_path='diagrams/wykresy2/probki_w_czasie.png')
