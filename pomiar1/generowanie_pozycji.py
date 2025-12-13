import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm 

from pomiar1.boxplot import calc_data, transmitter_order, dfs



n_samples = 10000
Sigma = 7

def generate_samples(n_samples = n_samples):
    samples = {}
    for i, d in calc_data.items():
        s={}
        for b in d:
            if (not np.isnan(b['avg'])):
                AVG = b['avg']
                # STD = b['std']

                s[b["label"]] = np.random.normal(loc=AVG, scale=Sigma, size=n_samples)

        samples[i] = s
    return samples

samples = generate_samples()

if __name__ == "__main__":

    colors = plt.cm.get_cmap('tab20', len(transmitter_order))
    transmitter_colors = {tx_id: colors(i) for i, tx_id in enumerate(transmitter_order)}

    global_min_signal = -90
    global_max_signal = -20

    for measurement_name, s_data in samples.items():

        current_df_measurement = dfs[measurement_name]

        pos_x = current_df_measurement['x'].iloc[0] if not current_df_measurement.empty else "N/A"
        pos_y = current_df_measurement['y'].iloc[0] if not current_df_measurement.empty else "N/A"

        active_transmitters_in_data = s_data.keys()
        n_transmitters = len(active_transmitters_in_data)

        if n_transmitters == 0:
            print(f"No active transmitters for measurement {measurement_name}. Skipping plot.")
            continue

        fig, ax = plt.subplots(figsize=(12, 6))
        fig.suptitle(f'Histogramy siły sygnału dla pozycji {measurement_name} (x = {pos_x}, y = {pos_y})', fontsize=16)
        fig.patch.set_edgecolor('black')
        fig.patch.set_linewidth(1)

        all_vals_for_hist = []
        hist_labels = []
        hist_colors = []
        x_range = np.linspace(global_min_signal, global_max_signal, 200)
        # Iterate through the global transmitter_order to ensure consistent numbering
        for tx_id in transmitter_order:
            if tx_id in s_data: # Check if this transmitter has data for the current measurement
                vals = np.array(s_data[tx_id], dtype=float)
                vals = vals[~np.isnan(vals)]

                if len(vals) == 0:
                    continue
                # ax.hist(vals, bins=x_range, orientation='vertical', label=f'Nadajnik {tx_id}', color=transmitter_colors[tx_id], rwidth=0.9,histtype="bar")

                AVG = calc_data[measurement_name][int(tx_id)-1]['avg']
                # STD = calc_data[measurement_name][int(tx_id)-1]['std']
                STD = 7
                if STD > 0: # Only plot a curve if there's actual variance

                    pdf = norm.pdf(x_range, AVG, STD)
                    bin_width = (global_max_signal - global_min_signal)/10000
                    scaled_pdf = pdf * len(vals) * bin_width
                    ax.plot(x_range, scaled_pdf, label=f'Nadajnik {tx_id}', color=transmitter_colors[tx_id], linestyle='-', linewidth=2)
                    ax.axvline(AVG, 0,color=transmitter_colors[tx_id], linewidth=1.5,  linestyle=':', label=f'avg = {AVG:.0f}')
                elif STD == 0 and len(vals) > 0: # If std_val is 0 but there are samples, plot a vertical line for the mean
                    ax.axvline(x=AVG, color=transmitter_colors[tx_id], linestyle=':', linewidth=1.5)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels, title='Nadajnik ID / Rozkład', loc='upper right')

        ax.set_xlabel('Moc sygnału (dBm)')
        ax.set_ylabel('Liczba próbek')
        ax.set_xlim(global_min_signal, global_max_signal) # Apply global y-axis limits



        plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust layout to make space for suptitle
        plt.savefig(f"obrazy/rozrzut_wygenowanych_probek_odleglosci_pozycji_{measurement_name}.png")
    plt.show()