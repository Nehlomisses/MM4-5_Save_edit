import struct
from tkinter import messagebox
import XEEN_editdata
from XEEN_editdata.common_dicts import (
    weapon_type_mapping,
    ring_ID_EQ,
    rinq_eq, # 確保匯入 rinq_eq
)

# 宣告全局變數
address_map = None
ringpon_vars = None
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
    ringpons = []
    for i in range(9):  # 每個隊員有 9 個配件欄位
        addr = start_addr + i * 4  # 計算配件數據的位址
        # 讀取指定位元組
        ringpon1 = data[addr]
        ringpon2 = data[addr + 1]
        ringpon4 = data[addr + 3] if addr + 3 < len(data) else None  # 讀取裝備類型, 确保不越界

        ringpons.append((ringpon1, ringpon2, ringpon4))  # 将配件数据添加到列表中
    return ringpons

# 更新顯示的配件數據
def update_ringpon_data(member):
    """
    更新 GUI 顯示的配件數據。

    Args:
        member (str): 隊員名稱。
    """
    try:
        base_addr = address_map[member] + 0x48
        ringpon_data = parse_ringpon_data(save_data, base_addr)
        for idx, (ringpon1, ringpon2, ringpon4) in enumerate(ringpon_data):  # 修改這裡
            if idx < len(ring_vars):
                # 使用配件數據更新 GUI 變數
                ring_vars[idx][0].set(weapon_type_mapping.get(ringpon1, "未知"))
                ring_vars[idx][1].set(ring_ID_EQ.get(ringpon2, "未知"))
                ring_vars[idx][2].set(rinq_eq.get(ringpon4, "未知")) # 修改這裡，使用 rinq_eq
    except KeyError:
        messagebox.showerror("錯誤", f"找不到 '{member}' 的配件地址。")
    except Exception as e:
        messagebox.showerror("錯誤", f"更新配件數據時發生錯誤：{e}")

# 保存配件數據
def save_ringpon_data(member):
    """
    保存 GUI 中修改後的配件數據到存檔檔案。

    Args:
        member (str): 隊員名稱。
    """
    try:
        base_addr = address_map[member] + 0x48
        for idx, ringpon_var in enumerate(ring_vars):
            addr = base_addr + idx * 4
            # 從 GUI 變數獲取配件數據，並轉換為對應的 ID
            ringpon1 = next((key for key, value in weapon_type_mapping.items() if value == ringpon_var[0].get()), None)
            ringpon2 = next((key for key, value in ring_ID_EQ.items() if value == ringpon_var[1].get()), None)
            ringpon4 = next((key for key, value in rinq_eq.items() if value == ringpon_var[2].get()), None)  # 新增，使用 rinq_eq

            if ringpon1 is not None and ringpon2 is not None and ringpon4 is not None: # 修改這裡
                struct.pack_into('B', save_data, addr, ringpon1)  # 保存配件類型
                struct.pack_into('B', save_data, addr + 1, ringpon2)  # 保存配件屬性
                struct.pack_into('B', save_data, addr + 3, ringpon4)  # 保存裝備類型 # 修改這裡

    except KeyError:
        messagebox.showerror("錯誤", f"找不到 '{member}' 的配件地址。")
    except Exception as e:
        messagebox.showerror("錯誤", f"保存配件數據時發生錯誤：{e}")

# 恢復配件選單的隊員選取狀態
def on_ringpon_select(*args):
    """
    在配件選單中恢復隊員選取狀態。
    """
    try:
        global selected_member
        if selected_member and team_name_mapping:  # 增加判斷，確保有選取隊員且隊伍資訊不為空
            member_name = list(team_name_mapping.keys())[list(team_name_mapping.values()).index(selected_member)]
            if member_name in team_listbox.get(0, 'end'):
                team_listbox.selection_clear(0, 'end')
                team_listbox.selection_set(team_listbox.get(0, 'end').index(member_name))
    except ValueError:
        print("警告: 無法恢復隊員選擇。")
    except Exception as e:
        messagebox.showerror("錯誤", f"恢復配件選單的隊員選取狀態發生錯誤：{e}")