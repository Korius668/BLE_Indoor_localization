from scipy.optimize import least_squares
import matplotlib.pyplot as plt
import numpy as np

from pomiar1.boxplot import calc_data, transmitter_order, dfs
from pomiar1.generowanie_pozycji import generate_samples
from pomiar1.regresja_liniowa import calculate_distance_from_rssi
from pomiar1.sila_sygnalu import plot_signal_strength_map
from pomiar1.dystans import plot_distance_from_signal
from mapa_nadajniki import df_transmitters, plot_map


def distance_between_2_points(x1, y1, x2, y2):
    return np.sqrt((x1 - x2)**2 + (y1 - y2)**2)


def objective_function(position, beacons, distances_from_rssi, weights=None):
    x, y = position
    geometrical_distances = distance_between_2_points(x,y,beacons[:, 0],beacons[:, 1])
    residuals =0
    if weights is None:
        residuals = geometrical_distances - distances_from_rssi
    else:        
        residuals = weights*(geometrical_distances - distances_from_rssi)
    return np.abs(residuals)


def prepare_distance_data(d):
        
    beacons_coords_list = []
    weights = []
    rssi_distances = []
    
    for j, b in enumerate(d):
        if (not np.isnan(b['count'])):
            transmitter_row = df_transmitters[df_transmitters['Id'] == j+1].iloc[0]
            beacons_coords_list.append([transmitter_row['x'], transmitter_row['y']])
            rssi_distance = calculate_distance_from_rssi(b['avg'])
            weights.append(b['count'])
            rssi_distances.append(rssi_distance)

    if not weights or np.sum(weights) == 0:
        return np.nan, np.nan

    weights = np.array(weights, dtype=float)
    weights /= np.sum(weights)
    beacons_coords = np.array(beacons_coords_list)
    
    return beacons_coords, rssi_distances, weights


def least_square_estimation(beacons_coords, distances_from_rssi, weights=None):
    min_real_x_loc, min_real_y_loc = -10, -10
    max_real_x_loc, max_real_y_loc = 20.0, 27.0
    random_x = np.random.uniform(min_real_x_loc, max_real_x_loc)
    random_y = np.random.uniform(min_real_y_loc, max_real_y_loc)
    
    initial_guess = np.array([random_x,random_y])
    position = least_squares(
        objective_function,
        initial_guess,
        args=(beacons_coords, distances_from_rssi)
    )
    return position.x

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
                rssi_distance = calculate_distance_from_rssi(rssi_sample)
                rssi_distances.append(rssi_distance)
            rssi_distances = np.array(rssi_distances)
            
            position = least_square_estimation(beacons_coords, rssi_distances)
            
            current_measurement_estimated_positions.append(position)

        estimated_positions_per_measurement[measurement_num] = np.array(current_measurement_estimated_positions)   
    return estimated_positions_per_measurement

def calculate_average_positions(d):
    beacons_coords, rssi_distances, weights = prepare_distance_data(d)
    average_pos = least_square_estimation(beacons_coords, rssi_distances, weights)
    
    return average_pos[0], average_pos[1]


def plot_area_of_function(X,Y,d,ax =None):
    if ax is None:
        ax = plot_map(ax)
    
    beacons_coords, rssi_distances, weights = prepare_distance_data(d)
    
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

def plot_average_positions(avg_pos_x, avg_pos_y , ax=None):
    if ax is None:
        ax = plot_map(ax)
    
    
    ax.scatter(
        avg_pos_x, avg_pos_y,
        color='orange',
        alpha=0.9,
        s=120,
        marker='v',
        label=f'Pozycja wyliczona z średnich rssi pomiarów: {avg_pos_x:.2f}, {avg_pos_y:.2f}'
    )
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
    samples = generate_samples(cnt)
    estimated_positions_per_measurement = calculate_monte_carlo_positions(samples, cnt=cnt)
    for measurement_num, estimated_positions in estimated_positions_per_measurement.items():
        fig, ax = plt.subplots(figsize=(10, 10))
        ax = plot_map(ax)
        ax= plot_area_of_function(X,Y,d=calc_data[measurement_num],ax=ax)
        ax = plot_estimated_positions(
            measurement_num,
            estimated_positions,
            ax=ax            
        )
        # ax = plot_signal_strength_map(measurement_num,dfs[measurement_num], ax=ax, fig=fig)
        ax = plot_distance_from_signal(measurement_num, dfs[measurement_num], ax)
        avg_x, avg_y = calculate_average_positions(d=calc_data[measurement_num])
        ax = plot_average_positions(avg_x,avg_y, ax=ax)
       
        ax.set_xlabel('Oś X (m)')
        ax.set_ylabel('Oś Y (m)')
        ax.set_aspect('equal', adjustable='box')
        ax.set_ylim(-10, 42)
        ax.set_xlim(-20, 20)
        ax.legend(loc='upper right')
        if measurement_num == 1:
            plt.savefig(f"obrazy2/4.png")
        # plt.savefig(f"obrazy/least_squares_estymacja_pozycji_{measurement_num}.png")
    plt.show()
    
    