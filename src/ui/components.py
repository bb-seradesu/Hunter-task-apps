"""
StreamlitアプリケーションのUIコンポーネントを定義する。
(Matplotlibによるグリッド描画：1～20の座標で表示)
"""

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

from src.env.game_env import GRID_SIZE

def draw_grid_matplotlib(state, game_mode="AI and AI", last_actions=None):
    """
    現在の状態 (state) をMatplotlibでグリッド描画する。
    内部座標 0-19 を、表示上 1-20 として扱う。
    last_actions: {agent_id: action_id} の辞書。向きの決定に使用。
    """
    
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # 各エージェントの位置を収集
    hunter_0_pos = None
    hunter_1_pos = None
    prey_pos = []
    
    for key, pos in state.items():
        display_pos = (pos[0] + 1, pos[1] + 1)
        
        if key == 'hunter_0':
            hunter_0_pos = display_pos
        elif key == 'hunter_1':
            hunter_1_pos = display_pos
        elif 'prey' in key:
            # prey_0 -> 0, prey_1 -> 1 を取り出す
            try:
                pid = int(key.split('_')[1])
            except:
                pid = 0
            prey_pos.append((display_pos, pid))

    # --- 描画 (1-20 の座標系で行う) ---
    
    # 行動IDから回転角度への変換 (Matplotlibのマーカーはデフォルトで上向き)
    # 0: STAY (上向きのまま), 1: UP (0度), 2: DOWN (180度), 3: LEFT (90度), 4: RIGHT (270度)
    # 注意: Matplotlibの回転は反時計回り。
    # ^ (上) を基準にする。
    # UP(1): 0度
    # DOWN(2): 180度
    # LEFT(3): 90度
    # RIGHT(4): 270度 (-90度)
    
    def _get_marker_rotation(action_id):
        if action_id == 1: return 0    # UP
        if action_id == 2: return 180  # DOWN
        if action_id == 3: return 90   # LEFT
        if action_id == 4: return 270  # RIGHT
        return 0 # STAY or Default
        
    # 獲物 (Green)
    if prey_pos:
        # 位置とIDを分離
        prey_x = [p[0][0] for p in prey_pos]
        prey_y = [p[0][1] for p in prey_pos]
        prey_ids = [p[1] for p in prey_pos]
        
        ax.scatter(prey_x, prey_y, c='green', marker='o', s=100, label='Prey')
        
        # 獲物番号を表示
        for px, py, pid in zip(prey_x, prey_y, prey_ids):
            ax.text(px, py, str(pid), fontsize=10, color='white', ha='center', va='center', fontweight='bold')

    # Hunter 0 (Player: Blue, AI: Cyan/Blue)
    if hunter_0_pos:
        color_h0 = 'blue' if game_mode == "Player and AI" else 'cyan'
        label_h0 = 'Player (H0)' if game_mode == "Player and AI" else 'Hunter 0'
        
        # 向きの決定
        rot = 0
        if last_actions and 'hunter_0' in last_actions:
            rot = _get_marker_rotation(last_actions['hunter_0'])
            
        # マーカーの作成 (回転付き)
        # marker=(numsides, style, angle) は正多角形用なので、
        # ここでは MarkerStyle を使うのが確実だが、scatter は個別の MarkerStyle を受け付けにくい。
        # しかし1点ずつプロットするなら問題ない。
        from matplotlib.markers import MarkerStyle
        m = MarkerStyle("^")
        m._transform = m.get_transform().rotate_deg(rot)
        
        ax.scatter([hunter_0_pos[0]], [hunter_0_pos[1]], c=color_h0, marker=m, s=150, label=label_h0)

    # Hunter 1 (AI: Red)
    if hunter_1_pos:
        rot = 0
        if last_actions and 'hunter_1' in last_actions:
            rot = _get_marker_rotation(last_actions['hunter_1'])
            
        from matplotlib.markers import MarkerStyle
        m = MarkerStyle("^") # 統一して ^ を使い、回転させる
        m._transform = m.get_transform().rotate_deg(rot)
        
        ax.scatter([hunter_1_pos[0]], [hunter_1_pos[1]], c='red', marker=m, s=150, label='Hunter 1 (AI)')

    # --- グリッドの設定 (1-20) ---
    display_grid_min = 1
    display_grid_max = GRID_SIZE # 20
    
    # 目盛りを 1 から 20 (or GRID_SIZE) に設定
    ticks = np.arange(display_grid_min, display_grid_max + 1, 1)
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    
    # グラフの表示範囲を 0.5 から 20.5 (or GRID_SIZE + 0.5) に設定
    ax.set_xlim(display_grid_min - 0.5, display_grid_max + 0.5)
    ax.set_ylim(display_grid_min - 0.5, display_grid_max + 0.5)
    
    # Y軸を反転させて、直感的な座標系（上が1、下が20）にするか、
    # あるいは数学的な座標系（下が1、上が20）にするか。
    # 元のコードでは反転していなかったので、そのままにする（下が小さい値、上が大きい値）。
    # ただし、グリッドワールドの慣習として (0,0) が左上なら反転が必要だが、
    # ここでは元の実装に従う。
    ax.invert_yaxis() # 一般的な行列座標((0,0)が左上)に合わせるため反転
    
    ax.grid(True)
    # 凡例を枠外に表示して見やすくする
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    ax.set_title("Hunter Task Grid")
    
    st.pyplot(fig)
    plt.close(fig)