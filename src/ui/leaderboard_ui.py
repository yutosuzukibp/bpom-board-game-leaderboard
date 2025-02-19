import streamlit as st
import plotly.express as px
import pandas as pd
from typing import List, Optional

from ..models.score_entry import ScoreEntry
from ..services.score_statistics import StatisticsResult

class LeaderboardUI:
    HIGHLIGHT_COLOR = "#8B0000"
    HIGHLIGHT_BACKGROUND = "rgba(255, 118, 118, 0.4)"
    HISTOGRAM_COLOR = "#aaaaaa"
    CELEBRATE_PERCENTILE = 50

    def __init__(self):
        st.set_page_config(page_title="【ボドゲ部】ジャマイカ成績表", layout="wide")
        st.title("ジャマイカ成績表")

    def show_statistics(self, stats: StatisticsResult):
        st.info(
            f"🏆 現在の記録\n\n"
            f"\t👑 1位: {stats.top_player.nickname}さん（{stats.max_score}点）\n\n"
            f"\t📊 平均点: {stats.avg_score}点\n\n"
            f"\t👥 これまでの挑戦者: {stats.total_players}人\n\n"
            f"あなたは何点取れるかな？ 👇"
        )

    def show_entry_form(self) -> Optional[ScoreEntry]:
        with st.sidebar.form("entry_form"):
            st.subheader("スコアを登録する")
            nickname = st.text_input("ニックネーム")
            category = st.radio("所属", ["社内", "社外"])
            score = st.number_input("スコア", min_value=0, step=1, value=0)
            submitted = st.form_submit_button("登録")

            if submitted and nickname:
                return ScoreEntry(nickname=nickname, category=category, score=score)
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

    def show_leaderboard(self, scores: List[ScoreEntry], highlight_entry: Optional[ScoreEntry] = None):
        if not scores:
            return

        df = pd.DataFrame([
            {"ニックネーム": s.nickname, "所属": s.category, "スコア": s.score}
            for s in scores
        ])
        df_sorted = df.sort_values(by="スコア", ascending=False).reset_index(drop=True)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("ランキング")
            highlight_index = None
            if highlight_entry:
                mask = (
                    (df_sorted["ニックネーム"] == highlight_entry.nickname) &
                    (df_sorted["所属"] == highlight_entry.category) &
                    (df_sorted["スコア"] == highlight_entry.score)
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
                    f"background-color: {self.HIGHLIGHT_BACKGROUND}; border-left: 3px solid {self.HIGHLIGHT_COLOR}"
                    if i == highlight_index
                    else ""
                    for i in range(len(df_sorted))
                ],
                axis=0,
            ).format({"順位": "{:d}位"})

            if len(df_sorted) > 20:
                st.dataframe(styled_df, height=400, hide_index=True, use_container_width=True)
            else:
                st.dataframe(styled_df, hide_index=True, use_container_width=True)

        with col2:
            st.subheader("スコア分布")
            fig = px.histogram(
                df_sorted,
                x="スコア",
                nbins=min(
                    int(df_sorted["スコア"].max() - df_sorted["スコア"].min() + 1),
                    10,
                ),
                title="スコア分布",
                color_discrete_sequence=[self.HISTOGRAM_COLOR],
            )

            if highlight_entry:
                fig.add_vline(
                    x=highlight_entry.score,
                    line_width=2,
                    line_color=self.HIGHLIGHT_COLOR,
                    annotation_text="あなたのスコア",
                    annotation_position="top",
                )

            fig.update_layout(
                xaxis_title="スコア",
                yaxis_title="人数",
                height=400,
                margin=dict(t=30, b=0, l=0, r=0),
            )
            st.plotly_chart(fig, use_container_width=True) 