import tkinter as tk
from tkinter import ttk
import struct

# 通用函數：從指定位址解析數據
def parse_data(data, addr, data_type='B', count=1):
    """
    從數據 buffer 的指定位址解析數據。

    Args:
        data (bytearray): 包含遊戲存檔數據的 bytearray。
        addr (int): 要讀取的數據的起始位址。
        data_type (str, optional): 數據類型，預設為 'B' (unsigned byte)。
        count (int, optional): 要讀取的數據數量，預設為 1。

    Returns:
        tuple: 包含解析後數據的 tuple。 如果發生錯誤，則返回包含預設值 (0) 的 tuple。
    """
    try:
        return struct.unpack_from(f'{count}{data_type}', data, addr)  # 使用 struct.unpack_from 解析數據
    except struct.error as e:
        print(f"錯誤: 無法從位址 {addr} 解析數據: {e}")  # 打印錯誤訊息
        return (0,) * count  # 返回包含預設值 (0) 的 tuple

def update_selected_member_label(member_name):  # 修改此處
    """
    更新標籤頁上方顯示的隊員名稱。

    Args:
        member_name (str): 隊員名稱。
    """
    global selected_member_label, selected_weapon_label, selected_def_label, selected_ring_label, selected_item_label
    #display_text = f"{member_name}-{member_occupation}"  # 組合顯示文字 # 刪除
    selected_member_label.config(text=f"{member_name}")  # **修改此處，只顯示隊員名稱**
    selected_weapon_label.config(text=f"{member_name}")  # **修改此處，只顯示隊員名稱**
    selected_def_label.config(text=f"{member_name}")  # **修改此處，只顯示隊員名稱**
    selected_ring_label.config(text=f"{member_name}")  # **修改此處，只顯示隊員名稱**
    selected_item_label.config(text=f"{member_name}")  # **修改此處，只顯示隊員名稱**

def initialize_labels(member_label, weapon_label, def_label, ring_label, item_label):
    """
    初始化標籤物件。

    Args:
        member_label: 能力標籤頁的標籤物件。
        weapon_label: 武器標籤頁的標籤物件。
        def_label: 防具標籤頁的標籤物件。
        ring_label: 配件標籤頁的標籤物件。
        item_label: 雜項標籤頁的標籤物件。
    """
    global selected_member_label, selected_weapon_label, selected_def_label, selected_ring_label, selected_item_label
    selected_member_label = member_label
    selected_weapon_label = weapon_label
    selected_def_label = def_label
    selected_ring_label = ring_label
    selected_item_label = item_label