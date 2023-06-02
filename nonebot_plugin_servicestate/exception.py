class ProtocolUnsopportError(Exception):
    """
    不支持该协议
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class NameConflictError(Exception):
    """
    名称冲突
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class NameNotFoundError(Exception):
    """
    未找到该名称
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ParamInvalidError(Exception):
    """
    参数类型或范围不正确
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ParamCountInvalidError(Exception):
    """
    参数个数不正确
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class NameEscapeCharacterCountError(Exception):
    """
    转义符个数不正确
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
