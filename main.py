"""
ハンタータスクシミュレーションのメインアプリケーション。

Streamlitを使用して以下の機能を提供する。
1. シミュレーション環境 (HunterTaskEnv) とエージェント (Lv0Agent) を初期化し、
   Streamlitのセッション状態 (st.session_state) に保持する。
2. グリッドの状態（ハンターと獲物の位置）をテキストで表示する。
3. 「1ステップ進む」ボタンにより、シミュレーションを1ステップ実行する。
4. 「リセット」ボタンにより、環境を初期状態に戻す。
"""

import streamlit as st
import random
import pickle
from game_env import HunterTaskEnv
from agents import Lv0Agent
from ui_components import draw_grid_matplotlib
from q_utils import ACTION_LABEL_TO_ID
from agents_q import QLearningAgent

def initialize_simulation():
    """
    シミュレーションの状態を初期化し、st.session_stateに格納する。
    """
    st.session_state.env = HunterTaskEnv(num_hunters=2, num_prey=2)
    st.session_state.agent_0 = Lv0Agent(agent_id='hunter_0')
    st.session_state.agent_1 = Lv0Agent(agent_id='hunter_1')
    st.session_state.step_count = 0
    # 捕獲状態とQテーブルの入れ物を初期化
    st.session_state.captured = {'prey_0': False, 'prey_1': False}
    st.session_state.q_tables = {'hunter_0': None, 'hunter_1': None}
    st.session_state.q_agents = {'hunter_0': None, 'hunter_1': None}

# --- 1. アプリケーションの開始 ---

st.title("ハンタータスク シミュレーション (Lv.0)")

# --- 2. 状態の初期化 ---
# st.session_stateに 'env' がまだ存在しない場合（＝アプリ起動時）のみ実行
if 'env' not in st.session_state:
    initialize_simulation()
# セーフガード: 既存セッションでも必要キーが無ければ初期化
if 'captured' not in st.session_state:
    st.session_state.captured = {'prey_0': False, 'prey_1': False}
if 'q_tables' not in st.session_state:
    st.session_state.q_tables = {'hunter_0': None, 'hunter_1': None}

# --- サイドバー（設定） ---
prey_move_enabled = st.sidebar.checkbox(
    "獲物を動かす",
    value=True,
    help="ONで獲物が毎ステップランダムに1マス動きます"
)

debug_info_H0 = st.sidebar.checkbox(
    "Hunter0の移動先デバック画面",
    value=False,
    help="ONでHunter0の動作先のデバッグ画面が表示されます。"
)

debug_info_H1 = st.sidebar.checkbox(
    "Hunter1の移動先デバック画面",
    value=False,
    help="ONでHunter1の動作先のデバッグ画面が表示されます。"
)

# （次ステップの準備のみ）Qテーブル読み込みUI
with st.sidebar.expander("Qテーブル（読み込みのみ）", expanded=False):
    file_options = ["(未使用)", "q_table.pkl", "q_table.pkl2"]
    sel_h0 = st.selectbox("Hunter 0 用", file_options, index=0, key="sel_h0")
    sel_h1 = st.selectbox("Hunter 1 用", file_options, index=0, key="sel_h1")

    def _load_q(path):
        try:
            with open(path, "rb") as f:
                q = pickle.load(f)
            if isinstance(q, dict):
                n = len(q)
                # サンプルキーを最大3件表示
                sample_keys = list(q.keys())[:3]
                st.write(f"{path}: dict, keys={n}, sample={sample_keys}")
            else:
                st.write(f"{path}: type={type(q)}")
            return q
        except Exception as e:
            st.warning(f"{path} の読み込みに失敗: {e}")
            return None

    st.session_state.q_tables['hunter_0'] = _load_q(sel_h0) if sel_h0 != "(未使用)" else None
    st.session_state.q_tables['hunter_1'] = _load_q(sel_h1) if sel_h1 != "(未使用)" else None

    # Qエージェントの用意（q_table が選ばれている場合のみ）
    if 'q_agents' not in st.session_state:
        st.session_state.q_agents = {'hunter_0': None, 'hunter_1': None}

    if st.session_state.q_tables['hunter_0'] is not None:
        st.session_state.q_agents['hunter_0'] = QLearningAgent(st.session_state.q_tables['hunter_0'], 'hunter_0')
    else:
        st.session_state.q_agents['hunter_0'] = None

    if st.session_state.q_tables['hunter_1'] is not None:
        st.session_state.q_agents['hunter_1'] = QLearningAgent(st.session_state.q_tables['hunter_1'], 'hunter_1')
    else:
        st.session_state.q_agents['hunter_1'] = None

