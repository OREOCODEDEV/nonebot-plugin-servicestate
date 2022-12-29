from typing import List
from .exception import NameEscapeCharacterCountError


class Escharacter:
    def __init__(self, keywords: str, max_count: int = 2) -> None:
        self.__raw_content = keywords
        self.__extract_content = list(
            map(
                lambda i: i.replace("^_^", "@"),
                keywords.replace("@@", "^_^").split("@"),
            )
        )
        self.is_group = False
        if len(self.__extract_content) != 1:
            self.is_group = True
        if self.is_group and len(self.is_group) > max_count:
            raise NameEscapeCharacterCountError

    def __repr__(self) -> str:
        return self.__extract_content if self.is_group else self.__raw_content

    @property
    def name(self) -> str:
        if self.is_group:
            raise ValueError("Group name should not access with name property")
        return self.__raw_content

    @property
    def group_name(self) -> List[str]:
        if not self.is_group:
            raise ValueError("Name should not access with group_name property")
        return self.__extract_content
