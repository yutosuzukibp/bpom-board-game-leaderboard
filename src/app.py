import streamlit as st
from typing import Optional

from .models.score_entry import ScoreEntry
from .repositories.score_repository import CSVScoreRepository
from .services.score_statistics import ScoreStatistics
from .ui.leaderboard_ui import LeaderboardUI

class LeaderboardApp:
    def __init__(self):
        self.repository = CSVScoreRepository()
        self.ui = LeaderboardUI()
        if "scores" not in st.session_state:
            st.session_state["scores"] = self.repository.load_scores()
        if "last_entry" not in st.session_state:
            st.session_state["last_entry"] = None

    def run(self):
        scores = st.session_state["scores"]
        stats = ScoreStatistics(scores)

        # 既存のニックネームのリストを作成
        existing_nicknames = [score.nickname for score in scores]

        # スコア入力フォームの表示と処理
        new_entry = self.ui.show_entry_form(existing_nicknames)

        # 統計情報の表示（new_entryがNoneの時のみ表示）
        if not new_entry and scores:
            if stats_result := stats.calculate_statistics():
                self.ui.show_statistics(stats_result)

        # 新しいエントリの処理
        if new_entry:
            self.repository.save_score(new_entry)
            st.session_state["scores"].append(new_entry)
            st.session_state["last_entry"] = new_entry

            # ランキング計算と結果表示
            rank, total = stats.calculate_rank(new_entry)
            self.ui.show_rank_result(rank, total)

        # リーダーボードの表示
        self.ui.show_leaderboard(
            scores=st.session_state["scores"],
            highlight_entry=st.session_state["last_entry"]
        )

def main():
    app = LeaderboardApp()
    app.run()

if __name__ == "__main__":
    main() 