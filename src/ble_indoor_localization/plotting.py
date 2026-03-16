"""
Plotting utilities for BLE Indoor Localization project.
Includes functions for visualizing positions, signal strength, and estimation results.
"""
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional


def plot_mesurement_position(df_positions, ax=None):
    """
    Plot measurement positions on a map.
    
    Parameters:
    -----------
    df_positions : pd.DataFrame
        DataFrame with 'x' and 'y' columns for positions
    ax : matplotlib.axes.Axes, optional
        Axes to plot on
        
    Returns:
    --------
    matplotlib.axes.Axes
        The axes with plotted positions
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))
    
    ax.scatter(df_positions['x'], df_positions['y'], color='red', s=50, label='Pozycje')
    
    for idx, row in df_positions.iterrows():
        x_val = float(row['x'])
        y_val = float(row['y'])
        idx_int = int(idx)
        ax.text(x_val, y_val, str(idx_int + 1), color='white', fontsize=8, ha='center', va='center')
    
    ax.set_title('Mapa z zaznaczonymi pozycjami i nadajnikami')
    ax.set_xlabel('Oś X (m)')
    ax.set_ylabel('Oś Y (m)')
    ax.set_ylim(-2, 32)
    ax.legend(loc='upper right')
    ax.set_aspect('equal', adjustable='box')
    
    return ax


def plot_signal_strength_map(measurement_name, df_measurement, df_transmitters, 
                             ax=None, fig=None, c_flag=True):
    """
    Plot signal strength map with transmitter positions.
    
    Parameters:
    -----------
    measurement_name : int or str
        Measurement identifier
    df_measurement : pd.DataFrame
        DataFrame with measurement data
    df_transmitters : pd.DataFrame
        DataFrame with transmitter positions
    ax : matplotlib.axes.Axes, optional
        Axes to plot on
    fig : matplotlib.figure.Figure, optional
        Figure for colorbar
    c_flag : bool
        Whether to show colorbar
        
    Returns:
    --------
    matplotlib.axes.Axes
        The axes with plotted signal strength
    """
    from .mapa_nadajniki import plot_map
    
    if ax is None:
        ax = plot_map(ax)
    if fig is None:
        fig = plt.figure(figsize=(4, 6))
    
    transmitter_stats = df_measurement.groupby('id nadajnika')['znormalizowana moc sygnalu'].agg(['mean', 'count']).reset_index()
    transmitter_stats = transmitter_stats.rename(columns={'mean': 'average_signal_strength', 'count': 'sample_count'})
    
    if not df_measurement.empty:
        ax.scatter(df_measurement['x'].iloc[0], df_measurement['y'].iloc[0], 
                  color='red', s=100, marker='o', label='Prawdziwa pozycja')
    
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
            ax.scatter(tx_x, tx_y, c=avg_signal, s=marker_size, cmap='Greens', 
                      edgecolors='black', linewidth=0.5, vmin=-100, vmax=-40)
            ax.text(tx_x, tx_y, sample_count, color='black', fontsize=8, ha='center', va='center')
        else:
            print(f"Warning: Transmitter ID {tx_id} not found in df_transmitters.")
    
    if len(ax.collections) > 1 and c_flag:
        cbar = fig.colorbar(ax.collections[1], ax=ax)
        cbar.set_label('Srednia moc sygnału (dBm)')
    
    representative_size = transmitter_stats['sample_count'].median() * 0.5 if not transmitter_stats.empty else 50
    label = 'Nadajniki (rozmiar ~ liczba probek)'
    proxy_transmitter = ax.scatter([], [], color='green', s=representative_size, label=label)
    
    handles, labels = ax.get_legend_handles_labels()
    if label not in labels:
        handles.append(proxy_transmitter)
        labels.append(label)
    
    ax.legend(handles, labels, loc='upper right')
    
    return ax


def plot_distance_from_signal(measurement_name, df_measurement, df_transmitters,
                              calculate_distance_func, ax=None, fig=None, c_flag=True):
    """
    Plot estimated distances from signal strength.
    
    Parameters:
    -----------
    measurement_name : int or str
        Measurement identifier
    df_measurement : pd.DataFrame
        DataFrame with measurement data
    df_transmitters : pd.DataFrame
        DataFrame with transmitter positions
    calculate_distance_func : callable
        Function to calculate distance from RSSI
    ax : matplotlib.axes.Axes, optional
        Axes to plot on
    fig : matplotlib.figure.Figure, optional
        Figure for plotting
    c_flag : bool
        Whether to show distance circles
        
    Returns:
    --------
    matplotlib.axes.Axes
        The axes with plotted distances
    """
    from .mapa_nadajniki import plot_map
    
    transmitter_stats = df_measurement.groupby('id nadajnika')['znormalizowana moc sygnalu'].agg(['mean', 'count']).reset_index()
    transmitter_stats = transmitter_stats.rename(columns={'mean': 'average_signal_strength', 'count': 'sample_count'})
    
    if not ax:
        ax = plot_map()
    if not fig:
        fig = plt.gcf()
    
    ax = plot_signal_strength_map(measurement_name, df_measurement, df_transmitters, 
                                  fig=fig, ax=ax, c_flag=c_flag)
    
    for index, tx_row in transmitter_stats.iterrows():
        tx_id = tx_row['id nadajnika']
        avg_signal = tx_row['average_signal_strength']
        
        transmitter_coords_row = df_transmitters[df_transmitters['Id'] == int(tx_id)]
        if not transmitter_coords_row.empty:
            transmitter_coords = transmitter_coords_row.iloc[0]
            tx_x = transmitter_coords['x']
            tx_y = transmitter_coords['y']
            
            estimated_distance = calculate_distance_func(avg_signal)
            if c_flag:
                circle = plt.Circle((tx_x, tx_y), estimated_distance, color='blue', 
                                   fill=False, linestyle='--', alpha=0.7)
                ax.add_patch(circle)
                ax.text(tx_x, tx_y + estimated_distance, f'{estimated_distance:.2f}m', 
                       color='blue', fontsize=8, ha='center', va='bottom')
        else:
            print(f"Warning: Transmitter ID {tx_id} not found in df_transmitters.")
    
    plt.Circle((0, 0), 0, color='blue', fill=False, linestyle='--', alpha=0.7, 
              label='Estimated Distance from RSSI')
    
    ax.legend(loc='upper right')
    
    if not df_measurement.empty:
        ax.set_title(f'Mapa z pozycją pomiaru {measurement_name} (x = {df_measurement["x"].iloc[0]}, y = {df_measurement["y"].iloc[0]})')
    else:
        ax.set_title(f'Mapa z pozycją pomiaru {measurement_name} (No data)')
    
    return ax


def plot_area_of_objective_function(X, Y, d, df_transmitters, value_func, 
                                    ax=None, func=None, w_flag=False):
    """
    Plot contour map of objective function values.
    
    Parameters:
    -----------
    X, Y : array-like
        Meshgrid coordinates
    d : list
        Calculation data for beacons
    df_transmitters : pd.DataFrame
        DataFrame with transmitter positions
    value_func : callable
        Function to calculate objective function value
    ax : matplotlib.axes.Axes, optional
        Axes to plot on
    func : callable, optional
        Objective function to use
    w_flag : bool
        Whether to use weights
        
    Returns:
    --------
    tuple
        (ax, result) where result contains minimum location and value
    """
    from .mapa_nadajniki import plot_map
    from .calculations import prepare_distance_data
    
    if ax is None:
        ax = plot_map(ax)
    
    beacons_coords, rssi_distances, weights = prepare_distance_data(d, df_transmitters)
    if not w_flag:
        weights = None
    
    Z = np.zeros_like(X)
    for j in range(X.shape[0]):
        for k in range(X.shape[1]):
            Z[j, k] = value_func(X[j, k], Y[j, k], beacons_coords, rssi_distances, weights, func=func)
    
    contour = plt.contourf(X, Y, Z, levels=100, alpha=0.5, cmap='viridis')
    max_idx = np.argmin(Z)
    max_coord = np.unravel_index(max_idx, Z.shape)
    max_x = X[max_coord]
    max_y = Y[max_coord]
    
    result = {"x": max_x, "y": max_y, "value": Z[max_coord]}
    ax.scatter(max_x, max_y, c='cyan', s=120, marker='X', 
              label=f'Minimum funkcji {max_x:0.2f}, {max_y:0.2f}')
    return ax, result


def plot_average_positions(avg_pos_x, avg_pos_y, ax=None):
    """
    Plot average estimated position.
    
    Parameters:
    -----------
    avg_pos_x, avg_pos_y : float
        Average position coordinates
    ax : matplotlib.axes.Axes, optional
        Axes to plot on
        
    Returns:
    --------
    matplotlib.axes.Axes
        The axes with plotted position
    """
    from .mapa_nadajniki import plot_map
    
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


def plot_estimated_positions(measurement_num, estimated_positions, ax=None, fig=None):
    """
    Plot cloud of estimated positions from Monte Carlo simulation.
    
    Parameters:
    -----------
    measurement_num : int
        Measurement number
    estimated_positions : array-like
        Nx2 array of estimated positions
    ax : matplotlib.axes.Axes, optional
        Axes to plot on
    fig : matplotlib.figure.Figure, optional
        Figure for plotting
        
    Returns:
    --------
    matplotlib.axes.Axes
        The axes with plotted positions
    """
    from .mapa_nadajniki import plot_map
    
    if estimated_positions.size == 0:
        print(f"No estimated positions to plot for measurement {measurement_num}.")
        return ax
    
    if ax is None:
        ax = plot_map(ax)
    if fig is None:
        fig = plt.gcf()
    
    points_x = estimated_positions[:, 0]
    points_y = estimated_positions[:, 1]
    
    ax.scatter(
        points_x,
        points_y,
        color='greenyellow',
        s=5,
        alpha=0.9,
        label=f'Estymowane pozycje z populacji wygenerowanej ({len(points_x)} samples)'
    )
    
    return ax


def plot_boxplots(calc_data, dfs, transmitter_order, positions):
    """
    Plot boxplots of signal strength for each measurement.
    
    Parameters:
    -----------
    calc_data : dict
        Dictionary of calculation data
    dfs : dict
        Dictionary of measurement DataFrames
    transmitter_order : list
        Ordered list of transmitter IDs
    positions : array-like
        Positions for boxplot x-axis
        
    Returns:
    --------
    dict
        Dictionary of figures
    """
    figs = {}
    for measurement_name, df_measurement in dfs.items():
        fig = plt.figure(figsize=(10, 6))
        figs[measurement_name] = fig
        ax = plt.gca()
        
        ax.bxp(calc_data[int(measurement_name)], positions=positions, showfliers=True)
        ax.yaxis.grid(True, linestyle='-', which='major', color='gray', alpha=1)
        ax.set_axisbelow(True)
        
        fig.patch.set_edgecolor('black')
        fig.patch.set_linewidth(1)
        
        plt.title(f'Boxplot siły sygnału dla nadajnika {measurement_name} (Pozycja: x = {df_measurement["x"].iloc[0] if not df_measurement.empty else "N/A"}, y = {df_measurement["y"].iloc[0] if not df_measurement.empty else "N/A"})')
        
        ax.set_xticks(positions)
        ax.set_xticklabels(transmitter_order, rotation=0, ha='center')
    
    return figs


__all__ = [
    'plot_mesurement_position',
    'plot_signal_strength_map',
    'plot_distance_from_signal',
    'plot_area_of_objective_function',
    'plot_average_positions',
    'plot_estimated_positions',
    'plot_boxplots'
]

# Made with Bob
