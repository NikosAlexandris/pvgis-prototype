from pathlib import Path

import xarray
from pvgisprototype.log import logger
from typing import List
from xarray import Dataset, open_dataset, concat, merge


def load_datasets(file_paths: List[Path]) -> List[Dataset]:
    datasets = []
    for file_path in file_paths:
        dataset = open_dataset(file_path)
        datasets.append(dataset)
    return datasets


def concatenate_datasets_by_spatial_dimensions(
    datasets: List[Dataset],
    longitude_dimension: str = "longitude",
    latitude_dimension: str = "latitude",
    time_dimension: str = "time",
):
    return merge(datasets)

def save_concatenated_dataset(
    concatenated_dataset: Dataset,
    output_file: Path,
    output_filename_prefix: str = "",
    output_filename_suffix: str = "concatenated",
):
    """Save concatenated dataset to a NetCDF file."""
    output_file = (
        output_file.parent
        / f"{output_filename_prefix}{output_file.stem}_{output_filename_suffix}{output_file.suffix}"
    )
    concatenated_dataset.to_netcdf(output_file)
    logger.info(f"Dataset saved to {output_file}")


def concatenate_datasets(
    file_paths: List[Path],
    output_file: Path,
    output_filename_prefix: str = "",
    output_filename_suffix: str = "concatenated",
):
    """Load, concatenate, and save datasets."""
    datasets = load_datasets(file_paths)
    concatenated_dataset = concatenate_datasets_by_spatial_dimensions(datasets)
    save_concatenated_dataset(
        concatenated_dataset=concatenated_dataset,
        output_file=output_file,
        output_filename_prefix=output_filename_prefix,
        output_filename_suffix=output_filename_suffix,
    )


if __name__ == "__main__":
    concatenate_datasets(input_files, output_file)
