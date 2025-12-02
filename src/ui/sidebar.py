"""
サイドバーのUIロジックを管理するモジュール。
"""

import streamlit as st
import pickle
import pandas as pd
from typing import Dict, Any

from src.config import (
    GAME_MODE_AI_AND_AI,
    GAME_MODE_PLAYER_AND_AI,
    CONTROL_MODE_SIMPLE,
    CONTROL_MODE_LV0_Q,
    CONTROL_MODE_MANUAL,
    DEFAULT_Q_TABLE_PATHS,
    AGENT_ID_HUNTER_0,
    AGENT_ID_HUNTER_1
)
from src.agents.q_learning import QLearningAgent

def _load_q_table(path: str) -> Any:
    """Qテーブルをファイルから読み込むヘルパー関数"""
    try:
        with open(path, "rb") as f:
            q = pickle.load(f)
        if isinstance(q, dict):
            n = len(q)
            sample_keys = list(q.keys())[:3]
            st.write(f"{path}: dict, keys={n}, sample={sample_keys}")
        else:
            st.write(f"{path}: type={type(q)}")
        return q
    except Exception as e:
        st.warning(f"{path} の読み込みに失敗: {e}")
        return None

def render_sidebar() -> Dict[str, Any]:
    """
    サイドバーを描画し、設定値を辞書として返す。
    副作用として、st.session_state に Qエージェント/テーブルをセットアップする。
    """
    
    # --- 基本設定 ---
    prey_move_enabled = st.sidebar.checkbox(
        "獲物を動かす",
        value=True,
        help="ONで獲物が毎ステップランダムに1マス動きます"
    )

    debug_info_h0 = st.sidebar.checkbox(
        "Hunter0の移動先デバック画面",
        value=False,
        help="ONでHunter0の動作先のデバッグ画面が表示されます。"
    )

    debug_info_h1 = st.sidebar.checkbox(
        "Hunter1の移動先デバック画面",
        value=False,
        help="ONでHunter1の動作先のデバッグ画面が表示されます。"
    )

    # --- ゲームモード選択 ---
    game_mode = st.sidebar.radio(
        "ゲームモード",
        [GAME_MODE_AI_AND_AI, GAME_MODE_PLAYER_AND_AI],
        index=0,
        help="Player and AIモードでは、Hunter 0を操作できます"
    )

    # --- ハンター制御モード ---
    if game_mode == GAME_MODE_AI_AND_AI:
        control_h0 = st.sidebar.selectbox("Hunter 0 制御", [CONTROL_MODE_SIMPLE, CONTROL_MODE_LV0_Q], index=1, key="ctrl_h0")
    else:
        control_h0 = CONTROL_MODE_MANUAL
        st.sidebar.info("Hunter 0 はプレイヤー操作です")

    control_h1 = st.sidebar.selectbox("Hunter 1 制御", [CONTROL_MODE_SIMPLE, CONTROL_MODE_LV0_Q], index=1, key="ctrl_h1")

    # --- Qテーブル読み込みUI (手動) ---
    with st.sidebar.expander("Qテーブル（読み込みのみ）", expanded=False):
        file_options = ["(未使用)", "q_table.pkl", "q_table.pkl2"]
        sel_h0 = st.selectbox("Hunter 0 用", file_options, index=1, key="sel_h0")
        sel_h1 = st.selectbox("Hunter 1 用", file_options, index=2, key="sel_h1")

        # st.session_state の箱が無い場合は作る
        if 'q_agents' not in st.session_state:
            st.session_state.q_agents = {AGENT_ID_HUNTER_0: None, AGENT_ID_HUNTER_1: None}
        if 'q_tables' not in st.session_state:
            st.session_state.q_tables = {AGENT_ID_HUNTER_0: None, AGENT_ID_HUNTER_1: None}

        # 選択されたファイルを読み込む
        st.session_state.q_tables[AGENT_ID_HUNTER_0] = _load_q_table(sel_h0) if sel_h0 != "(未使用)" else None
        st.session_state.q_tables[AGENT_ID_HUNTER_1] = _load_q_table(sel_h1) if sel_h1 != "(未使用)" else None

        # エージェントの初期化
        if st.session_state.q_tables[AGENT_ID_HUNTER_0] is not None:
            st.session_state.q_agents[AGENT_ID_HUNTER_0] = QLearningAgent(st.session_state.q_tables[AGENT_ID_HUNTER_0], AGENT_ID_HUNTER_0)
        else:
            st.session_state.q_agents[AGENT_ID_HUNTER_0] = None

        if st.session_state.q_tables[AGENT_ID_HUNTER_1] is not None:
            st.session_state.q_agents[AGENT_ID_HUNTER_1] = QLearningAgent(st.session_state.q_tables[AGENT_ID_HUNTER_1], AGENT_ID_HUNTER_1)
        else:
            st.session_state.q_agents[AGENT_ID_HUNTER_1] = None

    # --- Qテーブルの自動ロード ---
    # 制御モードが Q のハンターについて、まだロードされていなければ自動でデフォルトを読み込む
    for hunter_id in (AGENT_ID_HUNTER_0, AGENT_ID_HUNTER_1):
        control_mode = control_h0 if hunter_id == AGENT_ID_HUNTER_0 else control_h1

        if control_mode == CONTROL_MODE_LV0_Q:
            agent_exists = False
            if hunter_id in st.session_state.q_agents:
                if st.session_state.q_agents[hunter_id] is not None:
                    agent_exists = True

            if agent_exists is False:
                path = DEFAULT_Q_TABLE_PATHS[hunter_id]
                try:
                    with open(path, "rb") as f:
                        q = pickle.load(f)

                    if isinstance(q, dict):
                        st.session_state.q_tables[hunter_id] = q
                        st.session_state.q_agents[hunter_id] = QLearningAgent(q, hunter_id)
                        st.sidebar.caption(f"{hunter_id}: {path} を自動読み込みしました")
                    else:
                        st.sidebar.warning(f"{hunter_id}: {path} は想定外の形式です")
                except Exception as e:
                    st.sidebar.warning(f"{hunter_id}: {path} の自動読み込みに失敗しました: {e}")

    # --- ログダウンロード ---
    st.sidebar.markdown("---")
    if 'history' in st.session_state and st.session_state.history:
        df_log = pd.DataFrame(st.session_state.history)
        csv = df_log.to_csv(index=False).encode('utf-8')
        
        st.sidebar.download_button(
            label="ログをダウンロード (CSV)",
            data=csv,
            file_name='hunter_task_log.csv',
            mime='text/csv',
        )
    else:
        st.sidebar.caption("ログ: データなし")

    return {
        "game_mode": game_mode,
        "control_h0": control_h0,
        "control_h1": control_h1,
        "prey_move_enabled": prey_move_enabled,
        "debug_info_h0": debug_info_h0,
        "debug_info_h1": debug_info_h1
    }
