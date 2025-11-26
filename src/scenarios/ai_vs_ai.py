"""
AI vs AI モードの実行ロジック。
"""

import streamlit as st
from src.config import AGENT_ID_HUNTER_0, AGENT_ID_HUNTER_1
from src.game_logic import check_capture, move_prey, get_agent_action

def run_ai_vs_ai_step(control_h0: str, control_h1: str, debug_info_h0: bool, debug_info_h1: bool, prey_move_enabled: bool):
    """
    AI vs AI モードの1ステップを実行する。
    """
    st.session_state.step_count += 1
    current_state = st.session_state.env.get_state()
    
    # Hunter 0 Action
    action_0 = get_agent_action(AGENT_ID_HUNTER_0, control_h0, current_state, debug_info_h0)

    # Hunter 1 Action
    action_1 = get_agent_action(AGENT_ID_HUNTER_1, control_h1, current_state, debug_info_h1)

    # 実行
    st.session_state.env.step(agent_id=AGENT_ID_HUNTER_0, action_id=action_0)
    st.session_state.last_actions[AGENT_ID_HUNTER_0] = action_0
    
    st.session_state.env.step(agent_id=AGENT_ID_HUNTER_1, action_id=action_1)
    st.session_state.last_actions[AGENT_ID_HUNTER_1] = action_1
    
    check_capture()
    move_prey(prey_move_enabled)
    st.rerun()
