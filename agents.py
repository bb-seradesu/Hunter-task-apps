"""
ハンタータスクを実行するエージェント（Lv.0）を定義する。

主な機能：
1. 基礎行動モデル P(A|S,G) に基づく行動選択（Lv.0戦略）。
2. 現時点では「意図G（目標の獲物）」に向かって最短距離で移動する
   「決定論的ルール」として実装する。
"""

import numpy as np
from game_env import GRID_SIZE

class Lv0Agent:
    
    def __init__(self, agent_id):
        """
        エージェントの初期化
        """
        self.agent_id = agent_id
        self.grid_size = GRID_SIZE

    def _calculate_torus_distance(self, from_pos, to_pos):
        """
        トーラス空間における2点間の最短差分を返す (dx, dy)
        - x: 水平（右が正）
        - y: 垂直（下が正）
        """
        from_x, from_y = from_pos
        to_x, to_y = to_pos

        dx = to_x - from_x
        dy = to_y - from_y

        # グリッドの半分より遠い場合は反対側が近い（トーラス）
        if dx > self.grid_size / 2:
            dx -= self.grid_size
        elif dx < -self.grid_size / 2:
            dx += self.grid_size

        if dy > self.grid_size / 2:
            dy -= self.grid_size
        elif dy < -self.grid_size / 2:
            dy += self.grid_size

        return dx, dy

    def choose_action(self, state, intention_g):
        """
        状態Sと意図Gに基づき、行動Aを決定する（簡易版 P(A|S,G)）
        
        引数：
        state (dict): 環境の現在の状態 (例：{'hunter_0': (0,0), 'prey_0': (10,10)})
        intention_g (str): 意図（目標）とする獲物のID (例：'prey_0')
        
        戻り値：
        action_id (int): 決定した行動ID (0:停止, 1:上, 2:下, 3:左, 4:右)
        """
        
        my_pos = state.get(self.agent_id)
        target_pos = state.get(intention_g)
        
        if my_pos is None or target_pos is None:
            return 0 # 停止（エラーケース）

        # 目標までのトーラス距離（方向）を計算
        dx, dy = self._calculate_torus_distance(my_pos, target_pos)

        # 距離が0なら停止
        if dx == 0 and dy == 0:
            return 0 # 停止

        # より距離の大きい軸を優先して詰める（座標系: x=右正, y=下正）
        if abs(dy) >= abs(dx):
            # 垂直方向（上下）
            return 2 if dy > 0 else 1  # 下/上
        else:
            # 水平方向（左右）
            return 4 if dx > 0 else 3  # 右/左
