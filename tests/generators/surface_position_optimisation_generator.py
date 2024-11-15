import datetime
import math
import random
import warnings
from concurrent.futures import ProcessPoolExecutor
from zoneinfo import ZoneInfo

import typer
from tqdm import tqdm

from pvgisprototype import (
    Latitude,
    LinkeTurbidityFactor,
    Longitude,
    SpectralFactorSeries,
    SurfaceOrientation,
    SurfaceTilt,
    TemperatureSeries,
    WindSpeedSeries,
)
from pvgisprototype.api.datetime.datetimeindex import generate_datetime_series
from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel
from pvgisprototype.api.surface.optimize_angles import optimize_angles
from pvgisprototype.api.surface.parameter_models import (
    SurfacePositionOptimizerMethod,
    SurfacePositionOptimizerMethodSHGOSamplingMethod,
    SurfacePositionOptimizerMode,
)
from pvgisprototype.core.hashing import generate_hash

warnings.filterwarnings("ignore")

app = typer.Typer(
    help="Optimize angles for photovoltaic modules with specified mode (tilt, orientation, or tilt_and_orientation)."
)


def write_header_cases(file_name: str):
    """Write the header information to the output file based on the selected mode."""
    header = (
        "from zoneinfo import ZoneInfo\n"
        "from pvgisprototype.api.datetime.datetimeindex import generate_datetime_series\n"
        "from pvgisprototype.api.power.photovoltaic_module import PhotovoltaicModuleModel\n"
        "from pvgisprototype import (\n"
        "   Longitude,\n"
        "   Latitude,\n"
        "   TemperatureSeries,\n"
        "   WindSpeedSeries,\n"
        "   LinkeTurbidityFactor,\n"
        "   SpectralFactorSeries,\n"
        "   SurfaceOrientation,\n"
        "   SurfaceTilt,\n"
        ")\n"
        "from pvgisprototype.api.surface.parameter_models import (\n"
        "   SurfacePositionOptimizerMethod,\n"
        "   SurfacePositionOptimizerMode\n"
        ")\n"        
    )

    with open(file_name, "w") as fp:
        fp.write(header)


