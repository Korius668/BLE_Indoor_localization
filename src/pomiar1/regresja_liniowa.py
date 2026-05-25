import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ble_indoor_localization import create_rssi_distance_model

from .boxplot import dfs

df_regression_data = pd.concat([df[['distance', 'znormalizowana moc sygnalu']] for df in dfs.values()])

model, X_log = create_rssi_distance_model(df_regression_data)


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
    plt.savefig("docs/obrazy/regresja_liniowa.png")
    plt.show()
    
    plt.figure(figsize=(5, 4))   
    distance_linear = np.power(10, X_log)
    plt.scatter(distance_linear, df_regression_data['znormalizowana moc sygnalu'], color='blue', label='Dane pomiarowe')

    distance_range_linear = np.linspace(distance_linear.min(), distance_linear.max(), 100)
    log_distance_range = np.log10(distance_range_linear).reshape(-1, 1)
    predicted_linear = model.predict(log_distance_range)

    plt.plot(distance_range_linear, predicted_linear, color='red', label='Regesja liniowa')

    plt.xlabel('Dystans od nadajnika (m)')
    plt.ylabel('Moc sygnału (dBm)')
    plt.title('Regresja liniowa: Moc sygnału vs dystans')

    plt.legend()
    plt.savefig("docs/obrazy/regresja_liniowa2.png")
    plt.show()