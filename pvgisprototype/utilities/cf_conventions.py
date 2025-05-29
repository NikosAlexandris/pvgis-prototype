""" """

from pvgisprototype.log import logger
import re
from pathlib import Path
from xarray import Dataset, open_dataset
import typer
from devtools import debug
from pvgisprototype.api.irradiance.kato_bands import KATO_BANDS

CF_COMPLIANT_OUTPUT_FILENAME_SUFFIX = "_cf_compliant"


def comply_sarah_dataset_to_cf_conventions(
    dataset,
    filename: str,
    longitude: float | None = None,
    latitude: float | None = None,
    kato_bands: dict = KATO_BANDS,
):
    """
    Update the dataset to match the reference structure with appropriate renaming,
    attribute updates, and compliance to the CF-1.7 conventions.
    """
    # Rename variables for better clarity
    rename_dict = {
        "wv": "center_wavelength",
        "wvl": "center_wavelength",
        "SIS.kato": "SIS_kato",
        "SIS.broad": "SIS_broadband",
        "SIC.kato": "SIC_kato",
        "SIC.broad": "SIC_broadband",
        "lon": "longitude",
        "lat": "latitude",
    }
    filtered_rename_dict = {
        key: value for key, value in rename_dict.items() if key in dataset
    }
    dataset = dataset.rename(filtered_rename_dict)

    if not longitude and not latitude:
        # get latitude and longitude from filename, add dimensions + coordinates
        match = re.search(r"_(\-?\d+\.\d+)_(\-?\d+\.\d+)\.nc", filename)
        if match:
            latitude = float(match.group(1))
            longitude = float(match.group(2))

        else:
            raise ValueError("Could not parse latitude and longitude from filename")

    dataset = dataset.expand_dims({"latitude": [latitude], "longitude": [longitude]})
    dataset["latitude"].attrs["units"] = "degrees_north"
    dataset["latitude"].attrs["long_name"] = "Latitude"
    dataset["longitude"].attrs["units"] = "degrees_east"
    dataset["longitude"].attrs["long_name"] = "Longitude"

    # Add attributes to the variables
    variable_attrs = {
        "SIS": {
            "long_name": "Spectrally resolved irradiance",
            "units": "W/m^2/nm",
            "description": "Irradiance divided by Kato band width",
        },
        "SIS_kato": {
            "long_name": "Spectrally resolved irradiance",
            "units": "W/m^2",
            "description": "Full irradiance per Kato band",
        },
        "SIS_broadband": {
            "long_name": "Clear-sky Broadband irradiance",
            "units": "W/m^2",
            "description": "Total irradiance summed over all Kato bands",
        },
        "SIC": {
            "long_name": "Clear-sky Spectrally resolved irradiance",
            "units": "W/m^2/nm",
            "description": "Irradiance divided by Kato band width",
        },
        "SIC_kato": {
            "long_name": "Clear-sky Spectrally resolved irradiance",
            "units": "W/m^2",
            "description": "Full irradiance per Kato band",
        },
        "SIC_broadband": {
            "long_name": "Clear-sky Broadband irradiance",
            "units": "W/m^2",
            "description": "Total irradiance summed over all Kato bands",
        },
        "center_wavelength": {
            "long_name": "Spectral center wavelength",
            "units": "nm",
            "description": "Central wavelength of the Kato spectral bands",
        },
    }

    # Apply variable attributes
    for var, attrs in variable_attrs.items():
        if var in dataset:
            dataset[var].attrs.update(attrs)

    # Update dataset attributes
    dataset.attrs.update(
        {
            "broadband_description": "The broadband variable sums irradiance over all Kato bands.",
            "title": "Prototype Data Structure for Spectrally Resolved Irradiance Data",
            "conventions": "CF-1.7",
            "institution": "DWD, Germany",
            "source": "Simulated Data or Actual Source Information",
            "history": "Updated on 2024-09-09",
            "project": "Exploring the Spectral Mismatch Factor",
            "description": (
                "This dataset contains spectrally resolved irradiance data based on the Kato spectral bands. "
                "The data variables represent irradiance values for different wavelength bands, where each "
                "band corresponds to a specific center wavelength and bandwidth, as defined in the Kato band "
                "designation. The lower and upper limits of the wavelength range for each band are included "
                "as attributes in the data variables."
            ),
            "source_2": "Kato et al. (1999) spectral bands used for solar irradiance modeling.",
            "author": "Name LastName",
            "co-creators": "Name1 LastName1, Name2 LastName2",
            "references": "Your Reference Information (DOI or link)",
            "comment": (
                "This dataset was created as part of a collaborative work between the JRC, EC, and DWD, "
                "Germany to explore the spectral mismatch factor."
            ),
        }
    )

    # Add Kato band-related attributes to the dataset variables
    # for index, center in enumerate(kato_bands["Center [nm]"].values()):
    #     band_variable = f"Band {index + 1}"
    #     if band_variable in dataset:
    #         dataset[band_variable].attrs.update(
    #             {
    #                 "Index": index + 1,
    #                 "Lower limit [nm]": kato_bands["Lower limit [nm]"][index],
    #                 "Upper limit [nm]": kato_bands["Upper limit [nm]"][index],
    #                 "Center [nm]": center,
    #                 "Width [nm]": kato_bands["Width [nm]"][index],
    #             }
    #         )
    for index, center in kato_bands["Center [nm]"].items():
        band_variable = f"Band {index + 1}"
        if band_variable in dataset:
            dataset[band_variable].attrs.update(
                {
                    "long_name": "Spectral center wavelength",
                    "units": "nm",
                    "description": "Central wavelength of the Kato spectral bands",
                }
            )

    # Ensure CF-compliant geospatial and temporal attributes
    dataset.attrs["geospatial_lat_min"] = dataset["latitude"].min().item()
    dataset.attrs["geospatial_lat_max"] = dataset["latitude"].max().item()
    dataset.attrs["geospatial_lon_min"] = dataset["longitude"].min().item()
    dataset.attrs["geospatial_lon_max"] = dataset["longitude"].max().item()
    dataset.attrs["time_coverage_start"] = str(dataset["time"].min().values)
    dataset.attrs["time_coverage_end"] = str(dataset["time"].max().values)

    return dataset


