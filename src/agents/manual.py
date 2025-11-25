"""
マニュアル操作用エージェントを定義する。

主な機能：
1. 外部（UI）から指定された行動を実行する。
2. choose_action では、st.session_state に保存された次の行動を返す。
"""

import streamlit as st
from typing import Dict, Tuple, Optional

class ManualAgent:
    def __init__(self, agent_id: str):
        """
        エージェントの初期化
        """
        self.agent_id = agent_id

    def choose_action(self, state: Dict[str, Tuple[int, int]], intention_g: Optional[str] = None) -> int:
        """
        UIで設定された次の行動を返す。
        
        引数：
        state: 現在の状態（マニュアル操作では使用しないが、インターフェース統一のため受け取る）
        intention_g: 意図（同上）
        
        戻り値：
        action_id (int): 行動ID (0:停止, 1:上, 2:下, 3:左, 4:右)
        """
        # セッション状態から次の行動を取得
        # キーは 'manual_action_{agent_id}' とする
        action_key = f'manual_action_{self.agent_id}'
        
        if action_key in st.session_state:
            return st.session_state[action_key]
        
        return 0 # デフォルトは停止
