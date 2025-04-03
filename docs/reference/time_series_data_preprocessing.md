---
icon: simple/buildkite
title: Preprocessing
tags:
  - Data
  - Time Series
  - Solar Irradiance
  - Global Horizontal Irradiance
  - Direct Horizontal Irradiance
  - Spectral Factor
  - Temperature
  - Wind Speed
---

# Chunking Bytes

This is a data reading experiment involving NetCDF files + Kerchunk to Parquet Stores.

> - What does _chunking bytes_ mean ?
> 
> In short, _chunking bytes_ and in the context of this work/project, it means :
> _restructuring the shape of multi-dimensional data_.

## TL;DR

In the case of PVGIS : 
Transform daily space-time data stored in NetCDF files
to temporal contiguous space-time data stored in a Zarr Store.

## In short

1. Collect data
2. Inspect structure
3. Rechunk to uniform shape
4. _Optionally_ Clip to area of interest
5. Kerchunk NetCDF files and generate a Parquet Store
6. Read Parquet index via the Zarr engine
7. Rechunking experiments
8. Generate Zarr stores

## Collect raw data  >  NetCDF

   - Collect NetCDF files
   - Organise files per variable ?
   - SARAH3 2000 - 2023 : 8388 _daily_ time series data files
   - ERA5-Land

## Inspect internal structure

   - "Problem" of mixed chunking shapes -- *look-out for the `SIS` variable !*

  | Variable      | Shapes          | Files                                  | Count |
  |---------------|-----------------|----------------------------------------|-------|
  | time          | 524288          | SISin199902230000004231000101MA.nc ... | 2558  |
  | time          | 512             | SISin201407160000004231000101MA.nc ... | 6195  |
  | lon           | 2600            | SISin199902230000004231000101MA.nc ... | 8753  |
  | lon_bnds      | 2600 x 2        | SISin199902230000004231000101MA.nc ... | 8753  |
  | lat           | 2600            | SISin199902230000004231000101MA.nc ... | 8753  |
  | lat_bnds      | 2600 x 2        | SISin199902230000004231000101MA.nc ... | 8753  |
  | **SIS**           | 1 x 1300 x 1300 | SISin199902230000004231000101MA.nc ... | 2558  |
  | **SIS**           | 1 x 1 x 2600    | SISin201407160000004231000101MA.nc ... | 5465  |
  | **SIS**           | 1 x 2600 x 2600 | SISin2022031200000042310001I1MA.nc ... | 730   |
  | record_status | 48              | SISin199902230000004231000101MA.nc ... | 8752  |
  | record_status | 4096            | SISin2021110600000042310001I1MA.nc     | 1     |

## Rechunk

   - _Uniformity muss (hier) sein !_
   - Identical _shape_ for all daily NetCDF files : 48 x 2600 x 2600

One tool that can rechunk NetCDF files is `nccopy`.
`rekx` builds (currently/also) on top of it.
Effectively, `rekx` will generate a series of `nccopy` commands 
along with combinations of important options on
the size of chunks for `time`, `lat` and `lon`,
compression levels and shuffling,
fixing unlimited dimensions and caching.

For example
```
rekx rechunk-generator \
    /mnt/photovoltaic/sarah3/SIS/netcdf/sample/clipped/ \
    --output-directory /mnt/photovoltaic/sarah3/SIS/netcdf/sample/rechunking \
    --time 48 \
    --latitude 32,64,128 \
    --longitude 32,64,128 \
    --compression-level 0,2,4,8 \
    --shuffling \
    --memory
```

And another example
```
rekx rechunk-generator \
    /mnt/sandbox/clipped/ \
    --output-directory /mnt/sandbox/rechunking \
    --time 48 \
    --latitude 16,32,64 \
    --longitude 16,32,64 \
    --compression-level 0 \
    --shuffling \
    --memory \
    --fix-unlimited-dimensions
```

## Clip data to region of interest

In the context of
processing massive time series,
and specifically the reading performance,
what matters most is the _structure_ of the data!
The area to cover needs to be large enough,
yet there is no need to cover the complete extent!

