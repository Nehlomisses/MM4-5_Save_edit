#模組化版本
import sys  # 確保有這行
import os,struct,tkinter as tk  # 導入 os 模組，用於操作系統相關功能,struct處理二進位數據,導入 tkinter 模組，用於 GUI
import XEEN_editdata.gui_utils,XEEN_editdata.weapon_utils,XEEN_editdata.defpon_utils,XEEN_editdata.ringpon_utils,XEEN_editdata.itempon_utils #模組化區塊
from tkinter import ttk, filedialog, messagebox  # 導入 tkinter 的子模組


def resource_path(relative_path):
    """取得資源的絕對路徑，支援開發環境與 PyInstaller 打包環境"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

modified_data = {}  # 用於儲存被修改的隊員數據, 格式: {member: {offset: value}}
is_modified = False  # 標記是否有任何修改

# 從 common_dicts.py 導入多個字典
from XEEN_editdata.common_dicts import (  
    weapon_type_mapping,  # 武器類型對應表
    WEAPON_ID_DESCRIPTIONS,  # 武器 ID 描述對應表
    WEAPON_SPECIAL_EFFECTS,  # 武器特殊效果對應表
    WAP_Eq,                 #武器裝備種類
    Def_Eq,                 #防具裝備種類
    rinq_eq,                #飾品裝備種類
    def_Amo,  # 防具類型對應表
    ring_ID_EQ,  # 戒指 ID 對應表
    item_ID,  # 物品 ID 對應表
    item_type_mapping,  # 物品類型對應表
    member_addresses,  # 隊員地址資訊
    attributes,  # 屬性列表
    resistances,  # 抗性列表
    team_labels,  # 隊伍資訊標籤
    team_addresses,  # 隊伍資訊地址
    team_members,  # 隊員列表
    address_map,  # 位址映射表
    class_nb, #職業
)


# 全局變量初始化 (只保留這裡的初始化)
game_save_file = None  # 遊戲存檔檔案路徑，初始為 None
save_data = None  # 存檔數據，初始為 None
selected_member = None  # 目前選取的隊員，初始為 None
team_name_mapping = {}  # 隊員名稱與隊員物件的映射，初始為空字典
attribute_vars = {}  # 屬性變數，用於 GUI 更新，初始為空字典
weapon_vars = []  # 武器變數，用於 GUI 更新，初始為空列表
defpon_vars = []  # 防具變數，用於 GUI 更新，初始為空列表
ring_vars = []  # 戒指變數，用於 GUI 更新，初始為空列表
item_vars = []  # 物品變數，用於 GUI 更新，初始為空列表

# 載入遊戲存檔數據
def load_save_data(file_path):
    """
    載入遊戲存檔數據。

    Args:
        file_path (str): 遊戲存檔檔案路徑。

    Returns:
        bytearray: 包含遊戲存檔數據的 bytearray。 如果發生錯誤，則返回 None。
    """
    try:
        with open(file_path, 'rb') as file:  # 以二進位讀取模式開啟檔案
            data = bytearray(file.read())  # 讀取檔案內容並轉換為 bytearray
        return data  # 返回 bytearray
    except FileNotFoundError:
        messagebox.showerror("錯誤", "存檔檔案不存在！")  # 顯示錯誤訊息
        return None  # 返回 None
    except Exception as e:
        messagebox.showerror("錯誤", f"載入存檔時發生錯誤：{e}")  # 顯示錯誤訊息
        return None  # 返回 None

# 解析能力數據
def parse_attribute_data(data, start_addr):
    """
    解析隊員的能力數據。

    Args:
        data (bytearray): 包含遊戲存檔數據的 bytearray。
        start_addr (int): 能力數據的起始位址。

    Returns:
        dict: 包含解析後能力數據的字典。
    """
    attr_data = {}  # 存儲解析後的能力數據
    for i, attribute in enumerate(attributes):  # 遍歷屬性列表
        # 對於等級屬性，地址偏移量是特定的
        addr = start_addr + 7 * 2 + 1 if attribute == '等級' else start_addr + i * 2
        attr_data[attribute] = XEEN_editdata.gui_utils.parse_data(data, addr)[0]  # 使用通用函數解析數據
    return attr_data  # 返回能力數據字典

# 解析抗性數據
def parse_resistance_data(data, start_addr):
    """
    解析隊員的抗性數據。

    Args:
        data (bytearray): 包含遊戲存檔數據的 bytearray。
        start_addr (int): 抗性數據的起始位址。

    Returns:
        dict: 包含解析後抗性數據的字典。
    """
    resist_data = {}  # 存儲解析後的抗性數據
    for i, resistance in enumerate(resistances):  # 遍歷抗性列表
        addr = start_addr + i * 2  # 計算抗性數據的位址
        resist_data[resistance] = XEEN_editdata.gui_utils.parse_data(data, addr)[0]  # 使用通用函數解析數據
    return resist_data  # 返回抗性數據字典

# 更新顯示的能力和抗性數據
def update_attribute_data(member):
    """
    更新 GUI 顯示的能力和抗性數據。

    Args:
        member (str): 隊員名稱。
    """
    try:
        name_addr, attr_start_addr, resist_start_addr = member_addresses[member]  # 根據隊員名稱獲取地址資訊
        attribute_data = parse_attribute_data(save_data, attr_start_addr)  # 解析能力數據
        resistance_data = parse_resistance_data(save_data, resist_start_addr)  # 解析抗性數據
        for attribute, value in attribute_data.items():  # 遍歷能力數據
            attribute_vars[attribute].set(value)  # 更新 GUI 變數
        for resistance, value in resistance_data.items():  # 遍歷抗性數據
            attribute_vars[resistance].set(value)  # 更新 GUI 變數
    except KeyError:
        messagebox.showerror("錯誤", f"找不到 '{member}' 的屬性地址。")  # 顯示錯誤訊息
    except Exception as e:
        messagebox.showerror("錯誤", f"更新屬性資料時發生錯誤：{e}")  # 顯示錯誤訊息

# 解析隊伍資訊數據
def parse_team_data(data):
    """
    解析隊伍資訊數據。

    Args:
        data (bytearray): 包含遊戲存檔數據的 bytearray。
    """
    global team_data  # 聲明使用全局變數 team_data
    team_data = {}  # 初始化 team_data 字典
    for i, (addr, size) in enumerate(team_addresses):  # 遍歷隊伍資訊地址
        # 讀取指定位址的數據，使用小端格式轉換為整數
        team_data[team_labels[i]] = int.from_bytes(data[addr:addr+size], 'little')

# 更新顯示的隊伍資訊數據
def update_team_data_display():
    """
    更新 GUI 顯示的隊伍資訊數據。
    """
    for i, entry in enumerate(team_entries):  # 遍歷隊伍資訊輸入框
        entry.delete(0, tk.END)  # 清空輸入框
        entry.insert(0, str(team_data[team_labels[i]]))  # 插入對應數據

def write_team_data():
    """
    將 GUI 中修改後的隊伍資訊數據寫入到 save_data 中。
    """
    try: # 增加錯誤處理
        global save_data  # 聲明使用全局變數 save_data
        for i, (addr, size) in enumerate(team_addresses):  # 遍歷隊伍資訊地址
            try:
                value = int(team_entries[i].get())  # 從 GUI 輸入框獲取新數值
                value = max(0, min(4294967295, value))  # 限制數值範圍（避免溢出）
                save_data[addr:addr+size] = value.to_bytes(size, 'little')  # 轉換為小端格式字節並寫入 save_data
            except ValueError:
                pass  # 若輸入值無效（非數字），則跳過
    except Exception as e:
        messagebox.showerror("錯誤", f"寫入隊伍資料發生錯誤: {e}")


# 處理隊員選取事件
def on_member_select(event):
    """
    處理隊員選取事件，更新 GUI 顯示的隊員數據。
    """
    try:
        global selected_member, save_data, address_map  # 聲明使用全局變數 selected_member

        if team_listbox.curselection():  # 檢查是否有選取隊員
            selected_index = team_listbox.curselection()[0]  # 獲取選取隊員的索引
            selected_member = list(team_name_mapping.values())[selected_index]  # 獲取選取隊員的名稱
            if selected_member:  # 確保選取了有效的隊員
                member_name = list(team_name_mapping.keys())[list(team_name_mapping.values()).index(selected_member)]  # 獲取隊員名稱
                XEEN_editdata.gui_utils.update_selected_member_label(member_name)  # 更新標籤頁標題 只能傳一個參數

                # 1. 導入 class_nb 字典
                from XEEN_editdata.common_dicts import class_nb

                # 2. 獲取能力數據的起始位址
                name_addr, attr_start_addr, resist_start_addr = member_addresses[selected_member]

                # 3. 計算職業位址
                occupation_address = attr_start_addr - 1

                # 4. 從檔案中讀取職業代碼
                file_path = game_save_file  # 使用全局变量 game_save_file
                with open(file_path, "rb") as f:
                    f.seek(occupation_address)
                    byte_data = f.read(1)
                    occupation_code = byte_data[0] #** 讀取到的byte 數值**

                # 5. 轉換文字
                member_occupation = class_nb[occupation_code]

                # 6. 更新标签文字
                XEEN_editdata.gui_utils.selected_member_label.config(text=f"{member_name}-{member_occupation}")  # 更新**能力**標籤文字
                XEEN_editdata.gui_utils.selected_weapon_label.config(text=f"{member_name}-{member_occupation}")  # 更新**武器**標籤文字
                XEEN_editdata.gui_utils.selected_def_label.config(text=f"{member_name}-{member_occupation}")  # 更新**防具**標籤文字
                XEEN_editdata.gui_utils.selected_ring_label.config(text=f"{member_name}-{member_occupation}")  # 更新**配件**標籤文字
                XEEN_editdata.gui_utils.selected_item_label.config(text=f"{member_name}-{member_occupation}")  # 更新**雜項**標籤文字

                XEEN_editdata.weapon_utils.update_weapon_data(selected_member)  # 更新武器數據
                XEEN_editdata.defpon_utils.update_defpon_data(selected_member)  # 更新防具數據
                XEEN_editdata.ringpon_utils.update_ringpon_data(selected_member)  # 更新配件數據
                XEEN_editdata.itempon_utils.update_itempon_data(selected_member)  # 更新雜項數據
                update_attribute_data(selected_member)  # 更新屬性數據
                #update_defpon_data(selected_member)  # 更新防具數據
                #update_ringpon_data(selected_member)  # 更新配件數據
                #update_itempon_data(selected_member)  # 更新雜項數據

    except ValueError:
        print("警告: 無法選擇隊員。")  # 打印警告訊息
    except Exception as e:
        messagebox.showerror("錯誤", f"處理隊員選取事件發生錯誤：{e}")  # 顯示錯誤訊息


# 保存能力和抗性數據
def save_attribute_data(member):
    """
    保存 GUI 中修改後的能力和抗性數據到存檔檔案。

    Args:
        member (str): 隊員名稱。
    """
    try:  # 使用 try...except 區塊處理可能發生的錯誤
        name_addr, attr_start_addr, resist_start_addr = member_addresses[member]  # 根據隊員名稱從 member_addresses 字典中獲取對應的地址資訊

        for i, attribute in enumerate(attributes):  # 遍歷 attributes 列表，取得每個屬性的索引和名稱
            try:  # 使用 try...except 區塊處理單個屬性可能發生的錯誤
                value = int(attribute_vars[attribute].get())  # 從 GUI 元素 (attribute_vars) 取得屬性值，並轉換為整數
                value = max(0, min(255, value))  # 限制屬性值在 0~255 的範圍內

                addr = attr_start_addr + i * 2 if i < 7 else attr_start_addr + 7 * 2 + 1  # 計算屬性值在存檔檔案中的位址。 等級的位址計算方式不同
                struct.pack_into('B', save_data, addr, value)  # 將屬性值以 unsigned byte (B) 的格式寫入 save_data 的指定位址

            except ValueError:  # 如果屬性值無法轉換為整數
                pass  # 忽略錯誤，跳過此屬性

        for i, resistance in enumerate(resistances):  # 遍歷 resistances 列表，取得每個抗性的索引和名稱
            try:  # 使用 try...except 區塊處理單個抗性可能發生的錯誤
                value = int(attribute_vars[resistance].get())  # 從 GUI 元素 (attribute_vars) 取得抗性值，並轉換為整數
                value = max(0, min(255, value))  # 限制抗性值在 0~255 的範圍內

                addr = resist_start_addr + i * 2  # 計算抗性值在存檔檔案中的位址
                struct.pack_into('B', save_data, addr, value)  # 將抗性值以 unsigned byte (B) 的格式寫入 save_data 的指定位址

            except ValueError:  # 如果抗性值無法轉換為整數
                pass  # 忽略錯誤，跳過此抗性

    except KeyError:  # 如果找不到隊員的地址資訊
        messagebox.showerror("錯誤", f"找不到 '{member}' 的屬性地址。")  # 顯示錯誤訊息
    except Exception as e:  # 處理其他可能發生的錯誤
        messagebox.showerror("錯誤", f"保存能力和抗性數據發生錯誤：{e}")  # 顯示錯誤訊息

# 保存隊伍資訊數據
def save_partydata():
    """
    保存 GUI 中修改後的隊伍資訊數據到存檔檔案。
    """
    try:  # 使用 try...except 區塊處理可能發生的錯誤
        global save_data  # 聲明使用全局變數 save_data，表示要修改全局變數

        for i, (addr, size) in enumerate(team_addresses):  # 遍歷 team_addresses 列表，取得每個隊伍資訊的地址和大小
            try:  # 使用 try...except 區塊處理單個隊伍資訊可能發生的錯誤
                value = int(team_entries[i].get())  # 從 GUI 元素 (team_entries) 取得隊伍資訊數值，並轉換為整數
                value = max(0, min(4294967295, value))  # 限制數值範圍，避免溢出 (最大 32 位元無符號整數)
                save_data[addr:addr+size] = value.to_bytes(size, 'little')  # 將數值轉換為小端字節序列，並寫入 save_data 的指定位址
            except ValueError:  # 如果數值無法轉換為整數
                pass  # 忽略錯誤，跳過此隊伍資訊

    except Exception as e:  # 處理其他可能發生的錯誤
        messagebox.showerror("錯誤", f"保存隊伍資訊數據發生錯誤：{e}")  # 顯示錯誤訊息

# 保存數據到檔案
def save_to_file():
    """
    保存所有修改後的數據到存檔檔案。
    """
    try:
        global selected_member, save_data, address_map, weapon_vars,defpon_vars  # 聲明使用全局變數

        # 確保 XEEN_editdata.weapon_utils 使用最新的全局變數-武器
        XEEN_editdata.weapon_utils.address_map = address_map
        XEEN_editdata.weapon_utils.weapon_vars = weapon_vars
        XEEN_editdata.weapon_utils.save_data = save_data

        # 確保 XEEN_editdata.weapon_utils 使用最新的全局變數-防具
        XEEN_editdata.defpon_utils.address_map = address_map
        XEEN_editdata.defpon_utils.defpon_vars = defpon_vars
        XEEN_editdata.defpon_utils.save_data = save_data

        # 確保 XEEN_editdata.weapon_utils 使用最新的全局變數-配件
        XEEN_editdata.ringpon_utils.address_map = address_map
        XEEN_editdata.ringpon_utils.ring_vars = ring_vars
        XEEN_editdata.ringpon_utils.save_data = save_data

        # 確保 XEEN_editdata.weapon_utils 使用最新的全局變數-雜項
        XEEN_editdata.itempon_utils.address_map = address_map
        XEEN_editdata.itempon_utils.item_vars = item_vars
        XEEN_editdata.itempon_utils.save_data = save_data

        if selected_member:
            XEEN_editdata.weapon_utils.save_weapon_data(selected_member)  # 武器
            XEEN_editdata.defpon_utils.save_defpon_data(selected_member)  # 防具
            XEEN_editdata.ringpon_utils.save_ringpon_data(selected_member)  # 配件
            XEEN_editdata.itempon_utils.save_itempon_data(selected_member)  # 配件
            save_attribute_data(selected_member)
            #save_defpon_data(selected_member)
            #save_ringpon_data(selected_member)
            #save_itempon_data(selected_member)

        # 保存隊伍資訊數據
        save_partydata()

        # 確保在保存時，已經指定了保存檔案的路徑
        if game_save_file:
            with open(game_save_file, 'wb') as file:  # 以二進位寫入模式開啟檔案
                file.write(save_data)  # 寫入數據
            messagebox.showinfo("成功", "存檔成功！")  # 顯示成功訊息
        else:
            messagebox.showerror("錯誤", "保存檔案路徑未指定")  # 顯示錯誤訊息
    except Exception as e:
        messagebox.showerror("錯誤", f"保存檔案時發生錯誤：{e}")  # 顯示錯誤訊息
# 更新隊員列表框
def update_team_listbox():
    """
    更新隊員列表框的內容。
    """
    try:
        team_listbox.delete(0, 'end')  # 清空列表框
        global team_name_mapping  # 聲明使用全局變數 team_name_mapping
        team_name_mapping = {}  # 初始化隊員名稱映射
        for member in team_members:  # 遍歷隊員列表
            name_addr, attr_start_addr, resist_start_addr = member_addresses[member]  # 獲取隊員地址資訊
            member_name = get_member_name(save_data, name_addr, name_addr + 7)  # 獲取隊員名稱
            if member_name:  # 確保隊員名稱有效
                team_listbox.insert('end', member_name)  # 插入隊員名稱到列表框
                team_name_mapping[member_name] = member  # 更新隊員名稱映射
    except Exception as e:
        messagebox.showerror("錯誤", f"更新隊員列表框發生錯誤：{e}")  # 顯示錯誤訊息

# 獲取隊員名字
def get_member_name(data, start_addr, end_addr):
    """
    從存檔數據中獲取隊員名字。

    Args:
        data (bytearray): 包含遊戲存檔數據的 bytearray。
        start_addr (int): 隊員名稱的起始位址。
        end_addr (int): 隊員名稱的結束位址。

    Returns:
        str: 隊員名稱。 如果無法獲取隊員名稱，則返回 None。
    """
    try:
        name_bytes = data[start_addr:end_addr + 1]  # 讀取隊員名稱的字節

        if all(b == 0x00 for b in name_bytes):  # 檢查是否所有字節都是 0x00 (表示沒有隊員)
            return None  # 該隊員不存在

        valid_bytes = bytearray()  # 存儲有效的字節
        for b in name_bytes[:8]:  # 只取前 8 個字節
            if b == 0x00:  # 遇到 0x00 表示字串結束
                break  # 終止迴圈
            valid_bytes.append(b)  # 添加到有效字節

        try:
            name = valid_bytes.decode('big5').strip('\x00')  # 使用 Big5 解碼並移除空字節
        except UnicodeDecodeError:  # 解碼失敗
            name = None  # 如果解碼失敗，則返回 None

        return name  # 返回隊員名稱
    except Exception as e:
        messagebox.showerror("錯誤", f"獲取隊員名字發生錯誤：{e}")  # 顯示錯誤訊息
        return None  # 返回 None

# 載入數據
def load_new_file():
    """
    從檔案中載入遊戲數據。
    """
    global save_data, game_save_file, address_map, weapon_vars  # 聲明使用全局變數 save_data 和 game_save_file
    initial_dir = os.getcwd()  # 獲取程式目前的目錄，作為檔案選擇器的起始目錄
    file_path = filedialog.askopenfilename(initialdir=initial_dir, filetypes=[('SAV files', '*.sav')])  # 開啟檔案選擇器
    if file_path:  # 檢查是否選擇了檔案
        try:
            game_save_file = file_path  # 保存檔案路徑
            save_data = load_save_data(file_path)  # 載入存檔數據
            if save_data:  # 確保成功載入數據
                update_team_listbox()  # 更新隊員列表
                parse_team_data(save_data)  # 解析隊伍數據
                update_team_data_display()  # 更新隊伍數據顯示

                # 將主程式的全域變數賦值給 XEEN_editdata.weapon_utils-武器
                XEEN_editdata.weapon_utils.address_map = address_map
                XEEN_editdata.weapon_utils.weapon_vars = weapon_vars
                XEEN_editdata.weapon_utils.save_data = save_data

                # 將主程式的全域變數賦值給 XEEN_editdata.weapon_utils-防具
                XEEN_editdata.defpon_utils.address_map = address_map
                XEEN_editdata.defpon_utils.defpon_vars = defpon_vars
                XEEN_editdata.defpon_utils.save_data = save_data

                # 將主程式的全域變數賦值給 XEEN_editdata.weapon_utils-配件
                XEEN_editdata.ringpon_utils.address_map = address_map
                XEEN_editdata.ringpon_utils.ring_vars = ring_vars
                XEEN_editdata.ringpon_utils.save_data = save_data

                # 將主程式的全域變數賦值給 XEEN_editdata.weapon_utils-雜項
                XEEN_editdata.itempon_utils.address_map = address_map
                XEEN_editdata.itempon_utils.item_vars = item_vars
                XEEN_editdata.itempon_utils.save_data = save_data

        except Exception as e:
            messagebox.showerror("錯誤", f"讀取檔案或更新數據時發生錯誤：{e}")  # 顯示錯誤訊息

# 初始載入
def init():
    """
    初始化程式 (目前不執行任何操作)。
    """
    pass  # 程式啟動時不執行任何讀取動作

# 創建 GUI
root = tk.Tk()  # 創建 Tkinter 主視窗
root.title("魔法門外傳合輯修改器 2026/01/21 Ver.2.1")  # 設置視窗標題
icon_path = resource_path("xeen.ico")
root.iconbitmap(icon_path)

# 定義驗證函數和命令
def validate_input(value_if_allowed):
    """
    驗證輸入值是否為 0~255 的整數。
    """
    if value_if_allowed.isdigit() and 0 <= int(value_if_allowed) <= 255:
        return True  # 如果輸入值是數字且在 0~255 範圍內，則返回 True
    return False  # 否則返回 False

vcmd = (root.register(validate_input), '%P')  # 創建驗證命令，用於限制輸入框的輸入

# 創建主框架
main_frame = ttk.Frame(root)  # 創建主框架，用於容納所有其他 GUI 元素
main_frame.pack(fill='both', expand=True)  # 使用 pack 佈局管理器，填充視窗並自動調整大小

# 創建隊員欄
team_frame = ttk.Frame(main_frame)  # 創建隊員欄框架，用於顯示隊員列表
team_frame.pack(side='left', fill='y')  # 使用 pack 佈局管理器，將隊員欄框架放置在主框架的左側，並沿 Y 軸填充
ttk.Label(team_frame, text="隊員").pack()  # 創建標籤，顯示 "隊員" 文字

# 創建列表框和滾動條
team_listbox_frame = ttk.Frame(team_frame)  # 創建一個框架來容納列表框和滾動條
team_listbox_frame.pack(fill='both', expand=True)

team_listbox = tk.Listbox(team_listbox_frame, width=15, height=20)  # 創建列表框，用於顯示隊員名稱
team_listbox.pack(side='left', fill='both', expand=True)  # 使用 pack 佈局管理器，沿 Y 軸填充，並允許水平和垂直擴展
team_listbox.bind('<<ListboxSelect>>', on_member_select)  # 綁定列表框的選取事件到 on_member_select 函數

# 創建滾動條
scrollbar = ttk.Scrollbar(team_listbox_frame, orient="vertical", command=team_listbox.yview)
scrollbar.pack(side='right', fill='y')

# 將滾動條配置給 Listbox
team_listbox.config(yscrollcommand=scrollbar.set)


# 創建標籤頁
tab_control = ttk.Notebook(main_frame)  # 創建標籤頁控制元件
tab_control.pack(side='right', fill='both', expand=True)  # 使用 pack 佈局管理器，將標籤頁控制元件放置在主框架的右側，並填充和自動調整大小

# 創建能力標籤頁
abilities_frame = ttk.Frame(tab_control)  # 創建能力標籤頁框架
abilities_frame.pack(fill='both', expand=True)  # 填充標籤頁
selected_member_label = ttk.Label(abilities_frame, text="")  # 創建標籤，用於顯示選取的隊員名稱
selected_member_label.pack()  # 放置標籤


# 創建武器標籤頁
weapon_frame = ttk.Frame(tab_control)  # 創建武器標籤頁框架
weapon_frame.pack(fill='both', expand=True)  # 填充標籤頁
selected_weapon_label = ttk.Label(weapon_frame, text="")  # 創建標籤，用於顯示選取的隊員名稱
selected_weapon_label.pack()  # 放置標籤

# 創建防具標籤頁
def_frame = ttk.Frame(tab_control)  # 創建防具標籤頁框架
def_frame.pack(fill='both', expand=True)  # 填充標籤頁
selected_def_label = ttk.Label(def_frame, text="")  # 創建標籤，用於顯示選取的隊員名稱
selected_def_label.pack()  # 放置標籤

# 創建配件標籤頁
ring_frame = ttk.Frame(tab_control)  # 創建配件標籤頁框架
ring_frame.pack(fill='both', expand=True)  # 填充標籤頁
selected_ring_label = ttk.Label(ring_frame, text="")  # 創建標籤，用於顯示選取的隊員名稱
selected_ring_label.pack()  # 放置標籤

# 創建雜項標籤頁
item_frame = ttk.Frame(tab_control)  # 創建雜項標籤頁框架
item_frame.pack(fill='both', expand=True)  # 填充標籤頁
selected_item_label = ttk.Label(item_frame, text="")  # 創建標籤，用於顯示選取的隊員名稱
selected_item_label.pack()  # 放置標籤

XEEN_editdata.gui_utils.initialize_labels(selected_member_label, selected_weapon_label, selected_def_label, selected_ring_label, selected_item_label)

# 創建隊伍資訊標籤頁
teams_frame = ttk.Frame(tab_control)  # 創建隊伍資訊標籤頁框架
teams_frame.pack(fill='both', expand=True)  # 填充標籤頁
selected_team_label = ttk.Label(teams_frame, text="隊伍資訊")  # 創建標籤，顯示 "隊伍資訊"
selected_team_label.pack()  # 放置標籤

team_entries = []  # 存儲隊伍資訊輸入框的列表

for label in team_labels:  # 遍歷 team_labels 列表，為每個標籤創建一個輸入框
    frame = ttk.Frame(teams_frame)  # 創建一個框架，用於放置標籤和輸入框
    frame.pack(fill='x', padx=10, pady=5)  # 使用 pack 佈局管理器，水平填充，並添加內邊距
    ttk.Label(frame, text=label).pack(side='left')  # 創建標籤，顯示隊伍資訊的名稱，放置在框架的左側
    entry = ttk.Entry(frame, width=20)  # 創建輸入框，用於輸入隊伍資訊的數值
    entry.pack(side='left')  # 放置輸入框在框架的左側
    team_entries.append(entry)  # 將輸入框添加到 team_entries 列表中

# 能力數值分頁
ability_frame = tk.Frame(abilities_frame)  # 創建能力數值分頁框架
ability_frame.pack(expand=True, fill="both", padx=10, pady=10)  # 填充標籤頁，並添加內邊距

# 顯示能力數值標籤並設置輸入框
for i, label in enumerate(attributes):  # 遍歷 attributes 列表，為每個屬性創建一個標籤和輸入框
    tk.Label(ability_frame, text=label).grid(row=i, column=0, pady=2, sticky="w")  # 顯示標籤，並使用 grid 佈局管理器放置在網格中
    var = tk.StringVar()  # 創建一個 StringVar 變數，用於儲存輸入框的數值
    attribute_vars[label] = var  # 將變數添加到 attribute_vars 字典中，鍵為屬性名稱
    entry = tk.Entry(ability_frame, textvariable=var, width=8)  # 創建一個輸入框，並將其 textvariable 屬性設置為 var
    entry.grid(row=i, column=1, pady=2)  # 使用 grid 佈局管理器放置在網格中

# 顯示抗性數值標籤並設置輸入框
for i, label in enumerate(resistances):  # 遍歷 resistances 列表，為每個抗性創建一個標籤和輸入框
    tk.Label(ability_frame, text=label).grid(row=i, column=2, pady=2, sticky="w")  # 顯示標籤，並使用 grid 佈局管理器放置在網格中
    var = tk.StringVar()  # 創建一個 StringVar 變數，用於儲存輸入框的數值
    attribute_vars[label] = var  # 將變數添加到 attribute_vars 字典中，鍵為抗性名稱
    entry = tk.Entry(ability_frame, textvariable=var, width=8)  # 創建一個輸入框，並將其 textvariable 屬性設置為 var
    entry.grid(row=i, column=3, pady=2)  # 使用 grid 佈局管理器放置在網格中

# 增加武器說明文字框架
weapon_header_frame = ttk.Frame(weapon_frame)
weapon_header_frame.pack(fill='x', padx=10, pady=5)

# 說明文字和對應的寬度
labels = ["","屬性", "武器種類", "特殊能力", "裝備類型"]
widths = [18, 26, 17,12,0]  # 寬度與下拉式選單對應
for i, text in enumerate(labels):
    label = ttk.Label(weapon_header_frame, text=text, width=widths[i])
    label.pack(side='left', padx=5)


#武器
weapon_vars = []
for i in range(9):  # 9組武器
    weapon_frame_inner = ttk.Frame(weapon_frame)  # 創建武器標籤頁的內部框架
    weapon_frame_inner.pack(fill='x', padx=10, pady=5)  # 填充標籤頁，並添加內邊距
    ttk.Label(weapon_frame_inner, text=f"武器{i+1}").pack(side='left')  # 顯示武器編號標籤
    weapon_vars.append([tk.StringVar(), tk.StringVar(), tk.StringVar(),tk.StringVar()])  # 為每組武器創建 3 個 StringVar 變數
    for idx, var in enumerate(weapon_vars[-1]):  # 遍歷每組武器的 StringVar 變數
        if idx == 0:
            ttk.Combobox(weapon_frame_inner, textvariable=var, values=list(weapon_type_mapping.values()), width=30).pack(side='left', padx=5)  # 創建武器類型 Combobox
        elif idx == 1:
            ttk.Combobox(weapon_frame_inner, textvariable=var, values=list(WEAPON_ID_DESCRIPTIONS.values()), width=20).pack(side='left', padx=5)  # 創建武器 ID 描述 Combobox
        elif idx == 2:
            ttk.Combobox(weapon_frame_inner, textvariable=var, values=list(WEAPON_SPECIAL_EFFECTS.values()), width=10).pack(side='left', padx=5)  # 創建武器特殊效果 Combobox
        else:
            ttk.Combobox(weapon_frame_inner, textvariable=var, values=list(WAP_Eq.values()), width=8).pack(side='left', padx=5)  # 創建武器裝備選項 Combobox



# 增加防具說明文字框架
def_header_frame = ttk.Frame(def_frame)
def_header_frame.pack(fill='x', padx=10, pady=5)

# 說明文字和對應的寬度
def_labels = ["","屬性", "防具種類", "裝備類型"]
def_widths = [18,20, 11, 0]  # 寬度與下拉式選單對應
for i, text in enumerate(def_labels):
    label = ttk.Label(def_header_frame, text=text, width=def_widths[i])
    label.pack(side='left', padx=5)

#防具
defpon_vars = []
for i in range(9):  # 9組防具
    defpon_frame_inner = ttk.Frame(def_frame)  # 創建防具標籤頁的內部框架
    defpon_frame_inner.pack(fill='x', padx=10, pady=5)  # 填充標籤頁，並添加內邊距
    ttk.Label(defpon_frame_inner, text=f"防具{i+1}").pack(side='left')  # 顯示防具編號標籤
    defpon_vars.append([tk.StringVar(), tk.StringVar(), tk.StringVar()])  # 為每組防具創建 2 個 StringVar 變數
    for idx, var in enumerate(defpon_vars[-1]):  # 遍歷每組防具的 StringVar 變數
        if idx == 0:
            ttk.Combobox(defpon_frame_inner, textvariable=var, values=list(weapon_type_mapping.values()), width=30).pack(side='left', padx=5)  # 創建防具類型 Combobox
        elif idx == 1:
            ttk.Combobox(defpon_frame_inner, textvariable=var, values=list(def_Amo.values()), width=10).pack(side='left', padx=5)  # 創建防具屬性 Combobox
        else:
            ttk.Combobox(defpon_frame_inner, textvariable=var, values=list(Def_Eq.values()), width=6).pack(side='left', padx=5)  # 創建防具裝備選項 Combobox

# 增加配件說明文字框架
ring_header_frame = ttk.Frame(ring_frame)
ring_header_frame.pack(fill='x', padx=10, pady=5)

# 說明文字和對應的寬度
ring_labels = ["","屬性", "配件種類", "裝備類型"]
ring_widths = [18,22, 14, 0]  # 寬度與下拉式選單對應
for i, text in enumerate(ring_labels):
    label = ttk.Label(ring_header_frame, text=text, width=ring_widths[i])
    label.pack(side='left', padx=5)


#配件
ring_vars = []
for i in range(9):  # 9組配件
    ring_frame_inner = ttk.Frame(ring_frame)  # 創建配件標籤頁的內部框架
    ring_frame_inner.pack(fill='x', padx=10, pady=5)  # 填充標籤頁，並添加內邊距
    ttk.Label(ring_frame_inner, text=f"配件{i+1}").pack(side='left')  # 顯示配件編號標籤
    ring_vars.append([tk.StringVar(), tk.StringVar(), tk.StringVar()])  # 為每組配件創建 2 個 StringVar 變數
    for idx, var in enumerate(ring_vars[-1]):  # 遍歷每組配件的 StringVar 變數
        if idx == 0:
            ttk.Combobox(ring_frame_inner, textvariable=var, values=list(weapon_type_mapping.values()), width=30).pack(side='left', padx=5)  # 創建配件類型 Combobox
        elif idx == 1:
            ttk.Combobox(ring_frame_inner, textvariable=var, values=list(ring_ID_EQ.values()), width=15).pack(side='left', padx=5)  # 創建配件 ID Combobox
        else:
            ttk.Combobox(ring_frame_inner, textvariable=var, values=list(rinq_eq.values()), width=6).pack(side='left', padx=5)  # 創建飾品裝備選項 Combobox


# 增加雜項說明文字框架
item_header_frame = ttk.Frame(item_frame)
item_header_frame.pack(fill='x', padx=10, pady=5)

# 說明文字和對應的寬度
item_labels = ["","物品種類", "魔法種類"]
item_widths = [5,12,0]  # 寬度與下拉式選單對應
for i, text in enumerate(item_labels):
    label = ttk.Label(item_header_frame, text=text, width=item_widths[i])
    label.pack(side='left', padx=5)

#雜項
item_vars = []
for i in range(9):  # 9組雜項
    item_frame_inner = ttk.Frame(item_frame)  # 創建雜項標籤頁的內部框架
    item_frame_inner.pack(fill='x', padx=10, pady=5)  # 填充標籤頁，並添加內邊距
    ttk.Label(item_frame_inner, text=f"雜項{i+1}").pack(side='left')  # 顯示雜項編號標籤
    item_vars.append([tk.StringVar(), tk.StringVar(), tk.StringVar()])  # 為每組雜項創建 3 個 StringVar 變數
    for idx, var in enumerate(item_vars[-1]):  # 遍歷每組雜項的 StringVar 變數
        if idx == 0:
            ttk.Combobox(item_frame_inner, textvariable=var, values=list(item_ID.values()), width=8).pack(side='left', padx=5)  # 創建物品 ID Combobox
        elif idx == 1:
            ttk.Combobox(item_frame_inner, textvariable=var, values=list(item_type_mapping.values()), width=12).pack(side='left', padx=5)  # 創建物品類型 Combobox
        elif idx == 2:
            ttk.Label(item_frame_inner, text="使用次數：").pack(side='left', padx=5)  # 顯示 "使用次數" 標籤
            ttk.Entry(item_frame_inner, textvariable=var, width=5).pack(side='left', padx=5)  # 創建使用次數輸入框

# 將標籤頁加入到 Notebook
tab_control.add(abilities_frame, text='   能   力   ')  # 添加能力標籤頁到標籤頁控制元件
tab_control.add(weapon_frame, text='   武   器   ')  # 添加武器標籤頁到標籤頁控制元件
tab_control.add(def_frame, text='   防   具   ')  # 添加防具標籤頁到標籤頁控制元件
tab_control.add(ring_frame, text='   配   件   ')  # 添加配件標籤頁到標籤頁控制元件
tab_control.add(item_frame, text='   雜   項   ')  # 添加雜項標籤頁到標籤頁控制元件
tab_control.add(teams_frame, text=' 隊 伍 資 料 ')  # 添加隊伍資料標籤頁到標籤頁控制元件

# 設置標籤頁控制
tab_control.pack(expand=1, fill='both')  # 使用 pack 佈局管理器，填充和自動調整大小

# 創建按鈕框架來放置按鈕
button_frame = ttk.Frame(root)  # 創建按鈕框架
button_frame.pack(side='bottom', pady=10)  # 放置在底部，並添加垂直內邊距

# 增加讀取檔案按鈕
load_button = ttk.Button(button_frame, text="讀檔", command=load_new_file)  # 創建讀檔按鈕，並綁定 load_new_file 函數
load_button.pack(side='left', padx=5)  # 放置在左側，並添加水平內邊距

# 增加存檔按鈕
save_button = ttk.Button(button_frame, text="存檔", command=save_to_file)  # 創建存檔按鈕，並綁定 save_to_file 函數
save_button.pack(side='left', padx=5)  # 放置在左側，並添加水平內邊距

# 初始載入
def init():
    pass

# Run Init
init()

root.mainloop()