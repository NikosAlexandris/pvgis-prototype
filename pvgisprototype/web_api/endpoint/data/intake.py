def generate_intake_catalog():
    import yaml

    catalog = {
        "metadata": {
            "version": 1,
            "description": "Catalog for PVGIS 6 solar data resources.",
        },
        "sources": {
            "solar_radiation": {
                "description": "Time series data for solar radiation",
                "driver": "csv",
                "args": {
                    "urlpath": "s3://mybucket/pvgis_solar_radiation.csv",
                    "storage_options": {"anon": True},
                    "sep": ",",
                    "usecols": ["date", "GHI", "DNI", "DHI"],
                    "parse_dates": ["date"],
                    "index_col": "date",
                },
            },
            "temperature": {
                "description": "Time series data for temperature",
                "driver": "csv",
                "args": {
                    "urlpath": "s3://mybucket/pvgis_temperature.csv",
                    "storage_options": {"anon": True},
                    "sep": ",",
                    "usecols": ["date", "temperature"],
                    "parse_dates": ["date"],
                    "index_col": "date",
                },
            },
        },
    }

    # Convert the dictionary to a YAML string
    yaml_str = yaml.dump(catalog, default_flow_style=False)
    return yaml_str
