"""
ハンタータスクのシミュレーション環境（グリッドワールド）を定義する。

主な機能：
1. グリッドサイズ（トーラス状）の定義。
2. ハンターおよび獲物の位置情報の保持・管理。
3. エージェントからの行動を受け取り、状態（位置情報）を更新する。
4. 座標がグリッドの端を超えた場合、反対側にループさせる（トーラス処理）。
"""

import numpy as np

# グリッドサイズ（定数）
GRID_SIZE = 20

# 行動の定義（0=停止, 1=上, 2=下, 3=左, 4=右）; 座標系: (x, y) で x は右正, y は下正
ACTIONS = {
    0: (0, 0),   # 停止
    1: (0, -1),  # 上
    2: (0, 1),   # 下
    3: (-1, 0),  # 左
    4: (1, 0)    # 右
}

class HunterTaskEnv:
    
    def __init__(self, num_hunters=2, num_prey=2):
        """
        環境の初期化
        """
        self.grid_size = GRID_SIZE
        self.num_hunters = num_hunters
        self.num_prey = num_prey
        
        # 位置情報を辞書で管理（例：'hunter_0', 'prey_1'）
        self.positions = {}
        self.reset()

    def _normalize_pos(self, pos):
        """
        座標をトーラス状に正規化する（端と端をつなげる）
        """
        x, y = pos
        x = x % self.grid_size
        y = y % self.grid_size
        return (x, y)

    def reset(self):
        """
        ハンターと獲物の位置をランダムに初期化する
        """
        # (仮実装：ひとまず固定位置やランダム配置)
        # 実際には重複しないように配置するロジックが必要
        self.positions['hunter_0'] = self._normalize_pos((0, 0))
        self.positions['hunter_1'] = self._normalize_pos((0, 1))
        self.positions['prey_0'] = self._normalize_pos((10, 10))
        self.positions['prey_1'] = self._normalize_pos((15, 15))
        
        # 現在の状態を返す
        return self.get_state()

    def get_state(self):
        """
        現在の環境の状態（全エージェント・獲物の位置）を返す
        """
        return self.positions

    def step(self, agent_id, action_id):
        """
        指定されたエージェントの行動を実行し、状態を更新する
        """
        if agent_id not in self.positions:
            raise ValueError(f"エージェントID {agent_id} が見つかりません。")
            
        move = ACTIONS.get(action_id)
        if move is None:
            raise ValueError(f"無効な行動ID {action_id} です。")

        current_pos = self.positions[agent_id]
        new_pos = (current_pos[0] + move[0], current_pos[1] + move[1])
        
        # トーラス処理を適用して位置を更新
        self.positions[agent_id] = self._normalize_pos(new_pos)
        
        # (TODO: 将来的に獲物の捕獲判定などもここに追加)
        
        return self.get_state()
