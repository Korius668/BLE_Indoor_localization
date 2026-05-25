from tqdm import tqdm
from matplotlib.lines import Line2D
import numpy as np

import matplotlib.pyplot as plt

from ble_indoor_localization import (
    calculate_distance_from_rssi, 
    plot_signal_strength_map    
)
from pomiar import df_transmitters, plot_map

from .boxplot import dfs
from .regresja_liniowa import model


def plot_example_distance_from_signal(measurement_name, df_measurement, df_transmitters,
                            ax, fig=None):    
    transmitter_stats = df_measurement.groupby('id nadajnika')['znormalizowana moc sygnalu'].agg(['mean', 'count']).reset_index()
    transmitter_stats = transmitter_stats.rename(columns={'mean': 'average_signal_strength', 'count': 'sample_count'})
    
    if not fig:
        fig = plt.gcf()
    df_transmitters2 = df_transmitters[df_transmitters['Id'].isin((1, 2, 3, 4, 5, 6,7,8))]
    ax = plot_signal_strength_map(df_measurement, df_transmitters2, 
                                fig=fig, ax=ax, real_plot=False)
    example_point = np.array([-2, 10])
    
    distances = [3.16, 5.0, 8.0,3 ,5 , 7.07, 4.24, 6.32]
    for index, tx_row in transmitter_stats.iterrows():
        tx_id = tx_row['id nadajnika']

        transmitter_coords_row = df_transmitters2[df_transmitters2['Id'] == int(tx_id)]
        if not transmitter_coords_row.empty:
            transmitter_coords = transmitter_coords_row.iloc[0]
            tx_x = transmitter_coords['x']
            tx_y = transmitter_coords['y']
            estimated_distance =  distances[index]
            circle = plt.Circle((tx_x, tx_y), estimated_distance, color='blue', 
                                fill=False, linestyle='--', alpha=0.7, label=None)            
            ax.add_patch(circle)
            C = np.array((tx_x, tx_y))
            R = estimated_distance
            v = example_point - C
            v_norm = v / np.linalg.norm(v)
            Q = C + R * v_norm

            ax.annotate(
                "",
                xy=example_point,        # koniec na okręgu
                xytext=C,    # początek
                arrowprops=dict(arrowstyle="->", lw=2, color="darkorange"),
                label = "d"
            )
            ax.annotate(
                "",
                xy=Q,        # koniec na okręgu
                xytext=example_point,    # początek
                arrowprops=dict(arrowstyle="->", lw=2, color="red"),
                label = "d-d_P"
            )
                

            ax.text(tx_x, tx_y + estimated_distance, f'{estimated_distance:.2f}m', 
                    color='blue', fontsize=8, ha='center', va='bottom')
            
        else:
            print(f"Warning: Transmitter ID {tx_id} not found in df_transmitters.")
    
    plt.scatter(*example_point, s=100, marker='^', color='orange',label='p - przykładowy punkt')
    plt.Circle((0, 0), 0, color='blue', fill=False, linestyle='--', alpha=0.7, 
              label='Estimated Distance from RSSI')
    legend_elements = [
    Line2D([0], [0], color='darkorange', lw=2,
           label="d - odległość punktu p od nadajnika"),
    plt.Circle((0, 0), 0, color='blue', fill=False, linestyle='--', alpha=0.7, 
              label='d_P - odległość obliczona  z RSSI'),
    Line2D([0], [0], color='red', lw=2,
           label="|d - d_P| - różnica między odległościami"),
]
    handles, labels = ax.get_legend_handles_labels()
    handles += legend_elements
    ax.legend(handles=handles, loc='upper right')
    
    
    ax.set_title(f'Róźnice między odległościami')
    
    return ax

def plot_example_real_vs_calculated(measurement_name, ax, fig=None):    

    if not fig:
        fig = plt.gcf()

    example_point = np.array([-2, 7])
    
    real_point = np.array([1, 5])
    plt.annotate(
                "",
                xy=real_point,       
                xytext=example_point,
                arrowprops=dict(arrowstyle="->", lw=2, color="darkred"),
                label = "error - różnica między p a p_r"
            )
    
    mid_x = (real_point[0] + example_point[0]) / 2
    mid_y = (real_point[1] + example_point[1]) / 2

    dy = real_point[1] - example_point[1]
    dx = real_point[0] - example_point[0]
    angle = np.degrees(np.arctan2(dy, dx))

    # Adjust angle so text is never upside down (optional but nice)
    if angle > 90:
        angle -= 180
    elif angle < -90:
        angle += 180

    # 4. Add the rotated text slightly offset above the midpoint
    plt.text(
        mid_x, mid_y, 
        "błąd", 
        rotation=angle, 
        ha='center', 
        va='bottom',  # 'bottom' pushes the text slightly above the line
        color="darkred",
        fontweight="bold"
)
    plt.scatter(*example_point, s=200, marker='^', color='orange',label='p - przykładowy punkt')
    plt.scatter(*real_point, s=200, marker='o', color='red', label='p_r - rzeczywisty punkt')
    handlers, labels = ax.get_legend_handles_labels()
    handlers += [Line2D([0], [0], color='darkred', lw=2, label="błąd - różnica między p a p_r")]  
    
    ax.legend(handles=handlers, loc='upper right')
    
    
    ax.set_title(f'Róźnice między odległościami')
    
    return ax

if __name__ == "__main__":
    for measurement_name, df_measurement in tqdm(dfs.items()):
        if measurement_name > 1:
            break
        fig, ax = plt.subplots(figsize=(5, 5))
        # ax= plot_map()
        # func = lambda rssi: calculate_distance_from_rssi(rssi, model)
        # plot_example_distance_from_signal(measurement_name, df_measurement, df_transmitters, ax=ax,)
        plot_example_real_vs_calculated("Błąd estymacji", ax=ax)
        ax.set_ylim(4, 8)
        ax.set_xlim(-4, 4)
        ax.set_xlabel('Oś X (m)')
        ax.set_ylabel('Oś Y (m)')
    plt.show()