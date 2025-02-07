import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# ページの設定とCSSによるシンプルなおしゃれデザイン
st.set_page_config(page_title="ボードゲームリーダーボード", layout="wide")
st.markdown(
    """
<style>
body {
    background-color: #f0f2f6;
    font-family: 'Helvetica Neue', sans-serif;
}
header, .css-18ni7ap, .css-1d391kg { 
    color: #333333;
}
+.block-container {
    max-width: 1400px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("ボードゲームリーダーボード")

# 定数の設定
SCORE_MEAN = 10  # スコアの平均値
SCORE_STD = 3  # スコアの標準偏差
DUMMY_DATA_SIZE = 100  # ダミーデータの件数
HIGHLIGHT_COLOR = "#FF4B4B"  # 目立つ赤色
HIGHLIGHT_BACKGROUND = "rgba(255, 118, 118, 0.4)"  # 透明度を持った赤色の背景


def generate_dummy_data(size: int, mean: float, std: float) -> list:
    """
    ダミーデータを生成する関数

    Args:
        size (int): 生成するデータの件数
        mean (float): スコアの平均値
        std (float): スコアの標準偏差

    Returns:
        list: 生成されたダミーデータのリスト
    """
    dummy_data = []
    for i in range(1, size + 1):
        nickname = f"ユーザー{i}"
        category = np.random.choice(["社内", "社外"])
        # 正規分布からスコアを生成（負の値は0に調整）
        score = int(round(np.random.normal(mean, std)))
        score = max(0, score)
        dummy_data.append({"ニックネーム": nickname, "所属": category, "スコア": score})
    return dummy_data


# セッション状態にリーダーボードのデータを保持
if "leaderboard" not in st.session_state:
    st.session_state["leaderboard"] = []
    # 定数を使用してダミーデータを生成（初回のみ）
    st.session_state["leaderboard"] = generate_dummy_data(
        size=DUMMY_DATA_SIZE, mean=SCORE_MEAN, std=SCORE_STD
    )
    # 最後に登録したユーザー情報を初期化
    st.session_state["last_entry"] = None

# 入力フォーム
with st.form("entry_form"):
    st.subheader("スコアを登録する")
    nickname = st.text_input("ニックネーム")
    category = st.radio("所属", ["社内", "社外"])
    score = st.number_input("スコア", min_value=0, step=1, value=0)
    submitted = st.form_submit_button("登録")

if submitted and nickname:
    # 新しいエントリを追加
    new_entry = {"ニックネーム": nickname, "所属": category, "スコア": score}
    st.session_state["leaderboard"].append(new_entry)
    # 最後に登録したユーザー情報を保存
    st.session_state["last_entry"] = new_entry

    # ランキングを計算
    df = pd.DataFrame(st.session_state["leaderboard"])
    # スコアが高い順にソート
    df_sorted = df.sort_values(by="スコア", ascending=False).reset_index(drop=True)

    # 新しく追加したエントリの順位を特定 (同じニックネームとスコアがあった場合は最初の出現位置)
    rank = int(
        df_sorted[
            (df_sorted["ニックネーム"] == nickname) & (df_sorted["スコア"] == score)
        ].index[0]
    )
    total = len(df_sorted)
    # 上位何%かを計算
    percentile = 100 - int((total - rank) / total * 100)

    st.success(f"おめでとう！上位{percentile}%です！")
    if percentile <= 10:
        st.balloons()
    else:
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
            nbins=10,
            title="スコア分布",
            color_discrete_sequence=["#69b3a2"],
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