Therefore,
we can clip raw NetCDF data to a smaller region
(e.g. one that covers Italy)
before the generation of Zarr stores
with the aim to perform a feasibility assessment.


  1. Get NUTS vector map from Eurostat

  2. Extract Italy for Level 0
  
  3. Get bounding box coordinates zooming to vector boundaries :
  ```
  6.6274844369999997 18.5274844369999983 35.4916886779999956 47.0916886779999970
  ```
     - Longitude : 232, Latitude 238
  
  4. Clip using custom tool `rekx`
  ``` shell
  rekx clip \
      /mnt/photovoltaic/sarah3/SIS/netcdf/ \
      6.6274844369999997 \  # min Longitude
      18.5274844369999983 \  # max Longitude
      35.4916886779999956 \  # min Latitude
      47.0916886779999970 \  # max Latitude
      --output-filename-suffix Italia \
      --output-directory /mnt/photovoltaic/sarah3/SIS/netcdf/sample/clipped \
      --pattern SISin20[01]*.nc \
      --workers 36
  ```

## Kerchunk NetCDF files to generate per-file Parquet index

Actually two steps :

1. Generate Parquet indexes per NetCDF file

   - Read operations go through the _reference_ file (`JSON` or `Parquet`) typically faster.

2. Combine per-file indexes to one Parquet index

   - Reading metadata once. Only.
   - Subsequent read operations go through the reference index.

!!! example

    Using Kerchunk behind the scenes via `rekx` we create a reference for each
    clipped NetCDF file

    ``` shell
    rekx reference-multi-parquet . -v --output-directory reference_test
    ```

    and then combine the individual _references_ into one _Parquet reference_

    ``` shell
    rekx combine-parquet-stores . -v
    ```

## Read Parquet index via the Zarr engine

- Way faster than using `xarray.open_mfdataset()` !
- The latter reads the _same_ metadata for each and every NetCDF file

### Without Kerchunking

!!! warning

    Alternatively,
    instead of reading-in the Kerchunk-ed indexes,
    one can read the NetCDF files directly via Xarray.
    This is however slower!

An example _without_ Kerchunking into play :

#### Read NetCDF files

``` python
ds = xr.open_mfdataset(
    "chunks_48_4_4/*48_4_4_zlib_0.nc",
    combine="nested",
    concat_dim="time",
    engine="h5netcdf",
    parallel=True,
)
```

