"""
This module defines a factory to generate custom data classes (or else models)
dynamically using Pydantic's `BaseModel`. It includes utilities for unit
conversions (e.g., radians, degrees, timestamps), custom attribute handling,
and validation of model fields. The `DataModelFactory` enables efficient
creation of models with properties like solar incidence angles, coordinates,
and time series data, allowing for flexible data representation and
manipulation.

Key Features

- Dynamic generation of data models with custom attributes.
- Unit conversion utilities (e.g., degrees to radians, timestamps to hours).
- Integration with NumPy for handling array-based fields.
"""

from typing import Optional, Dict, Type, Any
import numpy
from pydantic import BaseModel, ConfigDict
from pydantic_numpy import NpNDArray
from pydantic_numpy.model import NumpyModel
from pvgisprototype.core.array_methods import create_array_method, fill_array_method
from pvgisprototype.core.factory.property_functions import PROPERTY_FUNCTIONS
from pvgisprototype.core.factory.extra_methods import EXTRA_METHODS
from pvgisprototype.core.factory.type_mapping import TYPE_MAPPING
from rich.console import Console


console = Console()


def _custom_getattr(self, attribute_name):
    """Optimized custom getattr function with pre-cached property functions."""
    value = PROPERTY_FUNCTIONS.get(attribute_name)
    if value:
        return value(self)
    else:
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{attribute_name}'"
        )

