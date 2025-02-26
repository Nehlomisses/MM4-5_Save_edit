import struct
from tkinter import messagebox
import XEEN_editdata
from XEEN_editdata.common_dicts import (
    item_ID,
    item_type_mapping,
)

# 宣告全局變數
address_map = None
itempon_vars = None # 宣告為全域變數
save_data = None

# 解析雜項數據
def parse_itempon_data(data, start_addr):
    """
    解析隊員的雜項數據。

    Args:
        data (bytearray): 包含遊戲存檔數據的 bytearray。
        start_addr (int): 雜項數據的起始位址。

    Returns:
        list: 包含解析後雜項數據的列表。
    """
    itempons = []  # 存儲雜項數據的列表
    for i in range(9):  # 每個隊員有 9 個雜項欄位
        addr = start_addr + i * 4  # 計算雜項數據的位址
        itempon_data = XEEN_editdata.gui_utils.parse_data(data, addr, count=3)  # 使用通用函數解析 3 個位元組的數據
        itempons.append(itempon_data)  # 將雜項數據添加到列表中
    return itempons  # 返回雜項數據列表

# 更新顯示的雜項數據
def update_itempon_data(member):
    """
    更新 GUI 顯示的雜項數據。

    Args:
        member (str): 隊員名稱。
    """
    try:
        base_addr = address_map[member] + 0x6C  # 根據隊員名稱獲取雜項數據的起始位址 (相較於武器位址偏移 0x6C)
        itempon_data = parse_itempon_data(save_data, base_addr)  # 解析雜項數據
        for idx, itempon in enumerate(itempon_data):  # 遍歷雜項數據
            if idx < len(item_vars):  # 確保 GUI 元素存在
                # 使用雜項數據更新 GUI 變數
                item_vars[idx][0].set(item_ID.get(itempon[0], "未知"))
                item_vars[idx][1].set(item_type_mapping.get(itempon[1], "未知"))
                item_vars[idx][2].set(itempon[2])  # 顯示使用次數
    except KeyError:
        messagebox.showerror("錯誤", f"找不到 '{member}' 的雜項地址。")  # 顯示錯誤訊息
    except Exception as e:
        messagebox.showerror("錯誤", f"更新雜項數據時發生錯誤：{e}")  # 顯示錯誤訊息

# 保存雜項數據
def save_itempon_data(member):
    """
    保存 GUI 中修改後的雜項數據到存檔檔案。

    Args:
        member (str): 隊員名稱。
    """
    try:
        base_addr = address_map[member] + 0x6C  # 根據隊員名稱獲取雜項數據的起始位址
        for idx, itempon_var in enumerate(item_vars):  # 遍歷雜項 GUI 變數
            addr = base_addr + idx * 4  # 計算雜項數據的位址
            # 從 GUI 變數獲取雜項數據，並轉換為對應的 ID
            itempon1 = next((key for key, value in item_ID.items() if value == itempon_var[0].get()), None)
            itempon2 = next((key for key, value in item_type_mapping.items() if value == itempon_var[1].get()), None)
            try:
                itempon3 = int(itempon_var[2].get())  # 獲取使用次數
                itempon3 = max(0, min(63, itempon3))  # 限制使用次數範圍為 0~63
            except ValueError:
                itempon3 = 0  # 若輸入值無效，則設為 0

            if itempon1 is not None and itempon2 is not None:
                struct.pack_into('B', save_data, addr, itempon1)  # 保存物品 ID
                struct.pack_into('B', save_data, addr + 1, itempon2)  # 保存物品類型
                struct.pack_into('B', save_data, addr + 2, itempon3)  # 保存使用次數
    except KeyError:
        messagebox.showerror("錯誤", f"找不到 '{member}' 的雜項地址。")  # 顯示錯誤訊息
    except Exception as e:
        messagebox.showerror("錯誤", f"保存雜項數據時發生錯誤：{e}")  # 顯示錯誤訊息

# 恢復雜項選單的隊員選取狀態
def on_itempon_select(*args):
    """
    在雜項選單中恢復隊員選取狀態。
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
        messagebox.showerror("錯誤", f"恢復雜項選單的隊員選取狀態發生錯誤：{e}")  # 顯示錯誤訊息
