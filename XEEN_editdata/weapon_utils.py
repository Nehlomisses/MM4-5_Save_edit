import struct
from tkinter import messagebox
import XEEN_editdata
from XEEN_editdata.common_dicts import (
    weapon_type_mapping,
    WEAPON_ID_DESCRIPTIONS,
    WEAPON_SPECIAL_EFFECTS,
    WAP_Eq,
)

# 宣告全局變數
address_map = None
weapon_vars = None # 宣告為全域變數
save_data = None

def parse_weapon_data(data, start_addr):
    """
    解析隊員的武器數據。

    Args:
        data (bytearray): 包含遊戲存檔數據的 bytearray。
        start_addr (int): 武器數據的起始位址。

    Returns:
        list: 包含解析後武器數據的列表。
    """
    weapons = []  # 存儲武器數據的列表
    for i in range(9):  # 每個隊員有 9 個武器欄位
        addr = start_addr + i * 4  # 計算武器數據的位址
        weapon_data = XEEN_editdata.gui_utils.parse_data(data, addr, count=4)  # 使用通用函數解析 4 個位元組的數據，簡單說就是讀取前面4組
        weapons.append(weapon_data)  # 將武器數據添加到列表中
    return weapons  # 返回武器數據列表

def update_weapon_data(selected_member):
    """
    更新 GUI 顯示的武器數據。

    Args:
        selected_member (str): 目前選取的隊員。
    """
    global address_map, save_data, weapon_vars  # 宣告為全域變數
    try:
        base_addr = address_map[selected_member]  # 根據隊員名稱獲取武器數據的起始位址
        weapon_data = parse_weapon_data(save_data, base_addr)  # 解析武器數據
        for idx, weapon in enumerate(weapon_data):  # 遍歷武器數據
            if idx < len(weapon_vars):  # 確保 GUI 元素存在
                # 使用武器數據更新 GUI 變數
                weapon_vars[idx][0].set(weapon_type_mapping.get(weapon[0], "未知"))
                weapon_vars[idx][1].set(WEAPON_ID_DESCRIPTIONS.get(weapon[1], "未知"))
                weapon_vars[idx][2].set(WEAPON_SPECIAL_EFFECTS.get(weapon[2], "未知"))
                weapon_vars[idx][3].set(WAP_Eq.get(weapon[3], "未知"))
    except KeyError:
        messagebox.showerror("錯誤", f"找不到 '{selected_member}' 的武器地址。")  # 顯示錯誤訊息
    except Exception as e:
        messagebox.showerror("錯誤", f"更新武器數據時發生錯誤：{e}")  # 顯示錯誤訊息


def on_weapon_select(selected_member, team_name_mapping, team_listbox):
    """
    在武器選單中恢復隊員選取狀態。
    """
    try:
        if selected_member and team_name_mapping:  # 增加判斷，確保有選取隊員且隊伍資訊不為空
            member_name = list(team_name_mapping.keys())[list(team_name_mapping.values()).index(selected_member)]  # 獲取隊員名稱
            if member_name in team_listbox.get(0, 'end'):   # 檢查隊員是否存在於清單中
                team_listbox.selection_clear(0, 'end')  # 清除所有選取
                team_listbox.selection_set(team_listbox.get(0, 'end').index(member_name))  # 重新選取隊員
    except ValueError:
        print("警告: 無法恢復隊員選擇。")  # 打印警告訊息
    except Exception as e:
        messagebox.showerror("錯誤", f"恢復武器選單的隊員選取狀態發生錯誤：{e}")  # 顯示錯誤訊息

def save_weapon_data(member):
    """
    保存 GUI 中修改後的武器數據到存檔檔案。

    Args:
        member (str): 隊員名稱。
    """
    global address_map, weapon_vars, save_data # 宣告為全域變數
    try:
        base_addr = address_map[member]  # 根據隊員名稱獲取武器數據的起始位址
        for idx, weapon_var in enumerate(weapon_vars):  # 遍歷武器 GUI 變數
            addr = base_addr + idx * 4  # 計算武器數據的位址
            # 從 GUI 變數獲取武器數據，並轉換為對應的 ID
            weapon1 = next((key for key, value in weapon_type_mapping.items() if value == weapon_var[0].get()), None)
            weapon2 = next((key for key, value in WEAPON_ID_DESCRIPTIONS.items() if value == weapon_var[1].get()), None)
            weapon3 = next((key for key, value in WEAPON_SPECIAL_EFFECTS.items() if value == weapon_var[2].get()), None)
            weapon4 = next((key for key, value in WAP_Eq.items() if value == weapon_var[3].get()), None)
            if weapon1 is not None and weapon2 is not None and weapon3 is not None:
                struct.pack_into('B', save_data, addr, weapon1)  # 保存武器類型
                struct.pack_into('B', save_data, addr + 1, weapon2)  # 保存武器 ID
                struct.pack_into('B', save_data, addr + 2, weapon3)  # 保存武器特殊效果
                struct.pack_into('B', save_data, addr + 3, weapon4)  # 保存武器裝備類型
    except KeyError:
        messagebox.showerror("錯誤", f"找不到 '{member}' 的武器地址。")  # 顯示錯誤訊息
    except Exception as e:
        messagebox.showerror("錯誤", f"保存武器數據時發生錯誤：{e}")  # 顯示錯誤訊息