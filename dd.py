import struct
import tkinter as tk
from tkinter import ttk, filedialog  # 確保匯入filedialog模組
from common_dicts import weapon_type_mapping, WEAPON_ID_DESCRIPTIONS, WEAPON_SPECIAL_EFFECTS,def_Amo,ring_ID_EQ,item_ID,item_type_mapping,member_addresses,attributes,resistances,team_labels,team_addresses,team_members,address_map

# 假設遊戲存檔是個二進位檔案
game_save_file = None  # 將初始值設為 None，表示未指定

# 載入遊戲存檔數據
def load_save_data(file_path):
    with open(file_path, 'rb') as file:
        data = bytearray(file.read())  # 將數據轉換為 bytearray
    return data

# 處理能力數據段落
# 解析能力數據
def parse_attribute_data(data, start_addr):
    attr_data = {}  # 存儲解析後的能力數據
    for i, attribute in enumerate(attributes):
        # 對於等級屬性，地址偏移量是特定的
        if attribute == '等級':
            addr = start_addr + 7 * 2 + 1
        else:
            addr = start_addr + i * 2
        # 從指定地址讀取一個字節的數據
        attr_data[attribute] = struct.unpack_from('B', data, addr)[0]
    return attr_data

# 解析抗性數據
def parse_resistance_data(data, start_addr):
    resist_data = {}  # 存儲解析後的抗性數據
    for i, resistance in enumerate(resistances):
        addr = start_addr + i * 2
        # 從指定地址讀取一個字節的數據
        resist_data[resistance] = struct.unpack_from('B', data, addr)[0]
    return resist_data

# 更新顯示的能力和抗性數據
def update_attribute_data(member):
    # 根據隊員名稱獲取其數據地址
    name_addr, attr_start_addr, resist_start_addr = member_addresses[member]
    
    # 解析能力數據
    attribute_data = parse_attribute_data(save_data, attr_start_addr)
    
    # 解析抗性數據
    resistance_data = parse_resistance_data(save_data, resist_start_addr)
    
    # 更新GUI顯示的能力數據
    for attribute, value in attribute_data.items():
        attribute_vars[attribute].set(value)
    
    # 更新GUI顯示的抗性數據
    for resistance, value in resistance_data.items():
        attribute_vars[resistance].set(value)

# 在分頁上方顯示目前選取的隊員
def update_selected_member_label(member_name):
    selected_member_label.config(text=f"{member_name}")
    selected_weapon_label.config(text=f"{member_name}")
    selected_def_label.config(text=f"{member_name}")
    selected_ring_label.config(text=f"{member_name}")
    selected_item_label.config(text=f"{member_name}")

# 處理武器數據段落
# 解析武器數據
def parse_weapon_data(data, start_addr):
    weapons = []
    for i in range(9):
        addr = start_addr + i * 4
        weapon1 = struct.unpack_from('B', data, addr)[0]
        weapon2 = struct.unpack_from('B', data, addr + 1)[0]
        weapon3 = struct.unpack_from('B', data, addr + 2)[0]
        weapons.append((weapon1, weapon2, weapon3))
    return weapons

# 更新顯示的武器數據
def update_weapon_data(member):
    base_addr = address_map[member]
    weapon_data = parse_weapon_data(save_data, base_addr)
    for idx, weapon in enumerate(weapon_data):
        if idx < len(weapon_vars):  # 確保不會超出現有的 GUI 元素
            weapon_vars[idx][0].set(weapon_type_mapping.get(weapon[0], "未知"))
            weapon_vars[idx][1].set(WEAPON_ID_DESCRIPTIONS.get(weapon[1], "未知"))
            weapon_vars[idx][2].set(WEAPON_SPECIAL_EFFECTS.get(weapon[2], "未知"))

# 保存武器數據
def save_weapon_data(member):
    base_addr = address_map[member]
    for idx, weapon_var in enumerate(weapon_vars):
        addr = base_addr + idx * 4
        weapon1 = next((key for key, value in weapon_type_mapping.items() if value == weapon_var[0].get()), None)
        weapon2 = next((key for key, value in WEAPON_ID_DESCRIPTIONS.items() if value == weapon_var[1].get()), None)
        weapon3 = next((key for key, value in WEAPON_SPECIAL_EFFECTS.items() if value == weapon_var[2].get()), None)

        # 檢查是否成功找到對應值
        if weapon1 is not None and weapon2 is not None and weapon3 is not None:
            struct.pack_into('B', save_data, addr, weapon1)
            struct.pack_into('B', save_data, addr + 1, weapon2)
            struct.pack_into('B', save_data, addr + 2, weapon3)

