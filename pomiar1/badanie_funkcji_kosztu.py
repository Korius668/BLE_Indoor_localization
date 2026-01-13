from scipy.optimize import least_squares
import matplotlib.pyplot as plt
import numpy as np

from pomiar1.boxplot import calc_data, dfs
from pomiar1.dystans import plot_distance_from_signal
from mapa_nadajniki import plot_map
from pomiar1.least_square import distance_between_2_points, prepare_distance_data



def objective_function1(position, beacons, distances_from_rssi, weights=None):
    x, y = position
    geometrical_distances = distance_between_2_points(x,y,beacons[:, 0],beacons[:, 1])
    residuals =0
    if weights is None:
        residuals = geometrical_distances - distances_from_rssi
    else:        
        residuals = weights*(geometrical_distances - distances_from_rssi)
    return np.abs(residuals)

def objective_function2(position, beacons, distances_from_rssi, weights=None):
    x, y = position
    geometrical_distances = distance_between_2_points(x,y,beacons[:, 0],beacons[:, 1])
    residuals =0
    if weights is None:
        residuals = geometrical_distances - distances_from_rssi
    else:        
        residuals = weights*(geometrical_distances - distances_from_rssi)
    return np.abs(residuals)/distances_from_rssi



def least_square_estimation(beacons_coords, distances_from_rssi, weights=None, func=objective_function1):
    min_real_x_loc, min_real_y_loc = -10, -10
    max_real_x_loc, max_real_y_loc = 20.0, 27.0
    random_x = np.random.uniform(min_real_x_loc, max_real_x_loc)
    random_y = np.random.uniform(min_real_y_loc, max_real_y_loc)
    
    initial_guess = np.array([random_x,random_y])
    position = least_squares(
        func,
        initial_guess,
        args=(beacons_coords, distances_from_rssi)
    )
    return position.x


def calculate_average_positions(d, func=objective_function1, w_flag=False):
    beacons_coords, rssi_distances, weights = prepare_distance_data(d)
    if not w_flag:
        weights = None

    average_pos = least_square_estimation(beacons_coords, rssi_distances, weights, func=func)
    
    return average_pos[0], average_pos[1]


def plot_area_of_function(X,Y,d,ax =None, func=objective_function1, w_flag=False):
    if ax is None:
        ax = plot_map(ax)
    
    
    beacons_coords, rssi_distances, weights = prepare_distance_data(d)
    if not w_flag:
        weights = None

    Z = np.zeros_like(X)
    for j in range(X.shape[0]):
        for k in range(X.shape[1]): 
           
            Z[j, k] =np.sum(func(
                (X[j, k], Y[j, k]), 
                beacons_coords, 
                rssi_distances,
                weights
            ))
    contour = plt.contourf(X, Y, Z, levels=100,alpha=0.5, cmap='viridis')
    max_idx = np.argmin(Z)
    max_coord = np.unravel_index(max_idx, Z.shape)
    max_x = X[max_coord]
    max_y = Y[max_coord]



    # plt.colorbar(contour, label="Wartość funkcji celu")
    
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

    
if __name__ == "__main__":
    x_range = np.linspace(-20, 20,100)
    y_range = np.linspace(-10, 42, 100)
    ymin = -5
    ymax = 32
    xmin = -10
    xmax = 13

    
    X, Y = np.meshgrid(x_range, y_range)
    for measurement_num, d in calc_data.items():
    
        fig =  plt.figure(figsize=(20, 10))
        
        ax = plt.subplot(1,4,1)
        ax = plot_map(ax)
        ax= plot_area_of_function(X,Y,d=d,ax=ax, func=objective_function1)
        ax = plot_distance_from_signal(measurement_num, dfs[measurement_num], ax, c_flag=False)
        avg_x, avg_y = calculate_average_positions(d=d, func=objective_function1)
        ax = plot_average_positions(avg_x,avg_y, ax=ax)
  
        ax.set_aspect('equal')
        ax.set_ylim(ymin, ymax)
        ax.set_xlim(xmin, xmax)
        ax.get_legend().remove()
        ax.set_title('Zwykła')

        
        ax = plt.subplot(1,4,2)
        ax = plot_map(ax)
        ax= plot_area_of_function(X,Y,d=d,ax=ax, func=objective_function2)
        ax = plot_distance_from_signal(measurement_num, dfs[measurement_num], ax, c_flag=False)
       
        avg_x, avg_y = calculate_average_positions(d=d, func=objective_function2)
        ax = plot_average_positions(avg_x,avg_y, ax=ax)

        ax.set_aspect('equal')
        ax.set_ylim(ymin, ymax)
        ax.set_xlim(xmin, xmax)
        ax.get_legend().remove()
        ax.set_title('Dzielona przez odległość od rssi')
     
                
        ax = plt.subplot(1,4,3)
        ax = plot_map(ax)
        ax= plot_area_of_function(X,Y,d=d,ax=ax, func=func, w_flag=True)
        ax = plot_distance_from_signal(measurement_num, dfs[measurement_num], ax, c_flag=False)  
        avg_x, avg_y = calculate_average_positions(d=d, func=objective_function1,  w_flag=True)
        ax = plot_average_positions(avg_x,avg_y, ax=ax)
        ax.set_aspect('equal')
        ax.set_ylim(ymin, ymax)
        ax.set_xlim(xmin, xmax)
        ax.get_legend().remove()
        ax.set_title('Zwykła z wagami')

        ax = plt.subplot(1,4,4)
        func = objective_function2
        ax = plot_map(ax)
        ax= plot_area_of_function(X,Y,d=d,ax=ax, func=objective_function2, w_flag=True)
        ax = plot_distance_from_signal(measurement_num, dfs[measurement_num], ax, c_flag=False)
        avg_x, avg_y = calculate_average_positions(d=d, func=objective_function2,  w_flag=True)
        ax = plot_average_positions(avg_x,avg_y, ax=ax)
        ax.set_aspect('equal')
        ax.set_ylim(ymin, ymax)
        ax.set_xlim(xmin, xmax)
        ax.get_legend().remove()
        ax.set_title('Dzielona przez odległość od rssi z wagami')

        plt.savefig(f"obrazy2/estymacja_pozycji_{measurement_num}.png")
        for c in fig.images:
            if c is plt.colorbar:
                c.remove()


    plt.show()
    
    