class DataModelFactory:
    _cache = {}

    @staticmethod
    def get_data_model(data_model_name: str, data_model_definitions: dict):
        if data_model_name not in DataModelFactory._cache:
            DataModelFactory._cache[data_model_name] = (
                DataModelFactory._generate_data_model(
                    data_model_name, data_model_definitions
                )
            )

        model = DataModelFactory._cache[data_model_name]
        model.data_model_name = data_model_name  # Assign data_model_name here
        return model

    @staticmethod
    def _hashable_array(array):
        try:
            # Assume a NumPy array and convert it to bytes for hashing
            return hash(array.tobytes())

        except AttributeError:
            # If it's not an array or doesn't have the 'tobytes' method, hash normally
            return hash(array)

    @staticmethod
    def _generate_hash_function(fields, annotations):
        import orjson

        def hash_model(self):
            hash_values = tuple(
                (
                    DataModelFactory._hashable_array(value)
                    if isinstance(value, numpy.ndarray)
                    or annotations[field] == NpNDArray
                    else (
                        orjson.dumps(
                            value,
                            default=lambda obj: obj.__dict__,
                            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY,
                        )
                        if isinstance(value, dict)
                        else hash(value)
                    )
                )
                for field in fields
                for value in [getattr(self, field)]
            )
            return hash(hash_values)

        return hash_model

    @staticmethod
    def _is_np_ndarray_type(field_type):
        """Utility function to check if a field type is or involves NpNDArray."""
        # Handle direct type comparisons
        if field_type is NpNDArray:
            return True

        # Handle complex types involving NpNDArray
        from types import GenericAlias

        if isinstance(field_type, GenericAlias):
            # Check if NpNDArray is part of a Union or other complex type
            return NpNDArray in getattr(field_type, "__args__", [])

        return False

    @staticmethod
    def _generate_alternative_eq_method(fields):
        def eq_model(self, other):
            if not isinstance(other, self.__class__):
                return False

            for field in fields:
                self_value = getattr(self, field)
                other_value = getattr(other, field)

                if isinstance(self_value, numpy.ndarray) and isinstance(
                    other_value, numpy.ndarray
                ):
                    if not numpy.array_equal(self_value, other_value):
                        return False
                else:
                    if self_value != other_value:
                        return False
            return True

        return eq_model

    @staticmethod
    def _is_simple_model(fields: Dict[str, Any]) -> bool:
        """
        Check if a model is a simple one by verifying if all field types are standard.
        """
        return all(field_data["type"] in TYPE_MAPPING for field_data in fields.values())

    @staticmethod
    def _can_generate_complex_model(fields: Dict[str, Any]) -> bool:
        """
        Determine if a model can be generated by checking if all custom types it depends on have already been generated and cached.
        """
        for field_data in fields.values():
            field_type = field_data["type"]
            if (
                field_type not in TYPE_MAPPING
                and field_type not in DataModelFactory._cache
            ):
                # Field type in question does not yet exist, thus we cannot generate this complex model
                return False
        return True

    @staticmethod
    def _generate_data_model(
        data_model_name: str, data_model_definitions: Dict
    ) -> Type[BaseModel]:
        """
        Generate PVGIS-native data models based on a Pydantic `BaseModel` or a
        "NumPy Array into Pydantic" `NumpyModel` (data) model with the
        specified fields, handling custom types, validation, and conversion
        functions as necessary.

        Parameters
        ----------
        data_model_name: str

        data_model_definitions: Dict

        Returns
        -------

        """
        fields = []
        annotations = {}
        default_values = {}
        use_numpy_model = False

        # Consume data model definitions

        # --%<--- use for debugging
        # console.print(f"> [code]{data_model_name=}[/code]")
        # --->%--

        for field_name, field_data in data_model_definitions[data_model_name].items():
            try:
                field_type = field_data["type"]
            except KeyError:
                console.print(f"> [code]{data_model_name=}[/code]")
                console.print_exception(extra_lines=8, show_locals=True)
                console.print(
                        f"The {field_name=} in {data_model_name=} lacks of a `type` key !\n"
                        f"See : {field_data=}"
                        )
                raise KeyError("Perhaps try to manually set the definitions dictionary to an empty dictionary and rerun the generation of the data models... ?")
            # vvvv --%<---
            # else:
            #     console.print(f"   > [bold]{field_name=}[/bold] in {field_data=}")
            # ^^^^ -->%--- may use this else for debugging !

            # # Handle union types (TypeA | TypeB)
            # if "|" in field_type:
            #     type_options = [t.strip() for t in field_type.split("|")]
            #     print(f"{type_options=}")
            #     resolved_types = []
                
            #     for type_option in type_options:
            #         if type_option in TYPE_MAPPING:
            #             resolved_type = TYPE_MAPPING[type_option]
            #         elif type_option in DataModelFactory._cache:
            #             resolved_type = DataModelFactory._cache[type_option]
            #             print(f"{resolved_type=}")
            #         else:
            #             raise ValueError(f"Unknown union member {type_option} in {field_type}")
                    
            #         resolved_types.append(resolved_type.__name__)
                
            #     print(f"{resolved_types=}")
            #     # Create Union type
            #     # type_a = resolved_types[0]
            #     # type_b = resolved_types[1]
            #     # print(f"{type_a.__name__=}")
            #     # print(f"{type_b=}")
            #     field_annotation = Union[resolved_types]
            #     print(f"{field_annotation=}")
                
            #     # Check if any type requires numpy model
            #     for rt in resolved_types:
            #         if DataModelFactory._is_np_ndarray_type(rt):
            #             use_numpy_model = True
            #             break

            if field_type in TYPE_MAPPING:
                # annotations[field_name] = TYPE_MAPPING[field_type]
                field_annotation = Optional[TYPE_MAPPING[field_type]]

                if DataModelFactory._is_np_ndarray_type(TYPE_MAPPING[field_type]):
                    use_numpy_model = True

            elif field_type in DataModelFactory._cache:
                # If an existing complex type, use it
                # annotations[field_name] = DataModelFactory._cache[field_type]
                field_annotation = Optional[DataModelFactory._cache[field_type]]

            else:
                console.print(f"[bold red]Error: Unknown field type {field_type=} for {field_name=} in {data_model_name=}.[/bold red]")
                raise ValueError(f"Unknown field type {field_type=} for {field_name=} in {data_model_name=}.")

            annotations[field_name] = field_annotation
            fields.append(field_name)

            if "initial" in field_data:
                default_values[field_name] = field_data["initial"]

        # Define additional model properties
        base_model = NumpyModel if use_numpy_model else BaseModel

        if use_numpy_model:
            EXTRA_METHODS["create_array"] = classmethod(create_array_method)
            EXTRA_METHODS["fill_array"] = fill_array_method

        model_attributes = {
            "__getattr__": _custom_getattr,
            "__annotations__": annotations,
            "__module__": __package__.split(".")[0],
            "__qualname__": data_model_name,
            "__hash__": DataModelFactory._generate_hash_function(fields, annotations),
            "model_config": ConfigDict(arbitrary_types_allowed=True),
            "__eq__": DataModelFactory._generate_alternative_eq_method(fields),
            **default_values,
            **EXTRA_METHODS,
        }
        
        return base_model.__class__(data_model_name, (base_model,), model_attributes)
