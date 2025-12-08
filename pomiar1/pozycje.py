import pandas as pd
import matplotlib.pyplot as plt
from mapa_nadajniki import plot_transmitters_on_map



pozycjePomiaru1_path = "dane/19.09.2025_01/pozycje.txt"
df_positions = pd.read_csv(pozycjePomiaru1_path, header="infer", names=None)


def plot_mesurement_position(ax=None, df_positions=df_positions):
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))
        
    ax.scatter(df_positions['x'], df_positions['y'], color='red', s=50, label='Pozycje')

    for i, row in df_positions.iterrows():
        ax.text(row['x'], row['y'], str(i + 1), color='white', fontsize=8, ha='center', va='center') # Use index + 1 for measurement number

    ax.set_title('Mapa z zaznaczonymi pozycjami i nadajnikami')
    ax.set_xlabel('Oś X (m)')
    ax.set_ylabel('Oś Y (m)')
    ax.set_ylim(-2, 32)

    ax.legend(loc='upper right')

    ax.set_aspect('equal', adjustable='box')

    return ax

if __name__ == "__main__":
    print("Pozycje pomiarów 1:")
    print(df_positions)
    ax = plot_transmitters_on_map()
    ax = plot_mesurement_position(ax)
    plt.savefig(f"obrazy/pozycje_pomiarowe.png")
    plt.show()