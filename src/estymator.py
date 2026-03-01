from scipy.optimize import least_squares
import numpy as np
from mapa_nadajniki import df_transmitters


COEF = -15.15626911
INTERCEPT = -53.671972082739735

min_real_x_loc, min_real_y_loc = 0, 0
max_real_x_loc, max_real_y_loc = 9.0, 27.0

bounds = ([min_real_x_loc, min_real_y_loc], [max_real_x_loc, max_real_y_loc])

def calculate_distance_from_rssi(signal_strength):
    slope = COEF
    intercept = INTERCEPT

    log_distance = (signal_strength - intercept) / slope
    distance = np.power(10 ,log_distance)
    return distance


def distance_between_2_points(x1, y1, x2, y2):
    return np.sqrt((x1 - x2)**2 + (y1 - y2)**2)



def objective_function(position, beacons, distances_from_rssi, weights=None):
    x, y = position
    geometrical_distances = distance_between_2_points(x,y,beacons[:, 0],beacons[:, 1])
    residuals =0
    if weights is None:
        residuals = geometrical_distances - distances_from_rssi
    else:        
        residuals = weights*(geometrical_distances - distances_from_rssi)
    return residuals/distances_from_rssi


def least_square_estimation(df, func=objective_function):
    
    distances_from_rssi = []
    beacons_coords = []
    
    for index, row in df.iterrows():
        i = row['id']
        rssi_value = row['value']
        distances_from_rssi.append(calculate_distance_from_rssi(rssi_value))
        beacons_coords.append((df_transmitters.loc[df_transmitters['Id'] == int(i), 'x'].values[0], df_transmitters.loc[df_transmitters['Id'] == int(i), 'y'].values[0]))
    beacons_coords= np.array(beacons_coords)
    distances_from_rssi = np.array(distances_from_rssi)
    initial_guess = beacons_coords[np.argmin(distances_from_rssi)]

    position = least_squares(
        func,
        initial_guess,
        args=(beacons_coords, distances_from_rssi, None),
        bounds=bounds,
        loss='soft_l1', 
        f_scale=1.0
    )
    x, y = position.x
    return x, y


def delta_least_square_estimation(
        df,
        last_position,
        window_step,
        max_speed=3,
        scale_factor=1,
        func=objective_function):

    x1, y1 = least_square_estimation(df, func=func)
    x0, y0 = last_position
    
    dx = x1 - x0
    dy = y1 - y0

    dist = np.sqrt(dx*dx + dy*dy)

    dt = window_step.total_seconds()
    max_dist = max_speed * dt

    if dist > max_dist:
        scale = max_dist / dist
    else:
        scale = 1.0

    scale *= scale_factor

    x = x0 + dx * scale
    y = y0 + dy * scale
    return x, y


def value_of_objective_function(x, y, beacons_coords,d_input,weights, func=objective_function):
    result = 0.5*np.sum(func(
                (x,y), 
                beacons_coords, 
                d_input,
                weights=weights
            )**2)
    return result


class EKFLocalizer:
    def __init__(self, 
                 initial_position=None,
                 process_noise=0.2,
                 measurement_noise=2.0,
                 bounds=bounds):
        
        [xmin, xmax], [ymin, ymax] = bounds

        if initial_position is None:
            self.state = np.array([(xmin + xmax)/2, (ymin + ymax)/2], dtype=float)
        else:
            self.state = np.array(initial_position, dtype=float)

        self.P = np.eye(2) * 5.0
        self.Q = np.eye(2) * process_noise
        self.R = measurement_noise
        self.bounds = bounds

    def predict(self):
        self.P = self.P + self.Q

    def update(self, beacons, distances):
        px, py = self.state

        d_pred = np.sqrt((px - beacons[:,0])**2 + (py - beacons[:,1])**2)
        d_pred = np.maximum(d_pred, 1e-6)

        H = np.zeros((len(beacons), 2))
        H[:,0] = (px - beacons[:,0]) / d_pred
        H[:,1] = (py - beacons[:,1]) / d_pred

        innovation = distances - d_pred

        S = H @ self.P @ H.T + self.R * np.eye(len(beacons))
        K = self.P @ H.T @ np.linalg.inv(S)

        self.state = self.state + K @ innovation

        [xmin, xmax], [ymin, ymax] = self.bounds
        self.state[0] = np.clip(self.state[0], xmin, xmax)
        self.state[1] = np.clip(self.state[1], ymin, ymax)

        self.P = (np.eye(2) - K @ H) @ self.P

        return self.state.copy()

def ekf_estimation(df, ekf_instance):
    beacons_coords = []
    distances = []

    for _, row in df.iterrows():
        beacon_id = int(row["id"])
        rssi = row["value"]

        bx = df_transmitters.loc[df_transmitters["Id"] == beacon_id, "x"].values[0]
        by = df_transmitters.loc[df_transmitters["Id"] == beacon_id, "y"].values[0]

        beacons_coords.append((bx, by))
        distances.append(calculate_distance_from_rssi(rssi))

    beacons_coords = np.array(beacons_coords)
    distances = np.array(distances)

    ekf_instance.predict()
    x, y = ekf_instance.update(beacons_coords, distances)

    return x, y


