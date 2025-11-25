"""
シミュレーションのコアロジックを管理するモジュール。
"""

import streamlit as st
import random
from typing import Dict, Any, Tuple

from src.env.game_env import HunterTaskEnv
from src.agents.lv0 import Lv0Agent
from src.agents.manual import ManualAgent
from src.config import (
    AGENT_ID_HUNTER_0,
    AGENT_ID_HUNTER_1,
    AGENT_ID_PREY_0,
    AGENT_ID_PREY_1,
    CONTROL_MODE_LV0_Q,
    CONTROL_MODE_MANUAL
)

def initialize_simulation():
    """
    シミュレーションの状態を初期化し、st.session_stateに格納する。
    """
    st.session_state.env = HunterTaskEnv(num_hunters=2, num_prey=2)
    st.session_state.agent_0 = Lv0Agent(agent_id=AGENT_ID_HUNTER_0)
    st.session_state.agent_1 = Lv0Agent(agent_id=AGENT_ID_HUNTER_1)
    st.session_state.manual_agent = ManualAgent(agent_id=AGENT_ID_HUNTER_0)
    st.session_state.step_count = 0
    
    st.session_state.captured = {AGENT_ID_PREY_0: False, AGENT_ID_PREY_1: False}
    st.session_state.q_tables = {AGENT_ID_HUNTER_0: None, AGENT_ID_HUNTER_1: None}
    st.session_state.q_agents = {AGENT_ID_HUNTER_0: None, AGENT_ID_HUNTER_1: None}
    
    if 'manual_action_hunter_0' not in st.session_state:
        st.session_state.manual_action_hunter_0 = 0
        
    if 'turn_phase' not in st.session_state:
        st.session_state.turn_phase = 'player'

def check_capture():
    """
    現在の状態に基づいて捕獲判定を行い、st.session_state.captured を更新する。
    """
    state_now = st.session_state.env.get_state()
    h0 = state_now.get(AGENT_ID_HUNTER_0)
    h1 = state_now.get(AGENT_ID_HUNTER_1)
    p0 = state_now.get(AGENT_ID_PREY_0)
    p1 = state_now.get(AGENT_ID_PREY_1)
    
    if p0 in (h0, h1):
        st.session_state.captured[AGENT_ID_PREY_0] = True
    if p1 in (h0, h1):
        st.session_state.captured[AGENT_ID_PREY_1] = True

def move_prey(enabled: bool):
    """
    獲物をランダムに移動させる。
    """
    if not enabled:
        return

    # 移動前の捕獲チェック
    check_capture()
    
    # prey_0
    if not st.session_state.captured[AGENT_ID_PREY_0]:
        a = 0 if random.random() < 0.1 else random.choice([1, 2, 3, 4])
        st.session_state.env.step(agent_id=AGENT_ID_PREY_0, action_id=a)
    
    # prey_1
    if not st.session_state.captured[AGENT_ID_PREY_1]:
        a = 0 if random.random() < 0.1 else random.choice([1, 2, 3, 4])
        st.session_state.env.step(agent_id=AGENT_ID_PREY_1, action_id=a)
        
    # 移動後の捕獲チェック
    check_capture()

def get_agent_action(agent_id: str, control_mode: str, current_state: Dict[str, Tuple[int, int]], debug: bool = False) -> int:
    """
    指定されたエージェントとモードに基づいて行動を決定する。
    """
    # ターゲット決定 (Lv0用フォールバック)
    if agent_id == AGENT_ID_HUNTER_0:
        target_lv0 = AGENT_ID_PREY_1 if st.session_state.captured.get(AGENT_ID_PREY_0, False) else AGENT_ID_PREY_0
    else:
        target_lv0 = AGENT_ID_PREY_0 if st.session_state.captured.get(AGENT_ID_PREY_1, False) else AGENT_ID_PREY_1

    action = 0
    
    # Q-Learning
    if control_mode == CONTROL_MODE_LV0_Q and st.session_state.q_agents.get(agent_id) is not None:
        action, chosen_prey, label = st.session_state.q_agents[agent_id].choose_action(current_state)
        if debug:
            st.info(f"[{agent_id}] mode=Lv0 (Q), chosen={chosen_prey or '-'} action={label or action}")
            
    # Manual
    elif control_mode == CONTROL_MODE_MANUAL:
        # ManualAgentは内部状態を持たず、session_stateから取る形だが、
        # ここでは ManualAgent クラス経由で呼ぶ形を維持
        action = st.session_state.manual_agent.choose_action(current_state)
        if debug:
            st.info(f"[{agent_id}] mode=Manual, action_id={action}")
            
    # Simple (Lv0)
    else:
        agent = st.session_state.agent_0 if agent_id == AGENT_ID_HUNTER_0 else st.session_state.agent_1
        action = agent.choose_action(current_state, target_lv0)
        if debug:
            st.info(f"[{agent_id}] mode=Simple, target={target_lv0} action_id={action}")
            
    return action
