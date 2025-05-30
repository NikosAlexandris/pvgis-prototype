from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from pandas import DatetimeIndex
from rich import print

from pvgisprototype.api.series.hardcodings import check_mark
from pvgisprototype.log import logger


def get_coordinates(data_array: xr.DataArray) -> tuple:
    """
    Ugly hack for when dimensions 'longitude', 'latitude' are not spelled out!
    Use `coords` : a time series of a single pair of coordinates has only a `time` dimension!
    """
    dimensions = [
        dimension for dimension in data_array.coords if isinstance(dimension, str)
    ]
    if set(["lon", "lat"]) & set(dimensions):
        x = "lon"
        y = "lat"
    elif set(["longitude", "latitude"]) & set(dimensions):
        x = "longitude"
        y = "latitude"
    if x and y:
        logger.info(f"Dimensions  : {x}, {y}")
    return x, y


def plot_series(
    data_array,
    time: DatetimeIndex,
    default_dimension='time',
    ask_for_dimension=True,
    # slice_options=None,
    figure_name: str = "series_plot",
    save_path: Path = Path.cwd(),
    file_extension: str = "png",
    add_offset: bool = False,
    variable_name_as_suffix: bool = None,
    tufte_style: bool = None,
    width: int = 16,
    height: int = 9,
    resample_large_series: bool = False,
    data_source: str = '',
    fingerprint: bool = False,
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
    fig, ax = plt.subplots(figsize=(width, height))

    # Set grid properties
    # ax.grid(color='grey', linestyle='-', linewidth=0.5, alpha=0.5, zorder=0)

    # Plot data
    if resample_large_series:
        logger.info(
                f"Request for `--resample-large-series`",
                alt=f"Request for `--resample-large-series`"
                )
        data_array = data_array.resample(time="1D").mean()
        logger.info(
                f"Resampled data array : {data_array}",
                alt=f"Resampled data array : {data_array}"
                )
    dimensions = list(data_array.dims)
    num_dimensions = len(dimensions)

    if num_dimensions == 1:
        data_array.plot(
            ax=ax,
            alpha=0.5,
            color="black",
            linewidth=1,
            marker="o",
            markersize=3,
            zorder=1,
        )

        # Remove unwanted spines
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # Remove x-axis label
        plt.xlabel("")

        # Set title with fallback for missing 'long_name'
        supertitle = getattr(data_array, "long_name", None)
        fig.suptitle(
            supertitle,
            fontsize="xx-large",
            ha="right",
            va="top",
            x=0.9,
            y=0.95,
            # rotation=270,
        )
        coordinate_x = round(float(data_array[x]), 3)
        coordinate_y = round(float(data_array[y]), 3)
        title = f"({data_array[x].name}, {data_array[y].name}) "
        title += f"{coordinate_x}, {coordinate_y}"
        ax.set_title(
            title,
            fontsize="xx-large",
            ha="left",
            va="top",
            x=0.7,
            y=0.95,
            # rotation=270,
        )
        # supertitle += f'\n{title}'

        # Format tick labels
        ax.tick_params(axis="both", which="major", labelsize=14, direction="in")
        ax.ticklabel_format(
            axis="y",
            style="scientific",
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
            ax.spines["bottom"].set_linewidth(0.5)
            # Convert datetime to numerical representation
            minimum_timestamp = mdates.date2num(data_array.time.values[0])
            maximum_timestamp = mdates.date2num(data_array.time.values[-1])
            ax.spines["bottom"].set_bounds(minimum_timestamp, maximum_timestamp)

            # Y spine
            ax.spines["left"].set_linewidth(0.5)
            ax.spines["left"].set_bounds(minimum_value, maximum_value)

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
            # ax.set_xlabel(data_array['time'].name, fontsize=16)
            # ax.set_ylabel(data_array[y].units, fontsize=18)

            # Do not plot the 'normal' title
            fig.suptitle('')
            plt.title('')

            # Plot title on the side
            if getattr(data_array, "long_name", None):
                # supertitle = f'{data_array.long_name}'
                # supertitle += f'\n{title}'

                # Adjust the positioning slightly to the right of the plot
                right_margin_offset = 0.02  # Adjust as needed based on figure size
                text_x_position = (
                    1 + right_margin_offset
                )  # 1 corresponds to the far right of the plot
                text_background_box = dict(
                    facecolor="white", alpha=0.5, edgecolor="none", boxstyle="round,pad=0.5"
                )
                # supertitle_right = ax.text(
                #     text_x_position,  # maximum_timestamp,
                #     1,  # maximum_value,
                #     f"{data_array.long_name}",
                #     fontsize="x-large",
                #     bbox=text_background_box,
                #     va="top",
                #     ha="right",
                #     transform=ax.transAxes,  # ensure positioning is relative to axes size
                # )
                # supertitle_right_bbox = supertitle_right.get_window_extent()
                # supertitle_right_height = supertitle_right_bbox.height
                # semi-transparent background box for legibility ?
                ax.text(
                    text_x_position,  # maximum_timestamp,
                    1,  # supertitle_right_bbox.y0 - supertitle_right_height,
                    f"{title}",
                    fontsize="large",
                    bbox=text_background_box,
                    va="top",
                    ha="right",
                    transform=ax.transAxes,  # ensure positioning is relative to axes size
                )
            else:
                # plt.suptitle(f'{data_array.name}')
                # Axis labels as a title annotation.
                ax.text(
                    data_array.time[-1],
                    maximum_value,
                    f"{data_array.name}",
                    fontsize="x-large",
                )

    elif num_dimensions > 1:
        # Set title with fallback for missing 'long_name'
        supertitle = getattr(data_array, "long_name", None)
        fig.suptitle(
            supertitle,
            fontsize="xx-large",
            ha="right",
            va="top",
            x=0.9,
            y=0.95,
            # rotation=270,
        )
        default_dimension = 'time'
        print(f"Detected complex structure with dimensions: {dimensions}.")
        
        # if ask_for_dimension:
        #     print(f"Please specify a dimension to plot over (choose from: {dimensions}):")
        #     plot_dimension = input("Dimension: ")
        # else:
        #     # Use default dimension if available
        #     plot_dimension = default_dimension if default_dimension in dimensions else dimensions[0]

        # ---
        print(f"Do you want to specify a dimension other than '{default_dimension}' to plot over (choose from: {dimensions}):")
        plot_dimension = input("Dimension: ")
        # plot_dimension = default_dimension if default_dimension in dimensions else dimensions[0]

        if plot_dimension not in dimensions:
            raise ValueError(f"Invalid dimension: {plot_dimension}. Available dimensions: {dimensions}")

        if plot_dimension == default_dimension:
            data_to_plot = data_array.mean(dim=[dim for dim in dimensions if dim != plot_dimension])
            print(f"Aggregating over other dimensions. From {data_to_plot} plotting {plot_dimension} vs data.")
            data_to_plot.plot()

        # elif slice_options and plot_dimension in slice_options:
        #     slice_values = slice_options[plot_dimension]
        #     fig, axes = plt.subplots(len(slice_values), 1, figsize=(10, 5 * len(slice_values)))

        #     for i, slice_value in enumerate(slice_values):
        #         data_slice = data_array.sel({plot_dimension: slice_value})
        #         data_slice.plot(ax=axes[i], alpha=0.5, color="black", linewidth=1)
        #         axes[i].set_title(f'{plot_dimension.capitalize()}: {slice_value}')
            
        else:
            print(f"Aggregating over other dimensions for {plot_dimension}.")
            data_to_plot = data_array.mean(dim=[dim for dim in dimensions if dim != plot_dimension])
            data_to_plot.plot(alpha=0.5, color="black", linewidth=1)


    # Identity
    plt.subplots_adjust(bottom=0.18)
    identity_text = f"© PVGIS" f"  ·  Joint Research Centre, European Commission"
    if data_source:
        identity_text += f"  ·  Data source : {data_source}"
    if fingerprint:
        from pvgisprototype.core.hashing import generate_hash
        data_array_hash = generate_hash(data_array)
        identity_text += f"  ·  Fingerprint : {data_array_hash}"
    fig.text(
        0.5,
        0.02,
        identity_text,
        fontsize=12,
        color="gray",
        ha="center",
        alpha=0.5,
    )

    if figure_name:
        # Handle variable name as suffix
        if variable_name_as_suffix:
            name_suffix = (
                getattr(data_array, "long_name", data_array.name)
                .replace(" ", "_")
                .lower()
            )
            figure_name = f"{figure_name}_{name_suffix}"

        # Handle time-based naming
        if isinstance(time, (list, tuple)) and len(time) == 1:
            time = time[0]
            time_string = str(time).replace("-", "")

        else:
            start_time = data_array.time.to_series().iloc[0].strftime("%Y%m%d%H%M%S")
            end_time = data_array.time.to_series().iloc[-1].strftime("%Y%m%d%H%M%S")
            time_string = f"{start_time}_{end_time}"

        figure_name = f"{figure_name}_{time_string}"

    else:
        figure_name = "series_plot"  # the long name of the input data array ?
        if supertitle:
            figure_name += f"_{supertitle}"  # the long name of the input data array ?
        from datetime import datetime

        figure_name += f"_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    if fingerprint:
        from pvgisprototype.core.hashing import generate_hash

        figure_name += f"{data_array_hash}"

    # plt.legend(loc='upper right')

    # Save figure
    if not tufte_style:
        plt.tight_layout()

    output_filename = f"{figure_name}.{file_extension}"
    plt.savefig(
        Path(save_path, output_filename,)
        # dpi=300,
        # bbox_inches='tight'
    )

    # Report
    number_of_values = int(data_array.count())
    logger.info(
        f"{check_mark} Time series plot of {number_of_values} values over ({float(data_array[x])}, {float(data_array[y])}) exported in {output_filename}!"
    )
    print(
        f"[green]{check_mark}[/green] Time series plot of {number_of_values} values over ({float(data_array[x])}, {float(data_array[y])}) exported in '{output_filename}'"
    )

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
    _, ax = plt.subplots(figsize=(16, 9))
    data_array.plot(alpha=0.7)
    outliers.plot.line(
        "rd", ms=7, label=f"Outliers (sensitivity : {sensitivity_factor})"
    )

    with_sensitivity_factor = "_iqr_with_sensitivity_" + str(
        sensitivity_factor
    ).replace(".", "")
    figure_name = Path(str(figure_name) + with_sensitivity_factor + "_on")

    if variable_name_as_suffix:
        if data_array.long_name:
            long_name = data_array.long_name.replace(" ", "_").lower()
            figure_name = Path(str(figure_name) + "_" + long_name)
        else:
            name = data_array.name.replace(" ", "_")
            figure_name = Path(str(figure_name) + "_" + name)

    if time:
        time = str(time).replace("-", "")
        figure_name = Path(str(figure_name) + "_" + str(time))

    if data_array.long_name:
        plt.suptitle(f"{data_array.long_name}")
    else:
        plt.suptitle(f"{data_array.name}")

    # ----------------------------------------------------------- Deduplicate me
    # Ugly hack for when dimensions 'longitude', 'latitude' are not spelled out!
    # Use `coords` : a time series of a single pair of coordinates has only a `time` dimension!
    dimensions = [
        dimension for dimension in data_array.coords if isinstance(dimension, str)
    ]
    if set(["lon", "lat"]) & set(dimensions):
        x = "lon"
        y = "lat"
    elif set(["longitude", "latitude"]) & set(dimensions):
        x = "longitude"
        y = "latitude"
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
        plt.text(
            0.5,
            0.1,
            # f'Outlier equals to offset!\nScale : {scale_factor}, Offset : {add_offset}',
            f"Outlier equals to Offset : {add_offset}",
            color="indigo",
            ha="center",
            va="center",
            transform=ax.transAxes,
        )
        plt.xlabel("")
    # Look out for this! ------------------------------------------------------

    plt.legend(loc="upper right")
    file_extension = "png"
    output_filename = f"{figure_name}.{file_extension}"
    plt.savefig(f"{output_filename}")

    number_of_outliers = len(outliers_values)
    logger.info(
        f"{check_mark} Time series plot of {number_of_outliers} values over ({float(data_array[x])}, {float(data_array[y])}) exported in {output_filename}!"
    )
    print(
        f"{check_mark} Time series plot of {number_of_outliers} values over ({float(data_array[x])}, {float(data_array[y])}) exported in {output_filename}!"
    )

    return output_filename
