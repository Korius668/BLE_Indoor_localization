from datetime import timedelta

from pomiar2.pozycja_w_czasie import plot_interactive_map, save_trajectory_plot
from pomiar3.dystans_w_czasie import WINDOW_STEP, WINDOW_WIDTH, df
from pomiar3.pozycje import df_positions

if __name__ == "__main__":
    plot_interactive_map(df, df_positions=df_positions, window_width=WINDOW_WIDTH, window_step=WINDOW_STEP)
    test_windows = [
        timedelta(seconds=1),
        timedelta(seconds=2),
        timedelta(seconds=5), 
        timedelta(seconds=15), 
        timedelta(seconds=30)
    ]

    for window_width in test_windows:
        save_trajectory_plot(df, window_width, WINDOW_STEP, folder_path="wykresy3/")