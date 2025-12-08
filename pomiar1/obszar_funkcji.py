import numpy as np
import matplotlib.pyplot as plt

from pomiar1.boxplot import calc_data, dfs
from mapa_nadajniki import df_transmitters, plot_map
from pomiar1.sila_sygnalu import plot_signal_strength_map


# Funkcja celu: suma kwadratów residuów
def objective_function(position, beacons, distances_from_rssi, weights=None):
    x, y = position
    true_distances = np.sqrt((x - beacons[:, 0])**2 + (y - beacons[:, 1])**2)
    if weights is None:
        residuals = true_distances - distances_from_rssi
    else:        
        residuals = weights*(true_distances - distances_from_rssi)
    return np.sum(residuals**2)

def calculate_distance(x1, y1, x2, y2):
    return np.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def plot_area_of_function(ax =None):
        
    x_range = np.linspace(-10, 20, 5)
    y_range = np.linspace(-5, 37, 5)
    
    X, Y = np.meshgrid(x_range, y_range)
    Z = np.zeros_like(X)
    for i, d in calc_data.items():
        beacons_coords_list = []
        distances_from_rssi = []
        weights = []
        total_count = 0
            
        for j, b in enumerate(d):
            if (not np.isnan(b['count'])):
                transmitter_row = df_transmitters[df_transmitters['Id'] == j+1].iloc[0]
                beacons_coords_list.append([transmitter_row['x'], transmitter_row['y']])
                weights.append(b['count'])
                total_count+=b['count']
                          

            distances_from_rssi = np.array(distances_from_rssi)
        total_count = np.sum(weights)
        weights = [w / total_count for w in weights]
        weights = np.array(weights)
        beacons_coords = np.array(beacons_coords_list)
       

        for j in range(X.shape[0]):
            for k in range(X.shape[1]):
                for cord in beacons_coords:
                    calculated_distances = calculate_distance(j,k,cord[0], cord[1])

                Z[j, k] = objective_function((X[j, k], Y[j, k]), beacons_coords, calculated_distances, weights=weights)
        df_measurement = dfs[str(i)]
        fig, ax = plt.subplots(figsize=(5, 6))
        contour = plt.contourf(X, Y, Z, levels=20,alpha=0.7, cmap='inferno')
        max_idx = np.argmin(Z)
        max_coord = np.unravel_index(max_idx, Z.shape)
        max_x = X[max_coord]
        max_y = Y[max_coord]

        print(f"Minimum funkcji: {max_x:.2f}, {max_y:.2f}")

        # Optional plotting
        
        plt.colorbar(contour, label="Wartość funkcji celu")
        ax = plot_map(ax=ax)
        ax = plot_signal_strength_map(str(i+1),df_measurement, ax=ax, fig=fig)
        ax.scatter(max_x, max_y, c='cyan', s=120, marker='X', label=f'KDE Maximum {max_x:0.2f}, {max_y:0.2f}')
        
        
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.legend()
        plt.xlim(-10, 20)
        plt.ylim(-5, 37)
        plt.title("Mapa wartości funkcji celu")
    return ax


if __name__ == "__main__":  
    
    ax = plot_area_of_function()

    plt.show()