# 恢復武器選單的隊員選取狀態
def on_weapon_select(*args):
    global selected_member
    #恢復隊員選取狀態
    if selected_member:
        member_name = list(team_name_mapping.keys())[list(team_name_mapping.values()).index(selected_member)]
        team_listbox.selection_clear(0, 'end')
        team_listbox.selection_set(team_listbox.get(0, 'end').index(member_name))

# 處理防具數據段落
# 解析防具數據
def parse_defpon_data(data, start_addr):
    defpons = []
    for i in range(9):
        addr = start_addr + i * 4
        defpon1 = struct.unpack_from('B', data, addr)[0]
        defpon2 = struct.unpack_from('B', data, addr + 1)[0]
        defpons.append((defpon1, defpon2))
    return defpons

# 更新顯示的防具數據
def update_defpon_data(member):
    base_addr = address_map[member] + 0x24  # 防具起始位址 = 武器起始位址 + 24
    defpon_data = parse_defpon_data(save_data, base_addr)
    for idx, defpon in enumerate(defpon_data):
        if idx < len(defpon_vars):  # 確保不會超出現有的 GUI 元素
            defpon_vars[idx][0].set(weapon_type_mapping.get(defpon[0], "未知"))
            defpon_vars[idx][1].set(def_Amo.get(defpon[1], "未知"))

# 保存防具數據
def save_defpon_data(member):
    base_addr = address_map[member] + 0x24  # 防具起始位址 = 武器起始位址 + 24
    for idx, defpon_var in enumerate(defpon_vars):
        addr = base_addr + idx * 4
        defpon1 = next((key for key, value in weapon_type_mapping.items() if value == defpon_var[0].get()), None)
        defpon2 = next((key for key, value in def_Amo.items() if value == defpon_var[1].get()), None)

        # 檢查是否成功找到對應值
        if defpon1 is not None and defpon2 is not None:
            struct.pack_into('B', save_data, addr, defpon1)
            struct.pack_into('B', save_data, addr + 1, defpon2)

# 恢復防具選單的隊員選取狀態
def on_defpon_select(*args):
    global selected_member
    if selected_member:
        member_name = list(team_name_mapping.keys())[list(team_name_mapping.values()).index(selected_member)]
        team_listbox.selection_clear(0, 'end')
        team_listbox.selection_set(team_listbox.get(0, 'end').index(member_name))

# 處理配件數據段落
# 解析配件數據
def parse_ringpon_data(data, start_addr):
    ringpons = []
    for i in range(9):
        addr = start_addr + i * 4
        ringpon1 = struct.unpack_from('B', data, addr)[0]
        ringpon2 = struct.unpack_from('B', data, addr + 1)[0]
        ringpons.append((ringpon1, ringpon2))
    return ringpons

# 更新顯示的配件數據
def update_ringpon_data(member):
    base_addr = address_map[member] + 0x48  # 配件起始位址 = 武器起始位址 + 48
    ringpon_data = parse_ringpon_data(save_data, base_addr)
    for idx, ringpon in enumerate(ringpon_data):
        if idx < len(ring_vars):  # 確保不會超出現有的 GUI 元素
            ring_vars[idx][0].set(weapon_type_mapping.get(ringpon[0], "未知"))
            ring_vars[idx][1].set(ring_ID_EQ.get(ringpon[1], "未知"))

# 保存配件數據
def save_ringpon_data(member):
    base_addr = address_map[member] + 0x48  # 配件起始位址 = 武器起始位址 + 48
    for idx, ringpon_var in enumerate(ring_vars):   #ring_vars是與下面的GUI名稱配合
        addr = base_addr + idx * 4
        ringpon1 = next((key for key, value in weapon_type_mapping.items() if value == ringpon_var[0].get()), None)
        ringpon2 = next((key for key, value in ring_ID_EQ.items() if value == ringpon_var[1].get()), None)

        # 檢查是否成功找到對應值
        if ringpon1 is not None and ringpon2 is not None:
            struct.pack_into('B', save_data, addr, ringpon1)
            struct.pack_into('B', save_data, addr + 1, ringpon2)

