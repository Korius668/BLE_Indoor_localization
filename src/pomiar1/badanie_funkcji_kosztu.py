import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ble_indoor_localization import (
    plot_distance_from_signal, 
    calculate_distance_from_rssi, 
    generate_samples, 
    distance_between_2_points, 
    prepare_distance_data,
    objective_function
    )
from pomiar import df_transmitters, plot_map

from .boxplot import (
    calc_data, 
    dfs, 
    transmitter_order, 
    df_positions
    )
from .least_square import least_square_estimation


def calculate_monte_carlo_positions(
    samples,
    cnt = 100,
    func=objective_function,
    w_flag=False
):
    
    estimated_positions_per_measurement = {}

    for measurement_num, s_data in samples.items():
        beacons_coords_list = []
        _, _, weights = prepare_distance_data(calc_data[measurement_num])
        if not w_flag:
            weights = None
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
            
            position, cost = least_square_estimation(beacons_coords, rssi_distances, weights, func=func)
            
            current_measurement_estimated_positions.append(position)

        estimated_positions_per_measurement[measurement_num] = np.array(current_measurement_estimated_positions)   
    return estimated_positions_per_measurement



def calculate_average_positions(calc_data, func=objective_function, w_flag=False):
    beacons_coords, rssi_distances, weights = prepare_distance_data(calc_data)
    if not w_flag:
        weights = None

    average_pos, cost = least_square_estimation(beacons_coords, rssi_distances, weights, func=func)
    
    return average_pos[0], average_pos[1], cost

def value_of_objective_function(x, y, beacons_coords,d_input,weights, func=objective_function):
    result = 0.5*np.sum(func(
                (x,y), 
                beacons_coords, 
                d_input,
                weights=weights
            )**2)
    return result
    
def plot_area_of_objective_function(X,Y,d,ax =None, func=objective_function, w_flag=False):
    if ax is None:
        ax = plot_map(ax)
    
    
    beacons_coords, rssi_distances, weights = prepare_distance_data(d)
    if not w_flag:
        weights = None

    Z = np.zeros_like(X)
    for j in range(X.shape[0]):
        for k in range(X.shape[1]): 
            
                        
            Z[j, k] = value_of_objective_function(X[j, k], Y[j, k], beacons_coords, rssi_distances, weights, func=func)
    contour = plt.contourf(X, Y, Z, levels=100,alpha=0.5, cmap='viridis')
    max_idx = np.argmin(Z)
    max_coord = np.unravel_index(max_idx, Z.shape)
    max_x = X[max_coord]
    max_y = Y[max_coord]



    # plt.colorbar(contour, label="Wartość funkcji celu")
    result = {"x": max_x, "y": max_y, "value": Z[max_coord]}
    ax.scatter(max_x, max_y, c='cyan', s=120, marker='X', label=f'Minimum funkcji {max_x:0.2f}, {max_y:0.2f}')
    return ax, result

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
    ymin = -5
    ymax = 32
    xmin = -10
    xmax = 13

    
    X, Y = np.meshgrid(x_range, y_range)
    cnt = 50
    samples = generate_samples(cnt)
    estimated_positions_1 = calculate_monte_carlo_positions(samples, cnt=cnt,func=objective_function)
    estimated_positions_3 = calculate_monte_carlo_positions(samples, cnt=cnt,func=objective_function,  w_flag=True)

    
    methods_config = [
    {
        "method": "Zwykla",
        "subplot": 1,
        "func": objective_function,
        "estimated_positions": estimated_positions_1,
        "w_flag": False
    },
    {
        "method": "Zwykla z wagami",
        "subplot": 3,
        "func": objective_function,
        "estimated_positions": estimated_positions_3,
        "w_flag": True
    }
    ]
    output_file = "tabela/estymacja_pozycji.csv"


    open(output_file, "w").close()
    
    for measurement_num, d in calc_data.items():

        true_x, true_y = df_positions.loc[measurement_num-1, ['x', 'y']]
        rows = []

        fig = plt.figure(figsize=(20, 7))

        for cfg in methods_config:

            ax = plt.subplot(1, 4, cfg["subplot"])
            func = cfg["func"]

            ax = plot_map(ax)
            ax, area = plot_area_of_objective_function(
                X, Y, d=d, ax=ax, func=func, w_flag=cfg["w_flag"]
            )
            beacons_coords, rssi_distances, weights = prepare_distance_data(d)
            if not cfg["w_flag"]:
                weights = None
            rows.append({
                "measurement_id": measurement_num,
                "method": cfg["method"],
                "wskaznik": "Minimum funkcji celu",
                "est_x": area["x"],
                "est_y": area["y"],
                
                "distance": distance_between_2_points(
                    true_x, true_y, area["x"], area["y"]
                ),
                "true_x": true_x,
                "true_y": true_y,
                "cost": area["value"],
                "funkcja_celu": value_of_objective_function(area["x"], area["y"], beacons_coords, rssi_distances, weights=weights, func=func)
            })

            ax = plot_estimated_positions(
                measurement_num,
                cfg["estimated_positions"][measurement_num],
                ax=ax
            )

            ax = plot_distance_from_signal(
                measurement_num, dfs[measurement_num], ax, c_flag=False
            )

            avg_x, avg_y, cost = calculate_average_positions(
                calc_data=d, func=func, w_flag=cfg["w_flag"]
            )

            ax = plot_average_positions(avg_x, avg_y, ax=ax)

            ax.set_aspect('equal')
            ax.set_ylim(ymin, ymax)
            ax.set_xlim(xmin, xmax)
            ax.get_legend().remove()
            ax.set_title(cfg["method"])

            # zapis do CSV (1 wiersz = metoda + wskaźnik)
            
            
            rows.append({
                "measurement_id": measurement_num,
                "method": cfg["method"],
                "wskaznik": "Pozycja wyliczona z uśrednionych zmierzonychrssi",
                "est_x": avg_x,
                "est_y": avg_y,
                
                "distance": distance_between_2_points(
                    true_x, true_y, avg_x, avg_y
                ),
                "true_x": true_x,
                "true_y": true_y,
                "cost": cost,
                "funkcja_celu": value_of_objective_function(avg_x, avg_y, beacons_coords, rssi_distances, weights=weights, func=func)
            })

        df = pd.DataFrame(rows)
        df.to_csv(
            output_file,
            mode="a",
            index=False,
            header=(measurement_num == list(calc_data.keys())[0])
        )
        with open(output_file, "a") as f:
            f.write("\n")

        for c in fig.images:
            if c is plt.colorbar:
                c.remove()
        plt.savefig(f"obrazy2/estymacja_pozycji_{measurement_num}.png")
    # plt.show()