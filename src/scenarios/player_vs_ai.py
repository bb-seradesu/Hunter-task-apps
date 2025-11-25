"""
Player vs AI モードの実行ロジック。
"""

import streamlit as st
import time
from src.config import AGENT_ID_HUNTER_0, AGENT_ID_HUNTER_1
from src.game_logic import check_capture, move_prey, get_agent_action

def run_player_turn():
    """
    Player vs AI モード：プレイヤーのターンを実行する。
    """
    st.session_state.step_count += 1
    
    # プレイヤーの行動を実行
    action_0 = st.session_state.manual_action_hunter_0
    st.session_state.env.step(agent_id=AGENT_ID_HUNTER_0, action_id=action_0)
    
    check_capture()
    
    # フェーズをAIに移行してリロード
    st.session_state.turn_phase = 'ai'
    st.rerun()

def run_ai_turn(control_h1: str, debug_info_h1: bool, prey_move_enabled: bool):
    """
    Player vs AI モード：AIのターンを実行する。
    """
    # 少し待機（演出）
    time.sleep(0.1)
    
    current_state = st.session_state.env.get_state()
    
    # Hunter 1 Action
    action_1 = get_agent_action(AGENT_ID_HUNTER_1, control_h1, current_state, debug_info_h1)
        
    st.session_state.env.step(agent_id=AGENT_ID_HUNTER_1, action_id=action_1)
    
    check_capture()
    move_prey(prey_move_enabled)
    
    # フェーズをPlayerに戻してリロード
    st.session_state.turn_phase = 'player'
    st.rerun()
