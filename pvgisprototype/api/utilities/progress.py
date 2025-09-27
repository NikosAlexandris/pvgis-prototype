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
from rich.progress import Progress


def track_progress(task_id):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            progress.update(task_id, advance=1)
            return result

        return wrapper

    return decorator


progress = Progress()


# ... for direct irradiance components
task_extraterrestrial_irradiance = progress.add_task(
    "[cyan]Calculating extraterrestrial normal irradiance series...", total=1
)
task_correct_linke_turbidity_factor = progress.add_task(
    "[magenta]Calculating corrected linke turbidity factor series...", total=1
)
task_rayleigh_optical_thickness = progress.add_task(
    "[green]Calculating rayleigh optical thickness series...", total=1
)
