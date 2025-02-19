from dataclasses import dataclass
from typing import Literal

CategoryType = Literal["社内", "社外"]

@dataclass
class ScoreEntry:
    nickname: str
    category: CategoryType
    score: int

    @property
    def is_internal(self) -> bool:
        return self.category == "社内" 