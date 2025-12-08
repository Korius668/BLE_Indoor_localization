from scipy.optimize import least_squares
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde

from pomiar1.pozycje import df_positions 
from pomiar1.boxplot import transmitter_order, calc_data
from mapa_nadajniki import background, df_transmitters
from pomiar1.generowanie_pozycji import samples
from pomiar1.regresja_liniowa import calculate_distance_from_rssi
from mapa_nadajniki import plot_map

def calculate_residuals(estimated_position, beacons, distances_from_rssi):
    x, y = estimated_position
    true_distances = np.sqrt((x - beacons[:, 0])**2 + (y - beacons[:, 1])**2)
    return true_distances - distances_from_rssi

def plot_estimated_positions_map(
    measurement_num,
    estimated_positions,
    df_positions,
    df_transmitters,
    calc_data
):

    if estimated_positions.size == 0:
        print(f"No estimated positions to plot for measurement {measurement_num}.")
        return

    if measurement_num - 1 >= len(df_positions):
        print(f"Skipping measurement {measurement_num}: no true position in df_positions.")
        return

    # True position
    true_pos_x = df_positions['x'].iloc[measurement_num - 1]
    true_pos_y = df_positions['y'].iloc[measurement_num - 1]

    points_x = estimated_positions[:, 0]
    points_y = estimated_positions[:, 1]

    fig, ax = plt.subplots(figsize=(10, 8))
   

    # KDE heatmap
    if len(points_x) > 1 and len(np.unique(points_x)) > 1 and len(np.unique(points_y)) > 1:
        data = np.vstack([points_x, points_y])
        try:
            kde = gaussian_kde(data)
        except np.linalg.LinAlgError:
            print(f"Skipping KDE for measurement {measurement_num} due to singular matrix (e.g., all points are collinear).")
            kde = None
    else:
        print(f"Skipping KDE for measurement {measurement_num} due to insufficient unique points.")
        kde = None

    if kde is not None:

        # x_min, x_max = points_x.min() - 0.5, points_x.max() + 0.5
        # y_min, y_max = points_y.min() - 0.5, points_y.max() + 0.5

        # x_min = min(x_min, min_real_x)
        # x_max = max(x_max, max_real_x)
        # y_min = min(y_min, min_real_y)
        # y_max = max(y_max, max_real_y)

        x_min = -10
        x_max = 20
        y_min = -5
        y_max = 37
        xi, yi = np.mgrid[
            x_min:x_max:1000j,
            y_min:y_max:1000j
        ]

        zi = kde(np.vstack([xi.flatten(), yi.flatten()])).reshape(xi.shape)

        contour = ax.contourf(
            xi, yi, zi,
            levels=20,
            cmap='inferno',
            alpha=0.7
        )

        max_idx = np.argmax(zi)
        max_coord = np.unravel_index(max_idx, zi.shape)
        max_x = xi[max_coord]
        max_y = yi[max_coord]

        print(f"Max KDE density coordinate: {max_x:.2f}, {max_y:.2f}")

        # Optional plotting
        ax.scatter(max_x, max_y, c='cyan', s=120, marker='X', label=f'KDE Maximum {max_x:0.2f}, {max_y:0.2f}')
        fig.colorbar(contour, ax=ax, label='Gęstość występowania punktów')

    ax = plot_map(ax)
    # # Background map
    # ax.imshow(background, extent=[min_real_x, max_real_x, min_real_y, max_real_y])

    # Estimated samples
    ax.scatter(
        points_x,
        points_y,
        color='purple',
        s=5,
        alpha=0.9,
        label=f'Estimated Positions ({len(points_x)} samples)'
    )

    # True point
    ax.scatter(
        true_pos_x, true_pos_y,
        color='red',
        alpha=0.9,
        s=100,
        marker='X',
        label='True Position'
    )

    # Transmitters
    first_label = True
    colored_scatter = None

    for _, row in df_transmitters.iterrows():
        txid = int(row['Id'])
        label = 'Transmitters' if first_label else ""

        entry = calc_data.get(measurement_num-1, [])
        AVG = entry[txid - 1]['avg'] if txid - 1 < len(entry) else np.nan
        CNT = entry[txid - 1]['count'] if txid - 1 < len(entry) else np.nan

        if not np.isnan(AVG) and CNT > 0:
            s = 80 + CNT

            if colored_scatter is None:
                colored_scatter = ax.scatter(
                    row['x'], row['y'],
                    c=[AVG],
                    s=s,
                    cmap='viridis',
                    edgecolors='black',
                    alpha=0.9,
                    vmin=-100, vmax=-40,
                    label=label
                )
            else:
                ax.scatter(
                    row['x'], row['y'],
                    c=[AVG],
                    s=s,
                    cmap='viridis',
                    edgecolors='black',
                    alpha=0.9,
                    vmin=-100, vmax=-40,
                    label=""
                )
            fontsize = 9

        else:
            ax.scatter(
                row['x'], row['y'],
                color='gray',
                s=30,
                marker='o',
                edgecolors='black',
                alpha=0.4,
                label=label
            )
            fontsize = 6

        ax.text(row['x'], row['y'], str(txid),
                color='white', fontsize=fontsize,
                ha='center', va='center')

        first_label = False

    # Add colorbar if at least 1 colored point exists
    if colored_scatter is not None:
        cbar = fig.colorbar(colored_scatter, ax=ax)
        cbar.set_label('Average Signal Strength (dBm)')

    ax.set_title(
        f'Estimated vs True Position for Measurement {measurement_num}'
        f' (True: x={true_pos_x:.2f}, y={true_pos_y:.2f})'
    )
    ax.set_xlabel('Oś X (m)')
    ax.set_ylabel('Oś Y (m)')
    ax.set_aspect('equal', adjustable='box')
    ax.set_ylim(-5, 37)
    ax.set_xlim(-10, 20)
    ax.legend(loc='upper right')

    return ax

