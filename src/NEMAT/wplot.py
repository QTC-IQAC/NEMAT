import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter1d
from scipy.stats import norm

def read_integ_data(file):
    """Reads integration data from a file and returns a DataFrame."""
    data = pd.read_csv(file, delimiter="\\s+", header=None,
                       names=['file', 'val'])
    return data

def BAR_DG(file):
    with open(file, 'r') as f:
        lines = f.readlines()

        dG = None
        dG_err = None

        for line in lines:
            if 'BAR: dG =' in line:
                dG = float(line.split()[-2])
            if 'BAR: Std Err (bootstrap)' in line:
                dG_err = float(line.split()[-2])

                dec_pos = len(str(dG_err).split('.')[-1])
                

            if dG is not None and dG_err is not None:
                break
                
        return dG, dG_err, dec_pos


def plot_work(color_f="#008080", color_b="#ff8559", results='results.txt', file_f='integ0.dat', file_b='integ1.dat', units='kJ/mol', output='wplot.png'):
    """Plots work values from forward and backward integration data."""
    df_f = read_integ_data(file_f)
    df_b = read_integ_data(file_b)
    dG, dG_err, dec_pos = BAR_DG(results)

    x = np.arange(len(df_f))

    if units == 'kcal/mol':
        df_f['val'] *= 0.239006
        df_b['val'] *= 0.239006

    # Plot forward integration data
    plt.figure()
    fig, axs = plt.subplots(1,2, figsize=(20,11))

    smooth_window = len(df_f) // 50

    val_smooth_f = gaussian_filter1d(df_f['val'], sigma=smooth_window)
    val_smooth_b = gaussian_filter1d(df_b['val'], sigma=smooth_window)

    axs[0].plot(x, df_f['val'], color=color_f, alpha=0.3)
    axs[0].plot(x, df_b['val'], color=color_b, alpha=0.3)
    axs[0].plot(x, val_smooth_f, color=color_f,label=r'Forward (0$\rightarrow$1)', linewidth=3)
    axs[0].plot(x, val_smooth_b, color=color_b, label=r'Backward (1$\rightarrow$0)', linewidth=3)

    axs[0].legend(fontsize=20)
    axs[0].set_xlabel('Frame', fontsize=20)
    axs[0].set_ylabel(f'W ({units})', fontsize=20)
    axs[0].tick_params(labelsize=20)
    axs[0].set_xlim(0, len(df_f))
    axs[0].grid(True)


    mu_f, std_f = norm.fit(df_f['val'])   # mean and standard deviation of forward work
    mu_b, std_b = norm.fit(df_b['val']) # mean and standard deviation of backward work


    axs[1].hist(df_f['val'], bins=20, density=True, alpha=0.6, color=color_f, edgecolor='black', orientation='horizontal')
    axs[1].hist(df_b['val'], bins=20, density=True, alpha=0.6, color=color_b, edgecolor='black', orientation='horizontal')

    xp = np.linspace(min(df_f['val'].min(), df_b['val'].min()), max(df_f['val'].max(), df_b['val'].max()), len(df_f))

    p_f = norm.pdf(xp, mu_f, std_f)
    p_b = norm.pdf(xp, mu_b, std_b)

    axs[1].plot(p_f, xp, linewidth=2, color=color_f, linestyle='--')
    axs[1].plot(p_b, xp, linewidth=2, color=color_b, linestyle='--')

    axs[1].hlines(dG, 0, max(p_f.max(), p_b.max()), linewidth=2, color='black', linestyle='--', label=f'ΔG = {dG:.{dec_pos}f} ± {dG_err:.{dec_pos}f} {units}')

    axs[1].set_xticks([])
    axs[1].set_yticks([])

    axs[1].legend(fontsize=20)
    for spine in axs[0].spines.values():
        spine.set_linewidth(2)     
    for spine in axs[1].spines.values():
        spine.set_linewidth(2)     
        
    fig.tight_layout()
    fig.subplots_adjust(wspace=0)
    fig.savefig(output)



if __name__ == "__main__":

    # Plot the work values
    plot_work()