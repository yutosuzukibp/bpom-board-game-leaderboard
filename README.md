# 【ボドゲ部】ジャマイカ成績表

このウェブアプリケーションは、ボードゲームのスコアを管理・表示するためのシンプルなシステムです。ユーザーは提案された形容詞と動物の組み合わせからニックネームを選択し、所属（社内 or 社外）、スコアを入力して成績を登録できます。社内ユーザーは部署も選択できます。登録されたデータはCSVファイルに保存され、アプリケーション内でランキング表やスコア分布のヒストグラムとして視覚化されます。

## 主な機能
- **スコア登録:** 
  - ユーザーは未使用の形容詞と動物の組み合わせからニックネームを選択できます
  - 所属（社内/社外）を選択できます
  - 社内ユーザーは部署を選択できます
  - 年齢を選択できます
  - スコアを入力して成績を登録できます
- **ランキング表示:** 登録されたスコアを元に、順位表を作成。最新のエントリはハイライト表示され、同率スコアの場合は同じ順位になります。
- **スコア分布の可視化:** Plotlyを用いてスコアの分布をヒストグラムとして表示。最新の登録スコアには縦線を追加して強調表示します。
- **アニメーションエフェクト:** 登録したスコアが上位10%の場合はバルーン、その他の場合は雪のアニメーションを表示して結果をフィードバックします。

## アーキテクチャ
このアプリケーションはSOLID原則に基づいて設計されています：

### ディレクトリ構造
```
src/
├── models/          # データモデル
│   └── score_entry.py
├── repositories/    # データの永続化
│   └── score_repository.py
├── services/       # ビジネスロジック
│   └── score_statistics.py
└── ui/            # ユーザーインターフェース
    └── leaderboard_ui.py
```

### コンポーネント
- **ScoreEntry (Model)**: スコアデータのモデルクラス（形容詞、動物、カテゴリ、スコア、部署、年齢）
- **ScoreRepository (Repository)**: データの永続化を担当するインターフェースとその実装
- **ScoreStatistics (Service)**: 統計計算やランキング計算を行うサービス
- **LeaderboardUI (UI)**: ユーザーインターフェースの表示を担当
- **LeaderboardApp (Application)**: アプリケーション全体の制御を担当

## 動作環境
- Python 3.8以上
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## 必要なパッケージ
- streamlit
- pandas
- plotly

## セットアップと実行方法
1. **環境のセットアップ**
   ```bash
   uv venv
   uv pip install -r requirements.txt
   ```

2. **CSVファイルの配置**
   アプリケーションは以下のCSVファイルを使用します：
   - `data/score.csv` - スコアデータ（自動作成）
   - `data/adjectives.csv` - 形容詞リスト
   - `data/animals.csv` - 動物リスト
   - `data/units.csv` - 部署リスト
   - `data/ages.csv` - 年齢リスト

3. **アプリケーションの起動**
   ```bash
   uv run streamlit run main.py
   ```

## 開発ガイドライン
- 新しいストレージ方式を追加する場合は、`ScoreRepositoryInterface`を実装してください
- UIの変更は`LeaderboardUI`クラスで行ってください
- ビジネスロジックの追加は`ScoreStatistics`クラスで行ってください
- データモデルの変更は`ScoreEntry`クラスで行ってください

## 注意事項
- ユーザーの入力内容はStreamlitのセッション状態に保存され、ランキング計算やデータのハイライト表示に利用されます。
- CSVの読み込みや書き込み時にエラーが発生した場合、エラーメッセージが表示されます。
- ニックネームは形容詞と動物の組み合わせから選択する必要があり、既に使用されている組み合わせは選択できません。

このアプリケーションは、SOLID原則に基づいた設計により、保守性が高く、拡張が容易な構造となっています。各コンポーネントは単一責任を持ち、依存関係が明確に定義されているため、新機能の追加や既存機能の修正が容易に行えます。
