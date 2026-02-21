from typing import Any
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

class DLSLocalizer:
    def __init__(self, startx,starty):
        self.x = startx
        self.y = starty


def delta_least_square_estimation(
        df,
        state_obj:  DLSLocalizer,
        window_step,
        max_speed=2,          # m/s – wolny krok człowieka
        scale_factor=1,
        func=objective_function):

    # 1. Estymacja LS
    x1, y1 = least_square_estimation(df, func=func)
    x0, y0 = state_obj.x, state_obj.y

    # 2. Wektor ruchu
    dx = x1 - x0
    dy = y1 - y0

    # 3. Rzeczywista długość ruchu LS
    dist = np.sqrt(dx*dx + dy*dy)

    # 4. Maksymalny możliwy ruch w tym oknie czasowym
    dt = window_step.total_seconds()
    max_dist = max_speed * dt

    # 5. Jeśli LS proponuje ruch większy niż możliwy → przytnij
    if dist > max_dist:
        scale = max_dist / dist
    else:
        scale = 1.0

    # 6. Dodatkowe wygładzanie (Twój scale_factor)
    scale *= scale_factor

    # 7. Nowa pozycja
    x = x0 + dx * scale
    y = y0 + dy * scale
    state_obj.x, state_obj.y = x,y
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
    """
    EKF 2D z prędkością (stan 4D: [x, y, vx, vy]) i pomiarem dystansów do beaconów.
    Funkcje:
      - Predykcja: model Constant Velocity z białym szumem przyspieszenia (sigma_a).
      - Update: range-only; R(d) = r0^2 + (k_dist * d)^2 (bliższym beaconom ufamy bardziej).
      - Robust: gating (odrzucanie/obniżanie wagi outlierów) + Huber weights.
      - Stabilność: zdrowe P (SPD clip), Joseph form, symetryzacja P, stabilne rozwiązywanie dla S.
      - Limit prędkości vmax + opcjonalne miękkie zwiększanie niepewności prędkości.
      - Bounds: obcinanie [x,y] do podanego prostokąta.

    Zgodność:
      - update(...) zwraca (x, y) — kompatybilne z Twoim obecnym wywołaniem.
      - predict(dt) dostępne osobno. Możesz też podać dt do update(...), a wtedy update zrobi predict.
    """

    # ---------- KONSTRUKTOR ----------

    def __init__(self,
                 initial_state=None,      # [x, y, vx, vy] lub None (start ze środka bounds)
                 bounds=bounds,             # ([xmin, xmax], [ymin, ymax]) lub None
                 vmax=3.0,                # [m/s] twardy limit prędkości
                 soft_vel_inflate=True,   # miękkie zwiększanie P przy przekroczonym vmax
                 soft_vel_inflate_pow=2.0,# potęga inflacji P (np. 2 => kwadratowo)
                 sigma_a=1.0,             # [m/s^2] szum przyspieszenia
                 r0=0.8,                  # [m] podłoga szumu pomiaru
                 k_dist=0.15,             # [m/m] narastanie niepewności z dystansem
                 P0_pos=6.0,              # początkowa wariancja pozycji (m^2)
                 P0_vel=1.0,              # początkowa wariancja prędkości ((m/s)^2)
                 use_joseph=True,         # forma Josepha (stabilniejsza numerycznie)
                 robust=None,             # ustawienia robust (gating + Huber)
                 r_min=1e-6,              # minimalna wariancja pomiaru (diag R)
                 r_max=1e6):              # maksymalna wariancja pomiaru (diag R)

        self.bounds = bounds
        self.vmax = float(vmax)
        self.soft_vel_inflate = bool(soft_vel_inflate)
        self.soft_vel_inflate_pow = float(soft_vel_inflate_pow)

        self.sigma_a = float(sigma_a)
        self.r0 = float(r0)
        self.k_dist = float(k_dist)

        self.use_joseph = bool(use_joseph)
        self.r_min = float(r_min)
        self.r_max = float(r_max)

        default_robust = {
            'use_gating': True,   # odrzucanie/obniżanie wagi outlierów
            'gate_r': 3.5,        # próg w jednostkach sigma
            'gate_inflate': 1e6,  # o ile zwiększyć wariancję outliera
            'use_huber': True,    # Huber weights
            'huber_tau': 2.0      # próg Huber'a [sigma]
        }
        if robust is None:
            robust = default_robust
        else:
            default_robust.update(robust)
            robust = default_robust
        self.robust = robust

        # Stan: [x, y, vx, vy]
        if initial_state is None:
            if bounds is None:
                raise ValueError("Dla initial_state=None podaj bounds=([xmin,xmax],[ymin,ymax]).")
            [xmin, xmax], [ymin, ymax] = bounds
            x0 = (xmin + xmax)/2.0
            y0 = (ymin + ymax)/2.0
            self.state = np.array([x0, y0, 0.0, 0.0], dtype=float)
        else:
            self.state = np.array(initial_state, dtype=float)

        # P0
        self.P = np.diag([P0_pos, P0_pos, P0_vel, P0_vel]).astype(float)

        # Bufory F i Q zależne od dt
        self._F = np.eye(4)
        self._Q = np.zeros((4,4))

    # ---------- POMOCNICZE: SANITY & STABILNOŚĆ ----------

    @staticmethod
    def _is_finite_array(a):
        return np.all(np.isfinite(a))

    @staticmethod
    def _sanitize_measurements(beacons, z, z_min=0.05, z_max=100.0):
        """
        Usuwa NaN/Inf i niepoprawne pomiary, tnie dystanse do [z_min, z_max].
        Zwraca: (beacons_s, z_s, mask_uzyte)
        """
        beacons = np.asarray(beacons, dtype=float)
        z = np.asarray(z, dtype=float)

        if beacons.ndim != 2 or beacons.shape[1] != 2:
            raise ValueError("beacons powinno mieć kształt (m,2)")

        mask = np.isfinite(z) & (z > 0.0)
        mask &= np.isfinite(beacons).all(axis=1)

        beacons_s = beacons[mask]
        z_s = z[mask]

        if len(z_s) == 0:
            return beacons_s, z_s, mask

        z_s = np.clip(z_s, z_min, z_max)
        return beacons_s, z_s, mask

    @staticmethod
    def _clip_covariance(P, min_eig=1e-9, max_val=1e9):
        """
        Gwarantuje SPD (podnosi własne do min_eig), obcina ekstremalne wartości i symetryzuje.
        """
        P = 0.5 * (P + P.T)
        P = np.clip(P, -max_val, max_val)
        eigvals, eigvecs = np.linalg.eigh(P)
        eigvals = np.maximum(eigvals, min_eig)
        P_spd = (eigvecs * eigvals) @ eigvecs.T
        return 0.5 * (P_spd + P_spd.T)

    def _safe_R_diag(self, sigma2):
        """
        Buduje diag(R) z podłogą i sufitem oraz bez NaN/Inf.
        """
        sigma2 = np.asarray(sigma2, dtype=float)
        sigma2 = np.where(np.isfinite(sigma2), sigma2, self.r_max)
        sigma2 = np.clip(sigma2, self.r_min, self.r_max)
        return np.diag(sigma2)
    
    def _build_R(self, d_for_R, per_beacon_scale=None, weights=None):

        sigma2 = np.maximum(self.r0**2 + (self.k_dist * d_for_R)**2, 1e-6)
        if per_beacon_scale is not None:
            sigma2 = sigma2 * np.asarray(per_beacon_scale, dtype=float)
        if weights is not None:
            # Wagi <1 => zwiększamy wariancję przez dzielenie wagą
            w = np.asarray(weights, dtype=float)
            w = np.clip(w, 1e-6, None)
            sigma2 = sigma2 / w
        return np.diag(sigma2)

    @staticmethod
    def _huber_weights(res_norm, tau):
        """
        Huber w jednostkach sigma: res_norm = |y_i| / sqrt(S_ii)
        Zwraca wagi w [0,1].
        """
        w = np.ones_like(res_norm)
        mask = res_norm > tau
        w[mask] = tau / res_norm[mask]
        return w

    def _invert_innovation_stable(self, S, base_eps=1e-9, tries=4):
        """
        Stabilne „odwrócenie” S przez rozwiązywanie układu:
         - sprawdza NaN/Inf,
         - symetryzuje,
         - dodaje adaptacyjny jitter,
         - najpierw Cholesky, potem solve, na końcu pinv,
         - jeśli się nie uda -> zwraca None (pominięcie update).
        """
        if not self._is_finite_array(S):
            return None

        S = 0.5 * (S + S.T)
        m = S.shape[0]
        I = np.eye(m)

        inf_norm = np.linalg.norm(S, ord=np.inf)
        if not np.isfinite(inf_norm) or inf_norm <= 0.0:
            inf_norm = 1.0
        eps = base_eps * inf_norm

        # 1) Próby z Cholesky
        for _ in range(tries):
            try:
                Sj = S + eps * I
                L = np.linalg.cholesky(Sj)
                def solve_rhs(B):
                    y = np.linalg.solve(L, B)
                    return np.linalg.solve(L.T, y)
                return solve_rhs
            except Exception:
                eps *= 10.0

        # 2) Zwykłe solve
        eps = base_eps * inf_norm
        for _ in range(tries):
            try:
                Sj = S + eps * I
                def solve_rhs(B):
                    return np.linalg.solve(Sj, B)
                # test
                _ = solve_rhs(I)
                return solve_rhs
            except Exception:
                eps *= 10.0

        # 3) Ostatecznie pinv
        try:
            Sj = S + eps * I
            Sinv = np.linalg.pinv(Sj)
            def solve_rhs(B):
                return Sinv @ B
            return solve_rhs
        except Exception:
            return None

    # ---------- MODEL RUCHU ----------

    def _set_F_Q(self, dt):
        dt = float(dt)
        self._F = np.array([
            [1, 0, dt, 0 ],
            [0, 1, 0 , dt],
            [0, 0, 1 , 0 ],
            [0, 0, 0 , 1 ],
        ], dtype=float)

        # Dyskretyzacja białego szumu przyspieszenia (2D, blokowo)
        dt2, dt3, dt4 = dt*dt, dt*dt*dt, dt*dt*dt*dt
        sa2 = self.sigma_a**2
        q11 = dt4/4 * sa2
        q12 = dt3/2 * sa2
        q22 = dt2    * sa2
        Q1D = np.array([[q11, q12],
                        [q12, q22]], dtype=float)

        self._Q = np.zeros((4,4), dtype=float)
        self._Q[np.ix_([0,2],[0,2])] = Q1D  # oś x: [pos, vel]
        self._Q[np.ix_([1,3],[1,3])] = Q1D  # oś y: [pos, vel]

    def predict(self, dt):
        """Predykcja stanu i kowariancji."""
        self._set_F_Q(dt)
        F, Q = self._F, self._Q
        self.state = F @ self.state
        self.P = F @ self.P @ F.T + Q

    # ---------- MODEL POMIARU ----------

    def _build_measurement(self, beacons):
        """
        Zwraca:
          d_pred: (m,) przewidywane dystanse
          H:      (m,4) Jacobian względem [x,y,vx,vy]
        """
        x, y = self.state[0], self.state[1]
        diffs = np.stack([x - beacons[:,0], y - beacons[:,1]], axis=1)
        d_pred = np.linalg.norm(diffs, axis=1)
        d_pred = np.maximum(d_pred, 1e-6)

        H = np.zeros((len(beacons), 4), dtype=float)
        H[:,0] = diffs[:,0] / d_pred
        H[:,1] = diffs[:,1] / d_pred
        # kolumny prędkości są zerami (pomiar nie zależy bezpośrednio od v)
        return d_pred, H

    def _apply_robust(self, y, S, base_R):
        """
        Modyfikuje R używając:
         - Gating: jeśli |r_i| > gate_r [sigma], R_ii *= gate_inflate.
         - Huber:  R_ii /= w_i, gdzie w_i = min(1, tau/|r_i|).
        """
        R_mod = base_R.copy()

        # Przybliżenie per-beacon na bazie diag(S)
        S_diag = np.clip(np.diag(S), 1e-12, None)
        res_norm = np.abs(y) / np.sqrt(S_diag)

        if self.robust.get('use_gating', False):
            gate_r = self.robust.get('gate_r', 3.5)
            gate_inflate = self.robust.get('gate_inflate', 1e6)
            if gate_inflate is None or gate_inflate <= 1.0:
                gate_inflate = 1e6
            mask_gate = res_norm > gate_r
            idxs = np.where(mask_gate)[0]
            for i in idxs:
                R_mod[i, i] *= gate_inflate

        if self.robust.get('use_huber', False):
            tau = self.robust.get('huber_tau', 2.0)
            w = self._huber_weights(res_norm, tau)
            for i in range(len(w)):
                # w < 1 => zwiększamy wariancję: R_ii /= w_i
                R_mod[i, i] = R_mod[i, i] / max(w[i], 1e-6)

        return R_mod

    # ---------- UPDATE ----------

    def update(self, beacons, z_distances,
               dt=None,                    # jeśli podasz dt, update zrobi predict(dt)
               per_beacon_scale=None,      # (m,) dodatkowa skala wariancji na beacon
               distance_for_R='pred'       # 'pred' (zalecane) lub 'meas'
               ):
        """
        beacons: (m,2) współrzędne beaconów
        z_distances: (m,) zmierzone odległości
        dt: jeśli nie None, wykona predict(dt) przed aktualizacją
        per_beacon_scale: (opcjonalnie) mnożniki wariancji per-beacon (np. z jakości RSSI)
        distance_for_R: do konstrukcji R użyj d_pred ('pred') lub z ('meas')

        Zwraca: (x, y)
        """

        # Opcjonalnie predykcja wewnątrz update
        if dt is not None:
            self.predict(dt)

        # 0) sanityzacja pomiarów
        beacons_s, z_s, _ = self._sanitize_measurements(
            beacons, z_distances, z_min=0.05, z_max=100.0
        )
        m = len(beacons_s)
        if m == 0:
            # brak użytecznych pomiarów -> pomiń update
            return float(self.state[0]), float(self.state[1])

        # 1) P w "zdrowej" formie
        self.P = self._clip_covariance(self.P, min_eig=1e-9, max_val=1e9)

        # 2) model pomiaru
        d_pred, H = self._build_measurement(beacons_s)
        if not (self._is_finite_array(d_pred) and self._is_finite_array(H)):
            return float(self.state[0]), float(self.state[1])

        # 3) innowacja
        y_innov = z_s - d_pred

        # 4) R(d) bazowe
        if distance_for_R == 'pred':
            d_for_R = d_pred
        else:
            d_for_R = np.maximum(z_s, 1e-6)

        sigma2 = self.r0**2 + (self.k_dist * d_for_R)**2
        if per_beacon_scale is not None:
            scale = np.asarray(per_beacon_scale, dtype=float)
            if len(scale) == m:
                sigma2 = sigma2 * np.clip(scale, 1e-6, self.r_max)
        R = self._safe_R_diag(sigma2)

        # 5) S (wstępne), robust modyfikacja R, S ponownie
        S = H @ self.P @ H.T + R
        R_mod = self._apply_robust(y_innov, S, R)
        S = H @ self.P @ H.T + R_mod

        # 6) Stabilne "odwrócenie" S
        solve_S = self._invert_innovation_stable(S, base_eps=1e-9, tries=4)
        if solve_S is None:
            # Pomiń update — pred-only step + lekka inflacja P
            self.P = self._clip_covariance(self.P * 1.05, min_eig=1e-9, max_val=1e9)
            return float(self.state[0]), float(self.state[1])

        # 7) Zysk K, update stanu
        K = self.P @ H.T @ solve_S(np.eye(m))
        self.state = self.state + K @ y_innov

        # 8) Bounds na pozycję
        if self.bounds is not None:
            [xmin, xmax], [ymin, ymax] = self.bounds
            self.state[0] = np.clip(self.state[0], xmin, xmax)
            self.state[1] = np.clip(self.state[1], ymin, ymax)

        # 9) Limit prędkości
        vx, vy = self.state[2], self.state[3]
        speed = np.hypot(vx, vy)
        if speed > self.vmax and speed > 1e-9:
            scale = self.vmax / speed
            self.state[2] *= scale
            self.state[3] *= scale
            if self.soft_vel_inflate:
                infl = (speed / max(self.vmax, 1e-9))**self.soft_vel_inflate_pow
                self.P[2,2] *= infl
                self.P[3,3] *= infl

        # 10) Update P (Joseph) + symetryzacja/clip
        I = np.eye(self.P.shape[0])
        if self.use_joseph:
            self.P = (I - K @ H) @ self.P @ (I - K @ H).T + K @ R_mod @ K.T
        else:
            self.P = (I - K @ H) @ self.P
        self.P = self._clip_covariance(self.P, min_eig=1e-9, max_val=1e9)

        # Zwróć tylko (x, y) — kompatybilnie z Twoim obecnym kodem
        return float(self.state[0]), float(self.state[1])

    

