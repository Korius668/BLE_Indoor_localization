import pandas as pd
import matplotlib.pyplot as plt
from mapa_nadajniki import plot_transmitters_on_map


pozycjePomiaru1_path = "dane/19.09.2025_06/pozycje.txt"
df_positions = pd.read_csv(pozycjePomiaru1_path, header="infer", names=None)


def plot_mesurement_position(ax=None, df_positions=df_positions):
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))

    first_position_label_added = False
    first_arrow_label_added = False

    for i in range(len(df_positions)):
        x_curr = df_positions.loc[i, "x"]
        y_curr = df_positions.loc[i, "y"]

        if pd.isna(x_curr) or pd.isna(y_curr):

            if (
                i > 0 and i < len(df_positions) - 1
            ):  # Ensure i-1 and i+1 exist within dataframe bounds
                x_prev = df_positions.loc[i - 1, "x"]
                y_prev = df_positions.loc[i - 1, "y"]
                x_next = df_positions.loc[i + 1, "x"]
                y_next = df_positions.loc[i + 1, "y"]

                if not (
                    pd.isna(x_prev)
                    or pd.isna(y_prev)
                    or pd.isna(x_next)
                    or pd.isna(y_next)
                ):
                    # Draw an arrow between the previous and next valid points
                    label_str = (
                        "Ścieżka dla brakujących punktów"
                        if not first_arrow_label_added
                        else None
                    )
                    ax.annotate(
                        "",
                        xy=(x_next, y_next),
                        xytext=(x_prev, y_prev),
                        arrowprops=dict(
                            facecolor="red",
                            edgecolor="red",
                            shrink=0.05,
                            width=2,
                            headwidth=8,
                            headlength=10,
                        ),
                        label=label_str,
                    )
                    first_arrow_label_added = True
                    # Add the point number (i+1) near the arrow's midpoint
                    ax.text(
                        (x_prev + x_next) / 2,
                        (y_prev + y_next) / 2,
                        str(i + 1),
                        color="black",
                        fontsize=8,
                        ha="center",
                        va="center",
                    )
        else:
            # Current point is valid, plot as usual
            label_str = "Pozycje" if not first_position_label_added else None
            ax.scatter(x_curr, y_curr, color="red", s=90, label=label_str)
            first_position_label_added = True
            ax.text(
                x_curr,
                y_curr,
                str(i + 1),
                color="black",
                fontsize=8,
                ha="center",
                va="center",
            )

    ax.set_title("Mapa z zaznaczonymi pozycjami i nadajnikami")
    ax.set_xlabel("Oś X (m)")
    ax.set_ylabel("Oś Y (m)")
    ax.set_ylim(-2, 32)

    ax.legend(loc="upper right")

    ax.set_aspect("equal", adjustable="box")

    return ax


if __name__ == "__main__":
    print("Pozycje pomiarów 1:")
    print(df_positions)
    ax = plot_transmitters_on_map()
    ax = plot_mesurement_position(ax)
    plt.savefig(f"obrazy/pozycje_pomiarowe.png")
    plt.show()