# 恢復配件選單的隊員選取狀態
def on_ringpon_select(*args):
    global selected_member
    if selected_member:
        member_name = list(team_name_mapping.keys())[list(team_name_mapping.values()).index(selected_member)]
        team_listbox.selection_clear(0, 'end')
        team_listbox.selection_set(team_listbox.get(0, 'end').index(member_name))


# 處理雜項數據段落
# 解析雜項數據
def parse_itempon_data(data, start_addr):
    itempons = []
    for i in range(9):
        addr = start_addr + i * 4
        itempon1 = struct.unpack_from('B', data, addr)[0]
        itempon2 = struct.unpack_from('B', data, addr + 1)[0]
        itempon3 = struct.unpack_from('B', data, addr + 2)[0]  # 解析使用次數
        itempons.append((itempon1, itempon2, itempon3))
    return itempons

# 更新顯示的雜項數據
def update_itempon_data(member):
    base_addr = address_map[member] + 0x6C  # 雜項起始位址 = 武器起始位址 + 72
    itempon_data = parse_itempon_data(save_data, base_addr)
    for idx, itempon in enumerate(itempon_data):
        if idx < len(item_vars):  # 確保不會超出現有的 GUI 元素
            item_vars[idx][0].set(item_ID.get(itempon[0], "未知"))
            item_vars[idx][1].set(item_type_mapping.get(itempon[1], "未知"))
            item_vars[idx][2].set(itempon[2])  # 顯示使用次數

# 保存雜項數據
def save_itempon_data(member):
    base_addr = address_map[member] + 0x6C  # 配件起始位址 = 武器起始位址 + 72
    for idx, itempon_var in enumerate(item_vars):   #item_vars是與下面的GUI名稱配合
        addr = base_addr + idx * 4
        itempon1 = next((key for key, value in item_ID.items() if value == itempon_var[0].get()), None)
        itempon2 = next((key for key, value in item_type_mapping.items() if value == itempon_var[1].get()), None)
        # 對使用次數進行範圍檢查，確保其值在0到63之間
        try:
            itempon3 = int(itempon_var[2].get())
            itempon3 = max(0, min(63, itempon3))  # 限制範圍為 0~63
        except ValueError:
            itempon3 = 0  # 若輸入數值無效則設為0
        # 檢查是否成功找到對應值
        if itempon1 is not None and itempon2 is not None:
            struct.pack_into('B', save_data, addr, itempon1)
            struct.pack_into('B', save_data, addr + 1, itempon2)
            struct.pack_into('B', save_data, addr + 2, itempon3)  # 保存使用次數  

# 恢復雜項選單的隊員選取狀態
def on_itempon_select(*args):
    global selected_member
    if selected_member:
        member_name = list(team_name_mapping.keys())[list(team_name_mapping.values()).index(selected_member)]
        team_listbox.selection_clear(0, 'end')
        team_listbox.selection_set(team_listbox.get(0, 'end').index(member_name))

# 解析隊伍資訊數據
def parse_team_data(data):
    global team_data
    team_data = {}
    for i, (addr, size) in enumerate(team_addresses):
        # 讀取指定位址的數據，使用小端格式轉換為整數
        team_data[team_labels[i]] = int.from_bytes(data[addr:addr+size], 'little')

# 更新顯示的隊伍資訊數據
def update_team_data_display():
    for i, entry in enumerate(team_entries):
        entry.delete(0, tk.END)  # 清空輸入框
        entry.insert(0, str(team_data[team_labels[i]]))  # 插入對應數據

# 處理隊員選取事件
def on_member_select(event):
    global selected_member
    if team_listbox.curselection():
        selected_index = team_listbox.curselection()[0]
        selected_member = list(team_name_mapping.values())[selected_index]
        if selected_member:
            member_name = list(team_name_mapping.keys())[list(team_name_mapping.values()).index(selected_member)]
            update_selected_member_label(member_name)
            update_weapon_data(selected_member)
            update_attribute_data(selected_member)
            update_defpon_data(selected_member)
            update_ringpon_data(selected_member)
            update_itempon_data(selected_member)

