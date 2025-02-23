import struct
from tkinter import messagebox
import XEEN_editdata
from XEEN_editdata.common_dicts import (
    weapon_type_mapping,
    def_Amo,
)

# 宣告全局變數
address_map = None
defpon_vars = None # 宣告為全域變數
save_data = None

# 解析防具數據
def parse_defpon_data(data, start_addr):
    """
    解析隊員的防具數據。

    Args:
        data (bytearray): 包含遊戲存檔數據的 bytearray。
        start_addr (int): 防具數據的起始位址。

    Returns:
        list: 包含解析後防具數據的列表。
    """
    defpons = []  # 存儲防具數據的列表
    for i in range(9):  # 每個隊員有 9 個防具欄位
        addr = start_addr + i * 4  # 計算防具數據的位址
        defpon_data = XEEN_editdata.gui_utils.parse_data(data, addr, count=2)  # 使用通用函數解析 2 個位元組的數據
        defpons.append(defpon_data)  # 將防具數據添加到列表中
    return defpons  # 返回防具數據列表

# 更新顯示的防具數據
def update_defpon_data(member):
    """
    更新 GUI 顯示的防具數據。

    Args:
        member (str): 隊員名稱。
    """
    try:
        base_addr = address_map[member] + 0x24  # 根據隊員名稱獲取防具數據的起始位址 (相較於武器位址偏移 0x24)
        defpon_data = parse_defpon_data(save_data, base_addr)  # 解析防具數據
        for idx, defpon in enumerate(defpon_data):  # 遍歷防具數據
            if idx < len(defpon_vars):  # 確保 GUI 元素存在
                # 使用防具數據更新 GUI 變數
                defpon_vars[idx][0].set(weapon_type_mapping.get(defpon[0], "未知"))
                defpon_vars[idx][1].set(def_Amo.get(defpon[1], "未知"))
    except KeyError:
        messagebox.showerror("錯誤", f"找不到 '{member}' 的防具地址。")  # 顯示錯誤訊息
    except Exception as e:
        messagebox.showerror("錯誤", f"更新防具數據時發生錯誤：{e}")  # 顯示錯誤訊息

# 保存防具數據
def save_defpon_data(member):
    """
    保存 GUI 中修改後的防具數據到存檔檔案。

    Args:
        member (str): 隊員名稱。
    """
    try:
        base_addr = address_map[member] + 0x24  # 根據隊員名稱獲取防具數據的起始位址
        for idx, defpon_var in enumerate(defpon_vars):  # 遍歷防具 GUI 變數
            addr = base_addr + idx * 4  # 計算防具數據的位址
            # 從 GUI 變數獲取防具數據，並轉換為對應的 ID
            defpon1 = next((key for key, value in weapon_type_mapping.items() if value == defpon_var[0].get()), None)
            defpon2 = next((key for key, value in def_Amo.items() if value == defpon_var[1].get()), None)

            if defpon1 is not None and defpon2 is not None:
                struct.pack_into('B', save_data, addr, defpon1)  # 保存防具類型
                struct.pack_into('B', save_data, addr + 1, defpon2)  # 保存防具屬性
    except KeyError:
        messagebox.showerror("錯誤", f"找不到 '{member}' 的防具地址。")  # 顯示錯誤訊息
    except Exception as e:
        messagebox.showerror("錯誤", f"保存防具數據時發生錯誤：{e}")  # 顯示錯誤訊息

# 恢復防具選單的隊員選取狀態
def on_defpon_select(*args):
    """
    在防具選單中恢復隊員選取狀態。
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
        messagebox.showerror("錯誤", f"恢復防具選單的隊員選取狀態發生錯誤：{e}")  # 顯示錯誤訊息
