import csv
import os
from datetime import timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.widgets import Slider
from tqdm import tqdm

from ble_indoor_localization import (DLSEstimator, 
                                     D2LSEstimator,
                                     D2LSDEstimator,
                                     EKFLocalizer,
                                     Estimator, 
                                     MLEstimator,
                                     foggy_wrapper,
                                     least_square_estimation,
                                     plot_average_positions,
                                     plot_active_measurement_position                                     
                                     )
from ble_indoor_localization.plotting import plot_signal_strength_map
from .dystans_w_czasie import (WINDOW_STEP, WINDOW_WIDTH,
                                    df,
                                      )
from .pozycje import df_positions
from pomiar import bounds, df_transmitters, plot_map

START_POS = (float(df_positions["x"].iloc[0]), float(df_positions["y"].iloc[0]))


def get_full_trajectory(df, window_width, window_step, func, start_pos=START_POS):
    start_time = df["data"].min()
    end_time = df["data"].max()
    time_steps = pd.date_range(start=start_time, end=end_time, freq=window_step)
    
    trajectory = []
    x_t, y_t = start_pos
    for center in tqdm(time_steps, desc="Processing time steps", unit="step"):
        df_window = df[
            (df["data"] >= center - window_width) &
            (df["data"] <= center)
        ]
        active_position = df_window["position"].mode().iloc[0] if not df_window.empty else None
        if not df_window.empty:
            x_t, y_t = func(df_window)
            trajectory.append({'x': x_t, 'y': y_t, 'time': center, 'position': active_position})
            
    return pd.DataFrame(trajectory)


