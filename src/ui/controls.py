"""
操作パネル（ボタン、キーボード入力）のUIロジックを管理するモジュール。
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import Tuple

from src.config import GAME_MODE_PLAYER_AND_AI

def render_control_buttons(game_mode: str) -> Tuple[bool, bool, bool]:
    """
    操作ボタンを描画し、実行フラグを返す。
    
    Returns:
        (run_step_ai_only, run_step_h0, run_step_h1)
    """
    run_step_ai_only = False
    run_step_h0 = False
    run_step_h1 = False

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
        
    return run_step_ai_only, run_step_h0, run_step_h1

def inject_wasd_controls(game_mode: str):
    """
    WASDキーボード操作用のJavaScriptを注入する。
    """
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