def ekf_estimation(df,  
                    state_obj: Any, 
                    window_step, 
                   per_beacon_scale=None,
                   distance_for_R='pred'
                   ):

    beacons_coords = []
    distances = []

    for _, row in df.iterrows():
        beacon_id = int(row["id"])
        rssi = float(row["value"])

        # Szukamy beacona w df_transmitters
        match = df_transmitters.loc[df_transmitters["Id"] == beacon_id]
        if match.empty:
            # brak tego beacona w słowniku – pomijamy
            continue


        bx = df_transmitters.loc[df_transmitters["Id"] == beacon_id, "x"].values[0]
        by = df_transmitters.loc[df_transmitters["Id"] == beacon_id, "y"].values[0]

        beacons_coords.append((bx, by))
        distances.append(calculate_distance_from_rssi(rssi))

    beacons_coords = np.array(beacons_coords, dtype=float)
    distances = np.array(distances, dtype=float)

    dt = window_step.total_seconds()
    state_obj.predict(dt)

    # Update (z debugiem opcjonalnie)
    x, y = state_obj.update(
        beacons_coords,
        distances,
        per_beacon_scale=per_beacon_scale,
        distance_for_R=distance_for_R
    )
    return x,y



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



def universal_position_estimator(df_window, method, state_obj=None, window_step=None):
    """
    method: 'LS', 'EKF', 'PF', 'MLE'
    state_obj: obiekt EKF lub PF (dla metod stanowych)
    """

    if method == "LS":
        return least_square_estimation(df_window)
    elif method == "DLS":
        return delta_least_square_estimation(df_window, state_obj=state_obj, window_step=window_step)

    elif method == "EKF":
        return ekf_estimation(df_window, state_obj, window_step)

    elif method == "PF":
        return pf_estimation(df_window, state_obj)

    elif method == "MLE":
        return mle_estimation_wrapper(df_window)

    else:
        raise ValueError(f"Unknown method: {method}")