def write_team_data():
    global save_data
    for i, (addr, size) in enumerate(team_addresses):
        try:
            value = int(team_entries[i].get())  # 從 GUI 輸入框獲取新數值
            value = max(0, min(4294967295, value))  # 限制數值範圍（避免溢出）
            save_data[addr:addr+size] = value.to_bytes(size, 'little')  # 轉換為小端格式字節並寫入 save_data
        except ValueError:
            pass  # 若輸入值無效（非數字），則跳過

# 保存能力和抗性數據
def save_attribute_data(member):
    name_addr, attr_start_addr, resist_start_addr = member_addresses[member]
    for i, attribute in enumerate(attributes):
        try:
            value = int(attribute_vars[attribute].get())
            value = max(0, min(255, value))  # 限制範圍為 0~255（避免存檔異常）

            # 計算存入存檔的位址
            addr = attr_start_addr + i * 2 if i < 7 else attr_start_addr + 7 * 2 + 1
            struct.pack_into('B', save_data, addr, value)  # 更新存檔數據

        except ValueError:
            pass  # 若輸入數值無效則忽略

    for i, resistance in enumerate(resistances):
        try:
            value = int(attribute_vars[resistance].get())
            value = max(0, min(255, value))  # 限制範圍為 0~255（避免存檔異常）

            # 計算存入存檔的位址
            addr = resist_start_addr + i * 2
            struct.pack_into('B', save_data, addr, value)  # 更新存檔數據

        except ValueError:
            pass  # 若輸入數值無效則忽略

# 保存隊伍資訊數據
def save_partydata():
    global save_data
    for i, (addr, size) in enumerate(team_addresses):
        try:
            value = int(team_entries[i].get())
            value = max(0, min(4294967295, value))  # 限制範圍，避免溢出
            save_data[addr:addr+size] = value.to_bytes(size, 'little')  # 轉換為小端格式並寫入 save_data
        except ValueError:
            pass  # 若輸入值無效則忽略

# 保存數據到檔案
def save_to_file():
    global selected_member, save_data
    if selected_member:
        save_weapon_data(selected_member)
        save_attribute_data(selected_member)
        save_defpon_data(selected_member)
        save_ringpon_data(selected_member)
        save_itempon_data(selected_member)

    # 保存隊伍資訊數據
    save_partydata()

    # 確保在保存時，已經指定了保存檔案的路徑
    if game_save_file:
        with open(game_save_file, 'wb') as file:
            file.write(save_data)
    else:
        print("保存檔案路徑未指定")

# 更新隊員列表框
def update_team_listbox():
    team_listbox.delete(0, 'end')
    global team_name_mapping
    team_name_mapping = {}
    for member in team_members:
        name_addr, attr_start_addr, resist_start_addr = member_addresses[member]
        member_name = get_member_name(save_data, name_addr, name_addr + 7)
        if member_name:
            team_listbox.insert('end', member_name)
            team_name_mapping[member_name] = member

# 獲取隊員名字
def get_member_name(data, start_addr, end_addr):
    name_bytes = data[start_addr:end_addr + 1]

    # 檢查是否所有數據都是 0x00
    if all(b == 0x00 for b in name_bytes):
        return None  # 該隊員不存在

    # 只取前8個字節，並在遇到0x00時終止
    valid_bytes = bytearray()
    for b in name_bytes[:8]:  # 只檢查前6個字節
        if b == 0x00:
            break  # 遇到0x00時終止
        valid_bytes.append(b)

    # 嘗試解碼為 Big5 編碼的字串
    try:
        name = valid_bytes.decode('big5').strip('\x00')
    except UnicodeDecodeError:
        name = None  # 如果解碼失敗，認為該隊員不存在

    return name


# 全局變量初始化
save_data = None
selected_member = None
team_name_mapping = {}
attribute_vars = {}  # 確保在全局作用範圍內定義
weapon_vars = []  # 初始化武器變數
defpon_vars = []  # 初始化防具變數
item_vars = []  # 初始化雜項變數

# 創建 GUI
root = tk.Tk()
root.title("魔法門外傳合輯修改器")

# 定義驗證函數和命令
def validate_input(value_if_allowed):
    if value_if_allowed.isdigit() and 0 <= int(value_if_allowed) <= 255:
        return True
    return False
vcmd = (root.register(validate_input), '%P')

# 創建主框架
main_frame = ttk.Frame(root)
main_frame.pack(fill='both', expand=True)

# 創建隊員欄
team_frame = ttk.Frame(main_frame)
team_frame.pack(side='left', fill='y')
ttk.Label(team_frame, text="隊員").pack()

