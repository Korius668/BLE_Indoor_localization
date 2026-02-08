from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import re
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.lines import Line2D

from estymator import calculate_distance_from_rssi
from pomiar2.pozycje import df_positions
from mapa_nadajniki import plot_map, df_transmitters

id_mapping = {
    ' 00:00:00:00:00:01': '1',
    ' 00:00:00:00:00:02': '2',
    ' 00:00:00:00:00:03': '3',
    ' 00:00:00:00:00:04': '4',
    ' 00:00:00:00:00:05': '5',
    ' 06:00:00:00:00:00': '6',
    ' 07:00:00:00:00:00': '7',
    ' 08:00:00:00:00:00': '8',
    ' 09:00:00:00:00:00': '9',
    ' 00:00:00:00:00:10': '10', 
    ' 00:00:00:00:00:11': '11',
    ' 00:00:00:00:00:12': '12'
}

folder_path = Path("dane/19.09.2025_06/")
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
    all_dfs = []

    for file in folder.glob("*.txt"):
        if file.name in ["pozycje.txt", "nadajniki.txt"]:
            continue
        position, motion = parse_filename(file.name)

        df = pd.read_csv(
            file,
            names=["time", "mac", "v1", "v2"],
            parse_dates=["time"]
        )

        df["position"] = position
        df["motion"] = motion
        df["source_file"] = file.name  # opcjonalnie

        all_dfs.append(df)

    return pd.concat(all_dfs, ignore_index=True)

def prepare_data(df):
    df["id"] = df["mac"].map(id_mapping).astype(int)
    df.drop(columns=["mac"], inplace=True)
    df["value"] = df["v2"] - df["v1"]
    df.drop(columns=["v1", "v2"], inplace=True)
    tx_coords = df_transmitters.set_index("Id")[["x", "y"]]
    df["x"] = df["id"].map(tx_coords["x"])
    df["y"] = df["id"].map(tx_coords["y"])
    df = df.sort_values("time").reset_index(drop=True)
    
    return df

def compute_transmitter_stats(df_window):
  
    if df_window.empty:
        return df_window, pd.DataFrame(
            columns=['id', 'average_signal_strength', 'sample_count']
        )

    transmitter_stats = (
        df_window
        .groupby('id')
        .agg(
            average_signal_strength=('value', 'mean'),
            sample_count=('value', 'count')
        )
        .reset_index()
    )

    return transmitter_stats


def plot_signal_strength_map(
    transmitter_stats,
    ax,
    fig,
    c_flag=False
):


    for _, tx_row in transmitter_stats.iterrows():
        tx_id = tx_row['id']
        avg_signal = tx_row['average_signal_strength']
        sample_count = tx_row['sample_count']

        row = df_transmitters[df_transmitters['Id'] == tx_id]
        if row.empty:
            continue

        tx = row.iloc[0]
        size = max(sample_count * 2, 100)

        ax.scatter(
            tx['x'], tx['y'],
            c=avg_signal,
            s=size,
            cmap='Greens',
            edgecolors='black',
            linewidth=0.5,
            vmin=-100,
            vmax=-40
        )

        estimated_distance = calculate_distance_from_rssi(avg_signal)
    
        circle = plt.Circle((tx['x'], tx['y']), estimated_distance, color='blue', fill=False, linestyle='--', alpha=0.7)
        ax.add_patch(circle)
        ax.text(tx['x'], tx['y'] + estimated_distance, f'{estimated_distance:.2f}m', color='blue', fontsize=8, ha='center', va='bottom')


        plt.Circle((0, 0), 0, color='blue', fill=False, linestyle='--', alpha=0.7, label='Estimated Distance from RSSI')

    
    if len(ax.collections) > 1 and c_flag:
        cbar = fig.colorbar(ax.collections[1], ax=ax)
        cbar.set_label('Srednia moc sygnału (dBm)')

    representative_size = transmitter_stats['sample_count'].median() * 0.5 if not transmitter_stats.empty else 50
    label = 'Nadajniki (rozmiar ~ liczba probek)'
    proxy_transmitter = ax.scatter([], [], color='green', s=representative_size, label=label)

    handles, labels = ax.get_legend_handles_labels()

    if label not in labels:
        handles.append(proxy_transmitter)
        labels.append(label)

    ax.legend(handles, labels, loc='upper right')

    return ax


