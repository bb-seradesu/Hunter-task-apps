"""
目的
- Qテーブルを使って、ハンターの次の一手を決めるエージェント。

使い方
- 生成: agent = QLearningAgent(q_table, agent_id)
- 実行: action_id, prey_id, action_label = agent.choose_action(state)
  - state は {'hunter_0': (x,y), 'prey_0': (x,y), ...} の形
  - 戻り値の action_id は環境の行動ID（1=上,2=下,3=左,4=右,0=停止）
"""

from typing import Any, Dict, Tuple, Optional
from src.agents.q_utils import q_choose_action


class QLearningAgent:
    def __init__(self, q_table: Any, agent_id: str) -> None:
        """
        q_table: 学習済みQテーブル（dict を想定）
        agent_id: 'hunter_0' / 'hunter_1' など
        """
        self.q_table = q_table
        self.agent_id = agent_id

    def choose_action(self, state: Dict[str, Tuple[int, int]]) -> Tuple[Optional[int], Optional[str], Optional[str]]:
        """
        state を見て、(action_id, 選んだ獲物ID, 行動ラベル) を返す。
        捕獲済みの獲物は q_utils 側で除外されます。
        """
        action_id, prey_id, label = q_choose_action(state, self.agent_id, self.q_table)
        return action_id, prey_id, label
