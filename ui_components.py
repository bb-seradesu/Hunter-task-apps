"""
StreamlitアプリケーションのUIコンポーネントを定義する。
(Matplotlibによるグリッド描画：1～20の座標で表示)
"""

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

from game_env import GRID_SIZE

def draw_grid_matplotlib(state):
    """
    現在の状態 (state) をMatplotlibでグリッド描画する。
    内部座標 0-19 を、表示上 1-20 として扱う。
    """
    
    fig, ax = plt.subplots(figsize=(6, 6))
    
    hunter_pos = []
    prey_pos = []
    
    for key, pos in state.items():
        # 内部座標 (0-19) に +1 して描画用座標 (1-20) に変換
        display_pos = (pos[0] + 1, pos[1] + 1) 
        
        if 'hunter' in key:
            hunter_pos.append(display_pos)
        elif 'prey' in key:
            prey_pos.append(display_pos)

    # --- 描画 (1-20 の座標系で行う) ---
    
    if prey_pos:
        prey_x = [p[0] for p in prey_pos]
        prey_y = [p[1] for p in prey_pos]
        ax.scatter(prey_x, prey_y, c='green', marker='o', s=100, label='Prey')

    if hunter_pos:
        hunter_x = [h[0] for h in hunter_pos]
        hunter_y = [h[1] for h in hunter_pos]
        ax.scatter(hunter_x, hunter_y, c='blue', marker='^', s=150, label='Hunter')

    # --- グリッドの設定 (1-20) ---
    display_grid_min = 1
    display_grid_max = GRID_SIZE # 20
    
    # 目盛りを 1 から 20 (or GRID_SIZE) に設定
    ticks = np.arange(display_grid_min, display_grid_max + 1, 1)
    # (例：ステップ数が多くなる場合は 2 刻み (..., 2) にしても良い)
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    
    # グラフの表示範囲を 0.5 から 20.5 (or GRID_SIZE + 0.5) に設定
    ax.set_xlim(display_grid_min - 0.5, display_grid_max + 0.5)
    ax.set_ylim(display_grid_min - 0.5, display_grid_max + 0.5)
    
    # (Y軸の向き：必要に応じて反転 ax.invert_yaxis() )
    
    ax.grid(True)
    ax.legend()
    ax.set_title("Hunter Task Grid")
    
    st.pyplot(fig)
    plt.close(fig)