import csv
import numpy as np


def write_irradiance_csv(
    longitude=None,
    latitude=None,
    timestamps=[],
    dictionary={},
    filename='irradiance.csv'
):
    # Prepare the header
    header = []
    if longitude:
        header.append('Longitude')
    if latitude:
        header.append('Latitude')
    header.append('Time')
    header.extend(dictionary.keys())
    
    rows = []
    
    # Convert single float or int values to arrays of the same length as timestamps
    for key, value in dictionary.items():
        if isinstance(value, (float, int)):
            dictionary[key] = np.full(len(timestamps), value)
    
    # Zip series and timestamps
    zipped_series = zip(*dictionary.values())
    zipped_data = zip(timestamps, zipped_series)
    
    for timestamp, values in zipped_data:
        row = []
        if longitude and latitude:
            row = [longitude, latitude]
        row.append(timestamp.strftime('%Y-%m-%d %H:%M:%S'))
        row.extend(values)
        rows.append(row)
    
    # Write to CSV
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)
