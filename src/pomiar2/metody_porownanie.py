import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_errors_for_methods(method_folders, labels=None, path=None):

    if labels is None:
        labels = method_folders
    if path is not None:
        method_folders = [os.path.join(path, folder) for folder in method_folders]

    plt.figure(figsize=(12, 6))

    for folder, label in zip(method_folders, labels):
        csv_path = os.path.join(folder, "pozycje.csv")

        if not os.path.exists(csv_path):
            print(f"Brak pliku: {csv_path}")
            continue

        df = pd.read_csv(csv_path)

        # obliczenie błędu euklidesowego
        df["error"] = np.sqrt(
            (df["x_estymowane"] - df["x_prawdziwe"])**2 +
            (df["y_estymowane"] - df["y_prawdziwe"])**2
        )

        # czas jako indeks (opcjonalnie)
        df["czas"] = pd.to_datetime(df["czas"])

        plt.plot(df["czas"], df["error"], label=label)

    plt.xlabel("Czas")
    plt.ylabel("Błąd [m]")
    plt.title("Porównanie błędu estymacji pozycji dla różnych metod")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("diagrams/wykresy2/metody_porownanie")



if __name__ == "__main__":
    plot_errors_for_methods(
    method_folders=["output_LS", "output_DLS", "output_D2LS"],
    labels=["Najmniejszych kwadratow", "Pochodna najmniejszych kwadratow", "Pochodna 2 st. najmniejszych kwadratow"],
    path="outputs"
)
