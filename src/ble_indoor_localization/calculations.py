"""
Calculation utilities for BLE Indoor Localization project.
Includes distance calculations, regression models, and position estimation.
"""
import numpy as np
from scipy.optimize import least_squares
from sklearn.linear_model import LinearRegression



def calculate_euclidean_distance(x1, y1, x2, y2):
    """Calculate Euclidean distance between two points."""
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)


def distance_between_2_points(x1, y1, x2, y2):
    """
    Calculate Euclidean distance between two points.
    Supports both scalar and array inputs.
    
    Parameters:
    -----------
    x1, y1 : float or array-like
        Coordinates of first point(s)
    x2, y2 : float or array-like
        Coordinates of second point(s)
        
    Returns:
    --------
    float or array-like
        Distance(s) between points
    """
    return np.sqrt((x1 - x2)**2 + (y1 - y2)**2)


def create_rssi_distance_model(df_regression_data):
    """
    Create a linear regression model for RSSI to distance conversion.
    
    Parameters:
    -----------
    df_regression_data : pd.DataFrame
        DataFrame with 'distance' and 'znormalizowana moc sygnalu' columns
        
    Returns:
    --------
    LinearRegression
        Trained model
    """
    log_distance = np.log10(df_regression_data['distance'])
    X_log = log_distance.values.reshape(-1, 1)
    y = df_regression_data['znormalizowana moc sygnalu']
    
    model = LinearRegression()
    model.fit(X_log, y)
    return model


def calculate_distance_from_rssi(signal_strength, model):
    """
    Calculate distance from RSSI using a trained model.
    
    Parameters:
    -----------
    signal_strength : float or array-like
        RSSI value(s) in dBm
    model : LinearRegression
        Trained regression model
        
    Returns:
    --------
    float or array-like
        Estimated distance(s) in meters
    """
    slope = model.coef_[0]
    intercept = model.intercept_
    
    log_distance = (signal_strength - intercept) / slope
    distance = np.power(10, log_distance)
    return distance


def objective_function(position, beacons, distances_from_rssi, weights=None):
    """
    Objective function for least squares optimization.
    
    Parameters:
    -----------
    position : array-like
        [x, y] coordinates to evaluate
    beacons : array-like
        Nx2 array of beacon coordinates
    distances_from_rssi : array-like
        Distances estimated from RSSI
    weights : array-like, optional
        Weights for each beacon
        
    Returns:
    --------
    array-like
        Residuals
    """
    x, y = position
    geometrical_distances = distance_between_2_points(x, y, beacons[:, 0], beacons[:, 1])
    residuals = geometrical_distances - distances_from_rssi
    
    if weights is not None:
        residuals = weights * residuals
    
    return np.abs(residuals)


def objective_function_normalized(position, beacons, distances_from_rssi, weights=None):
    """
    Normalized objective function (divided by distance from RSSI).
    
    Parameters:
    -----------
    position : array-like
        [x, y] coordinates to evaluate
    beacons : array-like
        Nx2 array of beacon coordinates
    distances_from_rssi : array-like
        Distances estimated from RSSI
    weights : array-like, optional
        Weights for each beacon
        
    Returns:
    --------
    array-like
        Normalized residuals
    """
    x, y = position
    geometrical_distances = distance_between_2_points(x, y, beacons[:, 0], beacons[:, 1])
    residuals = geometrical_distances - distances_from_rssi
    
    if weights is not None:
        residuals = weights * residuals
    
    return residuals / distances_from_rssi


