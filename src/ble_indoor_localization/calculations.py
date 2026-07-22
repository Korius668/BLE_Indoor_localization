import numpy as np
from sklearn.linear_model import LinearRegression


def distance_between_2_points(x1, y1, x2, y2):
    """Calculate Euclidean distance between two points."""
    return np.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def objective_function(position, beacons, distances_from_rssi, weights=None, distance_factor=1.0):
    x, y = position
    geometrical_distances = distance_between_2_points(x,y,beacons[:, 0],beacons[:, 1])
    residuals =0
    if weights is None:
        residuals = geometrical_distances - distances_from_rssi
    else:        
        residuals = weights*(geometrical_distances - distances_from_rssi)
    if distance_factor == 0:
        return residuals
    elif distance_factor == 1:
        return residuals/distances_from_rssi
    else:
        return residuals/(distances_from_rssi**distance_factor)

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
    return model, X_log


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
    
    
    beacons_coords_list = []
    weights = []
    rssi_distances = []
    
    for j, b in enumerate(calc_data):
        if not np.isnan(b['count']):
            transmitter_row = df_transmitters[df_transmitters['Id'] == j+1].iloc[0]
            beacons_coords_list.append([transmitter_row['x'], transmitter_row['y']])

            weights.append(b['count'])
            rssi_distances.append(b['avg'])
    if not weights or np.sum(weights) == 0:
        return np.nan, np.nan, np.nan
    
    weights = np.array(weights, dtype=float)
    weights /= np.sum(weights)
    beacons_coords = np.array(beacons_coords_list)
    
    return beacons_coords, np.array(rssi_distances), weights

def value_of_objective_function(x, y, beacons_coords,d_input,weights, func=objective_function):
    result = 0.5*np.sum(func(
                (x,y), 
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
    'value_of_objective_function',
    'generate_samples'
]