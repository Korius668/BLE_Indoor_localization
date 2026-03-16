import matplotlib.pyplot as plt
import numpy as np

from pomiar import df_transmitters, plot_map
from  ble_indoor_localization import ( 
    plot_area_of_objective_function,
    objective_function
)

from .boxplot import dfs, calc_data


if __name__ == "__main__":  
    
    x_range = np.linspace(-10, 20, 5)
    y_range = np.linspace(-5, 37, 5)
    
    X, Y = np.meshgrid(x_range, y_range)
    fig = {}
    for i, d in calc_data.items():
        fig[i] = plt.figure(figsize=(4, 6))
        ax = plot_map()
        plot_area_of_objective_function(X, Y, d, df_transmitters, objective_function,ax=ax)
  
    plt.show()
