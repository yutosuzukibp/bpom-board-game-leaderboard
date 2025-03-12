import csv
import random
from typing import List, Optional, Set, Tuple

import pandas as pd
import plotly.express as px
import streamlit as st

from ..models.score_entry import ScoreEntry
from ..services.score_statistics import StatisticsResult


class LeaderboardUI:
    HIGHLIGHT_COLOR = "#8B0000"
    HIGHLIGHT_BACKGROUND = "rgba(255, 118, 118, 0.4)"
    HISTOGRAM_COLOR = "#aaaaaa"
    CELEBRATE_PERCENTILE = 50
    LEADERBOARD_HEIGHT = 250
    DATAFRAME_FONT_SIZE = 100

    def __init__(self):
        st.set_page_config(page_title="【ボドゲ部】ジャマイカ成績表", layout="wide")

        # タイトルの上の余白を調整とヘッダーを非表示
        st.markdown(
            """
            <style>
                .block-container {
                    padding-top: 1rem;
                }
                header {
                    display: none !important;
                }
            </style>
        """,
            unsafe_allow_html=True,
        )

        st.title("ジャマイカ成績表")

    def show_statistics(self, stats: StatisticsResult):
        st.info(
            f"🏆 現在の記録\n\n"
            f"- 👑 1位: {stats.top_player.nickname}さん（{stats.max_score}点）\n"
            f"- 📊 平均点: {stats.avg_score}点\n"
            f"- 👥 これまでの挑戦者: {stats.total_players}人\n\n"
            f"あなたは何点取れるかな？ 👇"
        )

    def _load_csv_data(self, file_path: str) -> List[str]:
        """CSVファイルからデータを読み込む"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader)  # ヘッダーをスキップ
                return [row[0] for row in reader]
        except Exception as e:
            st.error(f"CSVファイル読み込みエラー: {e}")
            return []

    def _get_used_combinations(
        self, existing_entries: List[ScoreEntry]
    ) -> Set[Tuple[str, str]]:
        """既に使用されている形容詞と動物の組み合わせを取得"""
        return {(entry.adjective, entry.animal) for entry in existing_entries}

    def _suggest_combinations(
        self,
        adjectives: List[str],
        animals: List[str],
        used_combinations: Set[Tuple[str, str]],
        count: int = 10,
    ) -> List[Tuple[str, str]]:
        """未使用の組み合わせをランダムに提案"""
        all_combinations = [(adj, ani) for adj in adjectives for ani in animals]
        available_combinations = [
            comb for comb in all_combinations if comb not in used_combinations
        ]

        if len(available_combinations) <= count:
            return available_combinations

        return random.sample(available_combinations, count)

    def show_entry_form(
        self, existing_entries: List[ScoreEntry]
    ) -> Optional[ScoreEntry]:
        # CSVからデータを読み込む
        adjectives = self._load_csv_data("data/adjectives.csv")
        animals = self._load_csv_data("data/animals.csv")
        units = self._load_csv_data("data/units.csv")
        ages = self._load_csv_data("data/ages.csv")

        # 既に使用されている組み合わせを取得
        used_combinations = self._get_used_combinations(existing_entries)

        # 未使用の組み合わせを10個提案
        suggested_combinations = self._suggest_combinations(
            adjectives, animals, used_combinations
        )

        # フォームの外でカテゴリを選択
        st.sidebar.subheader("スコアを登録する")

        # カテゴリ選択（フォームの外）
        if "category" not in st.session_state:
            st.session_state["category"] = "社内"

        category = st.sidebar.radio("所属", ["社内", "社外"], key="category")

        # 社内かどうかのフラグ
        is_internal = category == "社内"

        with st.sidebar.form("entry_form"):
            # 提案された組み合わせを選択肢として表示
            nickname_options = []
            adjective_animal_map = {}

            if suggested_combinations:
                for adj, ani in suggested_combinations:
                    nickname = f"{adj}{ani}"
                    nickname_options.append(nickname)
                    adjective_animal_map[nickname] = (adj, ani)

                selected_nickname = st.selectbox(
                    "ニックネーム",
                    options=nickname_options,
                    help="以下の未使用の組み合わせから選択してください",
                )

                if selected_nickname:
                    selected_adjective, selected_animal = adjective_animal_map[
                        selected_nickname
                    ]
                else:
                    selected_adjective, selected_animal = None, None
            else:
                st.error("利用可能な組み合わせがありません。管理者に連絡してください。")
                return None

            # 部署選択（社外の場合はdisabled）
            unit = None
            if is_internal:
                unit = st.selectbox(
                    "部署",
                    options=units,
                )
            else:
                st.text("部署: 社外の方は選択不要です")

            # 年齢選択
            age = st.selectbox("年齢", options=ages)

            # スコア入力
            score = st.number_input("スコア", min_value=0, step=1, value=0)

            submitted = st.form_submit_button("登録")

            if submitted:
                # 入力チェック
                if not selected_adjective or not selected_animal:
                    st.error("ニックネームを選択してください")
                    return None

                return ScoreEntry(
                    adjective=selected_adjective,
                    animal=selected_animal,
                    category=category,
                    score=score,
                    unit=unit if is_internal else None,
                    age=age,
                )
            return None

    def show_rank_result(self, rank: int, total: int):
        percentile = 100 - int((total - rank) / total * 100)

        if percentile <= self.CELEBRATE_PERCENTILE:
            st.success(
                "🎊 おめでとう！！！！ 🎊\n\n"
                f"\t🏆 あなたの順位は{rank}位です！\n\n"
                f"\t✨ あなたは上位{percentile}%です！ ✨\n\n"
                f"\t🌟 素晴らしい成績です！ 🌟"
            )
            st.balloons()
        else:
            st.success(
                f"🎯 結果発表！\n\n"
                f"\t🏅 あなたの順位は{rank}位です！\n\n"
                f"\t📊 あなたは上位{percentile}%です！\n\n"
                f"\t💪 次は更に上を目指そう！"
            )
            st.snow()

    def show_leaderboard(
        self, scores: List[ScoreEntry], highlight_entry: Optional[ScoreEntry] = None
    ):
        if not scores:
            return

        df = pd.DataFrame(
            [
                {
                    "ニックネーム": s.nickname,
                    "所属": s.category,
                    "スコア": s.score,
                    "部署": s.unit if s.is_internal and s.unit else "-",
                    "年齢": s.age if s.age else "-",
                }
                for s in scores
            ]
        )
        df_sorted = df.sort_values(by="スコア", ascending=False).reset_index(drop=True)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("ランキング")
            highlight_index = None
            if highlight_entry:
                mask = (
                    (df_sorted["ニックネーム"] == highlight_entry.nickname)
                    & (df_sorted["所属"] == highlight_entry.category)
                    & (df_sorted["スコア"] == highlight_entry.score)
                )
                if mask.any():
                    highlight_index = df_sorted[mask].index[0]

            df_sorted = df_sorted.copy()
            df_sorted.insert(
                0,
                "順位",
                df_sorted["スコア"].rank(method="min", ascending=False).astype(int),
            )

            styled_df = df_sorted.style.apply(
                lambda _: [
                    f"background-color: {self.HIGHLIGHT_BACKGROUND}; border-left: 3px solid {self.HIGHLIGHT_COLOR}; font-weight: bold"
                    if i == highlight_index
                    else ""
                    for i in range(len(df_sorted))
                ],
                axis=0,
            ).format({"順位": "{:d}位"})

            if len(df_sorted) > 20:
                st.dataframe(
                    styled_df,
                    height=self.LEADERBOARD_HEIGHT,
                    hide_index=True,
                    use_container_width=True,
                )
            else:
                st.dataframe(
                    styled_df,
                    height=self.LEADERBOARD_HEIGHT,
                    hide_index=True,
                    use_container_width=True,
                )

        with col2:
            st.subheader("スコア分布")
            fig = px.histogram(
                df_sorted,
                x="スコア",
                nbins=min(
                    int(df_sorted["スコア"].max() - df_sorted["スコア"].min() + 1),
                    10,
                ),
                color_discrete_sequence=[self.HISTOGRAM_COLOR],
            )

            if highlight_entry:
                fig.add_vline(
                    x=highlight_entry.score,
                    line_width=2,
                    line_color=self.HIGHLIGHT_COLOR,
                    annotation_text="あなたのスコア",
                    annotation_position="top",
                    annotation_font_size=18,
                    annotation_font_color=self.HIGHLIGHT_COLOR,
                    annotation_font_weight="bold",
                )

            fig.update_layout(
                xaxis_title="スコア",
                yaxis_title="人数",
                height=self.LEADERBOARD_HEIGHT,
                margin=dict(t=30, b=0, l=0, r=0),
            )
            st.plotly_chart(fig, use_container_width=True)
