class UnsupportedProtocolError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class NameConflictError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class NameNotFoundError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ConfigError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)