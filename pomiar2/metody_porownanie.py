import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_errors_for_methods(method_folders, labels=None):
    """
    method_folders: lista folderów np. ["output_LS2", "output_EKF", "output_PF"]
    labels: opcjonalne nazwy metod do legendy
    """

    if labels is None:
        labels = method_folders

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
    plt.show()


if __name__ == "__main__":
    plot_errors_for_methods(
    ["output_LS2", "output_DLS2", "output_EKF2", "output_PF2", "output_MLE2"],
    labels=["Najmniejszych kwadratow", "Roznica najmniejszych kwadratow", "Rozszerzony filtr Kalmana", "Sekwencyjna metoda Monte Carlo", "Metoda Największej Wiarygodności"]
)
