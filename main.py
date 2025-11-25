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
import streamlit.components.v1 as components
import random
import pickle
import time
from src.env.game_env import HunterTaskEnv
from src.agents.lv0 import Lv0Agent
from src.ui.components import draw_grid_matplotlib
from src.agents.q_utils import ACTION_LABEL_TO_ID
from src.agents.q_learning import QLearningAgent
from src.agents.manual import ManualAgent

def initialize_simulation():
    """
    シミュレーションの状態を初期化し、st.session_stateに格納する。
    """
    st.session_state.env = HunterTaskEnv(num_hunters=2, num_prey=2)
    st.session_state.agent_0 = Lv0Agent(agent_id='hunter_0')
    st.session_state.agent_1 = Lv0Agent(agent_id='hunter_1')
    st.session_state.manual_agent = ManualAgent(agent_id='hunter_0') # マニュアル用エージェント
    st.session_state.step_count = 0
    # 捕獲状態とQテーブルの入れ物を初期化
    st.session_state.captured = {'prey_0': False, 'prey_1': False}
    st.session_state.q_tables = {'hunter_0': None, 'hunter_1': None}
    st.session_state.q_agents = {'hunter_0': None, 'hunter_1': None}
    
    # マニュアル操作の初期化
    if 'manual_action_hunter_0' not in st.session_state:
        st.session_state.manual_action_hunter_0 = 0
        
    # ターンフェーズの初期化 (player or ai)
    if 'turn_phase' not in st.session_state:
        st.session_state.turn_phase = 'player'

# --- 1. アプリケーションの開始 ---

st.title("ハンタータスク シミュレーション")

# --- 2. 状態の初期化 ---
# st.session_stateに 'env' がまだ存在しない場合（＝アプリ起動時）のみ実行
if 'env' not in st.session_state:
    initialize_simulation()

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

# ゲームモード選択
game_mode = st.sidebar.radio(
    "ゲームモード",
    ["AI and AI", "Player and AI"],
    index=0,
    help="Player and AIモードでは、Hunter 0を操作できます"
)

# ハンター制御モード
if game_mode == "AI and AI":
    control_h0 = st.sidebar.selectbox("Hunter 0 制御", ["Simple", "Lv0 (Q)"], index=1, key="ctrl_h0")
else:
    control_h0 = "Manual"
    st.sidebar.info("Hunter 0 はプレイヤー操作です")

control_h1 = st.sidebar.selectbox("Hunter 1 制御", ["Simple", "Lv0 (Q)"], index=1, key="ctrl_h1")

# Qテーブル読み込みUI
with st.sidebar.expander("Qテーブル（読み込みのみ）", expanded=False):
    file_options = ["(未使用)", "q_table.pkl", "q_table.pkl2"]
    sel_h0 = st.selectbox("Hunter 0 用", file_options, index=1, key="sel_h0")
    sel_h1 = st.selectbox("Hunter 1 用", file_options, index=2, key="sel_h1")

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

    # st.session_state の箱が無い場合は作る
    if 'q_agents' not in st.session_state:
        st.session_state.q_agents = {'hunter_0': None, 'hunter_1': None}
    if 'q_tables' not in st.session_state:
        st.session_state.q_tables = {'hunter_0': None, 'hunter_1': None}

    st.session_state.q_tables['hunter_0'] = _load_q(sel_h0) if sel_h0 != "(未使用)" else None
    st.session_state.q_tables['hunter_1'] = _load_q(sel_h1) if sel_h1 != "(未使用)" else None

    if st.session_state.q_tables['hunter_0'] is not None:
        st.session_state.q_agents['hunter_0'] = QLearningAgent(st.session_state.q_tables['hunter_0'], 'hunter_0')
    else:
        st.session_state.q_agents['hunter_0'] = None

    if st.session_state.q_tables['hunter_1'] is not None:
        st.session_state.q_agents['hunter_1'] = QLearningAgent(st.session_state.q_tables['hunter_1'], 'hunter_1')
    else:
        st.session_state.q_agents['hunter_1'] = None

