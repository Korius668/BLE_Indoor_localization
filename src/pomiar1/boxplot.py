import os
import numpy as np
from matplotlib import pyplot as plt

from pomiar import df_transmitters, id_mapping, calc_boxplot_data, read_pomiar_data
from .pozycje import df_positions, pomiar1_data_path

signals_path = [os.path.join(pomiar1_data_path, f"{i}_100.txt") for i in range(1, 12)]
transmitter_order = list(id_mapping.values())
dfs = read_pomiar_data(signals_path, df_positions, df_transmitters)
calc_data, transmitter_order, positions = calc_boxplot_data(transmitter_order=transmitter_order, dfs=dfs)

def plot_boxplots(calc_data, dfs, transmitter_order, positions):  
    for measurement_name, df_measurement in dfs.items():
        fig = {}
        fig[measurement_name] = plt.figure(figsize=(9, 4))
        ax = plt.gca()
    
        ax.bxp(calc_data[int(measurement_name)], positions=positions, showfliers=True)
        ax.yaxis.grid(True, linestyle='-', which='major', color='gray', alpha=1)
        ax.set_axisbelow(True)

        fig[measurement_name].patch.set_edgecolor('black')
        fig[measurement_name].patch.set_linewidth(1)

        plt.title(f'Boxplot siły sygnału dla pozycji nr. {measurement_name} (Pozycja: x = {df_measurement["x"].iloc[0] if not df_measurement.empty else "N/A"}, y = {df_measurement["y"].iloc[0] if not df_measurement.empty else "N/A"})')
        

        ax.set_xticks(positions)
        ax.set_xticklabels(transmitter_order, rotation=0, ha='center')

        total_count = 0
        for i, tx_id in enumerate(transmitter_order):
            count = calc_data[int(measurement_name)][int(tx_id)-1]['count']
            if np.isnan(count):
                count = 0
            total_count+=count
            ax.text(i + 1, -91, f'n={count}', ha='center', va='top', color='black') 

        plt.ylabel('Moc sygnału')
        plt.xlabel('ID nadajnika') 
        

        plt.text(len(transmitter_order), -96, f'Wszystkich próbek: {total_count}', ha='right')
        # plt.tight_layout()
        plt.ylim(-97, -38)
        plt.savefig(f"docs/obrazy/boxplot_rssi_pozycja_{measurement_name}.png")
    return fig

if __name__ == "__main__":
    fig = plot_boxplots(calc_data, dfs, transmitter_order, positions)
    
    plt.show()