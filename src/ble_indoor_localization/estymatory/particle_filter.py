import numpy as np

from .least_square import calculate_distance_from_rssi


class ParticleFilter:
    def __init__(self,df_transmitters, bounds,  N=500):
        self.N = N
        [xmin, xmax], [ymin, ymax] = bounds
        self.particles = np.column_stack([
            np.random.uniform(xmin, xmax, N),
            np.random.uniform(ymin, ymax, N)
        ])
        self.weights = np.ones(N) / N
        self.df_transmitters = df_transmitters

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


    def pf_estimation(self,df, pf_instance):
        beacons_coords = []
        distances = []

        for _, row in df.iterrows():
            beacon_id = int(row["id"])
            rssi = row["value"]

            bx = self.df_transmitters.loc[self.df_transmitters["Id"] == beacon_id, "x"].values[0]
            by = self.df_transmitters.loc[self.df_transmitters["Id"] == beacon_id, "y"].values[0]

            beacons_coords.append((bx, by))
            distances.append(calculate_distance_from_rssi(rssi))

        beacons_coords = np.array(beacons_coords)
        distances = np.array(distances)

        pf_instance.predict()
        pf_instance.update(beacons_coords, distances)
        pf_instance.resample()

        x, y = self.estimate()
        return x, y
