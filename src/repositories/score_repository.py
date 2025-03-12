from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

import pandas as pd

from ..models.score_entry import ScoreEntry


class ScoreRepositoryInterface(ABC):
    @abstractmethod
    def load_scores(self) -> List[ScoreEntry]:
        pass

    @abstractmethod
    def save_score(self, entry: ScoreEntry) -> None:
        pass


class CSVScoreRepository(ScoreRepositoryInterface):
    def __init__(self, file_path: str = "data/score.csv"):
        self.file_path = Path(file_path)

    def load_scores(self) -> List[ScoreEntry]:
        try:
            df = pd.read_csv(self.file_path)
            return [
                ScoreEntry(
                    adjective=row["adjective"],
                    animal=row["animal"],
                    category="社内"
                    if str(row["is_internal"]).strip().lower() == "true"
                    else "社外",
                    score=row["score"],
                    unit=row.get("unit")
                    if "unit" in df.columns and pd.notna(row.get("unit"))
                    else None,
                    age=row.get("age")
                    if "age" in df.columns and pd.notna(row.get("age"))
                    else None,
                )
                for _, row in df.iterrows()
            ]
        except Exception as e:
            print(f"CSV読み込みエラー: {e}")
            return []

    def save_score(self, entry: ScoreEntry) -> None:
        try:
            df = (
                pd.read_csv(self.file_path)
                if self.file_path.exists()
                else pd.DataFrame(
                    columns=[
                        "adjective",
                        "animal",
                        "score",
                        "is_internal",
                        "unit",
                        "age",
                    ]
                )
            )
            new_row = {
                "adjective": entry.adjective,
                "animal": entry.animal,
                "is_internal": str(entry.is_internal).lower(),
                "score": entry.score,
                "unit": entry.unit if entry.unit else "",
                "age": entry.age if entry.age else "",
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(self.file_path, index=False)
        except Exception as e:
            print(f"CSV保存エラー: {e}")
