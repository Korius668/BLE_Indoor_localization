from matplotlib import pyplot as plt

from mapa_nadajniki import plot_map, df_transmitters
from pomiar1.boxplot import dfs

def plot_signal_strength_map(measurement_name, df_measurement, ax=None, fig=None):
    if ax is None:
        ax = plot_map(ax)
    if fig is None:
        fig =  plt.figure(figsize=(4, 6))
        # transmitter_stats = df_measurement.groupby('id nadajnika')['moc sygnalu'].agg(['mean', 'count']).reset_index()
    transmitter_stats = df_measurement.groupby('id nadajnika')['znormalizowana moc sygnalu'].agg(['mean', 'count']).reset_index()
    transmitter_stats = transmitter_stats.rename(columns={'mean': 'average_signal_strength', 'count': 'sample_count'})

    if not df_measurement.empty:
        ax.scatter(df_measurement['x'].iloc[0], df_measurement['y'].iloc[0], color='red', s=100, marker='o', label='Current Position')

    for index, tx_row in transmitter_stats.iterrows():
        tx_id = tx_row['id nadajnika']
        avg_signal = tx_row['average_signal_strength']
        sample_count = tx_row['sample_count']

        transmitter_coords_row = df_transmitters[df_transmitters['Id'] == int(tx_id)]
        if not transmitter_coords_row.empty:
            transmitter_coords = transmitter_coords_row.iloc[0]
            tx_x = transmitter_coords['x']
            tx_y = transmitter_coords['y']

            marker_size = sample_count + 50 if sample_count > 50 else 100
            ax.scatter(tx_x, tx_y, c=avg_signal, s=marker_size, cmap='viridis', edgecolors='black', linewidth=0.5, vmin=-100, vmax=-40) # Removed label here to add it via a proxy artist later
            ax.text(tx_x, tx_y, sample_count, color='black', fontsize=8, ha='center', va='center')
        else:
            print(f"Warning: Transmitter ID {tx_id} not found in df_transmitters.")
        
    if len(ax.collections) > 1:
        cbar = fig.colorbar(ax.collections[1], ax=ax)
        cbar.set_label('Average Signal Strength (dBm)')

    representative_size = transmitter_stats['sample_count'].median() * 0.5 if not transmitter_stats.empty else 50
    proxy_transmitter = ax.scatter([], [], color='green', s=representative_size, label=f'Transmitters (size ~ sample count)')

    handles, labels = ax.get_legend_handles_labels()

    if f'Transmitters (size ~ sample count)' not in labels:
        handles.append(proxy_transmitter)
        labels.append(f'Transmitters (size ~ sample count)')

    ax.legend(handles, labels, loc='upper right')

    if not df_measurement.empty:
        ax.set_title(f'Mapa z pozycją pomiaru {measurement_name} (x = {df_measurement["x"].iloc[0]}, y = {df_measurement["y"].iloc[0]})')
    else:
        ax.set_title(f'Mapa z pozycją pomiaru {measurement_name} (No data)')

    # Set the axis labels
    ax.set_xlabel('Oś X (m)')
    ax.set_ylabel('Oś Y (m)')

    # Ensure the aspect ratio is equal to avoid distortion
    ax.set_aspect('equal', adjustable='box')
    ax.set_ylim(-1, 32)
    ax.set_xlim(-2, 10)

    return ax

def plot_signal_strength_maps():
   
    fig = {}

    for measurement_name, df_measurement in dfs.items():
        fig[measurement_name] = plt.figure(figsize=(4, 6))
        ax = plot_signal_strength_map(measurement_name, df_measurement, fig=fig[measurement_name])
        plt.savefig(f"obrazy/mapa_rssi_nadajnik_{measurement_name}.png")
    return ax
    
if __name__ == "__main__":
    ax = plot_signal_strength_maps()
    
    plt.show()
    