def generate_date_cases(mode: str):
    """Generates cases with various time ranges and frequencies."""
    start_time = []
    end_time = []
    frequency = []

    # Case 1: Generate cases for 10, 5, 1 years with hourly frequency
    base_start = datetime.datetime(2010, 1, 1)
    time_deltas = [10, 5, 1] if mode != "tilt_and_orientation" else [1]

    for years in time_deltas:
        start_time.append(base_start.strftime("%Y-%m-%d %H:%M:%S"))
        end_time.append(
            (base_start + datetime.timedelta(days=years * 365)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
        frequency.append("h")

    if mode != "tilt_and_orientation":
        # Case 2: Generate cases for each month of a random year with hourly and per 10 minutes frequency
        random_year = random.choice(range(2000, 2023))
        for month in range(1, 13):
            start_date = datetime.datetime(random_year, month, 1)
            end_date = start_date + datetime.timedelta(
                days=30
            )  # Assuming 30 days for simplicity

            start_time.extend([start_date.strftime("%Y-%m-%d %H:%M:%S")] * 2)
            end_time.extend([end_date.strftime("%Y-%m-%d %H:%M:%S")] * 2)
            frequency.extend(["h", "10min"])
    else:
        random_year = random.choice(range(2000, 2023))
        start_date = datetime.datetime(random_year, 6, 1)
        end_date = start_date + datetime.timedelta(
            days=30
        )  # Assuming 30 days for simplicity

        start_time.extend([start_date.strftime("%Y-%m-%d %H:%M:%S")] * 2)
        end_time.extend([end_date.strftime("%Y-%m-%d %H:%M:%S")] * 2)
        frequency.extend(["h", "10min"])

    if mode != "tilt_and_orientation":
        # Case 3: Generate an extra case for 1 year with hourly frequency and random start date
        random_year_start = datetime.datetime(
            random.choice(range(2000, 2023)), random.choice(range(1, 13)), 1
        )
        start_time.append(random_year_start.strftime("%Y-%m-%d %H:%M:%S"))
        end_time.append(
            (random_year_start + datetime.timedelta(days=365)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
        frequency.append("h")

    return start_time, end_time, frequency


def _generate_date_cases_sample(mode: str):
    """Generates cases with various time ranges and frequencies."""
    start_time = []
    end_time = []
    frequency = []

    # Case 1: Generate cases for 10, 5, 1 years with hourly frequency
    base_start = datetime.datetime(2010, 1, 1)
    time_deltas = [10, 5, 1] if mode != "tilt_and_orientation" else [1]

    for years in time_deltas:
        start_time.append(base_start.strftime("%Y-%m-%d %H:%M:%S"))
        end_time.append(
            (base_start + datetime.timedelta(days=years * 365)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
        frequency.append("h")

    return start_time, end_time, frequency


def optimized_case(params, mode):
    """Perform the optimization for given parameters in a specified mode (Tilt, Orientation, or Tilt_and_Orientation)."""
    (
        index,
        latitude_value,
        number_of_sampling_points,
        precision_goal,
        sampling_method_shgo,
        start_time,
        end_time,
        frequency,
    ) = params
    longitude_value = random.uniform(-180, 180)
    elevation_value = random.randrange(0, 100)
    temperature_value = random.uniform(0, 35)
    wind_value = random.uniform(0, 15)

    if mode == "tilt":
        surface_tilt = random.uniform(0, SurfaceTilt().max_radians)
        surface_orientation = math.radians(180)
    elif mode == "orientation":
        surface_tilt = math.radians(45)
        surface_orientation = random.uniform(0, SurfaceOrientation().max_radians)
    else:  # tilt_and_orientation
        surface_tilt = math.radians(45)
        surface_orientation = math.radians(180)

    input_data = [
        latitude_value,
        longitude_value,
        sampling_method_shgo,
        number_of_sampling_points,
        precision_goal,
        start_time,
        end_time,
        frequency,
    ]
    input_hash = generate_hash(input_data)

    test_id = (
        f"Index: {index}, Hash: {input_hash}, Input: "
        f"(Latitude: {latitude_value}, Longitude: {longitude_value}, "
        f"Method: {sampling_method_shgo}, Sampling points: {number_of_sampling_points}, "
        f"Precision goal: {precision_goal}, Start: {start_time}, End: {end_time}, Frequency: {frequency}),"
    )

    result = optimize_angles(
        longitude=Longitude(value=longitude_value, unit="degrees"),
        latitude=Latitude(value=latitude_value, unit="degrees"),
        elevation=elevation_value,
        timestamps=generate_datetime_series(
            start_time=str(start_time), end_time=str(end_time), frequency=frequency
        ),
        timezone=ZoneInfo("UTC"),
        spectral_factor_series=SpectralFactorSeries(value=1),
        photovoltaic_module=PhotovoltaicModuleModel.CIS_FREE_STANDING,
        temperature_series=TemperatureSeries(value=temperature_value),
        wind_speed_series=WindSpeedSeries(value=wind_value),
        linke_turbidity_factor_series=LinkeTurbidityFactor(value=1),
        method=SurfacePositionOptimizerMethod.brute,
        mode=(
            SurfacePositionOptimizerMode.Tilt
            if mode == "tilt"
            else (
                SurfacePositionOptimizerMode.Orientation
                if mode == "orientation"
                else SurfacePositionOptimizerMode.Tilt_and_Orientation
            )
        ),
        surface_tilt=surface_tilt,
        surface_orientation=surface_orientation,
        workers=7,
        precision_goal=precision_goal,
    )

    if mode == "tilt":
        write_mode = SurfacePositionOptimizerMode.Tilt
    elif mode == "orientation":
        write_mode = SurfacePositionOptimizerMode.Orientation
    else:
        write_mode = SurfacePositionOptimizerMode.Tilt_and_Orientation

    case = (
        "[",
        f"{{'longitude': Longitude(value={longitude_value}, unit='degrees'),\n"
        f"'latitude': Latitude(value={latitude_value}, unit='degrees'),\n"
        f"'elevation': {elevation_value},\n"
        f"'timestamps': generate_datetime_series(start_time='{start_time}', end_time='{end_time}', frequency='{frequency}'),\n"
        f"'timezone': ZoneInfo('UTC'),\n"
        f"'spectral_factor_series': SpectralFactorSeries(value=1),\n"
        f"'photovoltaic_module': PhotovoltaicModuleModel.CIS_FREE_STANDING,\n"
        f"'temperature_series': TemperatureSeries(value={temperature_value}),\n"
        f"'wind_speed_series': WindSpeedSeries(value={wind_value}),\n"
        f"'linke_turbidity_factor_series': LinkeTurbidityFactor(value=1),\n"
        f"'method': SurfacePositionOptimizerMethod.shgo, \n"
        f"'mode': {write_mode}, \n"
        f"'surface_tilt': {surface_tilt},\n"
        f"'surface_orientation': {surface_orientation},\n"
        f"'sampling_method_shgo': '{sampling_method_shgo.value}',\n"
        f"'number_of_sampling_points': {number_of_sampling_points},\n"
        f"'precision_goal': {precision_goal},\n"
        "},\n",
        f"{str(result)},\n",
        f"{{'index': {index}, 'hash': '{input_hash}'}},\n",
        "],\n",
    )

    return "".join(case), test_id


def execute_optimization(params):
    """Helper function to execute the optimization case."""
    case_params, mode = params
    return optimized_case(case_params, mode)


def write_cases_optimizer(mode: str, workers: int = 2):
    """Runs optimizations and writes the cases for the specified mode to a file."""
    file_name = f"../api/surface/cases/cases_optimizer_{mode}.py"

    write_header_cases(file_name)

    cases = "cases = [\n"
    test_ids = []
    index = 1
    parameters = []

    start_time, end_time, frequency = generate_date_cases(mode)

    for start, end, freq in zip(start_time, end_time, frequency):
        for latitude_value in range(-90, 100, 10): # Take -90 till 90 degrees values. 100 is used since range values are in [-90, 100)
            for sampling_points in [15, 50, 100]:
                for precision_goal in [1e-1, 1e-2]:
                    for sampling_method in [
                        SurfacePositionOptimizerMethodSHGOSamplingMethod.sobol,
                        SurfacePositionOptimizerMethodSHGOSamplingMethod.halton,
                        SurfacePositionOptimizerMethodSHGOSamplingMethod.simplicial,
                    ]:
                        parameters.append(
                            (
                                (
                                    index,
                                    latitude_value,
                                    sampling_points,
                                    precision_goal,
                                    sampling_method,
                                    start,
                                    end,
                                    freq,
                                ),
                                mode,
                            )
                        )
                        index += 1

    with ProcessPoolExecutor(max_workers=workers) as executor:
        print(f"Generating cases for mode '{mode}':")
        results = list(
            tqdm(executor.map(execute_optimization, parameters), total=len(parameters))
        )

    with open(file_name, "a") as fp:
        fp.write(cases)
        for case, test_id in results:
            fp.write(case)
            test_ids.append(test_id)

        fp.write("]\n")

        fp.write("\n\n# Test IDs\n")
        fp.write("cases_ids = [\n")
        for test_id in test_ids:
            fp.write(f"    '{test_id}',\n")
        fp.write("]\n")


@app.command()
def optimize(
    mode: str = typer.Option(
        ..., help="Optimization mode: 'tilt', 'orientation', or 'tilt_and_orientation'."
    ),
    workers: int = typer.Option(
        2, help="Number of jobs to be used for generating cases."
    ),
):
    """Generate test cases for the surface position optimization for photovoltaic modules with the specified mode."""

    if mode not in {"tilt", "orientation", "tilt_and_orientation"}:
        typer.echo(
            "Error: Mode must be 'tilt', 'orientation', or 'tilt_and_orientation'."
        )
        raise typer.Exit(code=1)

    typer.echo(f"Running optimization in {mode.replace('_and_', ' and ')} mode...")
    write_cases_optimizer(mode, workers=workers)


if __name__ == "__main__":
    app()
