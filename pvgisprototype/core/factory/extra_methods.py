from pvgisprototype.core.factory.context import populate_context


def to_dictionary(self):
    return {
        field: getattr(self, field)
        for field in self.__annotations__
        if hasattr(self, field)
    }


def build_output(self, verbose: int = 0, fingerprint: bool = False):
    return populate_context(self, verbose, fingerprint)


EXTRA_METHODS = {
    "to_dictionary": to_dictionary,
    "build_output": build_output,
}
