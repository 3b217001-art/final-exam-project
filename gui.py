#  Tkinter 的核心模組，用於建構 GUI
import tkinter as tk
#  messagebox 用於顯示對話框（警告、錯誤等）
from tkinter import ttk, messagebox
# 用於創建子執行緒，避免在主 UI 執行緒中執行網路請求
import threading
import requests

API_URL = "http://localhost:8000/quotes"

#  狀態列 & 按鈕鎖定工具 導入確保應用程式能處理 UI、多執行緒和網路通訊。
#  text（狀態訊息）；color（文字顏色，預設黑色）； auto_clear（是否自動清除訊息，預設 False）
def set_status(text, color="black", auto_clear=False):
    status_label.config(text=text, fg=color)
    if auto_clear:
        form.after(3000, lambda: status_label.config(text="", fg="black"))
#  目的：鎖定或解鎖按鈕，避免重複操作
def lock_buttons(lock: bool):
#  將 btn_refresh 和 btn_add 設為 DISABLED 或 NORMAL；如果鎖定，還禁用 btn_update 和 btn_delete
    state = tk.DISABLED if lock else tk.NORMAL
    btn_refresh.config(state=state)
    btn_add.config(state=state)

    if lock:
        btn_update.config(state=tk.DISABLED)
        btn_delete.config(state=tk.DISABLED)

#  Treeview 工具，專門處理表格（Treeview）的資料
#  清除表格中的所有資料
def clear_data():
    for i in tree.get_children():
        tree.delete(i)
#  清除輸入欄位的內容
def clear_inputs():
    text_entry.delete("1.0", tk.END)
    author_entry.delete(0, tk.END)
    tags_entry.delete(0, tk.END)
    
#  API 呼叫（子執行緒用）
def api_get():
    r = requests.get(API_URL, timeout=10)
    r.raise_for_status()
    return r.json()
#  新增名言
def api_add(text, author, tags):
    r = requests.post(API_URL, json={
        "text": text,
        "author": author,
        "tags": tags
    }, timeout=10)
    r.raise_for_status()
#   更新名言
def api_update(qid, text, author, tags):
    r = requests.put(f"{API_URL}/{qid}", json={
        "text": text,
        "author": author,
        "tags": tags
    }, timeout=10)
    r.raise_for_status()
#  刪除名言
def api_delete(qid):
    r = requests.delete(f"{API_URL}/{qid}", timeout=10)
    r.raise_for_status()

#   執行緒工作
def load_thread():
    try:
        data = api_get()
        form.after(0, lambda: update_table(data, "資料載入完成"))
    except Exception as e:
        form.after(0, lambda: show_error(str(e)))
# 新增名言執行緒
def add_thread(text, author, tags):
    try:
        api_add(text, author, tags)
        form.after(0, on_refresh_click)
        form.after(0, clear_inputs)
        form.after(0, lambda: set_status("新增成功！", "green", True))
    except Exception as e:
        form.after(0, lambda: show_error(str(e)))
#  更新名言執行緒
def update_thread(qid, text, author, tags):
    try:
        api_update(qid, text, author, tags)
        form.after(0, on_refresh_click)
        form.after(0, lambda: set_status("更新成功！", "green", True))
    except Exception as e:
        form.after(0, lambda: show_error(str(e)))
# 刪除名言執行緒
def delete_thread(qid):
    try:
        api_delete(qid)
        form.after(0, on_refresh_click)
        form.after(0, lambda: set_status("刪除成功！", "green", True))
    except Exception as e:
        form.after(0, lambda: show_error(str(e)))

#   UI 更新 
#  參數：data（名言列表）；message（狀態訊息）
def update_table(data, message):
    clear_data()
    for q in data:
        tree.insert("", tk.END, values=(q["id"], q["author"], q["text"], q["tags"]))
    lock_buttons(False)
    set_status(message, "green")
#  參數：msg（錯誤訊息）
def show_error(msg):
    messagebox.showerror("錯誤", msg)
    lock_buttons(False)
    set_status("錯誤：" + msg, "red", True)

#  按鈕事件處理函式
#  重新整理按鈕點擊
def on_refresh_click():
    lock_buttons(True)
    set_status("連線中，請稍候…", "red")
    threading.Thread(target=load_thread, daemon=True).start()
# 新增按鈕點擊
def on_add_click():
    text = text_entry.get("1.0", tk.END).strip()
    author = author_entry.get().strip()
    tags = tags_entry.get().strip()

    if not text or not author or not tags:
        messagebox.showwarning("警告", "請填寫所有欄位")
        return

    lock_buttons(True)
    set_status("連線中，請稍候…", "red")
    threading.Thread(target=lambda: add_thread(text, author, tags), daemon=True).start()
# 重新整理按鈕點擊
def on_update_click():
    sel = tree.selection()
    if not sel:
        return

    qid = tree.item(sel[0])["values"][0]

    text = text_entry.get("1.0", tk.END).strip()
    author = author_entry.get().strip()
    tags = tags_entry.get().strip()

    lock_buttons(True)
    set_status("連線中，請稍候…", "red")
    threading.Thread(target=lambda: update_thread(qid, text, author, tags), daemon=True).start()
