from typing import Any

import numpy as np
from scipy.optimize import least_squares

COEF = -15.15626911
INTERCEPT = -53.671972082739735


def calculate_distance_from_rssi(signal_strength):
    slope = COEF
    intercept = INTERCEPT

    log_distance = (signal_strength - intercept) / slope
    distance = np.power(10 ,log_distance)
    return distance


def distance_between_2_points(x1, y1, x2, y2):
    return np.sqrt((x1 - x2)**2 + (y1 - y2)**2)


def objective_function(position, beacons, distances_from_rssi, weights=None, distance_factor=1.0):
    x, y = position
    geometrical_distances = distance_between_2_points(x,y,beacons[:, 0],beacons[:, 1])
    residuals =0
    if weights is None:
        residuals = geometrical_distances - distances_from_rssi
    else:        
        residuals = weights*(geometrical_distances - distances_from_rssi)
    return residuals/(distances_from_rssi**distance_factor) if distance_factor != 1 else residuals/distances_from_rssi


def least_square_estimation(df,df_transmitters, bounds=None, func=objective_function, distance_factor=1.0):

    distances_from_rssi = []
    beacons_coords = []
    
    for index, row in df.iterrows():
        i = row['id nadajnika']
        rssi_value = row['znormalizowana moc sygnalu']
        distances_from_rssi.append(calculate_distance_from_rssi(rssi_value))
        beacons_coords.append((df_transmitters.loc[df_transmitters['Id'] == int(i), 'x'].values[0], df_transmitters.loc[df_transmitters['Id'] == int(i), 'y'].values[0]))
    beacons_coords= np.array(beacons_coords)
    distances_from_rssi = np.array(distances_from_rssi)
    initial_guess = beacons_coords[np.argmin(distances_from_rssi)]
    if bounds is not None:
        position = least_squares(
            func,
            initial_guess,
            args=(beacons_coords, distances_from_rssi, None, distance_factor),
            bounds=bounds,
            loss='soft_l1', 
            f_scale=1.0
        )
    else:
            position = least_squares(
            func,
            initial_guess,
            args=(beacons_coords, distances_from_rssi, None, distance_factor),
            loss='soft_l1', 
            f_scale=1.0
        )
    x, y = position.x
    return x, y


def value_of_objective_function(x, y, beacons_coords,d_input,weights, func=objective_function):
    result = 0.5*np.sum(func(
                (x,y), 
                beacons_coords, 
                d_input,
                weights=weights
            )**2)
    return result
