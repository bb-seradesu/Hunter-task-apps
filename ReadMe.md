# ハンタータスク シミュレーション（Streamlit）

このプロジェクトは、20×20 のグリッドで「2体のハンターが2体の獲物を捕獲する」タスクを、Streamlit 上で動かすシミュレーションです。サイドバーの設定で動作を切り替えながら、1ステップずつ実行できます。

## 対象環境
- OS: macOS / Linux / Windows
- Python: 3.10 〜 3.12 を推奨
- パッケージ管理: pip

## セットアップ（コマンドだけで実行可能）
以下のコマンドを順に実行してください。

```bash


# 1) 仮想環境を作成して有効化
python3 -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# 2) pip を更新して依存関係をインストール
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 起動
```bash
streamlit run main.py
```
ブラウザが開かない場合は、表示された URL（例: http://localhost:8501）をブラウザで開いてください。終了する場合は、ターミナルで Ctrl+C を押します。

## 使い方（画面の見方）
- 1ステップ進む: 1手だけ状態を更新します。
- リセット: 位置と状態を初期化します。
- サイドバーの主な設定:
  - 獲物を動かす: ON にすると、各ステップで獲物がランダムに1マス（時々停止）動きます。捕獲された獲物は停止します。
  - Hunter 0 制御 / Hunter 1 制御:
    - Lv0: 固定のターゲットに最短方針で1歩進みます。捕獲済みがある場合は残りへ切り替えます。
    - Q: Qテーブルで「より良い行動」を選びます。状態が無い場合は Lv0 にフォールバックします。
  - Qテーブル（読み込みのみ）: 手動で `.pkl` を選んで読み込むこともできます（任意）。

## Qテーブルの自動ロード
- Hunter を「Q」にした場合、以下のファイルが自動で読み込まれます。
  - Hunter 0: `q_table.pkl`
  - Hunter 1: `q_table.pkl2`
- これらのファイルはプロジェクトのルート（この ReadMe と同じ階層）に置いてください。
- 自動読み込みに失敗した場合は、サイドバーに警告が表示され、Lv0 にフォールバックします。

## 技術スタック（主要ライブラリ）
- Python
- Streamlit 1.51.0
- NumPy 2.3.x
- Pandas 2.3.x
- Matplotlib 3.10.x
- そのほか（requirements.txt 参照）
  - pydeck / altair（可視化関連）
  - requests / protobuf など

## 構成（主要ファイル）
- `main.py`: Streamlit アプリ本体
- `game_env.py`: グリッドと位置更新（トーラス）など環境の定義
- `agents.py`: Lv0 の行動ロジック
- `q_utils.py`: Qテーブルから行動を選ぶ共通処理
- `agents_q.py`: QLearningAgent（Qを用いた行動選択）
- `ui_components.py`: グリッド描画（Matplotlib）
- `q_table.pkl`, `q_table.pkl2`: 学習済みQテーブル（任意、Qモードで使用）

## よくあるトラブルと対処
- Port が使用中で起動できない:
  - 別の Streamlit が起動中の可能性があります。停止（Ctrl+C）してから再実行してください。
  - もしくはポートを変更して起動します:
    ```bash
    streamlit run main.py --server.port 8502
    ```
- `ModuleNotFoundError: streamlit` などパッケージが見つからない:
  - 仮想環境が有効化されているか確認し、`pip install -r requirements.txt` を再実行してください。
- Qモードで動かない / 手動選択も失敗する:
  - `q_table.pkl` / `q_table.pkl2` がプロジェクト直下にあるか、ファイル形式が `dict` かを確認してください。
  - 状態キーは `(hx, hy, px, py)`、値は `{"UP": float, "DOWN": float, ...}` の形を想定しています。

## ライセンス・参考
- 研究・学習用のサンプルです。
- 参考: 「他者理解と社会性の獲得メカニズム」におけるハンタータスク
