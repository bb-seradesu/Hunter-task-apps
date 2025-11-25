"""
ハンタータスクシミュレーションのメインアプリケーション。
"""

import streamlit as st
import streamlit.components.v1 as components
import time

from src.ui.components import draw_grid_matplotlib
from src.ui.sidebar import render_sidebar
from src.game_logic import (
    initialize_simulation,
    check_capture,
    move_prey,
    get_agent_action
)
from src.config import (
    GAME_MODE_PLAYER_AND_AI,
    AGENT_ID_HUNTER_0,
    AGENT_ID_HUNTER_1,
    AGENT_ID_PREY_0,
    AGENT_ID_PREY_1
)

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
    draw_grid_matplotlib(current_state, game_mode)

# --- 5. UIコンポーネント（ボタン）とメインロジック ---

col1, col2 = st.columns(2)

# フラグの初期化
run_step_ai_only = False # AI vs AI 用
run_step_h0 = False      # Player vs AI (Playerターン) 用
run_step_h1 = False      # Player vs AI (AIターン) 用

with col1:
    if game_mode == GAME_MODE_PLAYER_AND_AI:
        # プレイヤーのターン
        if st.session_state.turn_phase == 'player':
            st.write("Hunter 0 操作 (Your Turn)")
            
            # 上段（上ボタン）
            c_null1, c_up, c_null2 = st.columns([1, 1, 1])
            with c_up:
                if st.button("↑"):
                    st.session_state.manual_action_hunter_0 = 1
                    run_step_h0 = True
            
            # 中段（左、待機、右）
            c_left, c_stay, c_right = st.columns([1, 1, 1])
            with c_left:
                if st.button("←"):
                    st.session_state.manual_action_hunter_0 = 3
                    run_step_h0 = True
            with c_stay:
                if st.button("・"):
                    st.session_state.manual_action_hunter_0 = 0
                    run_step_h0 = True
            with c_right:
                if st.button("→"):
                    st.session_state.manual_action_hunter_0 = 4
                    run_step_h0 = True
                    
            # 下段（下ボタン）
            c_null3, c_down, c_null4 = st.columns([1, 1, 1])
            with c_down:
                if st.button("↓"):
                    st.session_state.manual_action_hunter_0 = 2
                    run_step_h0 = True
        
        else:
            # AIのターン（待機中）
            st.info("AI Thinking...")
            run_step_h1 = True # 自動的にAIターンを実行

    else:
        # AI vs AI
        run_step_ai_only = st.button("1ステップ進む")

with col2:
    # リセットボタン
    if st.button("リセット"):
        initialize_simulation()
        st.session_state.turn_phase = 'player'
        st.rerun()

# --- WASDキーボード操作の有効化 ---
if game_mode == GAME_MODE_PLAYER_AND_AI and st.session_state.turn_phase == 'player':
    components.html(
        """
        <script>
        const doc = window.parent.document;
        doc.addEventListener('keydown', function(e) {
            const key = e.key.toLowerCase();
            let targetText = null;
            if (key === 'w') targetText = "↑";
            if (key === 'a') targetText = "←";
            if (key === 's') targetText = "↓";
            if (key === 'd') targetText = "→";
            if (key === ' ') targetText = "・";

            if (targetText) {
                const buttons = Array.from(doc.querySelectorAll('button'));
                const button = buttons.find(b => b.innerText === targetText);
                if (button) {
                    button.click();
                }
            }
        });
        </script>
        """,
        height=0,
        width=0,
    )

# --- 6. シミュレーションの実行 ---

# --- ケースA: AI vs AI (一括実行) ---
if run_step_ai_only:
    st.session_state.step_count += 1
    current_state = st.session_state.env.get_state()
    
    # Hunter 0 Action
    action_0 = get_agent_action(AGENT_ID_HUNTER_0, control_h0, current_state, debug_info_h0)

    # Hunter 1 Action
    action_1 = get_agent_action(AGENT_ID_HUNTER_1, control_h1, current_state, debug_info_h1)

    # 実行
    st.session_state.env.step(agent_id=AGENT_ID_HUNTER_0, action_id=action_0)
    st.session_state.env.step(agent_id=AGENT_ID_HUNTER_1, action_id=action_1)
    
    check_capture()
    move_prey(prey_move_enabled)
    st.rerun()

# --- ケースB: Player vs AI (Playerターン) ---
if run_step_h0:
    st.session_state.step_count += 1
    
    # プレイヤーの行動を実行
    action_0 = st.session_state.manual_action_hunter_0
    st.session_state.env.step(agent_id=AGENT_ID_HUNTER_0, action_id=action_0)
    
    check_capture()
    
    # フェーズをAIに移行してリロード
    st.session_state.turn_phase = 'ai'
    st.rerun()

# --- ケースC: Player vs AI (AIターン) ---
if run_step_h1:
    # 少し待機（演出）
    time.sleep(0.5)
    
    current_state = st.session_state.env.get_state()
    
    # Hunter 1 Action
    action_1 = get_agent_action(AGENT_ID_HUNTER_1, control_h1, current_state, debug_info_h1)
        
    st.session_state.env.step(agent_id=AGENT_ID_HUNTER_1, action_id=action_1)
    
    check_capture()
    move_prey(prey_move_enabled)
    
    # フェーズをPlayerに戻してリロード
    st.session_state.turn_phase = 'player'
    st.rerun()

# --- 7. ステータス表示 ---
st.header(f"ステップ: {st.session_state.step_count}")
st.caption(
    f"獲物移動: {'ON' if prey_move_enabled else 'OFF'}"
    f" | 捕獲: prey_0={'済' if st.session_state.captured[AGENT_ID_PREY_0] else '未'}"
    f" / prey_1={'済' if st.session_state.captured[AGENT_ID_PREY_1] else '未'}"
)
