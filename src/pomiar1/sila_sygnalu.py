from matplotlib import pyplot as plt

from ble_indoor_localization import plot_signal_strength_map
from pomiar import df_transmitters, plot_map
from .boxplot import dfs


def plot_signal_strength_maps():
    fig = {}
    for measurement_name, df_measurement in dfs.items():
        fig[measurement_name] = plt.figure(figsize=(4, 6))
        ax = plot_map()
        plot_signal_strength_map(df_measurement, df_transmitters, ax, fig=fig[measurement_name])
        plt.savefig(f"docs/obrazy/mapa_rssi_pozycja_{measurement_name}.png")

    
if __name__ == "__main__":
    # plot_signal_strength_maps()

    fig = {}
    for measurement_name, df_measurement in dfs.items():
        if measurement_name in [1, 5, 11]:
            fig[measurement_name] = plt.figure(figsize=(5, 6))
            ax = plot_map()
            if measurement_name == 11:
                ax =plot_signal_strength_map(df_measurement, df_transmitters, ax, fig=fig[measurement_name])
            else:
                ax = plot_signal_strength_map(df_measurement, df_transmitters, ax, fig=fig[measurement_name], c_flag=False, legend=False)
            
            ax.set_xticks([])
            ax.set_yticks([])
            plt.ylim(-1, 34)
            plt.xlim(-10, 9)
            plt.savefig(f"docs/obrazy/mapa_rssi_pozycja_{measurement_name}.png")
       
    plt.show()
    