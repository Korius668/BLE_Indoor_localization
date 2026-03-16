from scipy.optimize import least_squares
import matplotlib.pyplot as plt
import numpy as np

from ble_indoor_localization import (
    objective_function, 
    calculate_distance_from_rssi, 
    least_square_estimation, 
    prepare_distance_data,
    generate_samples,
    plot_distance_from_signal,
    plot_average_positions
)

from pomiar import df_transmitters, plot_map

from .boxplot import transmitter_order, calc_data, dfs
from .regresja_liniowa import model

def calculate_monte_carlo_positions(
    samples,
    cnt = 100
):
    
    estimated_positions_per_measurement = {}

    for measurement_num, s_data in samples.items():
  

        beacons_coords_list = []
        active_transmitter_ids = []

        for tx_id in transmitter_order:

            if tx_id in s_data and len(s_data[tx_id]) > 0:
                active_transmitter_ids.append(tx_id)
                transmitter_row = df_transmitters[df_transmitters['Id'] == int(tx_id)].iloc[0]
                beacons_coords_list.append([transmitter_row['x'], transmitter_row['y']])
                
        if not beacons_coords_list:
            print(f"Skipping measurement {measurement_num} due to no active transmitters with samples.")
            estimated_positions_per_measurement[measurement_num] = np.array([])
            continue

        beacons_coords = np.array(beacons_coords_list)

        current_measurement_estimated_positions = []

        for i in range(cnt):
            rssi_distances = []
            for tx_id in active_transmitter_ids:                
                rssi_sample = np.random.choice(s_data[tx_id])
                rssi_distance = calculate_distance_from_rssi(rssi_sample, model)
                rssi_distances.append(rssi_distance)
            rssi_distances = np.array(rssi_distances)
            
            position, _ = least_square_estimation(beacons_coords, rssi_distances)
            
            current_measurement_estimated_positions.append(position)

        estimated_positions_per_measurement[measurement_num] = np.array(current_measurement_estimated_positions)   
    return estimated_positions_per_measurement

def calculate_average_positions(calc_data):
    beacons_coords, rssi_distances, weights = prepare_distance_data(calc_data, df_transmitters)
    average_pos, _ = least_square_estimation(beacons_coords, rssi_distances, weights)
    
    return average_pos[0], average_pos[1]


def plot_area_of_function(X,Y,calc_data,ax =None):
    if ax is None:
        ax = plot_map(ax)
    
    beacons_coords, rssi_distances, weights = prepare_distance_data(calc_data, df_transmitters)
    
    Z = np.zeros_like(X)
    for j in range(X.shape[0]):
        for k in range(X.shape[1]): 

            d_input = rssi_distances
            
            Z[j, k] =np.sum(objective_function(
                (X[j, k], Y[j, k]), 
                beacons_coords, 
                d_input
                # weights=weights
            ))
    contour = plt.contourf(X, Y, Z, levels=100,alpha=0.5, cmap='viridis')
    max_idx = np.argmin(Z)
    max_coord = np.unravel_index(max_idx, Z.shape)
    max_x = X[max_coord]
    max_y = Y[max_coord]



    plt.colorbar(contour, label="Wartość funkcji celu")
    
    ax.scatter(max_x, max_y, c='cyan', s=120, marker='X', label=f'Minimum funkcji {max_x:0.2f}, {max_y:0.2f}')
    return ax


def plot_estimated_positions(
    measurement_num,
    estimated_positions,
    ax=None,
    fig = None
):
    if estimated_positions.size == 0:
        print(f"No estimated positions to plot for measurement {measurement_num}.")
        return

    if ax is None:
        ax = plot_map(ax)
    if fig is None:
        fig = plt.gcf()
        
    
    points_x = estimated_positions[:, 0]
    points_y = estimated_positions[:, 1]

    ax.scatter(
        points_x,
        points_y,
        color='greenyellow',
        s=5,
        alpha=0.9,
        label=f'Estymowane pozycje z populacji wygenerowanej ({len(points_x)} samples)'
    )
    
    return ax
    
if __name__ == "__main__":
    x_range = np.linspace(-20, 20,100)
    y_range = np.linspace(-10, 42, 100)
    
    X, Y = np.meshgrid(x_range, y_range)
    cnt = 50
    samples = generate_samples(calc_data,cnt)
    estimated_positions_per_measurement = calculate_monte_carlo_positions(samples, cnt=cnt)
    for measurement_num, estimated_positions in estimated_positions_per_measurement.items():
        fig, ax = plt.subplots(figsize=(10, 10))
        ax = plot_map(ax)
        ax= plot_area_of_function(X,Y,calc_data=calc_data[measurement_num],ax=ax)
        ax = plot_estimated_positions(
            measurement_num,
            estimated_positions,
            ax=ax            
        )
        func = lambda rssi: calculate_distance_from_rssi(rssi,model)
        ax = plot_distance_from_signal(measurement_num, dfs[measurement_num],df_transmitters,func,  ax)
        avg_x, avg_y = calculate_average_positions(calc_data=calc_data[measurement_num])
        ax = plot_average_positions(avg_x,avg_y, ax=ax)
       
        ax.set_xlabel('Oś X (m)')
        ax.set_ylabel('Oś Y (m)')
        ax.set_aspect('equal', adjustable='box')
        ax.set_ylim(-10, 42)
        ax.set_xlim(-20, 20)
        ax.legend(loc='upper right')
        plt.savefig(f"docs/obrazy/least_squares_estymacja_pozycji_{measurement_num}.png")
    plt.show()