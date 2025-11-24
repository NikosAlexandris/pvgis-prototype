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


def plot_data_distribution(distribution, variable):
    plt.figure(figsize=(10, 6))
    plt.hist(distribution, bins=100, alpha=0.75)
    plt.title(f'Distribution of {variable}')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.show()


def plot_yearly_monthly_ecdfs(
    yearly_monthly_cdfs,
    plot_path="yearly_monthly_ecdfs.png",
):
    """Plot and save ECDFs for each month in a 3x4 grid."""
    fig, axes = plt.subplots(nrows=3, ncols=4, figsize=(20, 15))  # 3x4 grid of subplots
    axes = axes.flatten()  # flatten array to simplify indexing ?

    for idx, month in enumerate(yearly_monthly_cdfs.month.values):
        ax = axes[idx]
        yearly_monthly_cdfs.sel(month=month).plot(ax=ax)  # Plot on specific subplot
        ax.set_title(f"Month {month}")
        ax.set_xlabel("Value")
        ax.set_ylabel("ECDF")

    plt.tight_layout()  # prevent overlap ?
    plt.savefig(plot_path)
    plt.close(fig)


# def plot_yearly_monthly_ecdfs_with_seaborn(
#     yearly_monthly_cdfs, plot_path="yearly_monthly_ecdfs.png"
# ):
#     """Plot and save ECDFs for each month using Seaborn's FacetGrid."""
#     # Convert Xarray DataArray to a Pandas DataFrame
#     df = yearly_monthly_cdfs.to_dataframe(name="ECDF").reset_index()
#     g = sns.FacetGrid(
#         df, col="month", col_wrap=4, sharex=True, sharey=True, height=3, aspect=1.5
#     )
#     g.map_dataframe(sns.lineplot, x="data", y="ECDF")
#     g.set_titles("Month {col_name}")
#     g.set_axis_labels("Value", "ECDF")
#     g.add_legend()
#     g.fig.tight_layout(w_pad=1)
#     plt.savefig(plot_path)
#     plt.close(g.fig)


def plot_long_term_monthly_ecdfs(
    long_term_ecdf,
    plot_path="long_term_monthly_ecdfs.png",
):
    """Plot and save ECDFs for each month."""
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 6))
    # ax.plot(long_term_ecdf, label=f'Long-term Monthly')
    long_term_ecdf.plot(label='Long-term Empirical CDF')
    ax.set_title('Long-term Monthly Empirical Cumulative Distribution Function')
    ax.set_xlabel('Value')
    ax.set_ylabel('Month')
    ax.legend(loc='best')
    plt.savefig(plot_path)
    plt.close(fig)
