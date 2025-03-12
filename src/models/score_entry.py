from dataclasses import dataclass
from typing import Literal, Optional

CategoryType = Literal["社内", "社外"]


@dataclass
class ScoreEntry:
    adjective: str
    animal: str
    category: CategoryType
    score: int
    unit: Optional[str] = None
    age: Optional[str] = None

    @property
    def is_internal(self) -> bool:
        return self.category == "社内"

    @property
    def nickname(self) -> str:
        return f"{self.adjective}{self.animal}"
