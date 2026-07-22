import numpy as np
import pandas as pd
from .mapa_nadajniki import df_transmitters

from ble_indoor_localization.calculations import distance_between_2_points

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

transmitter_order = list(id_mapping.values())

def read_pomiar_data(file_paths, df_positions, df_transmitters=df_transmitters):
    """
    Read measurement data from multiple files and process it.
    
    Parameters:
    -----------
    file_paths : list
        List of file paths to measurement data
    df_positions : pd.DataFrame
        DataFrame containing position information
    df_transmitters : pd.DataFrame
        DataFrame containing transmitter information
        
    Returns:
    --------
    dict
        Dictionary mapping measurement number to processed DataFrame
    """
    dfs = {}

    for i, file_path in enumerate(file_paths):
        df_temp = pd.read_csv(
            file_path, 
            header=None, 
            names=['data', 'id nadajnika', 'wzmocnienie', 'moc sygnalu']
        )
        df_temp['data'] = pd.to_datetime(df_temp['data'])

        df_temp['x'] = df_positions['x'][i]
        df_temp['y'] = df_positions['y'][i]

        df_temp['id nadajnika'] = df_temp['id nadajnika'].map(id_mapping)
        df_temp['znormalizowana moc sygnalu'] = df_temp['moc sygnalu'] - df_temp['wzmocnienie']

        df_temp_merged = df_temp.copy()
        df_temp_merged['id_nadajnika_int'] = df_temp_merged['id nadajnika'].astype(int)
        df_temp_merged = pd.merge(
            df_temp_merged, 
            df_transmitters,
            left_on='id_nadajnika_int', 
            right_on='Id',
            how='left', 
            suffixes=('', '_tx')
        )

        df_temp_merged['distance'] = df_temp_merged.apply(
            lambda row: distance_between_2_points(
                row['x'], row['y'], row['x_tx'], row['y_tx']
            ),
            axis=1
        )

        df_temp = df_temp_merged.drop(columns=['Id', 'x_tx', 'y_tx', 'id_nadajnika_int'])

        dfs[i+1] = df_temp
    return dfs


def calc_boxplot_data(dfs, transmitter_order=transmitter_order):
    """
    Calculate boxplot statistics for each measurement and transmitter.
    
    Parameters:
    -----------
    dfs : dict
        Dictionary of measurement DataFrames
    transmitter_order : list
        Ordered list of transmitter IDs
        
    Returns:
    --------
    tuple
        (calc_data, transmitter_order, positions)
        - calc_data: dict mapping measurement to list of statistics
        - transmitter_order: list of transmitter IDs
        - positions: array of positions for plotting
    """
    calc_data = {}

    for measurement_name, df_measurement in dfs.items():
        boxplot_data = []

        for tx_id in transmitter_order:
            subset = df_measurement[df_measurement['id nadajnika'] == tx_id]['znormalizowana moc sygnalu']
            subset_dist = df_measurement[df_measurement['id nadajnika'] == tx_id][['znormalizowana moc sygnalu','distance']]

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

        calc_data[measurement_name] = boxplot_data
    
    positions = np.arange(1, len(transmitter_order) + 1)
    return calc_data, transmitter_order, positions


__all__ = [
    'read_pomiar_data',
    'calc_boxplot_data'
]

