#
# Copyright (C) 2025 European Union
#  
#  
# Licensed under the EUPL, Version 1.2 or – as soon they will be approved by the
# European Commission – subsequent versions of the EUPL (the “Licence”);
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at:
# *
# https://joinup.ec.europa.eu/collection/eupl/eupl-text-eupl-12 
# *
# Unless required by applicable law or agreed to in writing, software distributed under
# the Licence is distributed on an “AS IS” basis, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND, either express or implied. See the Licence for the specific language
# governing permissions and limitations under the Licence.
#
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_finkelstein_schafer_statistic(
    finkelstein_schafer_statistic,
    plot_path="finkelstein_schafer_statistic.png",
):
    """Plot and save ECDFs for each month."""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 6))
    # ax.plot(long_term_ecdf, label=f'Long-term Monthly')
    finkelstein_schafer_statistic.plot(label='FS scores')
    ax.set_title('Finkelstein-Schafer Statistic)')
    ax.set_xlabel('Month')
    ax.set_ylabel('Year')
    ax.legend(loc='best')
    plt.savefig(plot_path)
    plt.close(fig)


def plot_ranked_finkelstein_schafer_statistic(
    ranked_finkelstein_schafer_statistic,
    weighting_scheme: str,
    plot_path="ranked_finkelstein_schafer_statistic.png",
    to_file=True,
):
    fig, ax = plt.subplots(figsize=(12, 8))

    # Create heatmap
    c = ax.imshow(ranked_finkelstein_schafer_statistic, aspect='auto', origin='lower')

    # Add month labels as annotations on each tile
    for idx, value in np.ndenumerate(ranked_finkelstein_schafer_statistic):
        year_index, month_index = idx
        year = ranked_finkelstein_schafer_statistic.year.values[year_index]
        month = ranked_finkelstein_schafer_statistic.month.values[month_index]
        month_str = pd.to_datetime(f"{month}", format='%m').strftime('%b')  # Convert month index to month abbreviation
        ax.text(month_index, year_index, month_str, ha='center', va='center', color='white')

    # Set ticks and labels
    ax.set_xticks(range(len(ranked_finkelstein_schafer_statistic.month.values)))
    ax.set_yticks(range(len(ranked_finkelstein_schafer_statistic.year.values)))
    ax.set_xticklabels(
        [pd.to_datetime(f"{month}", format='%m').strftime('%b') for month in ranked_finkelstein_schafer_statistic.month.values]
    )
    ax.set_yticklabels(ranked_finkelstein_schafer_statistic.year.values)
    ax.set_xlabel('Month')
    ax.set_ylabel('Year')

    # Add a title and colorbar
    ax.set_title(f'Monthly Ranking of FS Scores Across Years ({weighting_scheme})')
    fig.colorbar(c, ax=ax, orientation='vertical')

    if to_file:
        plt.savefig(plot_path)
        plt.close(fig)
        return None  # Explicitly return None when saving to a file
    else:
        return fig  # Return the figure object when saving is not required
