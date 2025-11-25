"""
アプリケーション全体で使用する定数定義。
"""

# ゲームモード
GAME_MODE_AI_AND_AI = "AI and AI"
GAME_MODE_PLAYER_AND_AI = "Player and AI"

# エージェント制御モード
CONTROL_MODE_SIMPLE = "Simple"
CONTROL_MODE_LV0_Q = "Lv0 (Q)"
CONTROL_MODE_MANUAL = "Manual"

# デフォルトファイルパス
DEFAULT_Q_TABLE_PATHS = {
    'hunter_0': 'q_table.pkl',
    'hunter_1': 'q_table.pkl2',
}

# エージェントID
AGENT_ID_HUNTER_0 = 'hunter_0'
AGENT_ID_HUNTER_1 = 'hunter_1'
AGENT_ID_PREY_0 = 'prey_0'
AGENT_ID_PREY_1 = 'prey_1'
