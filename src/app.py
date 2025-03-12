import streamlit as st

from .repositories.score_repository import CSVScoreRepository
from .services.score_statistics import ScoreStatistics
from .ui.leaderboard_ui import LeaderboardUI

BODY_FONT_SIZE = 15
ALERT_FONT_SIZE = 15
DATAFRAME_FONT_SIZE = 20


class LeaderboardApp:
    def __init__(self):
        self.repository = CSVScoreRepository()
        self.ui = LeaderboardUI()
        if "scores" not in st.session_state:
            st.session_state["scores"] = self.repository.load_scores()
        if "last_entry" not in st.session_state:
            st.session_state["last_entry"] = None

        st.markdown(
            f"""
            <style>
                /* Streamlit全体のフォントサイズを変更 */
                html, body, [class*="st-"] {{
                    font-size: {BODY_FONT_SIZE}px !important;
                }}

                /* info, success, warning, error のフォントサイズ */
                .stAlert {{
                    font-size: {ALERT_FONT_SIZE}px !important;
                }}

                /* DataFrameのフォントサイズ */
                .dataframe th, .dataframe td {{
                    font-size: {DATAFRAME_FONT_SIZE}px !important;
                }}
            </style>
            """,
            unsafe_allow_html=True,
        )

    def run(self):
        scores = st.session_state["scores"]
        stats = ScoreStatistics(scores)

        # スコア入力フォームの表示と処理
        new_entry = self.ui.show_entry_form(scores)

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
            highlight_entry=st.session_state["last_entry"],
        )


def main():
    app = LeaderboardApp()
    app.run()


if __name__ == "__main__":
    main()