# ハンター制御モード
control_h0 = st.sidebar.selectbox("Hunter 0 制御", ["Lv0", "Q"], index=0, key="ctrl_h0")
control_h1 = st.sidebar.selectbox("Hunter 1 制御", ["Lv0", "Q"], index=0, key="ctrl_h1")

# Qテーブルの自動ロード（ユーザーが選ばなくても使えるように）
default_paths = {
    'hunter_0': 'q_table.pkl',
    'hunter_1': 'q_table.pkl2',
}

# st.session_state の箱が無い場合は作る
if 'q_agents' not in st.session_state:
    st.session_state.q_agents = {'hunter_0': None, 'hunter_1': None}
if 'q_tables' not in st.session_state:
    st.session_state.q_tables = {'hunter_0': None, 'hunter_1': None}

# 制御モードが Q のハンターについて、自動で q_table を読み込む
for hunter_id in ('hunter_0', 'hunter_1'):
    if hunter_id == 'hunter_0':
        control_mode = control_h0
    else:
        control_mode = control_h1

    if control_mode == "Q":
        agent_exists = False
        if hunter_id in st.session_state.q_agents:
            if st.session_state.q_agents[hunter_id] is not None:
                agent_exists = True

        if agent_exists is False:
            path = default_paths[hunter_id]
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

# --- 3. UIコンポーネント（ボタン）の配置 ---

col1, col2 = st.columns(2)

with col1:
    # 1ステップ進めるボタン
    run_step = st.button("1ステップ進む")

with col2:
    # リセットボタン
    if st.button("リセット"):
        initialize_simulation()
        st.rerun() # 画面を即座に再読み込みして初期状態を表示

# --- 4. メインロジック（シミュレーションの実行） ---

