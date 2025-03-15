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
        if "selected_nickname" not in st.session_state:
            st.session_state["selected_nickname"] = None
            st.session_state["selected_adjective"] = None
            st.session_state["selected_animal"] = None

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

        # フォーム送信後の再読み込み時に、セッション状態から最後のエントリを復元
        if st.session_state["selected_nickname"] and not st.session_state["last_entry"]:
            # セッション状態から最後に選択されたニックネーム情報を取得
            adjective = st.session_state["selected_adjective"]
            animal = st.session_state["selected_animal"]

            # 最後のエントリを探す
            for entry in reversed(scores):
                if entry.adjective == adjective and entry.animal == animal:
                    st.session_state["last_entry"] = entry
                    break

        # スコア入力フォームの表示と処理
        new_entry = self.ui.show_entry_form(scores)

        # 統計情報の表示（new_entryがNoneの時のみ表示）
        if not new_entry and scores:
            if stats_result := stats.calculate_statistics():
                self.ui.show_statistics(stats_result)

        # 新しいエントリの処理
        if new_entry:
            # 新しいエントリを保存する前に、ニックネーム情報を確認
            # セッション状態のニックネーム情報と一致するか確認
            if (
                st.session_state["selected_adjective"] != new_entry.adjective
                or st.session_state["selected_animal"] != new_entry.animal
            ):
                # 一致しない場合は、セッション状態を更新
                st.session_state["selected_adjective"] = new_entry.adjective
                st.session_state["selected_animal"] = new_entry.animal
                st.session_state["selected_nickname"] = new_entry.nickname

            self.repository.save_score(new_entry)
            st.session_state["scores"].append(new_entry)
            st.session_state["last_entry"] = new_entry

            # ランキング計算と結果表示
            rank, total = stats.calculate_rank(new_entry)
            self.ui.show_rank_result(rank, total)

            # フォーム送信後は、nickname_optionsをリセットして新しい選択肢を生成させる
            if "nickname_options" in st.session_state:
                st.session_state.pop("nickname_options")
                st.session_state.pop("adjective_animal_map")

        # リーダーボードの表示
        self.ui.show_leaderboard(
            scores=st.session_state["scores"],
            highlight_entry=st.session_state["last_entry"],
        )

        # リーダーボード表示後、選択状態をクリアするのは、新しいエントリが追加された場合のみ
        if new_entry:
            st.session_state["selected_nickname"] = None
            st.session_state["selected_adjective"] = None
            st.session_state["selected_animal"] = None


def main():
    app = LeaderboardApp()
    app.run()


if __name__ == "__main__":
    main()
