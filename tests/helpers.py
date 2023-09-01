from datetime import datetime
from datetime import timedelta


def generate_timestamps_for_a_year(start_date=datetime(2023, 1, 1), frequency_minutes=60):
    end_date = start_date + timedelta(days=365)
    timestamps = [start_date]
    current_time = start_date
    while current_time < end_date:
        current_time += timedelta(minutes=frequency_minutes)
        timestamps.append(current_time)

    return timestamps if timestamps[-1] != end_date else timestamps[:-1]
