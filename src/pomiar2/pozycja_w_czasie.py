import csv
from datetime import timedelta
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np
import pandas as pd
import os

from estymator import EKFLocalizer, ParticleFilter, least_square_estimation, universal_position_estimator, delta_least_square_estimation
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



def save_trajectory_plot(df, window_width,window_step=WINDOW_STEP, func=least_square_estimation, folder_path="wykresy/"):
    os.makedirs(folder_path, exist_ok=True)
    df_traj = get_full_trajectory(df, window_width, window_step=window_step, func=func)
    
    if not df_traj.empty:

        fig_test, ax_test = plt.subplots(figsize=(8, 10))
        ax_test = plot_map(ax=ax_test)

        unique_positions = sorted(df_traj["position"].unique())
        possible_colors = np.linspace(0, 1, len(unique_positions))
        color_map = {pos: possible_colors[i] for i, pos in enumerate(unique_positions)}
        colors = df_traj["position"].map(color_map).values

        cmap = plt.get_cmap('plasma')

        ax_test.plot(df_traj['x'], df_traj['y'], color='gray', alpha=0.3, lw=1)
        scatter = ax_test.scatter(
            df_traj['x'], df_traj['y'], 
            c=colors, cmap=cmap, 
            s=40, edgecolor='black', linewidth=0.3, zorder=3
        )
        
        step = max(1, len(df_traj) // 20) 
        for i in range(0, len(df_traj), step):
            row = df_traj.iloc[i]
            ax_test.text(row['x'] + 0.1, row['y'] + 0.1, str(i), fontsize=7)

        plt.colorbar(scatter, ax=ax_test, label='Postęp w czasie')
        
        window_str = str(window_width).replace(':', '-')
        ax_test.set_title(f"Trajektoria - okno: {window_width}")
        
        filename = folder_path+f"trajektoria_window_{window_str}.png"
        plt.savefig(filename, bbox_inches='tight')
        print(f"Zapisano: {filename}")

        plt.close(fig_test)



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
    # func = lambda df: universal_position_estimator(df, method="EKF", state_obj=ekf),
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
        timedelta(seconds=1),
        timedelta(seconds=2),
        timedelta(seconds=5), 
        timedelta(seconds=15), 
        timedelta(seconds=30)
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
