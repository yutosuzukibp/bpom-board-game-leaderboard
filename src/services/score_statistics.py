from dataclasses import dataclass
from typing import List, Optional

import pandas as pd

from ..models.score_entry import ScoreEntry


@dataclass
class StatisticsResult:
    max_score: int
    avg_score: float
    total_players: int
    top_player: ScoreEntry


class ScoreStatistics:
    def __init__(self, scores: List[ScoreEntry]):
        self.scores = scores

    def calculate_statistics(self) -> Optional[StatisticsResult]:
        if not self.scores:
            return None

        df = pd.DataFrame(
            [
                {
                    "adjective": s.adjective,
                    "animal": s.animal,
                    "category": s.category,
                    "score": s.score,
                }
                for s in self.scores
            ]
        )

        max_score = df["score"].max()
        avg_score = round(df["score"].mean(), 1)
        total_players = len(df)
        top_player_idx = df["score"].idxmax()
        top_player_row = df.loc[top_player_idx]
        top_player = ScoreEntry(
            adjective=top_player_row["adjective"],
            animal=top_player_row["animal"],
            category=top_player_row["category"],
            score=top_player_row["score"],
        )

        return StatisticsResult(
            max_score=max_score,
            avg_score=avg_score,
            total_players=total_players,
            top_player=top_player,
        )

    def calculate_rank(self, entry: ScoreEntry) -> tuple[int, int]:
        df = pd.DataFrame(
            [
                {
                    "adjective": s.adjective,
                    "animal": s.animal,
                    "nickname": s.nickname,
                    "score": s.score,
                }
                for s in self.scores
            ]
        )
        df_sorted = df.sort_values(by="score", ascending=False)
        df_sorted["rank"] = df_sorted["score"].rank(method="min", ascending=False)
        rank = int(
            df_sorted[
                (df_sorted["adjective"] == entry.adjective)
                & (df_sorted["animal"] == entry.animal)
                & (df_sorted["score"] == entry.score)
            ]["rank"].iloc[0]
        )
        total = len(df_sorted)
        return rank, total