# Qテーブルの自動ロード（ユーザーが選ばなくても使えるように）
default_paths = {
    'hunter_0': 'q_table.pkl',
    'hunter_1': 'q_table.pkl2',
}

# 制御モードが Q のハンターについて、自動で q_table を読み込む
for hunter_id in ('hunter_0', 'hunter_1'):
    if hunter_id == 'hunter_0':
        control_mode = control_h0
    else:
        control_mode = control_h1

    if control_mode == "Lv0 (Q)":
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

# グリッド描画をここに移動
if 'env' in st.session_state:
    current_state = st.session_state.env.get_state()
    draw_grid_matplotlib(current_state, game_mode)

# --- 3. UIコンポーネント（ボタン）とメインロジック ---

col1, col2 = st.columns(2)

# フラグの初期化
run_step_ai_only = False # AI vs AI 用
run_step_h0 = False      # Player vs AI (Playerターン) 用
run_step_h1 = False      # Player vs AI (AIターン) 用

with col1:
    if game_mode == "Player and AI":
        # プレイヤーのターン
        if st.session_state.turn_phase == 'player':
            st.write("Hunter 0 操作 (Your Turn)")
            
            # 上段（上ボタン）
            c_null1, c_up, c_null2 = st.columns([1, 1, 1])
            with c_up:
                if st.button("↑"):
                    st.session_state.manual_action_hunter_0 = 1
                    run_step_h0 = True
            
            # 中段（左、待機、右）
            c_left, c_stay, c_right = st.columns([1, 1, 1])
            with c_left:
                if st.button("←"):
                    st.session_state.manual_action_hunter_0 = 3
                    run_step_h0 = True
            with c_stay:
                if st.button("・"):
                    st.session_state.manual_action_hunter_0 = 0
                    run_step_h0 = True
            with c_right:
                if st.button("→"):
                    st.session_state.manual_action_hunter_0 = 4
                    run_step_h0 = True
                    
            # 下段（下ボタン）
            c_null3, c_down, c_null4 = st.columns([1, 1, 1])
            with c_down:
                if st.button("↓"):
                    st.session_state.manual_action_hunter_0 = 2
                    run_step_h0 = True
        
        else:
            # AIのターン（待機中）
            st.info("AI Thinking...")
            run_step_h1 = True # 自動的にAIターンを実行

    else:
        # AI vs AI
        run_step_ai_only = st.button("1ステップ進む")

with col2:
    # リセットボタン
    if st.button("リセット"):
        initialize_simulation()
        st.session_state.turn_phase = 'player' # フェーズもリセット
        st.rerun()

# --- WASDキーボード操作の有効化 ---
# Player and AI モードのときのみ有効にする
if game_mode == "Player and AI" and st.session_state.turn_phase == 'player':
    components.html(
        """
        <script>
        const doc = window.parent.document;
        doc.addEventListener('keydown', function(e) {
            const key = e.key.toLowerCase();
            let targetText = null;
            if (key === 'w') targetText = "↑";
            if (key === 'a') targetText = "←";
            if (key === 's') targetText = "↓";
            if (key === 'd') targetText = "→";
            if (key === ' ') targetText = "・";

            if (targetText) {
                const buttons = Array.from(doc.querySelectorAll('button'));
                const button = buttons.find(b => b.innerText === targetText);
                if (button) {
                    button.click();
                }
            }
        });
        </script>
        """,
        height=0,
        width=0,
    )

# --- 4. シミュレーションの実行 ---

# 共通関数: 捕獲判定
def check_capture():
    state_now = st.session_state.env.get_state()
    h0 = state_now.get('hunter_0')
    h1 = state_now.get('hunter_1')
    p0 = state_now.get('prey_0')
    p1 = state_now.get('prey_1')
    if p0 in (h0, h1):
        st.session_state.captured['prey_0'] = True
    if p1 in (h0, h1):
        st.session_state.captured['prey_1'] = True

