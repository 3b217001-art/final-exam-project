import time
# 導入 SQLite3 
import sqlite3
# Selenium 套件
# 核心 WebDriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# 例外處理
from selenium.common.exceptions import NoSuchElementException, TimeoutException
# 所有程式參考自:Selenium 套件的6.3 實戰：多頁面資料爬取
# 設定 headless 模式
options = Options()
# 無頭模式 (背景執行)
options.add_argument("--headless")
# 禁用 GPU 硬體加速，在某些伺服器環境可增加穩定性
options.add_argument("--disable-gpu")
# 讓瀏覽器以最高權限
options.add_argument("--no-sandbox")

URL = "http://quotes.toscrape.com/js/"
browser = webdriver.Chrome(options=options)
browser.get(URL)
# 儲存所有名言的清單
all_quotes = []
page_count = 1
# 最多爬取 5 頁
# 透過 while 迴圈控制翻頁
while page_count <= 5:
    print(f"正在爬取第 {page_count} 頁...")
    try:
        #  會等待最多 10 秒，直到頁面上出現類名為 "quote" 的元素
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".quote"))
        )
        # 找出這一頁的所有名言
        quotes = browser.find_elements(By.CSS_SELECTOR, ".quote")
        # 開始處理每一則名言
        for quote in quotes:
            # 提取名言內容、作者和標籤
            text = quote.find_element(By.CSS_SELECTOR, ".text").text
            author = quote.find_element(By.CSS_SELECTOR, ".author").text
            tags_elements = quote.find_elements(By.CSS_SELECTOR, ".tags .tag")
            tags = ", ".join([tag.text for tag in tags_elements])
            all_quotes.append({
                "text": text,
                "author": author,
                "tags": tags
            })
    except TimeoutException:
        print("等待頁面載入超時，提前結束。")
        break

    try:
        next_button = browser.find_element(By.CSS_SELECTOR, ".next a")
        next_button.click()
        page_count += 1
        time.sleep(2)  # 等待頁面刷新
    except NoSuchElementException:
        print("找不到下一頁按鈕，爬取結束。")
        break

browser.quit()

# 儲存到 SQLite
conn = sqlite3.connect("quotes.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    author TEXT NOT NULL,
    tags TEXT
)
""")

for quote in all_quotes:
    cursor.execute("INSERT INTO quotes (text, author, tags) VALUES (?, ?, ?)",
                   (quote["text"], quote["author"], quote["tags"]))

conn.commit()
conn.close()
# 顯示部分結果
print("爬取完成，資料已儲存到 quotes.db ")

# 顯示部分結果測試用
# print("\n" + "="*50)
# print(f"總共爬取了 {len(all_quotes)} 則名言。")
# print("部分資料如下：")
# for quote in all_quotes[:5]:
#     print(f"內容: {quote['text']}")
#     print(f"作者: {quote['author']}")
#     print(f"標籤: {quote['tags']}")
#     print("-" * 30)
# print("="*50)
