import typer
from .log import logger

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
from pathlib import Path
import numpy as np
from colorama import Fore, Style
import xarray as xr
from rich import print
from pvgisprototype.api.series.hardcodings import exclamation_mark
from pvgisprototype.api.series.hardcodings import check_mark
from pvgisprototype.api.series.hardcodings import x_mark


def get_coordinates(data_array: xr.DataArray) -> tuple:
    """
    Ugly hack for when dimensions 'longitude', 'latitude' are not spelled out!
    Use `coords` : a time series of a single pair of coordinates has only a `time` dimension!
    """
    dimensions = [dimension for dimension in data_array.coords if isinstance(dimension, str)]
    if set(['lon', 'lat']) & set(dimensions):
        x = 'lon'
        y = 'lat'
    elif set(['longitude', 'latitude']) & set(dimensions):
        x = 'longitude'
        y = 'latitude'
    if (x and y):
        logger.info(f'Dimensions  : {x}, {y}')
    return x, y


def plot_series(
    data_array,
    time,
    figure_name,
    add_offset=False,
    variable_name_as_suffix=None,
    tufte_style=None,
):
    """
    Plot series over a location
    """
    if not isinstance(data_array, xr.DataArray):
        raise ValueError(
            f"The input array {data_array} is not an xarray DataArray and cannot be plotted!"
        )
    x, y = get_coordinates(data_array)

    # Prepare plot
    fig, ax = plt.subplots(figsize=(16, 9))

    # Set grid properties
    # ax.grid(color='grey', linestyle='-', linewidth=0.5, alpha=0.5, zorder=0)
    
    # Plot data
    data_array.plot(
            alpha=0.7,
            color='black',
            linewidth=1,
            marker='o',
            markersize=3,
            zorder=1
            )

    # Remove unwanted spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Remove x-axis label
    plt.xlabel('')

    # Set title
    supertitle = f'{data_array.long_name}'
    fig.suptitle(
            supertitle,
            fontsize='xx-large',
            ha='right',
            va='top',
            x=0.9,
            y=0.95,
            # rotation=270,
            )
    # title = f'{data_array.long_name} '
    coordinate_x = round(float(data_array[x]), 3)
    coordinate_y = round(float(data_array[y]), 3)
    title = f"({data_array[x].name}, {data_array[y].name}) "
    title += f"{coordinate_x}, {coordinate_y}"
    ax.set_title(title,
                 fontsize='xx-large',
                 ha='left',
                 va='top',
                 x=0.7,
                 y=0.95,
                 # rotation=270,
                 )
    # supertitle += f'\n{title}'

    # Format tick labels
    ax.tick_params(
            axis='both',
            which='major',
            labelsize=14,
            direction='in'
            )
    ax.ticklabel_format(
            axis='y',
            style='scientific',
            # scilimits=(5, 5),
            useOffset=None,
            useLocale=None,
            useMathText=None,
            )

    if tufte_style:

        # First, get minimum and maximum values
        minimum_value = float(data_array.min())
        minimum_value = np.fix(minimum_value)  # if close to 0
        maximum_value = float(data_array.max())

        # X limits
        x_limits = ax.get_xlim()
        ax.set_xlim(x_limits[0], x_limits[1])

        # X spine
        ax.spines['bottom'].set_linewidth(0.5)
        # Convert datetime to numerical representation
        minimum_timestamp = mdates.date2num(data_array.time.values[0])
        maximum_timestamp = mdates.date2num(data_array.time.values[-1])
        ax.spines['bottom'].set_bounds(minimum_timestamp, maximum_timestamp)

        # Y spine
        ax.spines['left'].set_linewidth(0.5)
        ax.spines['left'].set_bounds(minimum_value, maximum_value)

        # Only show ticks on bottom and left frame
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_left()

        # Calculate tick positions
        # -----------------------------------------------------------
        # # Set the y-ticks to align with the minimum and maximum values
        # ax.set_yticks([minimum_value, maximum_value])
        # # Add an extra tick for the maximum value
        # ax.set_yticks(ax.get_yticks().tolist() + [maximum_value])
        # -----------------------------------------------------------
        num_ticks = 5  # Adjust the number of ticks as desired
        tick_locations = np.linspace(minimum_value, maximum_value, num_ticks)

        # Align y-ticks with tick positions
        ax.set_yticks(tick_locations)

        # Set axis labels
        ax.set_xlabel(data_array[x].name, fontsize=18)
        # ax.set_ylabel(data_array[y].units, fontsize=18)

        # Do not plot the 'normal' title
        fig.suptitle(None)
        plt.title(None)

        # Plot title on the side
        if data_array.long_name:
            # supertitle = f'{data_array.long_name}'
            # supertitle += f'\n{title}'
            supertitle_right = ax.text(
                maximum_timestamp,
                maximum_value,
                f"{data_array.long_name}",
                fontsize="x-large",
                # bbox=dict(boxstyle='round', facecolor='white', edgecolor='gray'),
                va="top",
                ha="right",
            )
            supertitle_right_bbox = supertitle_right.get_window_extent()
            supertitle_right_height = supertitle_right_bbox.height
            ax.text(
                    maximum_timestamp,
                    supertitle_right_bbox.y0 - supertitle_right_height,
                    f'{title}',
                    fontsize='large',
                    # bbox=dict(boxstyle='round', facecolor='white', edgecolor='gray'),
                    va='top',
                    ha='right',
                    )
        else:
            # plt.suptitle(f'{data_array.name}')
            # Axis labels as a title annotation.
            ax.text(
                    data_array.time[-1],
                    maximum_value,
                    f'{data_array.name}',
                    fontsize='x-large'
                    )


    if variable_name_as_suffix:
        if data_array.long_name:
            long_name = data_array.long_name.replace(' ', '_').lower()
            figure_name = Path(str(figure_name) + '_' + long_name)
        else:
            name = data_array.name.replace(' ', '_')
            figure_name = Path(str(figure_name) + '_' + name)

    if len(time) == 1:
        time = str(time).replace('-', '')
        figure_name = Path(str(figure_name) + '_' + str(time))
    else:
        minimum_timestamp = data_array.time.values[0]
        figure_name = Path(str(figure_name) + '_' + str(minimum_timestamp))

    # plt.legend(loc='upper right')
    file_extension='png'
    output_filename = f'{figure_name}.{file_extension}'

    # Save figure
    if not tufte_style:
        plt.tight_layout()
    plt.savefig(
            output_filename,
            # dpi=300,
            # bbox_inches='tight'
            )

    # Report
    number_of_values = int(data_array.count())
    logger.info(Fore.GREEN + f'{check_mark} Time series plot of {number_of_values} values over ({float(data_array[x])}, {float(data_array[y])}) exported in {output_filename}!' + Style.RESET_ALL)
    print(f'[green]{check_mark}[/green] Time series plot of {number_of_values} values over ({float(data_array[x])}, {float(data_array[y])}) exported in \'{output_filename}\'')

    return output_filename