def build_cf_compliant_netcdf_file(
    input_file: Path,
    output_path: Path,
    longitude: float | None = None,
    latitude: float | None = None,
    output_filename_prefix: str = "",
    output_filename_suffix: str = CF_COMPLIANT_OUTPUT_FILENAME_SUFFIX,
) -> None:
    """ """
    if input_file.suffix in {".nc", ".netcdf"}:
        output_file = (
            output_path
            / f"{output_filename_prefix}{input_file.stem}{output_filename_suffix}{input_file.suffix}"
        )
        logger.debug(
            f"Processing {input_file.name}",
            alt=f"[bold]Processing[/bold] {input_file.name}",
        )
        dataset = open_dataset(input_file)
        updated_dataset = comply_sarah_dataset_to_cf_conventions(
            dataset=dataset,
            filename=input_file.name,
            longitude=longitude,
            latitude=latitude,
            kato_bands=KATO_BANDS,
        )
        updated_dataset.to_netcdf(output_file)
        logger.debug(
            f"Updated dataset written to {output_file}",
            alt=f"Updated dataset written to {output_file}",
        )


def comply_dataset_to_cf_conventions(
    input_path: Path,
    output_path: Path,
    longitude: float = None,
    latitude: float = None,
    output_filename_prefix: str = "",
    output_filename_suffix: str = CF_COMPLIANT_OUTPUT_FILENAME_SUFFIX,
):
    """
    Loop over NetCDF files, update their structure, and save them to the output directory.
    """
    if not output_path.exists():
        output_path.mkdir(parents=True)

    for filename in input_path.iterdir():
        build_cf_compliant_netcdf_file(
            input_file=filename,
            output_path=output_path,
            longitude=longitude,
            latitude=latitude,
            output_filename_prefix=output_filename_prefix,
            output_filename_suffix=output_filename_suffix,
        )


if __name__ == "__main__":
    typer.run(comply_dataset_to_cf_conventions)
