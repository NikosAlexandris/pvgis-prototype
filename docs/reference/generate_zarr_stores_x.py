import xarray as xr
from xarray import Dataset
import dask
from dask.distributed import Client, LocalCluster
from distributed import progress
from pathlib import Path
import zarr
from zarr.storage import LocalStore
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Preamble
DASK_SCHEDULER_IP = 'localhost'
DASK_SCHEDULER_PORT = '8888'
NUMBER_OF_WORKERS = 38

XARRAY_OPEN_DATA_COMBINE = "nested"
XARRAY_OPEN_DATA_CONCATENATE_DIMENSION = "time"
XARRAY_OPEN_DATA_ENGINE = "h5netcdf"
XARRAY_OPEN_DATA_IN_PARALLEL = True

ZARR_STORE_BASE_PATH = Path("sis_italia")
ZARR_CONSOLIDATE = True
ZARR_COMPRESSOR_CODEC = "zstd"
ZARR_COMPRESSOR_LEVEL = 1
ZARR_COMPRESSOR_SHUFFLE = "shuffle"
ZARR_COMPRESSOR = zarr.codecs.BloscCodec(
    cname=ZARR_COMPRESSOR_CODEC,
    clevel=ZARR_COMPRESSOR_LEVEL,
    shuffle=ZARR_COMPRESSOR_SHUFFLE,
)
NETCDF_FILENAME_PREFIX = 'SISin2000*'
NETCDF_COMPRESSOR_CODEC = 'zlib'
NETCDF_COMPRESSOR_LEVEL = 0
NETCDF_FILENAME_SUFFIX = f"{NETCDF_COMPRESSOR_CODEC}_{NETCDF_COMPRESSOR_LEVEL}"
NETCDF_FILENAME_EXTENSION = 'nc'

CHUNKING_SHAPES = [
    #(48, 2, 2),
    #(48, 4, 4),
    #(48, 8, 8),
    #(48, 16, 16),
    #(48, 32, 32),
    (48, 64, 64),
    (48, 128, 128)
]
GREEN_DASH = "[green]-[/green]"

def open_netcdf_via_mfdataset(
    source_directory: Path,
    filename_pattern: str,
) -> Dataset:
    """
    Define the source to the NetCDF files with and for the current chunking shape
    """
    logger.info(f" - Searching in [code]{source_directory}[/code] for files matching : [code]{filename_pattern}[/code]")
    netcdf_files_matching_pattern = list(source_directory.glob(filename_pattern))
    if not netcdf_files_matching_pattern:
        logger.error("   [red]No files found matching the pattern. Skipping...[/red]")
        return None
    else:
        logger.info(f" - [green]Found {len(netcdf_files_matching_pattern)} files[/green]")
        
    try:
        logger.info(f" {GREEN_DASH} Read multiple NetCDF files as an Xarray Dataset")
        netcdf_filename_pattern = source_directory / f"{filename_pattern}"
        return xr.open_mfdataset(
            str(netcdf_filename_pattern),
            combine=XARRAY_OPEN_DATA_COMBINE,
            concat_dim=XARRAY_OPEN_DATA_CONCATENATE_DIMENSION,
            engine=XARRAY_OPEN_DATA_ENGINE,
            parallel=XARRAY_OPEN_DATA_IN_PARALLEL,
        )
    except Exception as e:
        logger.error(f"   [red]Error reading NetCDF files[/red] : {e}")
        return None

def generate_zarr_store(
    dataset: Dataset,
    store: str,
    time_chunks: int,
    latitude_chunks: int,
    longitude_chunks: int,
    consolidate: bool = ZARR_CONSOLIDATE,
    compressor=ZARR_COMPRESSOR,
    mode='w-',
):
    """
    Chunk the dataset and save it to a Zarr store.
    """
    logger.info(f" {GREEN_DASH} Chunk the dataset")
    dataset = dataset.chunk({"time": -1, "lat": latitude_chunks, "lon": longitude_chunks})
    logger.info(f'   > Dataset shape after chunking : {dataset.data_vars}')

    logger.info(f"   Define the store path for the current chunking shape")
    store = LocalStore(store)

    logger.info(f' {GREEN_DASH} Build the Dask task graph')
    return dataset.to_zarr(
        store=store,
        compute=False,
        consolidated=consolidate,
        encoding={
            dataset.SIS.name: {"compressors": compressor},
            "time": {"compressors": compressor},
            "lat": {"compressors": compressor},
            "lon": {"compressors": compressor},
        },
        mode=mode,
    )

def process_chunking_shape(
    shape: tuple,
    netcdf_source_directory: Path,
    netcdf_filename_pattern: str,
    store_path: Path,
):
    """
    Process a single chunking shape by opening NetCDF files, creating a Dask client,
    and generating a Zarr store.
    """
    time_chunks, latitude_chunks, longitude_chunks = shape

    if store_path.exists():
        logger.warning(f'   > [red]Store {store_path} already exists, skipping to the next iteration![/red]')
        return

    logger.info(f'  - The requested Zarr store\'s path {store_path} does not exist. Let\'s create it...')

    netcdfs_as_dataset = open_netcdf_via_mfdataset(
        source_directory=netcdf_source_directory,
        filename_pattern=netcdf_filename_pattern,
    )
    if netcdfs_as_dataset is None:
        logger.error("   [red]Failed to open NetCDF files. Skipping this chunking shape.[/red]")
        return

    logger.info(f' {GREEN_DASH} NetCDF files as a Dataset : {netcdfs_as_dataset}')

    logger.info(f' {GREEN_DASH} Launching a Dask client @ {DASK_SCHEDULER_IP}:{DASK_SCHEDULER_PORT}')
    with LocalCluster(
        host=DASK_SCHEDULER_IP,
        scheduler_port=DASK_SCHEDULER_PORT,
        n_workers=NUMBER_OF_WORKERS,
    ) as cluster:
        logger.info(f" {GREEN_DASH} Connect to local cluster")
        with Client(cluster) as client:
            future = generate_zarr_store(
                dataset=netcdfs_as_dataset,
                store=str(store_path),
                time_chunks=time_chunks,
                latitude_chunks=latitude_chunks,
                longitude_chunks=longitude_chunks,
            )
            logger.info(f' {GREEN_DASH} Run the graph of tasks')
            future = future.persist()
            progress(future)
            logger.info('')

if __name__ == "__main__":
    for shape in CHUNKING_SHAPES:
        logger.info(f' {GREEN_DASH} [bold]Processing input chunking shape[/bold] : {shape}')
        time_chunks, latitude_chunks, longitude_chunks = shape

        store_path = ZARR_STORE_BASE_PATH / f"space_chunk_size_{time_chunks}_{latitude_chunks}_{longitude_chunks}_{ZARR_COMPRESSOR_CODEC}_{ZARR_COMPRESSOR_LEVEL}.zarr"
        netcdf_source_directory = Path(f"chunks_{time_chunks}_{latitude_chunks}_{longitude_chunks}")
        netcdf_filename_pattern = f"{NETCDF_FILENAME_PREFIX}_{time_chunks}_{latitude_chunks}_{longitude_chunks}_{NETCDF_FILENAME_SUFFIX}.{NETCDF_FILENAME_EXTENSION}"

        process_chunking_shape(
            shape=shape,
            netcdf_source_directory=netcdf_source_directory,
            netcdf_filename_pattern=netcdf_filename_pattern,
            store_path=store_path,
        )
