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
    plt.scatter(X_log, df_regression_data['znormalizowana moc sygnalu'], color='blue', label='Data Points')

    distance_range = np.linspace(X_log.min(),X_log.max(), 100).reshape(-1, 1)
    predicted_med = model.predict(distance_range)

    plt.plot(distance_range, predicted_med, color='red', label='Linear Regression Fit')

    plt.xlabel('Log10 distance ')
    plt.ylabel('Signal Strength (dBm)')
    plt.title('Signal Strength vs. Distance with Linear Regression Fit')

    plt.legend()
    plt.savefig("obrazy/regresja_liniowa.png")
    plt.show()