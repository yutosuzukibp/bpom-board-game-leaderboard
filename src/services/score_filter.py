from typing import List, Optional, Set

from ..models.score_entry import ScoreEntry


class ScoreFilterService:
    """スコアデータをフィルタリングするサービスクラス"""

    def __init__(self, scores: List[ScoreEntry]):
        self.scores = scores

    def get_unique_categories(self) -> List[str]:
        """利用可能な所属カテゴリのリストを取得"""
        categories = set()
        for score in self.scores:
            categories.add(score.category)
        return sorted(list(categories))

    def get_unique_units(self) -> List[str]:
        """利用可能な部署のリストを取得（社内のみ）"""
        units = set()
        for score in self.scores:
            if score.is_internal and score.unit:
                units.add(score.unit)
        return sorted(list(units))

    def get_unique_ages(self) -> List[str]:
        """利用可能な年齢のリストを取得"""
        ages = set()
        for score in self.scores:
            if score.age:
                ages.add(score.age)
        return sorted(list(ages))

    def filter_scores(
        self,
        selected_categories: Optional[Set[str]] = None,
        selected_units: Optional[Set[str]] = None,
        selected_ages: Optional[Set[str]] = None,
    ) -> List[ScoreEntry]:
        """スコアをフィルタリング"""
        filtered_scores = self.scores.copy()

        # カテゴリでフィルタリング
        if selected_categories:
            filtered_scores = [
                score
                for score in filtered_scores
                if score.category in selected_categories
            ]

        # 部署でフィルタリング
        if selected_units:
            filtered_scores = [
                score
                for score in filtered_scores
                if score.is_internal and score.unit and score.unit in selected_units
            ]

        # 年齢でフィルタリング
        if selected_ages:
            filtered_scores = [
                score for score in filtered_scores if score.age in selected_ages
            ]

        return filtered_scores
