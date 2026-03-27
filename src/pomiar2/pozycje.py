import matplotlib.pyplot as plt
import pandas as pd

from pomiar import plot_transmitters_on_map
from ble_indoor_localization import ( plot_measurement_positions)

pomiar2_data_path = "data/19.09.2025_06/"
pozycje_path = pomiar2_data_path + "pozycje.txt"
df_positions = pd.read_csv(pozycje_path, header="infer", names=None)



if __name__ == "__main__":
    print("Pozycje pomiarów 2:")
    print(df_positions)
    ax = plot_transmitters_on_map()
    ax = plot_measurement_positions(df_positions, ax=ax)
    plt.savefig(f"docs/obrazy/pozycje_pomiar2.png")
    plt.show()