def prepare_distance_data(calc_data, df_transmitters):
    """
    Prepare beacon coordinates, distances, and weights from calculation data.
    
    Parameters:
    -----------
    calc_data : list
        List of dictionaries with beacon statistics
    df_transmitters : pd.DataFrame
        DataFrame with transmitter positions
        
    Returns:
    --------
    tuple
        (beacons_coords, rssi_distances, weights)
    """
    from .calculations import calculate_distance_from_rssi
    
    beacons_coords_list = []
    weights = []
    rssi_distances = []
    
    for j, b in enumerate(calc_data):
        if not np.isnan(b['count']):
            transmitter_row = df_transmitters[df_transmitters['Id'] == j+1].iloc[0]
            beacons_coords_list.append([transmitter_row['x'], transmitter_row['y']])
            # Note: This requires the model to be passed or stored globally
            # For now, keeping the function signature but noting this dependency
            weights.append(b['count'])
            rssi_distances.append(b['avg'])  # Will need conversion via model
    
    if not weights or np.sum(weights) == 0:
        return np.nan, np.nan, np.nan
    
    weights = np.array(weights, dtype=float)
    weights /= np.sum(weights)
    beacons_coords = np.array(beacons_coords_list)
    
    return beacons_coords, np.array(rssi_distances), weights


def least_square_estimation(beacons_coords, distances_from_rssi, weights=None, 
                           func=None, bounds=None):
    """
    Estimate position using least squares optimization.
    
    Parameters:
    -----------
    beacons_coords : array-like
        Nx2 array of beacon coordinates
    distances_from_rssi : array-like
        Distances estimated from RSSI
    weights : array-like, optional
        Weights for each beacon
    func : callable, optional
        Objective function to use (default: objective_function)
    bounds : tuple, optional
        Bounds for optimization (min_x, min_y, max_x, max_y)
        
    Returns:
    --------
    tuple
        (position, cost) where position is [x, y]
    """
    if func is None:
        func = objective_function
    
    if bounds is None:
        min_real_x_loc, min_real_y_loc = -10, -10
        max_real_x_loc, max_real_y_loc = 20.0, 27.0
    else:
        min_real_x_loc, min_real_y_loc, max_real_x_loc, max_real_y_loc = bounds
    
    random_x = np.random.uniform(min_real_x_loc, max_real_x_loc)
    random_y = np.random.uniform(min_real_y_loc, max_real_y_loc)
    
    initial_guess = np.array([random_x, random_y])
    result = least_squares(
        func,
        initial_guess,
        args=(beacons_coords, distances_from_rssi, weights)
    )
    return result.x, result.cost


def value_of_objective_function(x, y, beacons_coords, d_input, weights, func=None):
    """
    Calculate the value of the objective function at a specific point.
    
    Parameters:
    -----------
    x, y : float
        Coordinates to evaluate
    beacons_coords : array-like
        Nx2 array of beacon coordinates
    d_input : array-like
        Distances from RSSI
    weights : array-like
        Weights for each beacon
    func : callable, optional
        Objective function to use
        
    Returns:
    --------
    float
        Value of objective function
    """
    if func is None:
        func = objective_function
    
    result = 0.5 * np.sum(func(
        (x, y), 
        beacons_coords, 
        d_input,
        weights=weights
    )**2)
    return result


def generate_samples(calc_data, n_samples=10000, sigma=7):
    """
    Generate random samples from normal distributions based on measurement data.
    
    Parameters:
    -----------
    calc_data : dict
        Dictionary mapping measurement ID to list of beacon statistics
    n_samples : int
        Number of samples to generate
    sigma : float
        Standard deviation for normal distribution
        
    Returns:
    --------
    dict
        Dictionary mapping measurement ID to dict of transmitter samples
    """
    samples = {}
    np.random.seed(1)  # For reproducibility
    
    for i, d in calc_data.items():
        s = {}
        for b in d:
            if not np.isnan(b['avg']):
                AVG = b['avg']
                s[b["label"]] = np.random.normal(loc=AVG, scale=sigma, size=n_samples)
        samples[i] = s
    
    return samples


__all__ = [
    'distance_between_2_points',
    'create_rssi_distance_model',
    'calculate_distance_from_rssi',
    'objective_function',
    'objective_function_normalized',
    'prepare_distance_data',
    'least_square_estimation',
    'value_of_objective_function',
    'generate_samples'
]

# Made with Bob
