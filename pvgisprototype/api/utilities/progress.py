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
