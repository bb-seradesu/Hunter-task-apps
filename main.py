
"""
ハンタータスクシミュレーションのメインアプリケーション。
"""

import streamlit as st
from src.ui.components import draw_grid_html
from src.ui.sidebar import render_sidebar
from src.game_logic import initialize_simulation
from src.config import (
    AGENT_ID_PREY_0,
    AGENT_ID_PREY_1
)
from src.ui.controls import render_control_buttons, inject_wasd_controls
from src.scenarios.ai_vs_ai import run_ai_vs_ai_step
from src.scenarios.player_vs_ai import run_player_turn, run_ai_turn

# --- 1. アプリケーションの開始 ---
st.title("ハンタータスク シミュレーション")

# --- 2. 状態の初期化 ---
if 'env' not in st.session_state:
    initialize_simulation()

# セーフガード
if 'captured' not in st.session_state:
    st.session_state.captured = {AGENT_ID_PREY_0: False, AGENT_ID_PREY_1: False}

# --- 3. サイドバー設定の読み込み ---
config = render_sidebar()
game_mode = config["game_mode"]
control_h0 = config["control_h0"]
control_h1 = config["control_h1"]
prey_move_enabled = config["prey_move_enabled"]
debug_info_h0 = config["debug_info_h0"]
debug_info_h1 = config["debug_info_h1"]

# --- 4. グリッド描画 ---
if 'env' in st.session_state:
    current_state = st.session_state.env.get_state()
    # 初期化直後などで last_actions が無い場合のガード
    last_actions = st.session_state.get('last_actions', {})
    draw_grid_html(current_state, game_mode, last_actions)

# --- 5. UIコンポーネント（ボタン）とメインロジック ---

col1, col2 = st.columns(2)

with col1:
    # 操作ボタンの描画と実行フラグの取得
    run_step_ai_only, run_step_h0, run_step_h1 = render_control_buttons(game_mode)

with col2:
    # リセットボタン
    if st.button("リセット"):
        initialize_simulation()
        st.session_state.turn_phase = 'player'
        st.rerun()

# --- WASDキーボード操作の有効化 ---
inject_wasd_controls(game_mode)


# --- 6. シミュレーションの実行 ---

# --- ケースA: AI vs AI (一括実行) ---
if run_step_ai_only:
    run_ai_vs_ai_step(control_h0, control_h1, debug_info_h0, debug_info_h1, prey_move_enabled)

# --- ケースB: Player vs AI (Playerターン) ---
if run_step_h0:
    run_player_turn()

# --- ケースC: Player vs AI (AIターン) ---
if run_step_h1:
    run_ai_turn(control_h1, debug_info_h1, prey_move_enabled)

# --- 7. ステータス表示 ---
st.header(f"ステップ: {st.session_state.step_count}")
st.caption(
    f"獲物移動: {'ON' if prey_move_enabled else 'OFF'}"
    f" | 捕獲: prey_0={'済' if st.session_state.captured[AGENT_ID_PREY_0] else '未'}"
    f" / prey_1={'済' if st.session_state.captured[AGENT_ID_PREY_1] else '未'}"
)