def save_trajectory_plot(
    df: pd.DataFrame,
    window_width: timedelta,
    window_step: timedelta = WINDOW_STEP,
    func = least_square_estimation,
    folder_path: str = "diagrams/",
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
    position_indices = df_traj["position"].map(lambda pos: position_to_index[pos]).values
    
    cmap = plt.get_cmap(colormap, n_positions)
    
    ax.plot(
        df_traj['x'], df_traj['y'],
        color='gray', alpha=0.3, linewidth=1,
        label='Trajectory path'
    )
    
    scatter = ax.scatter(
        df_traj['x'], df_traj['y'],
        c=position_indices.tolist(), cmap=cmap,
        s=40, edgecolor='black', linewidth=0.3,
        vmin=0.5, vmax=n_positions + 0.5,
        zorder=3, label='Position estimates'
    )
    
    n_points = len(df_traj)
    label_step = max(1, n_points // label_step_divisor)
    
    for i in tqdm(range(0, n_points, label_step), desc="Adding labels", unit="label"):
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


def generate_frame(df, df_positions, center_time, window_width, func, last_position=START_POS):
    x_t, y_t, active_position, p_x, p_y, df_window = compute_position_values(df, df_positions, center_time, window_width, func, last_position)

    fig, ax = plt.subplots(figsize=(6, 10))
    ax = plot_map(ax=ax)
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    # Plot the active position (but we already have p_x, p_y)
    plot_active_measurement_position(df_positions=df_positions, ax=ax,
                             active_position=active_position,
                             part_position=None)  # part_position not needed since we computed p_x, p_y

    if active_position is not None:
        plot_signal_strength_map(
            df_window,
            df_transmitters,
            ax=ax,
            fig=fig,
            c_flag=False
        )
        plot_average_positions(x_t, y_t, ax=ax)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    fig.canvas.draw()

    buf = fig.canvas.buffer_rgba()  # type: ignore[attr-defined]
   
    image = np.asarray(buf, dtype=np.uint8)[..., :3]

    plt.close(fig)
    return image, x_t, y_t, active_position, p_x, p_y


def compute_position_values(df, df_positions, center_time, window_width, func, last_position=START_POS):
    df_window = df[
        (df["data"] >= center_time - window_width/2) &
        (df["data"] <= center_time + window_width/2)
    ]
    
    x_t, y_t = last_position
    if df_window.empty:
        active_position = None
        part_position = None
        x_t = y_t = None
        p_x = p_y = None
    else:
        active_position = df_window["position"].mode().iloc[0]
        begin_t_pos = df[df["position"] == active_position]["data"].min()
        end_t_pos = df[df["position"] == active_position]["data"].max()
        part_position = (center_time - begin_t_pos).value / (end_t_pos - begin_t_pos).value
        x_t, y_t = func(df_window)
        
        # Compute true position
        if active_position is not None:
            row = df_positions.iloc[active_position - 1]
            if pd.isna(row['x']) or pd.isna(row['y']):
                prev_row = df_positions.iloc[active_position - 2]
                next_row = df_positions.iloc[active_position]
                p_x = prev_row['x'] + (next_row['x'] - prev_row['x']) * part_position
                p_y = prev_row['y'] + (next_row['y'] - prev_row['y']) * part_position
            else:
                p_x, p_y = row['x'], row['y']
        else:
            p_x = p_y = None

    return x_t, y_t, active_position, p_x, p_y, df_window


def precompute_frames(df, df_positions,  window_width, window_step, func=least_square_estimation, output_dir="frames", start_pos=START_POS):
    os.makedirs(output_dir, exist_ok=True)

    with open(output_dir+"/pozycje.csv", "w", newline="") as f: 
        writer = csv.writer(f) 
        writer.writerow([ "l.p.", "czas", "pozycja", "x_estymowane", "y_estymowane", "x_prawdziwe", "y_prawdziwe" ])
    
    
    t0 = df["data"].min()
    times_sec = (df["data"] - t0).dt.total_seconds()
    slider_values = np.arange(times_sec.min(), times_sec.max()+1, window_step.total_seconds())

    frames = []
    x_t, y_t = start_pos
    for i, t in enumerate(tqdm(slider_values, desc="Generating frames", unit="frame")):
        center_time = t0 + timedelta(seconds=t)
        frame, x_t, y_t, active_position, p_x, p_y = generate_frame(df, df_positions, center_time, window_width, func=func, last_position=(x_t, y_t))

        frames.append(frame)
        plt.imsave(f"{output_dir}/frame_{i:04d}.png", frame)
        with open(output_dir+"/pozycje.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([ i, center_time.isoformat(), active_position, x_t, y_t, p_x, p_y ])

    return frames, slider_values


def precompute_trajectory(df, df_positions, window_width, window_step, func=least_square_estimation, output_file=None, start_pos=START_POS):

    if output_file is not None:
        with open("outputs/" + output_file, "w", newline="") as f: 
            writer = csv.writer(f) 
            writer.writerow([ "l.p.", "czas", "pozycja", "x_estymowane", "y_estymowane", "x_prawdziwe", "y_prawdziwe", "blad" ])
        
        
    t0 = df["data"].min()
    times_sec = (df["data"] - t0).dt.total_seconds()
    slider_values = np.arange(times_sec.min(), times_sec.max()+1, window_step.total_seconds())

    trajectory = []
    x_t, y_t = start_pos
    for i, t in enumerate(tqdm(slider_values, desc="Computing trajectory", unit="step")):
        center_time = t0 + timedelta(seconds=t)
        
        x_t, y_t, active_position, p_x, p_y, _ = compute_position_values(df, df_positions, center_time, window_width, func, last_position=(x_t, y_t))
        error = np.sqrt((x_t - p_x)**2 + (y_t - p_y)**2) if p_x is not None and p_y is not None else None
        trajectory.append({
            'l.p.': i,
            'czas': center_time.isoformat(),
            'pozycja': active_position,
            'x_estymowane': x_t,
            'y_estymowane': y_t,
            'x_prawdziwe': p_x,
            'y_prawdziwe': p_y,
            'blad': error
        })
        if output_file is not None:
            with open("outputs/" + output_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([ i, center_time.isoformat(), active_position, x_t, y_t, p_x, p_y, error ])

    return pd.DataFrame(trajectory)


def plot_interactive_precomputed(frames, slider_values):
    fig, ax = plt.subplots(figsize=(6, 10))
    img = ax.imshow(frames[0])
    ax.axis("off")
   
    ax_slider = plt.axes((0.15, 0.05, 0.7, 0.03))
    slider = Slider(ax_slider, "czas [s]", 0, len(frames)-1, valinit=0, valstep=1)

    def update(val):
        idx = int(slider.val)
        img.set_data(frames[idx])
        fig.canvas.draw_idle()

    slider.on_changed(update)
    plt.show()


if __name__ == "__main__":
    distance_factor=0
    acceleration = 1.0
    speed = 1.2
    # frames, slider_values = precompute_frames(
    # df=df,
    # df_positions=df_positions,
    # func = lambda df: least_square_estimation(df, df_transmitters, bounds, distance_factor=distance_factor),
    # window_width=WINDOW_WIDTH,
    # window_step=WINDOW_STEP,
    # output_dir="outputs/output_LS"
    # )

    # dls = DLSEstimator(*START_POS, window_step=WINDOW_STEP,df_transmitters=df_transmitters,bounds=bounds, distance_factor=distance_factor)
    # frames, slider_values = precompute_frames(
    # df=df,
    # df_positions=df_positions,
    # func = dls.estimation,
    # window_width=WINDOW_WIDTH,
    # window_step=WINDOW_STEP,
    # output_dir="outputs/output_DLS"
    # )
    
    # d2ls = D2LSEstimator(*START_POS, window_step=WINDOW_STEP,df_transmitters=df_transmitters,bounds=bounds,distance_factor=0.5, acceleration=0.30)
    # frames, slider_values = precompute_frames(
    # df=df,
    # df_positions=df_positions,
    # func = d2ls.estimation,
    # window_width=WINDOW_WIDTH,
    # window_step=WINDOW_STEP,
    # output_dir="outputs/output_D2LS"
    # )

    # ekf = EKFLocalizer(initial_position=START_POS)    
    # frames, slider_values = precompute_frames(
    # df=df,
    # df_positions=df_positions,
    # func = lambda df: universal_position_estimator(df, method="EKF", state_obj=ekf, window_step=WINDOW_STEP),
    # window_width=WINDOW_WIDTH,
    # window_step=WINDOW_STEP,
    # output_dir="outputs/output_EKF"
    # )
    
    # pf = ParticleFilter()
    
    # frames, slider_values = precompute_frames(
    # df=df,
    # df_positions=df_positions,
    # func = lambda df: universal_position_estimator(df, method="PF", state_obj=pf),
    # window_width=WINDOW_WIDTH,
    # window_step=WINDOW_STEP,
    # output_dir="outputs/output_PF"
    # )
    
    # frames, slider_values = precompute_frames(
    # df=df,
    # df_positions=df_positions,
    # func = lambda df: universal_position_estimator(df, method="MLE"),
    # window_width=WINDOW_WIDTH,
    # window_step=WINDOW_STEP,
    # output_dir="outputs/output_MLE"
    # )
    
    window_width = timedelta(seconds=3)
    # plot_interactive_precomputed(frames, slider_values)
    # func = lambda df: least_square_estimation(df, df_transmitters, bounds=None, distance_factor=3)
    # save_trajectory_plot(df, window_width, folder_path="diagrams/wykresy2_LS/", filename=f"LS_distance_factor_3.png", func=func)

    # dls = DLSEstimator(*START_POS, window_step=WINDOW_STEP,df_transmitters=df_transmitters,bounds=bounds, speed=1, distance_factor=1.4 )
    # save_trajectory_plot(df, window_width, folder_path="diagrams/wykresy2_DLS/", filename=f"DLS.png",
    #                     func = dls.estimation
    #                     )
    d2ls = D2LSEstimator(*START_POS, window_step=WINDOW_STEP,df_transmitters=df_transmitters,bounds=bounds,distance_factor=2.4, speed=0.9, acceleration=1.05)
    save_trajectory_plot(df, window_width, folder_path="diagrams/wykresy2_D2LS/", filename=f"D2LS_sz.png",
                    func = d2ls.estimation
                        )
    # d2lsd = D2LSDEstimator(*START_POS, window_step=WINDOW_STEP,df_transmitters=df_transmitters,bounds=bounds,distance_factor=0.71, speed=0.9, acceleration=1.31, damping_factor=-0.1)
    # save_trajectory_plot(df, window_width, folder_path="diagrams/wykresy2_D2LSD/", filename=f"D2LSD.png",
    #                 func = d2lsd.estimation
    #                     )
    
    
    # distance_factors = [0.45,0.48,0.5,0.54,0.58]
    # for distance_factor in distance_factors:
    # distance_factor = 0.5
    
    # for acceleration in [0.35,0.40,0.45]:
        # d2ls = D2LSEstimator(*START_POS, window_step=WINDOW_STEP,df_transmitters=df_transmitters,bounds=bounds,distance_factor=distance_factor, acceleration=acceleration)
        # save_trajectory_plot(df, timedelta(seconds=15), folder_path="diagrams/wykresy2_D2LS/", filename=f"D2LS_{acceleration}.png",
        #                 func = d2ls.estimation
        #                     )

    # d2ls = D2LSEstimator(*START_POS, window_step=WINDOW_STEP,df_transmitters=df_transmitters,bounds=bounds,distance_factor=distance_factor,speed=speed, acceleration=acceleration)
    # save_trajectory_plot(df, timedelta(seconds=15), folder_path="diagrams/wykresy2_D2LS/", filename=f"D2LS_v2.png",
    #                 func = d2ls.estimation1
    #                     )
    # d2ls = D2LSEstimator(*START_POS, window_step=WINDOW_STEP,df_transmitters=df_transmitters,bounds=bounds,distance_factor=distance_factor,speed=speed, acceleration=acceleration)
    # save_trajectory_plot(df, timedelta(seconds=15), folder_path="diagrams/wykresy2_D2LS/", filename=f"D2LS_v3.png",
    #                 func = d2ls.estimation2
    #                     )
    # ekf = EKFLocalizer(initial_position=START_POS)
    # save_trajectory_plot(df, window_width, folder_path="wykresy2_EKF/", func = ekf.estimation)
    # pf = ParticleFilter()
    # save_trajectory_plot(df, window_width, folder_path="wykresy2_PF/", func = lambda df: universal_position_estimator(df, method="PF", state_obj=pf))
    # save_trajectory_plot(df, window_width, folder_path="wykresy2_MLE/", func = lambda df: universal_position_estimator(df, method="MLE"))
    
    # func = foggy_wrapper(dls,d2ls, proportion=0.5)
    # frames, slider_values = precompute_frames(
    # df=df,
    # df_positions=df_positions,
    # func = d2ls.estimation,
    # window_width=WINDOW_WIDTH,
    # window_step=WINDOW_STEP,
    # output_dir="outputs/output_FOGGY"
    # )
    # for proportion in [0.1, 0.3, 0.5, 0.7, 0.9]:
    #     func = foggy_wrapper(dls,d2ls, proportion=proportion)
    #     save_trajectory_plot(df, WINDOW_WIDTH, folder_path="wykresy2_FOGGY/", filename=f"FOGGY_{proportion}.png", func = func)