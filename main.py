import pandas as pd
import plotly.express as px
import streamlit as st

# 定数の設定
HIGHLIGHT_COLOR = "#8B0000"  # BPのテーマカラーは#7F0003だが暗すぎるので若干明るくした
HIGHLIGHT_BACKGROUND = "rgba(255, 118, 118, 0.4)"  # 透明度を持った赤色の背景
HISTOGRAM_COLOR = "#aaaaaa"
CELEBRATE_PERCENTILE = 10

# ページの設定とCSSによるシンプルなおしゃれデザイン
st.set_page_config(page_title="【ボドゲ部】ジャマイカ成績表", layout="wide")

st.title("ジャマイカ成績表")


# セッション状態にリーダーボードのデータを保持
if "leaderboard" not in st.session_state:
    try:
        df_leaderboard = pd.read_csv("data/score.csv")
    except Exception as e:
        st.error("CSV読み込みエラー: " + str(e))
        df_leaderboard = pd.DataFrame(columns=["name", "is_internal", "score"])

    leaderboard_list = []
    for _, row in df_leaderboard.iterrows():
        category = (
            "社内" if str(row["is_internal"]).strip().lower() == "true" else "社外"
        )
        entry = {"ニックネーム": row["name"], "所属": category, "スコア": row["score"]}
        leaderboard_list.append(entry)
    st.session_state["leaderboard"] = leaderboard_list
    st.session_state["last_entry"] = None

# 入力フォーム
with st.sidebar.form("entry_form"):
    st.subheader("スコアを登録する")
    nickname = st.text_input("ニックネーム")
    category = st.radio("所属", ["社内", "社外"])
    score = st.number_input("スコア", min_value=0, step=1, value=0)
    submitted = st.form_submit_button("登録")

# 統計情報の表示（submittedがFalseの時のみ表示）
if not submitted and st.session_state["leaderboard"]:
    df = pd.DataFrame(st.session_state["leaderboard"])
    max_score = df["スコア"].max()
    avg_score = round(df["スコア"].mean(), 1)
    total_players = len(df)
    top_player = df.loc[df["スコア"].idxmax()]
    
    st.info(
        f"🏆 現在の記録\n\n"
        f"\t👑 1位: {top_player['ニックネーム']}さん（{max_score}点）\n\n"
        f"\t📊 平均点: {avg_score}点\n\n"
        f"\t👥 これまでの挑戦者: {total_players}人\n\n"
        f"あなたは何点取れるかな？ 👇"
    )

if submitted and nickname:
    # 新しいエントリを追加
    new_entry = {"ニックネーム": nickname, "所属": category, "スコア": score}
    st.session_state["leaderboard"].append(new_entry)
    # 最後に登録したユーザー情報を保存
    st.session_state["last_entry"] = new_entry

    try:
        df_csv = pd.read_csv("data/score.csv")
    except Exception as e:
        st.error("CSV読み込みエラー（登録時）: " + str(e))
        df_csv = pd.DataFrame(columns=["name", "is_internal", "score"])

    new_row = {
        "name": nickname,
        "is_internal": "true" if category == "社内" else "false",
        "score": score,
    }
    df_csv = pd.concat([df_csv, pd.DataFrame([new_row])], ignore_index=True)
    df_csv.to_csv("data/score.csv", index=False)

    # ランキングを計算
    df = pd.DataFrame(st.session_state["leaderboard"])
    # スコアが高い順にソート
    df_sorted = df.sort_values(by="スコア", ascending=False).reset_index(drop=True)

    # 新しく追加したエントリの順位を特定 (同じニックネームとスコアがあった場合は最初の出現位置)
    rank = int(
        df_sorted[
            (df_sorted["ニックネーム"] == nickname) & (df_sorted["スコア"] == score)
        ].index[0]
    ) + 1
    total = len(df_sorted)
    # 上位何%かを計算
    percentile = 100 - int((total - rank) / total * 100)

    if percentile <= CELEBRATE_PERCENTILE:
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

# 登録が1件以上ある場合、ランキングとスコア分布を表示
if st.session_state["leaderboard"]:
    df = pd.DataFrame(st.session_state["leaderboard"])
    df_sorted = df.sort_values(by="スコア", ascending=False).reset_index(drop=True)

    # 2つのカラムを作成
    col1, col2 = st.columns(2)

    # 左カラム：ランキング表
    with col1:
        st.subheader("ランキング")

        # 最後に登録したユーザーの行のインデックスを特定
        highlight_index = None
        if st.session_state["last_entry"] is not None:
            mask = (
                (
                    df_sorted["ニックネーム"]
                    == st.session_state["last_entry"]["ニックネーム"]
                )
                & (df_sorted["所属"] == st.session_state["last_entry"]["所属"])
                & (df_sorted["スコア"] == st.session_state["last_entry"]["スコア"])
            )
            if mask.any():
                highlight_index = df_sorted[mask].index[0]

        # 順位列を追加（同率スコアは同じ順位に）
        df_sorted = df_sorted.copy()
        # スコアの降順で順位を計算（同率は同じ順位、次の順位はスキップ）
        df_sorted.insert(
            0,
            "順位",
            df_sorted["スコア"].rank(method="min", ascending=False).astype(int),
        )

        # スタイル適用済みのデータフレームを作成
        styled_df = df_sorted.style.apply(
            lambda _: [
                f"background-color: {HIGHLIGHT_BACKGROUND}; border-left: 3px solid {HIGHLIGHT_COLOR}"
                if i == highlight_index
                else ""
                for i in range(len(df_sorted))
            ],
            axis=0,
        ).format(
            {
                "順位": "{:d}位"  # 順位列に「位」を付ける
            }
        )

        if len(df_sorted) > 20:
            # 20行以上の場合はスクロール可能なデータフレームを表示
            st.dataframe(
                styled_df, height=400, hide_index=True, use_container_width=True
            )
        else:
            # 20行以下の場合は従来通りの表を表示
            st.dataframe(styled_df, hide_index=True, use_container_width=True)

    # 右カラム：スコア分布グラフ
    with col2:
        st.subheader("スコア分布")
        fig = px.histogram(
            df_sorted,
            x="スコア",
            nbins=min(
                int(df_sorted["スコア"].max() - df_sorted["スコア"].min() + 1),
                10,  # 最大10区間まで
            ),
            title="スコア分布",
            color_discrete_sequence=[HISTOGRAM_COLOR],
        )
        # 最後に登録したユーザーのスコアに縦線を追加
        if st.session_state["last_entry"] is not None:
            last_score = st.session_state["last_entry"]["スコア"]
            fig.add_vline(
                x=last_score,
                line_width=2,
                line_color=HIGHLIGHT_COLOR,
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
