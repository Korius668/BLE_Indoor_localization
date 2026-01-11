import matplotlib.pyplot as plt

from mapa_nadajniki import df_transmitters, plot_map
from pomiar1.boxplot import dfs
from pomiar1.regresja_liniowa import calculate_distance_from_rssi
from pomiar1.sila_sygnalu import plot_signal_strength_map


def plot_distance_from_signal(measurement_name, df_measurement, ax=None,fig = None,  c_flag=True):
    transmitter_stats = df_measurement.groupby('id nadajnika')['znormalizowana moc sygnalu'].agg(['mean', 'count']).reset_index()
    transmitter_stats = transmitter_stats.rename(columns={'mean': 'average_signal_strength', 'count': 'sample_count'})
    if not ax:
        ax = plot_map()
        
    if not fig:
        fig = plt.gcf()
    ax = plot_signal_strength_map(measurement_name, df_measurement, fig=fig, ax=ax)

    for index, tx_row in transmitter_stats.iterrows():
        tx_id = tx_row['id nadajnika']
        avg_signal = tx_row['average_signal_strength']

        transmitter_coords_row = df_transmitters[df_transmitters['Id'] == int(tx_id)]
        if not transmitter_coords_row.empty:
            transmitter_coords = transmitter_coords_row.iloc[0]
            tx_x = transmitter_coords['x']
            tx_y = transmitter_coords['y']

            estimated_distance = calculate_distance_from_rssi(avg_signal)
            if c_flag:
                circle = plt.Circle((tx_x, tx_y), estimated_distance, color='blue', fill=False, linestyle='--', alpha=0.7)
                ax.add_patch(circle)
                ax.text(tx_x, tx_y + estimated_distance, f'{estimated_distance:.2f}m', color='blue', fontsize=8, ha='center', va='bottom')
        else:
            print(f"Warning: Transmitter ID {tx_id} not found in df_transmitters.")

        plt.Circle((0, 0), 0, color='blue', fill=False, linestyle='--', alpha=0.7, label='Estimated Distance from RSSI')

    ax.legend( loc='upper right')

    if not df_measurement.empty:
        ax.set_title(f'Mapa z pozycją pomiaru {measurement_name} (x = {df_measurement["x"].iloc[0]}, y = {df_measurement["y"].iloc[0]})')
    else:
        ax.set_title(f'Mapa z pozycją pomiaru {measurement_name} (No data)')


if __name__ == "__main__":
    
    for measurement_name, df_measurement in dfs.items():
        fig, ax = plt.subplots(figsize=(8, 8))
        ax= plot_map()
        plot_distance_from_signal(measurement_name, df_measurement, ax)
        ax.set_ylim(-10, 42)
        ax.set_xlim(-20, 20)
        ax.set_xlabel('Oś X (m)')
        ax.set_ylabel('Oś Y (m)')
    plt.show()