def plot_outliers(
        data_array,
        time,
        outliers,
        sensitivity_factor,
        figure_name,
        add_offset=None,
        variable_name_as_suffix=None,
        ):
    """
    Plot outliers in location series
    """
    fig, ax = plt.subplots(figsize=(16, 9))
    data_array.plot(alpha=0.7)
    outliers.plot.line('rd', ms=7, label=f'Outliers (sensitivity : {sensitivity_factor})')

    with_sensitivity_factor = '_iqr_with_sensitivity_' + str(sensitivity_factor).replace('.', '')
    figure_name = Path(str(figure_name) + with_sensitivity_factor + '_on')

    if variable_name_as_suffix:
        if data_array.long_name:
            long_name = data_array.long_name.replace(' ', '_').lower()
            figure_name = Path(str(figure_name) + '_' + long_name)
        else:
            name = data_array.name.replace(' ', '_')
            figure_name = Path(str(figure_name) + '_' + name)

    if time:
        time = str(time).replace('-', '')
        figure_name = Path(str(figure_name) + '_' + str(time))

    if data_array.long_name:
        plt.suptitle(f'{data_array.long_name}')
    else:
        plt.suptitle(f'{data_array.name}')

    # ----------------------------------------------------------- Deduplicate me
    # Ugly hack for when dimensions 'longitude', 'latitude' are not spelled out!
    # Use `coords` : a time series of a single pair of coordinates has only a `time` dimension!
    dimensions = [dimension for dimension in data_array.coords if isinstance(dimension, str)]
    if set(['lon', 'lat']) & set(dimensions):
        x = 'lon'
        y = 'lat'
    elif set(['longitude', 'latitude']) & set(dimensions):
        x = 'longitude'
        y = 'latitude'
    # Deduplicate me -----------------------------------------------------------

    title = f"({data_array[x].name}, {data_array[y].name}) {data_array[x].values}, {data_array[y].values}"
    plt.title(title)

    # Special case : ----------------------------------------------------------
    # Scaling a map is done via :
    #    `output = input * scale + offset`.
    # This operation might be technically successful.
    # Hoever, if the input map is empty (say something went wrong in reading it),
    # the output map will present pixel values equal to the offset!
    # In pseudo-code:
    #     `if input == 0 : output = offset`
    outliers_values = np.unique(outliers.values[~np.isnan(outliers.values)])
    if add_offset in outliers_values:
        plt.text(0.5, 0.1,
                # f'Outlier equals to offset!\nScale : {scale_factor}, Offset : {add_offset}',
                f'Outlier equals to Offset : {add_offset}',
                color='indigo',
                ha='center', va='center',
                transform=ax.transAxes,
                )
        plt.xlabel('')
    # Look out for this! ------------------------------------------------------

    plt.legend(loc='upper right')
    file_extension='png'
    output_filename = f'{figure_name}.{file_extension}'
    plt.savefig(f'{output_filename}')

    number_of_outliers = len(outliers_values)
    logger.info(Fore.GREEN + f'{check_mark} Time series plot of {number_of_outliers} values over ({float(data_array[x])}, {float(data_array[y])}) exported in {output_filename}!' + Style.RESET_ALL)
    typer.echo(Fore.GREEN + check_mark + f' Time series plot of {number_of_outliers} value sover ({float(data_array[x])}, {float(data_array[y])}) exported in \'{output_filename}\'')
    return output_filename
