import csv
import random
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd
import plotly.express as px
import streamlit as st

from ..models.score_entry import ScoreEntry
from ..services.score_filter import ScoreFilterService
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

        # フィルタリング状態の初期化
        if "filter_categories" not in st.session_state:
            st.session_state["filter_categories"] = set()
        if "filter_units" not in st.session_state:
            st.session_state["filter_units"] = set()
        if "filter_ages" not in st.session_state:
            st.session_state["filter_ages"] = set()
        if "show_filters" not in st.session_state:
            st.session_state["show_filters"] = False

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

    def _show_filter_controls(
        self, filter_service: ScoreFilterService
    ) -> Dict[str, Set[str]]:
        """フィルタリングコントロールを表示"""
        # フィルタ表示の切り替え
        show_filters = st.checkbox(
            "フィルタを表示",
            value=st.session_state["show_filters"],
            key="show_filters_checkbox",
        )
        st.session_state["show_filters"] = show_filters

        if not show_filters:
            return {"categories": set(), "units": set(), "ages": set()}

        st.subheader("フィルタ設定")

        # 利用可能なフィルタオプションを取得
        categories = filter_service.get_unique_categories()
        units = filter_service.get_unique_units()
        ages = filter_service.get_unique_ages()

        # フィルタコントロールを表示
        col1, col2, col3 = st.columns(3)

        with col1:
            selected_categories = st.multiselect(
                "所属",
                options=categories,
                default=list(st.session_state["filter_categories"])
                if st.session_state["filter_categories"]
                else None,
                key="filter_categories_select",
            )
            st.session_state["filter_categories"] = set(selected_categories)

        with col2:
            selected_units = st.multiselect(
                "部署",
                options=units,
                default=list(st.session_state["filter_units"])
                if st.session_state["filter_units"]
                else None,
                key="filter_units_select",
            )
            st.session_state["filter_units"] = set(selected_units)

        with col3:
            selected_ages = st.multiselect(
                "年齢",
                options=ages,
                default=list(st.session_state["filter_ages"])
                if st.session_state["filter_ages"]
                else None,
                key="filter_ages_select",
            )
            st.session_state["filter_ages"] = set(selected_ages)

        # フィルタのリセットボタン
        if st.button("フィルタをリセット"):
            st.session_state["filter_categories"] = set()
            st.session_state["filter_units"] = set()
            st.session_state["filter_ages"] = set()
            st.experimental_rerun()

        return {
            "categories": set(selected_categories),
            "units": set(selected_units),
            "ages": set(selected_ages),
        }

    def show_leaderboard(
        self, scores: List[ScoreEntry], highlight_entry: Optional[ScoreEntry] = None
    ):
        if not scores:
            return

        # フィルタリングサービスの初期化
        filter_service = ScoreFilterService(scores)

        # フィルタコントロールの表示
        filters = self._show_filter_controls(filter_service)

        # フィルタリングの適用
        filtered_scores = scores
        if any([filters["categories"], filters["units"], filters["ages"]]):
            filtered_scores = filter_service.filter_scores(
                selected_categories=filters["categories"],
                selected_units=filters["units"],
                selected_ages=filters["ages"],
            )

            if not filtered_scores:
                st.warning(
                    "フィルタ条件に一致するデータがありません。フィルタ条件を変更してください。"
                )
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
                for s in filtered_scores
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

            # スコアの最小値と最大値を取得
            min_score = int(df_sorted["スコア"].min())
            max_score = int(df_sorted["スコア"].max())

            # スコアごとの頻度を計算
            score_counts = df_sorted["スコア"].value_counts().sort_index()

            # 全てのスコア値（1刻み）を含むインデックスを作成
            all_scores = pd.Series(range(min_score, max_score + 1))

            # 欠損しているスコア値を0で埋める
            score_counts = score_counts.reindex(all_scores, fill_value=0)

            # データフレームに変換
            score_df = pd.DataFrame(
                {"スコア": score_counts.index, "人数": score_counts.values}
            )

            # 累積和と累積パーセンテージを計算
            total_players = len(df_sorted)
            score_df = score_df.sort_values("スコア", ascending=False)
            score_df["累積人数"] = score_df["人数"].cumsum()
            score_df["累積パーセンテージ"] = (
                score_df["累積人数"] / total_players * 100
            ).round(1)

            # 棒グラフとライン（累積パーセンテージ）の2軸グラフを作成
            fig = px.bar(
                score_df.sort_values("スコア"),  # スコアの昇順にソート
                x="スコア",
                y="人数",
                color_discrete_sequence=[self.HISTOGRAM_COLOR],
            )

            # 棒グラフに細めのborderを追加
            fig.update_traces(marker=dict(line=dict(width=1, color="white")))

            # 累積パーセンテージのラインを追加
            fig2 = px.line(
                score_df.sort_values("スコア"),  # スコアの昇順にソート
                x="スコア",
                y="累積パーセンテージ",
                markers=True,
            )

            # 2つのグラフを結合
            for trace in fig2.data:
                trace.yaxis = "y2"  # 2つ目のy軸を使用
                fig.add_trace(trace)

            # 2つ目のy軸を設定
            fig.update_layout(
                yaxis2=dict(
                    title=dict(
                        text="累積パーセンテージ (%)", font=dict(color="#1f77b4")
                    ),
                    tickfont=dict(color="#1f77b4"),
                    anchor="x",
                    overlaying="y",
                    side="right",
                    range=[0, 100],
                )
            )

            if highlight_entry:
                # ハイライトエントリがフィルタリング結果に含まれているか確認
                highlight_in_filtered = any(
                    s.adjective == highlight_entry.adjective
                    and s.animal == highlight_entry.animal
                    and s.score == highlight_entry.score
                    for s in filtered_scores
                )

                if highlight_in_filtered:
                    # ハイライトエントリのスコアに対応する累積パーセンテージを取得
                    highlight_score = highlight_entry.score
                    highlight_percentile = score_df[
                        score_df["スコア"] >= highlight_score
                    ]["累積パーセンテージ"].min()

                    # ハイライトエントリの位置に縦線を追加
                    fig.add_vline(
                        x=highlight_entry.score,
                        line_width=2,
                        line_color=self.HIGHLIGHT_COLOR,
                        annotation_text=f"あなたのスコア (上位{highlight_percentile}%)",
                        annotation_position="top",
                        annotation_font_size=14,
                        annotation_font_color=self.HIGHLIGHT_COLOR,
                        annotation_font_weight="bold",
                    )

            # グラフのレイアウト設定
            fig.update_layout(
                xaxis_title="スコア",
                yaxis_title="人数",
                height=self.LEADERBOARD_HEIGHT,
                margin=dict(t=30, b=0, l=0, r=0),
                bargap=0.1,  # バー間のギャップを小さく
            )

            # X軸の設定を別途行う
            if max_score - min_score < 20:  # スコアの範囲が狭い場合は1刻みで表示
                fig.update_xaxes(tickmode="linear", dtick=1)

            # 凡例の設定
            fig.update_layout(
                legend=dict(
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
                )
            )

            st.plotly_chart(fig, use_container_width=True)

            # フィルタリング情報の表示
            if any([filters["categories"], filters["units"], filters["ages"]]):
                filter_info = []
                if filters["categories"]:
                    filter_info.append(f"所属: {', '.join(filters['categories'])}")
                if filters["units"]:
                    filter_info.append(f"部署: {', '.join(filters['units'])}")
                if filters["ages"]:
                    filter_info.append(f"年齢: {', '.join(filters['ages'])}")

                st.caption(f"フィルタ適用中: {' / '.join(filter_info)}")
                st.caption(f"表示件数: {len(filtered_scores)}件 / 全{len(scores)}件")