team_listbox = tk.Listbox(team_frame, width=15, height=20)
team_listbox.pack(fill='y')
team_listbox.bind('<<ListboxSelect>>', on_member_select)

# 創建標籤頁
tab_control = ttk.Notebook(main_frame)
tab_control.pack(side='right', fill='both', expand=True)

# 創建能力標籤頁
abilities_frame = ttk.Frame(tab_control)
abilities_frame.pack(fill='both', expand=True)
selected_member_label = ttk.Label(abilities_frame, text="")
selected_member_label.pack()

# 創建武器標籤頁
weapon_frame = ttk.Frame(tab_control)
weapon_frame.pack(fill='both', expand=True)
selected_weapon_label = ttk.Label(weapon_frame, text="")
selected_weapon_label.pack()

# 創建防具標籤頁
def_frame = ttk.Frame(tab_control)
def_frame.pack(fill='both', expand=True)
selected_def_label = ttk.Label(def_frame, text="")
selected_def_label.pack()

# 創建配件標籤頁
ring_frame = ttk.Frame(tab_control)
ring_frame.pack(fill='both', expand=True)
selected_ring_label = ttk.Label(ring_frame, text="")
selected_ring_label.pack()

# 創建雜項標籤頁
item_frame = ttk.Frame(tab_control)
abilities_frame.pack(fill='both', expand=True)
selected_item_label = ttk.Label(item_frame, text="")
selected_item_label.pack()

# 創建隊伍資訊標籤頁
teams_frame = ttk.Frame(tab_control)
teams_frame.pack(fill='both', expand=True)
selected_team_label = ttk.Label(teams_frame, text="隊伍資訊")
selected_team_label.pack()

team_entries = []

for label in team_labels:
    frame = ttk.Frame(teams_frame)
    frame.pack(fill='x', padx=10, pady=5)
    ttk.Label(frame, text=label).pack(side='left')
    entry = ttk.Entry(frame, width=20)
    entry.pack(side='left')
    team_entries.append(entry)

# 能力數值分頁
ability_frame = tk.Frame(abilities_frame)
ability_frame.pack(expand=True, fill="both", padx=10, pady=10)

# 顯示能力數值標籤並設置輸入框
for i, label in enumerate(attributes):
    tk.Label(ability_frame, text=label).grid(row=i, column=0, pady=2, sticky="w")  # 顯示標籤
    var = tk.StringVar()
    attribute_vars[label] = var
    entry = tk.Entry(ability_frame, textvariable=var, width=8)  # 移除驗證限制
    entry.grid(row=i, column=1, pady=2)  # 放置輸入框

# 顯示抗性數值標籤並設置輸入框
for i, label in enumerate(resistances):
    tk.Label(ability_frame, text=label).grid(row=i, column=2, pady=2, sticky="w")  # 顯示標籤
    var = tk.StringVar()
    attribute_vars[label] = var
    entry = tk.Entry(ability_frame, textvariable=var, width=8)  # 移除驗證限制
    entry.grid(row=i, column=3, pady=2)  # 放置輸入框

#武器
weapon_vars = []
for i in range(9):  # 9組武器
    weapon_frame_inner = ttk.Frame(weapon_frame)
    weapon_frame_inner.pack(fill='x', padx=10, pady=5)
    ttk.Label(weapon_frame_inner, text=f"武器{i+1}").pack(side='left')
    weapon_vars.append([tk.StringVar(), tk.StringVar(), tk.StringVar()])
    for idx, var in enumerate(weapon_vars[-1]):
        if idx == 0:
            ttk.Combobox(weapon_frame_inner, textvariable=var, values=list(weapon_type_mapping.values()), width=30).pack(side='left', padx=5)
        elif idx == 1:
            ttk.Combobox(weapon_frame_inner, textvariable=var, values=list(WEAPON_ID_DESCRIPTIONS.values()), width=22).pack(side='left', padx=5)
        else:
            ttk.Combobox(weapon_frame_inner, textvariable=var, values=list(WEAPON_SPECIAL_EFFECTS.values()), width=10).pack(side='left', padx=5)

