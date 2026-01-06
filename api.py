# api.py
import sqlite3
from fastapi import FastAPI, HTTPException, Path
from models import PostCreate, PostResponse

#  建立應用程式物件
app = FastAPI(
    title="名言佳句 API",
    description=(
        "這是一個名言佳句管理系統的API"
        ",可以用來新增、修改、刪除和查詢名言資料。\n"
        )
     )
# 參考自 第 3 次小考老師提供的 api.py 範例程式碼
#  1.建立資料庫連線
def get_connection() -> sqlite3.Connection:
    """取得資SQLite料庫連線"""
    conn = sqlite3.connect('quotes.db')
    # 讓結果像字典一樣存取
    conn.row_factory = sqlite3.Row
    return conn
#  2.取得所有名言
def get_all_quotes() -> list[dict]:
    """取得所有名言"""
    conn = get_connection()
    cursor = conn.cursor()
    # SQL 查詢
    cursor.execute("SELECT id, text, author, tags FROM quotes")
    rows = cursor.fetchall()
    conn.close()
    # FastAPI 回傳 JSON
    return [dict(row) for row in rows]
#  3.用 ID 查單一名言
def get_quote_by_id(quote_id: int) -> dict | None:
    """根據 ID 取得單一名言"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, text, author, tags FROM quotes WHERE id = ?", (quote_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None
#  4.新增名言（POST）
def create_quote(text: str, author: str, tags: str):
    """新增名言，回傳新 ID"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO quotes (text, author, tags) VALUES (?, ?, ?)", (text, author, tags))
    conn.commit()
    quote_id = cursor.lastrowid
    conn.close()
    return quote_id
#  5.更新名言（PUT）
def update_quote(quote_id: int, text: str, author: str, tags: str):
    """更新名言"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE quotes SET text = ?, author = ?, tags = ? WHERE id = ?", (text, author, tags, quote_id))
    conn.commit()
    changed = cursor.rowcount > 0
    conn.close()
    return changed
# 6.刪除名言（DELETE）
def delete_quote(quote_id: int):
    """刪除名言"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM quotes WHERE id = ?", (quote_id,))
    conn.commit()
    changed = cursor.rowcount > 0
    conn.close()
    return changed
# 建立 API 路由
@app.get("/")
def Read_root():
    """API 根路徑，回傳歡迎訊息"""
    return {"message": "Quotes API is running."}
# 取得所有名言
@app.get("/quotes", response_model=list[PostResponse])
def get_quotes():
    """取得所有名言"""
    quotes = get_all_quotes()
    return [PostResponse(**quote) for quote in quotes]
# 取得指定 ID 的名言
@app.post("/quotes", response_model=PostResponse, status_code=201)
def create_Quote(quote: PostCreate):
    """新增名言"""
    quote_id = create_quote(quote.text, quote.author, quote.tags)
    new_quote = get_quote_by_id(quote_id)
    return PostResponse(**new_quote)
# 更新指定 ID 的名言
@app.put("/quotes/{quote_id}", response_model=PostResponse)
def update_Quote(quote: PostCreate, quote_id: int = Path(..., gt=0, description="名言 ID")):
    """更新指定 ID 的名言"""
    if not get_quote_by_id(quote_id):
        raise HTTPException(status_code=404, detail="Quote not found")
    update_quote(quote_id, quote.text, quote.author, quote.tags)
    updated_quote = get_quote_by_id(quote_id)
    return PostResponse(**updated_quote)
# 刪除指定 ID 的名言
@app.delete("/quotes/{quote_id}")
def delete_Quote(quote_id: int = Path(..., gt=0, description="名言 ID")):
    """刪除指定 ID 的名言"""
    if not get_quote_by_id(quote_id):
        raise HTTPException(status_code=404, detail="Quote not found")
    delete_quote(quote_id)
    return {"message": "Quote deleted successfully"}