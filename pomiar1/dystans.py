import matplotlib.pyplot as plt

from mapa_nadajniki import df_transmitters as df_nadajniki
from pomiar1.boxplot import dfs
from pomiar1.regresja_liniowa import calculate_distance_from_rssi
from pomiar1.sila_sygnalu import plot_signal_strength_map

if __name__ == "__main__":
    for measurement_name, df_measurement in dfs.items():
        # Calculate average signal strength and sample count for each transmitter
        # transmitter_stats = df_measurement.groupby('id nadajnika')['moc sygnalu'].agg(['mean', 'count']).reset_index()
        transmitter_stats = df_measurement.groupby('id nadajnika')['znormalizowana moc sygnalu'].agg(['mean', 'count']).reset_index()
        transmitter_stats = transmitter_stats.rename(columns={'mean': 'average_signal_strength', 'count': 'sample_count'})
        fig, ax = plt.subplots(figsize=(3, 6))
        ax = plot_signal_strength_map(measurement_name, df_measurement, fig=fig, ax=ax)
        if not df_measurement.empty:
            ax.scatter(df_measurement['x'].iloc[0], df_measurement['y'].iloc[0], color='red', s=100, marker='o', label='Current Position')

        for index, tx_row in transmitter_stats.iterrows():
            tx_id = tx_row['id nadajnika']
            avg_signal = tx_row['average_signal_strength']
            sample_count = tx_row['sample_count']

            # Find the real-world coordinates of the transmitter
            transmitter_coords_row = df_nadajniki[df_nadajniki['Id'] == int(tx_id)]
            if not transmitter_coords_row.empty:
                transmitter_coords = transmitter_coords_row.iloc[0]
                tx_x = transmitter_coords['x']
                tx_y = transmitter_coords['y']

                # Plot the transmitter on the map
                marker_size = sample_count + 50 if sample_count > 50 else 100
                estimated_distance = calculate_distance_from_rssi(avg_signal)

                # Draw a circle around the transmitter with the estimated distance as radius
                circle = plt.Circle((tx_x, tx_y), estimated_distance, color='blue', fill=False, linestyle='--', alpha=0.7)
                ax.add_patch(circle)
                ax.text(tx_x, tx_y + estimated_distance, f'{estimated_distance:.2f}m', color='blue', fontsize=8, ha='center', va='bottom')


            else:
                print(f"Warning: Transmitter ID {tx_id} not found in df_nadajniki.")



        # Update legend to include transmitters and explain marker size
        representative_size = transmitter_stats['sample_count'].median() * 0.5 if not transmitter_stats.empty else 50
        proxy_transmitter = ax.scatter([], [], color='green', s=representative_size, label=f'Transmitters (size ~ sample count)')

        # Add a proxy artist for the estimated distance circles to the legend
        proxy_circle = plt.Circle((0, 0), 0, color='blue', fill=False, linestyle='--', alpha=0.7, label='Estimated Distance from RSSI')


        handles, labels = ax.get_legend_handles_labels()

        if f'Transmitters (size ~ sample count)' not in labels:
            handles.append(proxy_transmitter)
            labels.append(f'Transmitters (size ~ sample count)')

        # Add the proxy circle to the legend handles and labels
        handles.append(proxy_circle)
        labels.append('Estimated Distance from RSSI')


        ax.legend(handles, labels, loc='upper right')


        # Set the title of the plot
        if not df_measurement.empty:
            ax.set_title(f'Mapa z pozycją pomiaru {measurement_name} (x = {df_measurement["x"].iloc[0]}, y = {df_measurement["y"].iloc[0]})')
        else:
            ax.set_title(f'Mapa z pozycją pomiaru {measurement_name} (No data)')

        # Set the axis labels
        ax.set_xlabel('Oś X (m)')
        ax.set_ylabel('Oś Y (m)')

        # Ensure the aspect ratio is equal to avoid distortion
        ax.set_aspect('equal', adjustable='box')
       


    # Display the plot
    plt.show()