#防具
defpon_vars = []
for i in range(9):  # 9組防具
    defpon_frame_inner = ttk.Frame(def_frame)
    defpon_frame_inner.pack(fill='x', padx=10, pady=5)
    ttk.Label(defpon_frame_inner, text=f"防具{i+1}").pack(side='left')
    defpon_vars.append([tk.StringVar(), tk.StringVar()])
    for idx, var in enumerate(defpon_vars[-1]):
        if idx == 0:
            ttk.Combobox(defpon_frame_inner, textvariable=var, values=list(weapon_type_mapping.values()), width=30).pack(side='left', padx=5)
        elif idx == 1:
            ttk.Combobox(defpon_frame_inner, textvariable=var, values=list(def_Amo.values()), width=10).pack(side='left', padx=5)

#配件
ring_vars = []
for i in range(9):  # 9組配件
    ring_frame_inner = ttk.Frame(ring_frame)
    ring_frame_inner.pack(fill='x', padx=10, pady=5)
    ttk.Label(ring_frame_inner, text=f"配件{i+1}").pack(side='left')
    ring_vars.append([tk.StringVar(), tk.StringVar()])
    for idx, var in enumerate(ring_vars[-1]):
        if idx == 0:
            ttk.Combobox(ring_frame_inner, textvariable=var, values=list(weapon_type_mapping.values()), width=30).pack(side='left', padx=5)
        elif idx == 1:
            ttk.Combobox(ring_frame_inner, textvariable=var, values=list(ring_ID_EQ.values()), width=15).pack(side='left', padx=5)

#雜項
item_vars = []
for i in range(9):  # 9組雜項
    item_frame_inner = ttk.Frame(item_frame)
    item_frame_inner.pack(fill='x', padx=10, pady=5)
    ttk.Label(item_frame_inner, text=f"雜項{i+1}").pack(side='left')
    item_vars.append([tk.StringVar(), tk.StringVar(), tk.StringVar()])  # 增加一個變數用於保存使用次數
    for idx, var in enumerate(item_vars[-1]):
        if idx == 0:
            ttk.Combobox(item_frame_inner, textvariable=var, values=list(item_ID.values()), width=8).pack(side='left', padx=5)
        elif idx == 1:
            ttk.Combobox(item_frame_inner, textvariable=var, values=list(item_type_mapping.values()), width=12).pack(side='left', padx=5)
        elif idx == 2:
            ttk.Label(item_frame_inner, text="使用次數：").pack(side='left', padx=5)  # 增加使用次數文字
            ttk.Entry(item_frame_inner, textvariable=var, width=5).pack(side='left', padx=5)  # 增加使用次數的可編輯框框


# 將標籤頁加入到 Notebook
tab_control.add(abilities_frame, text='   能   力   ')
tab_control.add(weapon_frame, text='   武   器   ')
tab_control.add(def_frame, text='   防   具   ')
tab_control.add(ring_frame, text='   配   件   ')
tab_control.add(item_frame, text='   雜   項   ')
tab_control.add(teams_frame, text=' 隊 伍 資 料 ')


# 設置標籤頁控制
tab_control.pack(expand=1, fill='both')

# 綁定武器選單的事件
for i in range(len(weapon_vars)):
    for var in weapon_vars[i]:
        var.trace('w', on_weapon_select)

# 載入數據
def load_new_file():
    global save_data, game_save_file
    file_path = filedialog.askopenfilename(initialdir='.', filetypes=[('SAV files', '*.sav')])  # 限制只選擇 .sav 檔案
    if file_path:
        game_save_file = file_path  # 保存選擇的檔案路徑
        save_data = load_save_data(file_path)
        update_team_listbox()
        parse_team_data(save_data)  # 解析隊伍數據
        update_team_data_display()  # 更新隊伍數據顯示

def load_file():
    global save_data, game_save_file
    game_save_file = 'D:\\dos-games\\XEEN\\ARK01.SAV'  # 設定預設檔案路徑
    save_data = load_save_data(game_save_file)
    update_team_listbox()  # 更新隊員列表框

# 創建按鈕框架來放置按鈕
button_frame = ttk.Frame(root)
button_frame.pack(side='bottom', pady=10)

# 增加讀取檔案按鈕
load_button = ttk.Button(button_frame, text="讀檔", command=load_new_file)
load_button.pack(side='left', padx=5)

# 增加存檔按鈕
save_button = ttk.Button(button_frame, text="存檔", command=save_to_file)
save_button.pack(side='left', padx=5)

root.mainloop()
