import matplotlib.pyplot as plt
import pandas as pd

from pomiar2.pozycje import plot_measurement_positions
from src.mapa_nadajniki import plot_transmitters_on_map

pozycjePomiaru1_path = "dane/19.09.2025_07/pozycje.txt"
df_positions = pd.read_csv(pozycjePomiaru1_path, header="infer", names=None)


if __name__ == "__main__":
    print("Pozycje pomiarów 1:")
    print(df_positions)
    ax = plot_transmitters_on_map()
    ax = plot_measurement_positions(ax,df_positions)
    plt.savefig(f"obrazy/pozycje_pomiar3.png")
    plt.show()
