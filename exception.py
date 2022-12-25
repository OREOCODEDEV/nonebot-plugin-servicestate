class NameConflictException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class BindFailedException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
