from scipy.optimize import minimize
import numpy as np

class MLEstimator:
    def __init__(self, df_transmitters, bounds):
        self.df_transmitters = df_transmitters
        self.bounds = bounds
        
    def _neg_log_likelihood(self, xy, beacons, rssi, A=-50, n=2.0, sigma=2.0):
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

    def _mle_estimation(self, beacons, rssi, bounds):
        initial = beacons.mean(axis=0)
        res = minimize(self._neg_log_likelihood, initial,
                    args=(beacons, rssi),
                    bounds=self.bounds)
        return res.x


    def estimation(self, df,df_transmitters, bounds):
        beacons_coords = []
        rssi_values = []

        for _, row in df.iterrows():
            beacon_id = int(row["id"])
            rssi = row["value"]

            bx = df_transmitters.loc[self.df_transmitters["Id"] == beacon_id, "x"].values[0]
            by = df_transmitters.loc[self.df_transmitters["Id"] == beacon_id, "y"].values[0]

            beacons_coords.append((bx, by))
            rssi_values.append(rssi)

        beacons_coords = np.array(beacons_coords)
        rssi_values = np.array(rssi_values)

        x, y = self._mle_estimation(beacons_coords, rssi_values, self.bounds)
        return x, y
