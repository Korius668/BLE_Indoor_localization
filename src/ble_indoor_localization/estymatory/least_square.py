import numpy as np
from scipy.optimize import least_squares
from joblib import Memory

from ..calculations import objective_function

memory = Memory("./cache", verbose=0)


COEF = -15.15626911
INTERCEPT = -53.671972082739735


def calculate_distance_from_rssi(signal_strength):
    slope = COEF
    intercept = INTERCEPT

    log_distance = (signal_strength - intercept) / slope
    distance = np.power(10 ,log_distance)
    return distance
    

@memory.cache
def preprocess_inputs(df, df_transmitters):
    distances_from_rssi = []
    beacons_coords = []
    weights = []

    time_start = df['data'].min()
    full_duration = df['data'].max() - time_start

    for index, row in df.iterrows():
        i = row['id nadajnika']
        rssi_value = row['znormalizowana moc sygnalu']

        distances_from_rssi.append(calculate_distance_from_rssi(rssi_value))

        beacons_coords.append((
            df_transmitters.loc[df_transmitters['Id'] == int(i), 'x'].values[0],
            df_transmitters.loc[df_transmitters['Id'] == int(i), 'y'].values[0]
        ))

        time = time_start - row['data']
        if full_duration.total_seconds() > 0:
            weights.append(time.total_seconds() / full_duration.total_seconds())

    beacons_coords = np.array(beacons_coords)
    distances_from_rssi = np.array(distances_from_rssi)
    weights = np.array(weights)

    initial_guess = beacons_coords[np.argmin(distances_from_rssi)]

    return beacons_coords, distances_from_rssi, weights, initial_guess


def least_square_estimation(df,df_transmitters, bounds=None, func=objective_function, distance_factor=1.0):   
    beacons_coords, distances_from_rssi, weights, initial_guess = preprocess_inputs(df, df_transmitters)
    if bounds is not None:
        position = least_squares(
            func,
            initial_guess,
            args=(beacons_coords, distances_from_rssi, weights, distance_factor),
            bounds=bounds,
            loss='soft_l1', 
            f_scale=1.0
        )
    else:
            position = least_squares(
            func,
            initial_guess,
            args=(beacons_coords, distances_from_rssi, weights, distance_factor),
            loss='soft_l1', 
            f_scale=1.0
        )
    x, y = position.x
    return x, y


