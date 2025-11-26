"""
StreamlitアプリケーションのUIコンポーネントを定義する。
(Matplotlibによるグリッド描画：1～20の座標で表示)
"""

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

from src.env.game_env import GRID_SIZE

def draw_grid_html(state, game_mode="AI and AI", last_actions=None):
    """
    現在の状態 (state) をHTML/CSSで描画する（軽量版）。
    Matplotlibの画像生成オーバーヘッドを回避し、ネットワーク転送量を削減する。
    """
    
    # グリッドサイズ
    grid_size = GRID_SIZE # 20
    
    # エージェント位置のマップを作成
    # (x, y) -> list of html_content
    cell_contents = {}
    
    for key, pos in state.items():
        x, y = pos
        
        # 向きの取得
        rot = 0
        if last_actions and key in last_actions:
            action_id = last_actions[key]
            # HTMLのrotationは時計回りが標準的だが、transform: rotate(deg) は時計回り。
            # Matplotlibのロジック(UP=0)に合わせる。
            # UP(1): 0deg
            # DOWN(2): 180deg
            # LEFT(3): -90deg (or 270deg)
            # RIGHT(4): 90deg
            if action_id == 1: rot = 0
            elif action_id == 2: rot = 180
            elif action_id == 3: rot = -90
            elif action_id == 4: rot = 90
            
        if key == 'hunter_0':
            color = 'blue' if game_mode == "Player and AI" else 'cyan'
            # 三角形 (CSS border trick or unicode)
            # Unicode ▲ (U+25B2) を使用し、transformで回転させる
            content = f'<div style="color:{color}; transform: rotate({rot}deg); display:inline-block; font-size: 20px;">▲</div>'
            
        elif key == 'hunter_1':
            # Hunter 1 (AI: Red)
            content = f'<div style="color:red; transform: rotate({rot}deg); display:inline-block; font-size: 20px;">▲</div>'
            
        elif 'prey' in key:
            try:
                pid = int(key.split('_')[1])
            except:
                pid = 0
            # 丸 (CSS border-radius) + 数字
            content = f'<div style="background-color:green; color:white; border-radius:50%; width:20px; height:20px; text-align:center; line-height:20px; font-size:12px; font-weight:bold; margin:auto;">{pid}</div>'
            
        else:
            continue
            
        if (x, y) not in cell_contents:
            cell_contents[(x, y)] = []
        cell_contents[(x, y)].append(content)

    # HTML生成
    html = '<div style="display: flex; justify-content: center;">'
    html += '<table style="border-collapse: collapse; border: 2px solid #333;">'
    
    for y in range(grid_size):
        html += '<tr>'
        for x in range(grid_size):
            cell_style = 'width: 25px; height: 25px; border: 1px solid #ddd; text-align: center; vertical-align: middle; padding: 0;'
            
            # コンテンツの取得
            contents = cell_contents.get((x, y), [])
            inner_html = "".join(contents)
            
            html += f'<td style="{cell_style}">{inner_html}</td>'
        html += '</tr>'
    
    html += '</table></div>'
    
    # Streamlitで表示
    st.markdown(html, unsafe_allow_html=True)