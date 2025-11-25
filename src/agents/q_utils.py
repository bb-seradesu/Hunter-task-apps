"""
目的
- Qテーブルを使って次の一手を決める共通処理。

使い方
- ACTION_LABEL_TO_ID: 行動ラベルを action_id に変換する。
- q_choose_best_action_for_target(q, hx, hy, px, py):
  行動ラベルとそのスコアを返す。見つからないときは (None, None)。
- q_choose_action(state, hunter_id, q):
  (action_id, prey_id, action_label) を返す。候補が無いときは (0, None, "STAY")。
"""

from typing import Any, Dict, Optional, Tuple
import streamlit as st

# 行動ラベル → 環境の行動ID（上=1, 下=2, 左=3, 右=4, 停止=0）
ACTION_LABEL_TO_ID: Dict[str, int] = {
    "UP": 1,
    "DOWN": 2,
    "LEFT": 3,
    "RIGHT": 4,
    "STAY": 0,
}


def q_choose_best_action_for_target(
    q_table: Any,
    hx: int,
    hy: int,
    px: int,
    py: int,
) -> Tuple[Optional[str], Optional[float]]:
    """
    指定のハンター位置(hx,hy)と獲物位置(px,py)に対して、
    Qテーブルが最も良いと判断した (行動ラベル, スコア) を返す。
    見つからないときは (None, None)。
    """
    if isinstance(q_table, dict) is False:
        return None, None

    state_key = (hx, hy, px, py)
    q_dict = q_table.get(state_key)

    if isinstance(q_dict, dict) is False:
        return None, None
    if len(q_dict) == 0:
        return None, None

    best_label: Optional[str] = None
    best_value: Optional[float] = None

    for action_label, score in q_dict.items():
        if best_value is None:
            best_label = action_label
            best_value = score
        else:
            if score > best_value:
                best_label = action_label
                best_value = score

    return best_label, best_value


def q_choose_action(
    state: Dict[str, Tuple[int, int]],
    hunter_id: str,
    q_table: Any,
) -> Tuple[Optional[int], Optional[str], Optional[str]]:
    """
    prey_0 と prey_1 を評価して、より良い方の行動を選ぶ。
    捕獲済みの獲物は候補から外す。
    候補が無いときは (0, None, "STAY")。
    """
    if isinstance(q_table, dict) is False:
        return None, None, None

    hunter_pos = state.get(hunter_id)
    if hunter_pos is None:
        return None, None, None

    hx = hunter_pos[0]
    hy = hunter_pos[1]

    if "captured" in st.session_state:
        captured = st.session_state.captured
    else:
        captured = {"prey_0": False, "prey_1": False}

    candidates: list[tuple[str, str, float]] = []

    for prey_id in ("prey_0", "prey_1"):
        if prey_id in captured:
            if captured[prey_id] is True:
                continue

        prey_pos = state.get(prey_id)
        if prey_pos is None:
            continue

        px = prey_pos[0]
        py = prey_pos[1]

        label, value = q_choose_best_action_for_target(q_table, hx, hy, px, py)
        if label is None:
            continue

        if value is None:
            score = float("-inf")
        else:
            score = float(value)

        candidates.append((prey_id, label, score))

    if len(candidates) == 0:
        return ACTION_LABEL_TO_ID["STAY"], None, "STAY"

    best_prey_id: Optional[str] = None
    best_label: Optional[str] = None
    best_score: Optional[float] = None

    for prey_id, label, score in candidates:
        if best_score is None:
            best_prey_id = prey_id
            best_label = label
            best_score = score
        else:
            if score > best_score:
                best_prey_id = prey_id
                best_label = label
                best_score = score

    if best_label in ACTION_LABEL_TO_ID:
        action_id = ACTION_LABEL_TO_ID[best_label]
    else:
        action_id = ACTION_LABEL_TO_ID["STAY"]

    return action_id, best_prey_id, best_label
