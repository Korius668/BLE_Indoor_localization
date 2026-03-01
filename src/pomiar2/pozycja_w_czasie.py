import csv
from datetime import timedelta
from typing import Any
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np
import pandas as pd
import os

from estymator import EKFLocalizer, ParticleFilter, least_square_estimation, universal_position_estimator, delta_least_square_estimation, DLSLocalizer
from mapa_nadajniki import plot_map
from pomiar2.dystans_w_czasie import compute_transmitter_stats, df, WINDOW_STEP, WINDOW_WIDTH, plot_signal_strength_map, plot_mesurement_position
from pomiar2.pozycje import df_positions

START_POS = (float(df_positions["x"].iloc[0]), float(df_positions["y"].iloc[0]))

def plot_position(avg_pos_x, avg_pos_y , ax):  
    ax.scatter(
        avg_pos_x, avg_pos_y,
        color='orange',
        alpha=0.9,
        s=120,
        marker='v',
        label=f'Pozycja wyliczona: {avg_pos_x:.2f}, {avg_pos_y:.2f}'
    )
    return ax


def get_full_trajectory(df, window_width, window_step,func=least_square_estimation, start_pos=START_POS):
    start_time = df["time"].min()
    end_time = df["time"].max()
    time_steps = pd.date_range(start=start_time, end=end_time, freq=window_step)
    
    trajectory = []
    xt, yt = start_pos
    for center in time_steps:
        df_window = df[
            (df["time"] >= center - window_width/2) &
            (df["time"] <= center + window_width/2)
        ]
        active_position = df_window["position"].mode().iloc[0] if not df_window.empty else None
        if not df_window.empty:
            xt, yt = func(df_window,(xt,yt)) if func == delta_least_square_estimation else func(df_window)
            trajectory.append({'x': xt, 'y': yt, 'time': center, 'position': active_position})
            
    return pd.DataFrame(trajectory)