if run_step:
    st.session_state.step_count += 1
    
    # 現状の環境状態を取得
    current_state = st.session_state.env.get_state()
    
    if debug_info_H0:
        st.subheader("Debug Info (Hunter 0)")
        h0_pos_before = current_state.get('hunter_0')
        p0_pos = current_state.get('prey_0')
        st.info(f"[Before] Hunter 0 Pos: {h0_pos_before} | Target Prey 0 Pos: {p0_pos}")
    if debug_info_H1:
        st.subheader("Debug Info (Hunter 1)")
        h1_pos_before = current_state.get('hunter_1')
        p1_pos = current_state.get('prey_1')
        st.info(f"[Before] Hunter 1 Pos: {h1_pos_before} | Target Prey 1 Pos: {p1_pos}")
        
    # --- エージェントの行動決定 ---
    # 捕獲状況に応じたLv0のターゲット切替（フォールバック用）
    target0_lv0 = 'prey_1' if st.session_state.captured.get('prey_0', False) else 'prey_0'
    target1_lv0 = 'prey_0' if st.session_state.captured.get('prey_1', False) else 'prey_1'

    # Hunter 0
    if control_h0 == "Q" and st.session_state.q_agents.get('hunter_0') is not None:
        action_0, chosen_prey0, label0 = st.session_state.q_agents['hunter_0'].choose_action(current_state)
        if debug_info_H0:
            st.info(f"[H0] mode=Q, chosen={chosen_prey0 or '-'} action={label0 or action_0}")
    else:
        action_0 = st.session_state.agent_0.choose_action(current_state, target0_lv0)
        if debug_info_H0:
            st.info(f"[H0] mode=Lv0, target={target0_lv0} action_id={action_0}")

    # Hunter 1
    if control_h1 == "Q" and st.session_state.q_agents.get('hunter_1') is not None:
        action_1, chosen_prey1, label1 = st.session_state.q_agents['hunter_1'].choose_action(current_state)
        if debug_info_H1:
            st.info(f"[H1] mode=Q, chosen={chosen_prey1 or '-'} action={label1 or action_1}")
    else:
        action_1 = st.session_state.agent_1.choose_action(current_state, target1_lv0)
        if debug_info_H1:
            st.info(f"[H1] mode=Lv0, target={target1_lv0} action_id={action_1}")

    # --- 環境の状態更新 ---
    # (注：本来は同時に行動すべきだが、簡易的に順番に行動させる)
    st.session_state.env.step(agent_id='hunter_0', action_id=action_0)
    st.session_state.env.step(agent_id='hunter_1', action_id=action_1)

    # --- 捕獲判定（ハンターと同じマスの獲物は以後停止） ---
    state_after = st.session_state.env.get_state()
    h0 = state_after.get('hunter_0')
    h1 = state_after.get('hunter_1')
    p0 = state_after.get('prey_0')
    p1 = state_after.get('prey_1')
    if p0 in (h0, h1):
        st.session_state.captured['prey_0'] = True
    if p1 in (h0, h1):
        st.session_state.captured['prey_1'] = True

    # --- 獲物の移動（任意） ---
    if prey_move_enabled:
        def _rand_action():
            # 10%で停止、90%で上下左右を等確率に選択
            return 0 if random.random() < 0.1 else random.choice([1, 2, 3, 4])

        # 獲物を動かす前にも重なりを最終確認（保険）
        state_mid = st.session_state.env.get_state()
        h0_mid = state_mid.get('hunter_0')
        h1_mid = state_mid.get('hunter_1')
        p0_mid = state_mid.get('prey_0')
        p1_mid = state_mid.get('prey_1')
        if p0_mid in (h0_mid, h1_mid):
            st.session_state.captured['prey_0'] = True
        if p1_mid in (h0_mid, h1_mid):
            st.session_state.captured['prey_1'] = True

        # prey_0 を必要に応じて移動 → 直後に再度捕獲チェック
        if not st.session_state.captured['prey_0']:
            st.session_state.env.step(agent_id='prey_0', action_id=_rand_action())
            state_after_p0 = st.session_state.env.get_state()
            p0_new = state_after_p0.get('prey_0')
            h0_new = state_after_p0.get('hunter_0')
            h1_new = state_after_p0.get('hunter_1')
            if p0_new in (h0_new, h1_new):
                st.session_state.captured['prey_0'] = True

        # prey_1 も同様
        if not st.session_state.captured['prey_1']:
            st.session_state.env.step(agent_id='prey_1', action_id=_rand_action())
            state_after_p1 = st.session_state.env.get_state()
            p1_new = state_after_p1.get('prey_1')
            h0_new = state_after_p1.get('hunter_0')
            h1_new = state_after_p1.get('hunter_1')
            if p1_new in (h0_new, h1_new):
                st.session_state.captured['prey_1'] = True
            

# --- 5. 状態の描画 ---

st.header(f"ステップ: {st.session_state.step_count}")
st.caption(
    f"獲物移動: {'ON' if prey_move_enabled else 'OFF'}"
    f" | 捕獲: prey_0={'済' if st.session_state.captured['prey_0'] else '未'}"
    f" / prey_1={'済' if st.session_state.captured['prey_1'] else '未'}"
)

# 現在の全エージェントと獲物の位置情報を表示
current_state = st.session_state.env.get_state()
draw_grid_matplotlib(current_state)

# (TODO: 将来的には、ここをグリッド描画に置き換える)