# 刪除按鈕點擊
def on_delete_click():
    sel = tree.selection()
    if not sel:
        return

    if not messagebox.askyesno("確認", "確定要刪除？"):
        return

    qid = tree.item(sel[0])["values"][0]

    lock_buttons(True)
    set_status("連線中，請稍候…", "red")
    threading.Thread(target=lambda: delete_thread(qid), daemon=True).start()
# Treeview 選取事件處理
def on_tree_select(event):
    sel = tree.selection()
    if not sel:
        return
    #  取得選取列的值
    values = tree.item(sel[0])["values"]
    #  填入輸入欄位
    author_entry.delete(0, tk.END)
    author_entry.insert(0, values[1])
    #  名言內容
    text_entry.delete("1.0", tk.END)
    text_entry.insert("1.0", values[2])
    # 標籤
    tags_entry.delete(0, tk.END)
    tags_entry.insert(0, values[3])
    # 啟用更新與刪除按鈕
    btn_update.config(state=tk.NORMAL)
    btn_delete.config(state=tk.NORMAL)
    #  顯示狀態
    qid = values[0]
    set_status(f"已選取 ID: {qid}", "black")

#  主視窗 
def main():
    global form, tree, text_entry, author_entry, tags_entry
    global btn_refresh, btn_add, btn_update, btn_delete, status_label

    form = tk.Tk()
    form.title("名言管理系統 (Threading)")
    form.geometry("800x600")
    #  1.上方：Treeview 區  
    frame_table = tk.Frame(form)
    frame_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

    scrollbar = ttk.Scrollbar(frame_table)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    columns = ("ID", "Author", "Text", "Tags")
    tree = ttk.Treeview(
        frame_table,
        columns=columns,
        show="headings",
        yscrollcommand=scrollbar.set
    )
    # 連結滾動條
    scrollbar.config(command=tree.yview)

    tree.heading("ID", text="ID")
    tree.column("ID", width=50, anchor="center")

    tree.heading("Author", text="作者")
    tree.column("Author", width=150)

    tree.heading("Text", text="名言內容")
    tree.column("Text", width=430)

    tree.heading("Tags", text="標籤")
    tree.column("Tags", width=200)
    tree.pack(fill=tk.BOTH, expand=True)
    tree.bind("<<TreeviewSelect>>", on_tree_select)
    #  2. 編輯 / 新增 
    frame_edit = tk.LabelFrame(form, text="編輯 / 新增區", padx=12, pady=12)
    frame_edit.pack(fill=tk.X, padx=10, pady=5)

    # 名言內容
    tk.Label(frame_edit, text="名言內容 (Text):").grid(row=0, column=0, sticky="w", pady=(0, 2))
    text_entry = tk.Text(frame_edit, height=8, wrap="word")
    text_entry.grid(row=1, column=0, columnspan=4, sticky="we", padx=4, pady=(0, 10))

    # 作者
    tk.Label(frame_edit, text="作者 (Author):").grid(row=2, column=0, sticky="w", pady=(0, 2))
    author_entry = tk.Entry(frame_edit)
    author_entry.grid(row=3, column=0, sticky="we", padx=4)

    # 標籤
    tk.Label(frame_edit, text="標籤 (Tags):").grid(row=2, column=2, sticky="w", pady=(0, 2))
    tags_entry = tk.Entry(frame_edit)
    tags_entry.grid(row=3, column=2, sticky="we", padx=4)

    # 撐開欄位
    frame_edit.columnconfigure(0, weight=1)
    frame_edit.columnconfigure(2, weight=1)
    #  3. 操作按鈕
    frame_btn = tk.LabelFrame(form, text="操作選項", padx=10, pady=12)
    frame_btn.pack(fill=tk.X, padx=10, pady=5)

    frame_btn.columnconfigure(0, weight=2)
    frame_btn.columnconfigure(1, weight=1)
    frame_btn.columnconfigure(2, weight=1)
    frame_btn.columnconfigure(3, weight=1)

    btn_refresh = tk.Button(
        frame_btn, text="重新整理 (Refresh)",
        bg="#B0E0E6", command=on_refresh_click
    )
    btn_refresh.grid(row=0, column=0, sticky="we", padx=6)

    btn_add = tk.Button(
        frame_btn, text="新增 (Add)",
        bg="#90EE90", command=on_add_click
    )
    btn_add.grid(row=0, column=1, sticky="we", padx=6)

    btn_update = tk.Button(
        frame_btn, text="更新 (Update)",
        bg="#FFD700", state=tk.DISABLED,
        command=on_update_click
    )
    btn_update.grid(row=0, column=2, sticky="we", padx=6)

    btn_delete = tk.Button(
        frame_btn, text="刪除 (Delete)",
        bg="#FF7F7F", state=tk.DISABLED,
        command=on_delete_click
    )
    btn_delete.grid(row=0, column=3, sticky="we", padx=6)

    # 4. 狀態列 
    #  啟動載入on_refresh_click()
    status_label = tk.Label(
        frame_btn,
        text="",
        relief=tk.SUNKEN,
        anchor=tk.W
    )
    status_label.grid(
        row=1, column=0,
        columnspan=4,
        sticky="we",
        padx=6,
        pady=(10, 0)
        )
    # 啟動載入
    on_refresh_click()

    form.mainloop()

if __name__ == "__main__":
    main()
