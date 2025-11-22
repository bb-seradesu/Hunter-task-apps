"""
check_pkl.py
.pkl ファイルの中身を覗き見る（introspect）ための専用スクリプト
"""

import pickle
import sys

# 確認したいファイル名を指定
# (必要に応じて "q_table.pkl2" に変更してください)
FILE_TO_INSPECT = "q_table.pkl"

print(f"\n--- {FILE_TO_INSPECT} の中身（Introspect） ---")

try:
    with open(FILE_TO_INSPECT, "rb") as f:
        # pickleファイルをロード（解凍）
        data = pickle.load(f)

    print(f"\n[1] データの型 (Type):")
    print(type(data))

    # 型に応じて、さらに詳細を表示
    if isinstance(data, dict):
        # 中身が「辞書 (dict)」の場合
        print(f"\n[2] キーの総数 (Keys):")
        print(len(data.keys()))
        
        keys_list = list(data.keys())
        
        print("\n[3] キーの例 (Key samples) [最初の5件]:")
        print(keys_list[:5])
        
        if keys_list:
            print(f"\n[4] 最初のキー `{keys_list[0]}` の中身 (Value):")
            print(data[keys_list[0]])

    elif hasattr(data, 'shape'):
        # 中身が「Numpy配列 (ndarray)」などの場合
        print(f"\n[2] データの形状 (Shape):")
        print(data.shape)
        
    else:
        # それ以外（リストなど）
        try:
            print(f"\n[2] データの長さ (Length):")
            print(len(data))
            print("\n[3] データの例 (Sample) [最初の5件]:")
            print(data[:5])
        except TypeError:
            print("\n[2] 辞書、配列、リスト以外のデータ構造です。")

    print("\n--- 確認終了 ---")

except FileNotFoundError:
    print(f"エラー: ファイル '{FILE_TO_INSPECT}' が見つかりません。")
except Exception as e:
    print(f"読み込み中にエラーが発生しました: {e}")