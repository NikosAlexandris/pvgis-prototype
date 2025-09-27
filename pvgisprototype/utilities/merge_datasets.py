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
from pathlib import Path

from pvgisprototype.log import logger
from typing import List
from xarray import Dataset, open_dataset, merge


def load_datasets(file_paths: List[Path]) -> List[Dataset]:
    datasets = []
    for file_path in file_paths:
        dataset = open_dataset(file_path)
        datasets.append(dataset)
    return datasets


def merge_datasets_by_spatial_dimensions(
    datasets: List[Dataset],
    longitude_dimension: str = "longitude",
    latitude_dimension: str = "latitude",
    time_dimension: str = "time",
):
    return merge(datasets)


def save_merged_dataset(
    merged_dataset: Dataset,
    output_file: Path,
    output_filename_prefix: str = "",
    output_filename_suffix: str = "concatenated",
):
    """Save merged dataset to a NetCDF file."""
    output_file = (
        output_file.parent
        / f"{output_filename_prefix}{output_file.stem}_{output_filename_suffix}{output_file.suffix}"
    )
    merged_dataset.to_netcdf(output_file)
    logger.debug(f"Dataset saved to {output_file}")


def merge_datasets(
    file_paths: List[Path],
    output_file: Path,
    output_filename_prefix: str = "",
    output_filename_suffix: str = "concatenated",
):
    """Load, concatenate, and save datasets."""
    datasets = load_datasets(file_paths)
    merged_dataset = merge_datasets_by_spatial_dimensions(datasets)
    save_merged_dataset(
        merged_dataset=merged_dataset,
        output_file=output_file,
        output_filename_prefix=output_filename_prefix,
        output_filename_suffix=output_filename_suffix,
    )


if __name__ == "__main__":
    merge_datasets(input_files, output_file)
