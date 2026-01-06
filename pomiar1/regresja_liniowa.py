import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np

from pomiar1.sila_sygnalu import dfs

df_regression_data = pd.concat([df[['distance', 'znormalizowana moc sygnalu']] for df in dfs.values()])

def model_signal_strength_vs_distance(X_log, y): 
    model = LinearRegression()
    model.fit(X_log, y)
    return model

log_distance = np.log10(df_regression_data['distance'])
X_log = log_distance.values.reshape(-1, 1)
y = df_regression_data['znormalizowana moc sygnalu']

model = model_signal_strength_vs_distance(X_log, y)

def calculate_distance_from_rssi(signal_strength, model=model):
    slope = model.coef_[0]
    intercept = model.intercept_

    log_distance = (signal_strength - intercept) / slope
    distance = np.power(10 ,log_distance)
    return distance


if __name__ == "__main__":
    
    plt.figure(figsize=(10, 6))   
    plt.scatter(X_log, df_regression_data['znormalizowana moc sygnalu'], color='blue', label='Dane pomiarowe')

    distance_range = np.linspace(X_log.min(),X_log.max(), 100).reshape(-1, 1)
    predicted_med = model.predict(distance_range)

    plt.plot(distance_range, predicted_med, color='red', label='Regesja liniowa')

    plt.xlabel('Log10 dystans od nadajnika (m)')
    plt.ylabel('Moc sygnału (dBm)')
    plt.title('Wykres regresji liniowej: Moc sygnału vs Log10 dystans')

    plt.legend()
    plt.savefig("obrazy/regresja_liniowa.png")
    plt.show()
    
    plt.figure(figsize=(10, 6))   
    distance_linear = np.power(10, X_log)
    plt.scatter(distance_linear, df_regression_data['znormalizowana moc sygnalu'], color='blue', label='Dane pomiarowe')

    distance_range_linear = np.linspace(distance_linear.min(), distance_linear.max(), 100)
    log_distance_range = np.log10(distance_range_linear).reshape(-1, 1)
    predicted_linear = model.predict(log_distance_range)

    plt.plot(distance_range_linear, predicted_linear, color='red', label='Regesja liniowa')

    plt.xlabel('Dystans od nadajnika (m)')
    plt.ylabel('Moc sygnału (dBm)')
    plt.title('Wykres regresji liniowej: Moc sygnału vs dystans')

    plt.legend()
    plt.savefig("obrazy/regresja_liniowa2.png")
    plt.show()