!!! note

    Using the [h5netcdf](https://github.com/h5netcdf/h5netcdf) package
    by passing `engine='h5netcdf'`
    to [`open_dataset()`](https://docs.xarray.dev/en/stable/generated/xarray.open_dataset.html#xarray.open_dataset)
    can sometimes be quicker
    than the default `engine='netcdf4'`
    that uses the [netCDF4](https://github.com/Unidata/netcdf4-python) package.

``` python
<xarray.Dataset> Size: 77GB
Dimensions:  (time: 350016, lat: 232, lon: 238)
Coordinates:
  * time     (time) datetime64[ns] 3MB 2000-01-01 ... 2019-12-31T23:30:00
  * lon      (lon) float32 952B 6.675 6.725 6.775 6.825 ... 18.42 18.48 18.52
  * lat      (lat) float32 928B 35.53 35.58 35.62 35.67 ... 46.97 47.03 47.08
Data variables:
    SIS      (time, lat, lon) float32 77GB dask.array<chunksize=(350016, 2, 2), meta=np.ndarray>
Attributes: (12/38)
    Conventions:                CF-1.7,ACDD-1.3
    id:                         DOI:10.5676/EUM_SAF_CM/SARAH/V003
    product_version:            3.0
    institution:                EUMETSAT/CMSAF
    creator_name:               DE/DWD
    creator_email:              contact.cmsaf@dwd.de
    ...                         ...
    instrument_vocabulary:      GCMD Instruments, Version 8.6
    instrument:                 MVIRI > Meteosat Visible Infra-Red Imager
    variable_id:                SIS
    license:                    The CM SAF data are owned by EUMETSAT and are...
    title:                      CM SAF Surface Solar Radiation Climate Data R...
    summary:                    This file contains data from the CM SAF Surfa...
```

## Rechunk. Again.

This is the most essential step.

   - Combinations of chunk sizes for `time`, `latitude` and `longitude`.
   - 📦 Without or with compression
   - 📦 🔀 Compression without or with Shuffling


### Example

``` python
ds = ds.chunk({'time': -1, 'lat': 4, 'lon': 4})
```

## Generate Zarr store

   Key points :

   - One chunk in time for contiguous time series
   - Using Dask for parallel processing
   - Compressed data stores for a specific chunking shape can be re-generated from the respective uncompressed & chunked dataset

   Advantages of Zarr :

   - Very flexible
   - Performant
   - Extendable
   - Support for **In-Memory Stores** 

   ``` rekx
   rekx parquet-to-zarr \
      /mnt/sandbox/rechunking/chunks_48_2_2_zlib_0_350016_records.parquet \
      teststore.zarr SIS \
      --time ' -1' \
      --latitude 2 \
      --longitude 2 \
      --workers 36
   ```

### Example

#### Define important parameters

``` python
store = LocalStore(Path('sis_italia_space_chunk_size_4_zstd_1.zarr'))
CONSOLIDATE = True
COMPRESSOR = zarr.codecs.BloscCodec(cname="zstd", clevel=1, shuffle='shuffle')
```

Build the graph

``` python
future = ds.to_zarr(
    store=store,
    compute=False,
    consolidated=CONSOLIDATE,
    encoding={
        ds.SIS.name: {"compressors": COMPRESSOR},
        "time": {"compressors": COMPRESSOR},
        "lat": {"compressors": COMPRESSOR},
        "lon": {"compressors": COMPRESSOR},
    },
    mode="w",
)
```

and run

```python
future = future.persist()
progress(future)

[..]

[                                        ] | 0% Completed |  8.2s2025-01-25 21:28:42,741 - distributed.shuffle._scheduler_plugin - WARNING - Shuffle 30493b7515e17be28db30684e0636c2a initialized by task ('rechunk-merge-rechunk-transfer-2a1e349691e47f29993e61e477ee7c8e', 0, 0, 0, 586, 0, 0) executed on worker tcp://127.0.0.1:33093
[####################################### ] | 99% Completed |  2min 55.3s2025-01-25 21:31:29,568 - distributed.shuffle._scheduler_plugin - WARNING - Shuffle 30493b7515e17be28db30684e0636c2a deactivated due to stimulus 'task-finished-1737837089.5594862'
```

## Examples

### No Kerchunking & Dask-supported Parallelisation

All of the steps above, however in one-go for various chunking shapes

``` python
import xarray as xr
import dask
from dask.distributed import Client
from pathlib import Path
import zarr

# Preamble: Set fixed parameters
store_base_path = Path('sis_italia')
CONSOLIDATE = True
COMPRESSOR = zarr.codecs.BloscCodec(cname="zstd", clevel=1, shuffle='shuffle')

# Define the chunking shapes
chunking_shapes = [
    #(48, 4, 4),
    (48, 8, 8),
    (48, 16, 16),
    (48, 32, 32),
    (48, 64, 64),
    (48, 128, 128)
]

# Launch a Dask client
client = Client()

for shape in chunking_shapes:
    time_chunks, lat_chunks, lon_chunks = shape

    # Step 1: Read multiple NetCDF files
    ds = xr.open_mfdataset(
        f"chunks_{time_chunks}_{lat_chunks}_{lon_chunks}/*{time_chunks}_{lat_chunks}_{lon_chunks}_zlib_0.nc",
        combine="nested",
        concat_dim="time",
        engine="h5netcdf",
        parallel=True,
    )

    # Step 2: Chunk the dataset
    ds = ds.chunk({'time': -1, 'lat': lat_chunks, 'lon': lon_chunks})

    # Define the store path for the current chunking shape
    store = LocalStore(store_base_path / f"space_chunk_size_{time_chunks}_{lat_chunks}_{lon_chunks}_zarr")

    # Step 4: Build the graph
    future = ds.to_zarr(
        store=store,
        compute=False,
        consolidated=CONSOLIDATE,
        encoding={
            ds.SIS.name: {"compressors": COMPRESSOR},
            "time": {"compressors": COMPRESSOR},
            "lat": {"compressors": COMPRESSOR},
            "lon": {"compressors": COMPRESSOR},
        },
        mode="w",
    )

    # Step 5: Run the graph
    future = future.persist()
    dask.distributed.progress(future)

# Optionally, close the Dask client when done
client.close()
```