def calculate_estimated_positions(
    samples,
    df_transmitters
):
    cnt = 100
    estimated_positions_per_measurement = {}
    min_real_x_loc, min_real_y_loc = 0, 0
    max_real_x_loc, max_real_y_loc = 2.6, 27.0

    for measurement_num_str, s_data in samples.items():
        measurement_num = int(measurement_num_str)

        random_x = np.random.uniform(min_real_x_loc, max_real_x_loc)
        random_y = np.random.uniform(min_real_y_loc, max_real_y_loc)
        initial_guess = np.array([random_x, random_y])

        beacons_coords_list = []
        active_transmitter_ids = []

        for tx_id in transmitter_order:

            if tx_id in s_data and len(s_data[tx_id]) > 0:
                active_transmitter_ids.append(tx_id)
                transmitter_row = df_transmitters[df_transmitters['Id'] == int(tx_id)].iloc[0]
                beacons_coords_list.append([transmitter_row['x'], transmitter_row['y']])

        if not beacons_coords_list:
            print(f"Skipping measurement {measurement_num} due to no active transmitters with samples.")
            estimated_positions_per_measurement[measurement_num_str] = np.array([])
            continue

        beacons_coords = np.array(beacons_coords_list)

        current_measurement_estimated_positions = []

        for i in range(cnt):
            distances_from_rssi = []
            for tx_id in active_transmitter_ids:                
                rssi_sample = np.random.choice(s_data[tx_id])
                distance = calculate_distance_from_rssi(rssi_sample)
                distances_from_rssi.append(distance)

            distances_from_rssi = np.array(distances_from_rssi)

            result = least_squares(
                calculate_residuals,
                initial_guess,
                args=(beacons_coords, distances_from_rssi)
                # bounds=((min_real_x_loc, min_real_y_loc), (max_real_x_loc, max_real_y_loc))
            )
            current_measurement_estimated_positions.append(result.x)

        estimated_positions_per_measurement[measurement_num_str] = np.array(current_measurement_estimated_positions)   
    return estimated_positions_per_measurement

if __name__ == "__main__":

    estimated_positions_per_measurement = calculate_estimated_positions(samples, df_transmitters)
    for measurement_num, estimated_positions in estimated_positions_per_measurement.items():
        ax= plot_estimated_positions_map(
            measurement_num,
            estimated_positions,
            df_positions,
            df_transmitters,
            calc_data
        )
        plt.savefig(f"obrazy/least_squares_estymacja_pozycji_{measurement_num}.png")
    plt.show()