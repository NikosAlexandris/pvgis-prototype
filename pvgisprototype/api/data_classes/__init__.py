import os
from .model import generate_dataclass_models

current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)

generate_dataclass_models(os.path.join(
    parent_directory,
    'parameters_info.yaml')
)