class ParticleFilter:
    def __init__(self, N=500, bounds=bounds):
        self.N = N
        xmin, xmax, ymin, ymax = bounds
        self.particles = np.column_stack([
            np.random.uniform(xmin, xmax, N),
            np.random.uniform(ymin, ymax, N)
        ])
        self.weights = np.ones(N) / N

    def predict(self, noise=0.5):
        self.particles += np.random.normal(0, noise, size=self.particles.shape)

    def update(self, beacons, distances, sigma=1.0):
        d_pred = np.sqrt(((self.particles[:,None,:] - beacons)**2).sum(axis=2))
        error = np.abs(d_pred - distances)
        likelihood = np.exp(-np.sum(error, axis=1) / sigma)
        self.weights = likelihood + 1e-12
        self.weights /= np.sum(self.weights)

    def resample(self):
        idx = np.random.choice(self.N, self.N, p=self.weights)
        self.particles = self.particles[idx]
        self.weights = np.ones(self.N) / self.N

    def estimate(self):
        return np.average(self.particles, weights=self.weights, axis=0)


def ekf_estimation(df, ekf_instance):
    beacons_coords = []
    distances = []

    for _, row in df.iterrows():
        beacon_id = int(row["id"])
        rssi = row["value"]

        bx = df_transmitters.loc[df_transmitters["Id"] == beacon_id, "x"].values[0]
        by = df_transmitters.loc[df_transmitters["Id"] == beacon_id, "y"].values[0]

        beacons_coords.append((bx, by))
        distances.append(calculate_distance_from_rssi(rssi))

    beacons_coords = np.array(beacons_coords)
    distances = np.array(distances)

    ekf_instance.predict()
    x, y = ekf_instance.update(beacons_coords, distances)

    return x, y


class ParticleFilter:
    def __init__(self, N=500, bounds=bounds):
        self.N = N
        [xmin, xmax], [ymin, ymax] = bounds
        self.particles = np.column_stack([
            np.random.uniform(xmin, xmax, N),
            np.random.uniform(ymin, ymax, N)
        ])
        self.weights = np.ones(N) / N

    def predict(self, noise=0.5):
        self.particles += np.random.normal(0, noise, size=self.particles.shape)

    def update(self, beacons, distances, sigma=1.0):
        d_pred = np.sqrt(((self.particles[:,None,:] - beacons)**2).sum(axis=2))
        error = np.abs(d_pred - distances)
        likelihood = np.exp(-np.sum(error, axis=1) / sigma)
        self.weights = likelihood + 1e-12
        self.weights /= np.sum(self.weights)

    def resample(self):
        idx = np.random.choice(self.N, self.N, p=self.weights)
        self.particles = self.particles[idx]
        self.weights = np.ones(self.N) / self.N

    def estimate(self):
        return np.average(self.particles, weights=self.weights, axis=0)


def pf_estimation(df, pf_instance):
    beacons_coords = []
    distances = []

    for _, row in df.iterrows():
        beacon_id = int(row["id"])
        rssi = row["value"]

        bx = df_transmitters.loc[df_transmitters["Id"] == beacon_id, "x"].values[0]
        by = df_transmitters.loc[df_transmitters["Id"] == beacon_id, "y"].values[0]

        beacons_coords.append((bx, by))
        distances.append(calculate_distance_from_rssi(rssi))

    beacons_coords = np.array(beacons_coords)
    distances = np.array(distances)

    pf_instance.predict()
    pf_instance.update(beacons_coords, distances)
    pf_instance.resample()

    x, y = pf_instance.estimate()
    return x, y

from scipy.optimize import minimize

def neg_log_likelihood(xy, beacons, rssi, A=-50, n=2.0, sigma=2.0):
    x, y = xy
    d = np.sqrt((x - beacons[:,0])**2 + (y - beacons[:,1])**2)
    d = np.maximum(d, 1e-6)
    rssi_pred = A - 10*n*np.log10(d)


    # Huber loss
    diff = rssi - rssi_pred
    delta = 3.0
    huber = np.where(np.abs(diff) < delta,
                     0.5 * diff**2,
                     delta * (np.abs(diff) - 0.5 * delta))

    return np.sum(huber) / (2*sigma**2)

def mle_estimation(beacons, rssi):
    initial = beacons.mean(axis=0)
    res = minimize(neg_log_likelihood, initial,
                   args=(beacons, rssi),
                   bounds=bounds)
    return res.x


def mle_estimation_wrapper(df):
    beacons_coords = []
    rssi_values = []

    for _, row in df.iterrows():
        beacon_id = int(row["id"])
        rssi = row["value"]

        bx = df_transmitters.loc[df_transmitters["Id"] == beacon_id, "x"].values[0]
        by = df_transmitters.loc[df_transmitters["Id"] == beacon_id, "y"].values[0]

        beacons_coords.append((bx, by))
        rssi_values.append(rssi)

    beacons_coords = np.array(beacons_coords)
    rssi_values = np.array(rssi_values)

    x, y = mle_estimation(beacons_coords, rssi_values)
    return x, y



def universal_position_estimator(df_window, method, state_obj=None, window_step=None, last_position=None):
    """
    method: 'LS', 'EKF', 'PF', 'MLE'
    state_obj: obiekt EKF lub PF (dla metod stanowych)
    """

    if method == "LS":
        return least_square_estimation(df_window)
    elif method == "DLS":
        return delta_least_square_estimation(df_window, last_position=last_position, window_step=window_step)

    elif method == "EKF":
        return ekf_estimation(df_window, state_obj)

    elif method == "PF":
        return pf_estimation(df_window, state_obj)

    elif method == "MLE":
        return mle_estimation_wrapper(df_window)

    else:
        raise ValueError(f"Unknown method: {method}")
