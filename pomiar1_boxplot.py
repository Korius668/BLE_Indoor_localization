import math
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from pomiar1_pozycje import df_positions
from mapa_nadajniki import df_transmitters

def calculate_euclidean_distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)


df_combined = pd.DataFrame()
pozycjePomiaru1_paths = [f"dane/19.09.2025_01/{i}_100.txt" for i in range(1, 12)]

id_mapping = {
    ' 00:00:00:00:00:01': '1',
    ' 00:00:00:00:00:02': '2',
    ' 00:00:00:00:00:03': '3',
    ' 00:00:00:00:00:04': '4',
    ' 00:00:00:00:00:05': '5',
    ' 06:00:00:00:00:00': '6',
    ' 07:00:00:00:00:00': '7',
    ' 08:00:00:00:00:00': '8',
    ' 09:00:00:00:00:00': '9',
    ' 00:00:00:00:00:10': '10',
    ' 00:00:00:00:00:11': '11',
    ' 00:00:00:00:00:12': '12'
}

def read_pomiar1_data(pozycjePomiaru1_paths= pozycjePomiaru1_paths, df_transmitters = df_transmitters):
    dfs = {}

    for i, file_path in enumerate(pozycjePomiaru1_paths):
        df_temp = pd.read_csv(file_path, header=None, names=['data', 'id nadajnika', 'wzmocnienie', 'moc sygnalu'])
        df_temp['data'] = pd.to_datetime(df_temp['data'])

        df_temp['x'] = df_positions['x'][i]
        df_temp['y'] = df_positions['y'][i]

        df_temp['id nadajnika'] = df_temp['id nadajnika'].map(id_mapping)
        df_temp['znormalizowana moc sygnalu'] = df_temp['moc sygnalu']- df_temp['wzmocnienie']

        df_temp_merged = df_temp.copy()
        df_temp_merged['id_nadajnika_int'] = df_temp_merged['id nadajnika'].astype(int)
        df_temp_merged = pd.merge(df_temp_merged, df_transmitters,
                                left_on='id_nadajnika_int', right_on='Id',
                                how='left', suffixes=('', '_tx'))

        df_temp_merged['distance'] = df_temp_merged.apply(
            lambda row: calculate_euclidean_distance(row['x'], row['y'], row['x_tx'], row['y_tx']),
            axis=1
        )


        df_temp = df_temp_merged.drop(columns=['Id', 'x_tx', 'y_tx', 'id_nadajnika_int'])

        dfs[f'{i+1}'] = df_temp
    return dfs

def calc_boxplot_data(id_mapping=id_mapping, pozycjePomiaru1_paths=pozycjePomiaru1_paths, df_positions=df_positions, df_transmitters=df_transmitters):
        
    dfs = read_pomiar1_data(pozycjePomiaru1_paths,df_transmitters)

    transmitter_order = list(id_mapping.values())
    calc_data = {}

    for measurement_name, df_measurement in dfs.items():
        
        boxplot_data = []
        counts_dict = {}
        max_moc_sygnalu = df_measurement['znormalizowana moc sygnalu'].max() if not df_measurement.empty else 0
        min_moc_sygnalu = df_measurement['znormalizowana moc sygnalu'].min() if not df_measurement.empty else 0
    # max_moc_sygnalu = df_measurement['moc sygnalu'].max() if not df_measurement.empty else 0
    # min_moc_sygnalu = df_measurement['moc sygnalu'].min() if not df_measurement.empty else 0

        for tx_id in transmitter_order:
            # subset = df_measurement[df_measurement['id nadajnika'] == tx_id]['moc sygnalu']
            subset = df_measurement[df_measurement['id nadajnika'] == tx_id]['znormalizowana moc sygnalu']
            subset_dist = df_measurement[df_measurement['id nadajnika'] == tx_id][['znormalizowana moc sygnalu','distance']]
            counts_dict[tx_id] = len(subset)

            if not subset.empty:
                q1 = subset.quantile(0.25)
                median = subset.median()
                q3 = subset.quantile(0.75)
                iqr = q3 - q1
                lower_whisker = subset[subset >= q1 - 1.5 * iqr].min()
                upper_whisker = subset[subset <= q3 + 1.5 * iqr].max()
                fliers = subset[(subset < q1 - 1.5 * iqr) | (subset > q3 + 1.5 * iqr)].tolist()
                avg = subset.mean()
                std = subset.std()
                distance = subset_dist['distance'].iloc[0] if not subset.empty else np.nan

                boxplot_data.append({
                    'avg': avg,
                    'std': std,
                    'med': median,
                    'q1': q1,
                    'q3': q3,
                    "distance": distance,
                    "count": len(subset),
                    'whislo': lower_whisker,
                    'whishi': upper_whisker,
                    'fliers': fliers,
                    'label': tx_id
                })

            else:
                boxplot_data.append({
                    'avg': np.nan,
                    'std': np.nan,
                    'med': np.nan,
                    'q1': np.nan,
                    'q3': np.nan,
                    "distance": np.nan,
                    "count": np.nan,
                    'whislo': np.nan,
                    'whishi': np.nan,
                    'fliers': [],
                    'label': tx_id
                })

        calc_data[int(measurement_name)] = boxplot_data
        positions = np.arange(1, len(transmitter_order) + 1)
    return calc_data, dfs, transmitter_order, positions, counts_dict, max_moc_sygnalu

if __name__ == "__main__":
    calc_data, dfs, transmitter_order, positions, counts_dict, max_moc_sygnalu = calc_boxplot_data()
    fig = {}
    for measurement_name, df_measurement in dfs.items():
        fig[measurement_name] = plt.figure(figsize=(12, 6))
        ax = plt.gca()
        for tx_id in transmitter_order:
        
            ax.bxp(calc_data[int(measurement_name)], positions=positions, showfliers=True)
            ax.yaxis.grid(True, linestyle='-', which='major', color='gray', alpha=1)
            ax.set_axisbelow(True)

            fig[measurement_name].patch.set_edgecolor('black')
            fig[measurement_name].patch.set_linewidth(1)

            plt.title(f'Boxplot of Signal Strength by Transmitter ID for {measurement_name} (Position: x = {df_measurement["x"].iloc[0] if not df_measurement.empty else "N/A"}, y = {df_measurement["y"].iloc[0] if not df_measurement.empty else "N/A"})')
            plt.xlabel('ID nadajnika', labelpad=30) 

            ax.set_xticks(positions)
            ax.set_xticklabels(transmitter_order, rotation=0, ha='center')

            y_text_position = ax.get_ylim()[0] - (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.08 
            for i, tx_id in enumerate(transmitter_order):
                count = counts_dict.get(tx_id, 0)
                ax.text(i + 1, y_text_position, f'n={int(count)}', ha='center', va='top', color='black') 

            plt.ylabel('Moc sygnału')

            total_count = len(df_measurement)

            plt.text(len(transmitter_order), max_moc_sygnalu + 5, f'Total samples: {total_count}', ha='right')
            plt.tight_layout()

    plt.show()
