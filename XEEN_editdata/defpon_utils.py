import struct
from tkinter import messagebox
import XEEN_editdata
from XEEN_editdata.common_dicts import (
    weapon_type_mapping,
    def_Amo,
    Def_Eq,
)

# 宣告全局變數
address_map = None
defpon_vars = None
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
    defpons = []
    for i in range(9):  # 每個隊員有 9 個防具欄位
        addr = start_addr + i * 4  # 計算防具數據的位址
        # 讀取指定位元組
        defpon1 = data[addr]
        defpon2 = data[addr + 1]
        defpon4 = data[addr + 3] if addr + 3 < len(data) else None  # 讀取裝備類型, 确保不越界

        defpons.append((defpon1, defpon2, defpon4))  # 将防具数据添加到列表中
    return defpons

# 更新顯示的防具數據
def update_defpon_data(member):
    """
    更新 GUI 顯示的防具數據。

    Args:
        member (str): 隊員名稱。
    """
    try:
        base_addr = address_map[member] + 0x24
        defpon_data = parse_defpon_data(save_data, base_addr)
        for idx, (defpon1, defpon2, defpon4) in enumerate(defpon_data):  # 修改這裡
            if idx < len(defpon_vars):
                # 使用防具數據更新 GUI 變數
                defpon_vars[idx][0].set(weapon_type_mapping.get(defpon1, "未知"))
                defpon_vars[idx][1].set(def_Amo.get(defpon2, "未知"))
                defpon_vars[idx][2].set(Def_Eq.get(defpon4, "未知")) # 修改這裡
    except KeyError:
        messagebox.showerror("錯誤", f"找不到 '{member}' 的防具地址。")
    except Exception as e:
        messagebox.showerror("錯誤", f"更新防具數據時發生錯誤：{e}")

# 保存防具數據
def save_defpon_data(member):
    """
    保存 GUI 中修改後的防具數據到存檔檔案。

    Args:
        member (str): 隊員名稱。
    """
    try:
        base_addr = address_map[member] + 0x24
        for idx, defpon_var in enumerate(defpon_vars):
            addr = base_addr + idx * 4
            # 從 GUI 變數獲取防具數據，並轉換為對應的 ID
            defpon1 = next((key for key, value in weapon_type_mapping.items() if value == defpon_var[0].get()), None)
            defpon2 = next((key for key, value in def_Amo.items() if value == defpon_var[1].get()), None)
            defpon4 = next((key for key, value in Def_Eq.items() if value == defpon_var[2].get()), None)  # 新增

            if defpon1 is not None and defpon2 is not None and defpon4 is not None: # 修改這裡
                struct.pack_into('B', save_data, addr, defpon1)  # 保存防具類型
                struct.pack_into('B', save_data, addr + 1, defpon2)  # 保存防具屬性
                struct.pack_into('B', save_data, addr + 3, defpon4)  # 保存裝備類型 # 修改這裡
                # 跳過第三個位元組，不進行任何寫入

    except KeyError:
        messagebox.showerror("錯誤", f"找不到 '{member}' 的防具地址。")
    except Exception as e:
        messagebox.showerror("錯誤", f"保存防具數據時發生錯誤：{e}")

# 恢復防具選單的隊員選取狀態
def on_defpon_select(*args):
    """
    在防具選單中恢復隊員選取狀態。
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
        messagebox.showerror("錯誤", f"恢復防具選單的隊員選取狀態發生錯誤：{e}")