# 共通関数: 獲物の移動
def move_prey():
    if prey_move_enabled:
        # 獲物を動かす前にも重なりを最終確認
        check_capture()
        
        # prey_0
        if not st.session_state.captured['prey_0']:
            # 10%で停止、90%で移動
            a = 0 if random.random() < 0.1 else random.choice([1, 2, 3, 4])
            st.session_state.env.step(agent_id='prey_0', action_id=a)
        
        # prey_1
        if not st.session_state.captured['prey_1']:
            a = 0 if random.random() < 0.1 else random.choice([1, 2, 3, 4])
            st.session_state.env.step(agent_id='prey_1', action_id=a)
            
        # 移動後の捕獲判定
        check_capture()

# --- ケースA: AI vs AI (一括実行) ---
if run_step_ai_only:
    st.session_state.step_count += 1
    current_state = st.session_state.env.get_state()
    
    # ターゲット決定
    target0_lv0 = 'prey_1' if st.session_state.captured.get('prey_0', False) else 'prey_0'
    target1_lv0 = 'prey_0' if st.session_state.captured.get('prey_1', False) else 'prey_1'

    # Hunter 0 Action
    if control_h0 == "Lv0 (Q)" and st.session_state.q_agents.get('hunter_0') is not None:
        action_0, _, _ = st.session_state.q_agents['hunter_0'].choose_action(current_state)
    else:
        action_0 = st.session_state.agent_0.choose_action(current_state, target0_lv0)

    # Hunter 1 Action
    if control_h1 == "Lv0 (Q)" and st.session_state.q_agents.get('hunter_1') is not None:
        action_1, _, _ = st.session_state.q_agents['hunter_1'].choose_action(current_state)
    else:
        action_1 = st.session_state.agent_1.choose_action(current_state, target1_lv0)

    # 実行
    st.session_state.env.step(agent_id='hunter_0', action_id=action_0)
    st.session_state.env.step(agent_id='hunter_1', action_id=action_1)
    
    # 捕獲判定
    check_capture()
    
    move_prey()
    st.rerun()

# --- ケースB: Player vs AI (Playerターン) ---
if run_step_h0:
    st.session_state.step_count += 1
    
    # プレイヤーの行動を実行
    action_0 = st.session_state.manual_action_hunter_0
    st.session_state.env.step(agent_id='hunter_0', action_id=action_0)
    
    # 捕獲判定（自分が動いて捕まえたか）
    check_capture()
    
    # フェーズをAIに移行してリロード
    st.session_state.turn_phase = 'ai'
    st.rerun()

# --- ケースC: Player vs AI (AIターン) ---
if run_step_h1:
    # 少し待機（演出）
    time.sleep(0.5)
    
    current_state = st.session_state.env.get_state()
    
    # Hunter 1 Action
    target1_lv0 = 'prey_0' if st.session_state.captured.get('prey_1', False) else 'prey_1'
    if control_h1 == "Lv0 (Q)" and st.session_state.q_agents.get('hunter_1') is not None:
        action_1, _, _ = st.session_state.q_agents['hunter_1'].choose_action(current_state)
    else:
        action_1 = st.session_state.agent_1.choose_action(current_state, target1_lv0)
        
    st.session_state.env.step(agent_id='hunter_1', action_id=action_1)
    
    # 捕獲判定
    check_capture()
    
    move_prey()
    
    # フェーズをPlayerに戻してリロード
    st.session_state.turn_phase = 'player'
    st.rerun()
# --- 5. 状態の描画 ---

st.header(f"ステップ: {st.session_state.step_count}")
st.caption(
    f"獲物移動: {'ON' if prey_move_enabled else 'OFF'}"
    f" | 捕獲: prey_0={'済' if st.session_state.captured['prey_0'] else '未'}"
    f" / prey_1={'済' if st.session_state.captured['prey_1'] else '未'}"
)

# 現在の全エージェントと獲物の位置情報を表示
# current_state = st.session_state.env.get_state()
# draw_grid_matplotlib(current_state, game_mode)

# (TODO: 将来的には、ここをグリッド描画に置き換える)
