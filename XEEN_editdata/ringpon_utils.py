import struct
from tkinter import messagebox
import XEEN_editdata
from XEEN_editdata.common_dicts import (
    weapon_type_mapping,
    ring_ID_EQ,
)

# 宣告全局變數
address_map = None
ringpon_vars = None # 宣告為全域變數
save_data = None

# 解析配件數據
def parse_ringpon_data(data, start_addr):
    """
    解析隊員的配件數據。

    Args:
        data (bytearray): 包含遊戲存檔數據的 bytearray。
        start_addr (int): 配件數據的起始位址。

    Returns:
        list: 包含解析後配件數據的列表。
    """
    ringpons = []  # 存儲配件數據的列表
    for i in range(9):  # 每個隊員有 9 個配件欄位
        addr = start_addr + i * 4  # 計算配件數據的位址
        ringpon_data = XEEN_editdata.gui_utils.parse_data(data, addr, count=2)  # 使用通用函數解析 2 個位元組的數據
        ringpons.append(ringpon_data)  # 將配件數據添加到列表中
    return ringpons  # 返回配件數據列表

# 更新顯示的配件數據
def update_ringpon_data(member):
    """
    更新 GUI 顯示的配件數據。

    Args:
        member (str): 隊員名稱。
    """
    try:
        base_addr = address_map[member] + 0x48  # 根據隊員名稱獲取配件數據的起始位址 (相較於武器位址偏移 0x48)
        ringpon_data = parse_ringpon_data(save_data, base_addr)  # 解析配件數據
        for idx, ringpon in enumerate(ringpon_data):  # 遍歷配件數據
            if idx < len(ring_vars):  # 確保 GUI 元素存在
                # 使用配件數據更新 GUI 變數
                ring_vars[idx][0].set(weapon_type_mapping.get(ringpon[0], "未知"))
                ring_vars[idx][1].set(ring_ID_EQ.get(ringpon[1], "未知"))
    except KeyError:
        messagebox.showerror("錯誤", f"找不到 '{member}' 的配件地址。")  # 顯示錯誤訊息
    except Exception as e:
        messagebox.showerror("錯誤", f"更新配件數據時發生錯誤：{e}")  # 顯示錯誤訊息

# 保存配件數據
def save_ringpon_data(member):
    """
    保存 GUI 中修改後的配件數據到存檔檔案。

    Args:
        member (str): 隊員名稱。
    """
    try:
        base_addr = address_map[member] + 0x48  # 根據隊員名稱獲取配件數據的起始位址
        for idx, ringpon_var in enumerate(ring_vars):  # 遍歷配件 GUI 變數
            addr = base_addr + idx * 4  # 計算配件數據的位址
            # 從 GUI 變數獲取配件數據，並轉換為對應的 ID
            ringpon1 = next((key for key, value in weapon_type_mapping.items() if value == ringpon_var[0].get()), None)
            ringpon2 = next((key for key, value in ring_ID_EQ.items() if value == ringpon_var[1].get()), None)

            if ringpon1 is not None and ringpon2 is not None:
                struct.pack_into('B', save_data, addr, ringpon1)  # 保存配件類型
                struct.pack_into('B', save_data, addr + 1, ringpon2)  # 保存配件屬性
    except KeyError:
        messagebox.showerror("錯誤", f"找不到 '{member}' 的配件地址。")  # 顯示錯誤訊息
    except Exception as e:
        messagebox.showerror("錯誤", f"保存配件數據時發生錯誤：{e}")  # 顯示錯誤訊息

# 恢復配件選單的隊員選取狀態
def on_ringpon_select(*args):
    """
    在配件選單中恢復隊員選取狀態。
    """
    try:
        global selected_member
        if selected_member and team_name_mapping:  # 增加判斷，確保有選取隊員且隊伍資訊不為空
            member_name = list(team_name_mapping.keys())[list(team_name_mapping.values()).index(selected_member)]  # 獲取隊員名稱
            if member_name in team_listbox.get(0, 'end'):  # 檢查隊員是否存在於清單中
                team_listbox.selection_clear(0, 'end')  # 清除所有選取
                team_listbox.selection_set(team_listbox.get(0, 'end').index(member_name))  # 重新選取隊員
    except ValueError:
        print("警告: 無法恢復隊員選擇。")  # 打印警告訊息
    except Exception as e:
        messagebox.showerror("錯誤", f"恢復配件選單的隊員選取狀態發生錯誤：{e}")  # 顯示錯誤訊息