def plot_mesurement_position(
    ax=None,
    df_positions=df_positions,
    active_position=None,
    part_position=None
):
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))

    first_position_label_added = False
    first_arrow_label_added = False

    for i in range(len(df_positions)):
        x_curr = df_positions.loc[i, "x"]
        y_curr = df_positions.loc[i, "y"]
        pos_number = i + 1
        is_active = (active_position == pos_number)
        p_x, p_y = x_curr, y_curr
        color = "red" if is_active else "grey"
        if pd.isna(x_curr) or pd.isna(y_curr):

            if (
                i > 0 and i < len(df_positions) - 1
            ):  # Ensure i-1 and i+1 exist within dataframe bounds
                x_prev = df_positions.loc[i - 1, "x"]
                y_prev = df_positions.loc[i - 1, "y"]
                x_next = df_positions.loc[i + 1, "x"]
                y_next = df_positions.loc[i + 1, "y"]

                if not (
                    pd.isna(x_prev)
                    or pd.isna(y_prev)
                    or pd.isna(x_next)
                    or pd.isna(y_next)
                ):
                    # Draw an arrow between the previous and next valid points
                    label_str = (
                        "Ścieżka dla brakujących punktów"
                        if not first_arrow_label_added
                        else None
                    )
                    ax.annotate(
                        "",
                        xy=(x_next, y_next),
                        xytext=(x_prev, y_prev),
                        arrowprops=dict(facecolor=color, edgecolor=color, shrink=0.05, width=2, headwidth=8, headlength=10)
                    )
                    
                    first_arrow_label_added = True
                    # Add the point number (i+1) near the arrow's midpoint
                    ax.text(
                        (x_prev + x_next) / 2,
                        (y_prev + y_next) / 2,
                        str(i + 1),
                        color="black",
                        fontsize=8,
                        ha="center",
                        va="center",
                    )
                    if is_active and part_position is not None:
                        p_x, p_y = x_prev+ (x_next - x_prev) * part_position, y_prev + (y_next - y_prev) * part_position
                        ax.scatter(p_x, p_y, color='red', s=100, label='Szacowana pozycja' if not first_position_label_added else None, zorder=5)

                    
        else:
            # Current point is valid, plot as usual
            
            size = 140 if is_active else 90

            label_str = (
                "Aktualna pozycja" if is_active and not first_position_label_added
                else "Pozycje" if (not is_active and not first_position_label_added)
                else None
            )

            ax.scatter(
                x_curr,
                y_curr,
                color=color,
                s=size,
                label=label_str,
                zorder=5 if is_active else 3
            )

            first_position_label_added = True
            ax.text(
                x_curr,
                y_curr,
                str(i + 1),
                color="black",
                fontsize=8,
                ha="center",
                va="center",
            )

    ax.set_title("Mapa z zaznaczonymi pozycjami i nadajnikami")
    ax.set_xlabel("Oś X (m)")
    ax.set_ylabel("Oś Y (m)")
    ax.set_ylim(-2, 32)

    

    arrow_proxy = Line2D(
        [0], [0],
        color="grey",
        linewidth=2,
        linestyle="-",
        label="Ścieżka dla brakujących punktów"
    )

    handles, labels = ax.get_legend_handles_labels()

    if "Ścieżka dla brakujących punktów" not in labels:
        handles.append(arrow_proxy)
        labels.append("Ścieżka dla brakujących punktów")

    ax.legend(handles, labels, loc="upper right")


    ax.set_aspect("equal", adjustable="box")

    return ax, p_x, p_y

def save_probki_w_czasie_plot(df, window_width, window_step, save_path='wykresy/probki_w_czasie.png'):
    fig, ax = plt.subplots()

    counts = df.groupby([pd.Grouper(key='time', freq=window_step), 'position']).size().unstack(fill_value=0)

    full_range = pd.date_range(start=df['time'].min().floor(window_width/2), 
                           end=df['time'].max().floor(window_width/2), 
                           freq=window_step)
    
    counts = counts.reindex(full_range, fill_value=0)

    ax = counts.plot(kind='bar', stacked=True, figsize=(12, 6))

    plt.title(f'Ilość próbek na okno czasowe ({window_width.total_seconds()} sekund) z podziałem na pozycje')
    plt.xlabel('Okno czasowe')
    plt.ylabel('Liczba próbek')
    ax.set_xticklabels([])
    plt.legend(title='Pozycja', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    plt.savefig(save_path)


def plot_interactive_map(df, window_width=WINDOW_WIDTH, window_step=WINDOW_STEP):
    fig, ax = plt.subplots(figsize=(6, 10))
    
    
    def redraw_base_map():
        ax.clear()
        plot_map(ax=ax)   
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

    def update(val):
        center_time = t0 + timedelta(seconds=slider.val)
        df_window = df[
            (df["time"] >= center_time - window_width/2) &
            (df["time"] <= center_time + window_width/2)
        ]

        active_position = (
            df_window["position"].mode().iloc[0] if not df_window.empty else None
        )
        transmitter_stats = compute_transmitter_stats(df_window)
        
        redraw_base_map()
        plot_mesurement_position(ax=ax, active_position=active_position)
        if active_position is not None:
            plot_signal_strength_map(
                transmitter_stats=transmitter_stats,
                ax=ax,
                fig=fig,
                c_flag=False
            )
        fig.canvas.draw_idle()
        
    ax = plot_map(ax=ax)
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    
    ax_slider = plt.axes([0.15, 0.05, 0.7, 0.03])
    t0 = df["time"].min()
    times_sec = (df["time"] - t0).dt.total_seconds()

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


df = load_measurements(folder_path)
df = prepare_data(df)

if __name__ == "__main__":
    plot_interactive_map(df, window_width=WINDOW_WIDTH, window_step=WINDOW_STEP)
    save_probki_w_czasie_plot(df, WINDOW_WIDTH, WINDOW_STEP, save_path='wykresy2/probki_w_czasie.png')