def save_trajectory_plot(
    df: pd.DataFrame,
    window_width: timedelta,
    window_step: timedelta = WINDOW_STEP,
    func = least_square_estimation,
    folder_path: str = "wykresy/",
    colormap: str = 'plasma',
    label_step_divisor: int = 20,
    filename = None
) -> None:
   
    try:
        os.makedirs(folder_path, exist_ok=True)
    except OSError as e:
        raise OSError(f"Failed to create directory '{folder_path}': {e}")
    
    df_traj = get_full_trajectory(df, window_width, window_step=window_step, func=func)
    
    if df_traj.empty:
        print(f"Warning: No trajectory data generated for window {window_width}")
        return
    
    required_columns = {'x', 'y', 'position'}
    if not required_columns.issubset(df_traj.columns):
        raise ValueError(f"Trajectory data missing required columns: {required_columns - set(df_traj.columns)}")
    
    fig, ax = plt.subplots(figsize=(8, 10))
    ax = plot_map(ax=ax)
    
    unique_positions = sorted(df_traj["position"].unique())
    n_positions = len(unique_positions)
    
    if n_positions == 0:
        print(f"Warning: No valid positions in trajectory for window {window_width}")
        plt.close(fig)
        return
    
    position_to_index = {pos: idx + 1 for idx, pos in enumerate(unique_positions)}
    position_indices = df_traj["position"].map(position_to_index).values
    
    cmap = plt.get_cmap(colormap, n_positions)
    
    ax.plot(
        df_traj['x'], df_traj['y'],
        color='gray', alpha=0.3, linewidth=1,
        label='Trajectory path'
    )
    
    scatter = ax.scatter(
        df_traj['x'], df_traj['y'],
        c=position_indices, cmap=cmap,
        s=40, edgecolor='black', linewidth=0.3,
        vmin=0.5, vmax=n_positions + 0.5,
        zorder=3, label='Position estimates'
    )
    
    n_points = len(df_traj)
    label_step = max(1, n_points // label_step_divisor)
    
    for i in range(0, n_points, label_step):
        row = df_traj.iloc[i]
        ax.text(
            row['x'] + 0.1, row['y'] + 0.1,
            str(i),
            fontsize=7, alpha=0.7
        )
    colorbar = plt.colorbar(scatter, ax=ax, label='Pozycja')
    colorbar.set_ticks(range(1, n_positions + 1))
    colorbar.set_ticklabels([str(idx) for idx in range(1, n_positions + 1)])

    window_str = str(window_width.seconds)
    ax.set_title(f"Trajektoeria - Okno szerokość: {window_width.seconds} sekund", fontsize=12, pad=10)
    if filename == None:
        filename =  f"trajektoria_window_{window_str}.png"
    filename = os.path.join(folder_path,filename)
    try:
        plt.savefig(filename, bbox_inches='tight', dpi=150)
        print(f"Successfully saved: {filename}")
    except Exception as e:
        print(f"Error saving plot to '{filename}': {e}")
        raise
    finally:
        plt.close(fig)




def generate_frame(df, df_positions, center_time, window_width, func=least_square_estimation, last_position=START_POS):
    df_window = df[
        (df["time"] >= center_time - window_width/2) &
        (df["time"] <= center_time + window_width/2)
    ]
    
    x_t, y_t = last_position
    if df_window.empty:
        active_position = None
        part_position = None
        transmitter_stats = None
        x_t = y_t = None
    else:
        active_position = df_window["position"].mode().iloc[0]
        begin_t_pos = df[df["position"] == active_position]["time"].min()
        end_t_pos = df[df["position"] == active_position]["time"].max()
        part_position = (center_time - begin_t_pos).value / (end_t_pos - begin_t_pos).value
        transmitter_stats = compute_transmitter_stats(df_window)
        x_t, y_t = func(df_window,(x_t,y_t)) if func == delta_least_square_estimation else func(df_window)

    fig, ax = plt.subplots(figsize=(6, 10))
    ax = plot_map(ax=ax)
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    _,p_x, p_y = plot_mesurement_position(ax=ax, df_positions=df_positions,
                             active_position=active_position,
                             part_position=part_position)

    if active_position is not None:
        plot_signal_strength_map(
            transmitter_stats=transmitter_stats,
            ax=ax,
            fig=fig,
            c_flag=False
        )
        plot_position(x_t, y_t, ax=ax)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    fig.canvas.draw()

    buf = fig.canvas.buffer_rgba() 
  
    image = np.asarray(buf, dtype=np.uint8)[..., :3]

    plt.close(fig)
    return image, x_t, y_t, active_position, p_x, p_y


def precompute_frames(df, df_positions,  window_width, window_step, func=least_square_estimation, output_dir="frames", start_pos=START_POS):
    os.makedirs(output_dir, exist_ok=True)

    with open(output_dir+"/pozycje.csv", "w", newline="") as f: 
        writer = csv.writer(f) 
        writer.writerow([ "l.p.", "czas", "pozycja", "x_estymowane", "y_estymowane", "x_prawdziwe", "y_prawdziwe" ])
    
    
    t0 = df["time"].min()
    times_sec = (df["time"] - t0).dt.total_seconds()
    slider_values = np.arange(times_sec.min(), times_sec.max()+1, window_step.total_seconds())

    frames = []
    x_t, y_t = start_pos
    for i, t in enumerate(slider_values):
        print(f"Przetwarzanie klatki {i+1}/{len(slider_values)} - czas: {t:.2f} s")
        center_time = t0 + timedelta(seconds=t)
        frame, x_t, y_t, active_position, p_x, p_y = generate_frame(df, df_positions, center_time, window_width, func=func, last_position=(x_t, y_t))

        frames.append(frame)
        plt.imsave(f"{output_dir}/frame_{i:04d}.png", frame)
        with open(output_dir+"/pozycje.csv", "a", newline="") as f: 
            writer = csv.writer(f) 
            writer.writerow([ i, center_time.isoformat(), active_position, x_t, y_t, p_x, p_y ])

    return frames, slider_values


def plot_interactive_precomputed(frames, slider_values):
    fig, ax = plt.subplots(figsize=(6, 10))
    img = ax.imshow(frames[0])
    ax.axis("off")
   
    ax_slider = plt.axes([0.15, 0.05, 0.7, 0.03])
    slider = Slider(ax_slider, "czas [s]", 0, len(frames)-1, valinit=0, valstep=1)

    def update(val):
        idx = int(slider.val)
        img.set_data(frames[idx])
        fig.canvas.draw_idle()

    slider.on_changed(update)
    plt.show()


if __name__ == "__main__":

    # frames, slider_values = precompute_frames(
    # df=df,
    # df_positions=df_positions,
    # func = least_square_estimation,
    # window_width=WINDOW_WIDTH,
    # window_step=WINDOW_STEP,
    # output_dir="output_LS2"
    # )

    # dls = DLSLocalizer(df_positions["x"].iloc[0], df_positions["y"].iloc[0])
    # frames, slider_values = precompute_frames(
    # df=df,
    # df_positions=df_positions,
    # func = lambda df, last_position=START_POS: universal_position_estimator(df, method="DLS", window_step=WINDOW_STEP, last_position=last_position),
    # window_width=WINDOW_WIDTH,
    # window_step=WINDOW_STEP,
    # output_dir="output_DLS2"
    # )

    # ekf = EKFLocalizer(initial_position=START_POS)
    
    # frames, slider_values = precompute_frames(
    # df=df,
    # df_positions=df_positions,
    # func = lambda df: universal_position_estimator(df, method="EKF", state_obj=ekf, window_step=WINDOW_STEP),
    # window_width=WINDOW_WIDTH,
    # window_step=WINDOW_STEP,
    # output_dir="output_EKF2"
    # )
    
    # pf = ParticleFilter()
    
    # frames, slider_values = precompute_frames(
    # df=df,
    # df_positions=df_positions,
    # func = lambda df: universal_position_estimator(df, method="PF", state_obj=pf),
    # window_width=WINDOW_WIDTH,
    # window_step=WINDOW_STEP,
    # output_dir="output_PF2"
    # )
    
    # frames, slider_values = precompute_frames(
    # df=df,
    # df_positions=df_positions,
    # func = lambda df: universal_position_estimator(df, method="MLE"),
    # window_width=WINDOW_WIDTH,
    # window_step=WINDOW_STEP,
    # output_dir="output_MLE2"
    # )
    
    
    # plot_interactive_precomputed(frames, slider_values)

    test_windows = [
        # timedelta(seconds=1),
        # timedelta(seconds=2),
        # timedelta(seconds=5), 
        # timedelta(seconds=15), 
        timedelta(seconds=30)
    ]
    sigma = [
        1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05, 0.01
    ]

    for window_width in test_windows:
        # save_trajectory_plot(df, window_width, folder_path="wykresy2_LS/", func=least_square_estimation)
        save_trajectory_plot(df, window_width, folder_path="wykresy2_DLS/", 
                            func = lambda df, last_position=START_POS: universal_position_estimator(df, method="DLS", window_step=WINDOW_STEP, last_position=last_position)
                            )

        # ekf = EKFLocalizer(initial_position=START_POS)
        # save_trajectory_plot(df, window_width, folder_path="wykresy2_EKF/", func = lambda df: universal_position_estimator(df, method="EKF", state_obj=ekf))
        # pf = ParticleFilter()
        # save_trajectory_plot(df, window_width, folder_path="wykresy2_PF/", func = lambda df: universal_position_estimator(df, method="PF", state_obj=pf))
        # save_trajectory_plot(df, window_width, folder_path="wykresy2_MLE/", func = lambda df: universal_position_estimator(df, method="MLE"))
