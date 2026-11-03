# 練習：三民書局暢銷榜爬蟲 → MariaDB

用 `requests` + `BeautifulSoup` 抓「三民網路書店 暢銷總榜」的書名，存進 MariaDB。

- 網址：<https://www.sanmin.com.tw/promote/top>
- 只需要 Python 基本語法：變數、`list`、`for`、`if`。不用寫 class。

---

## 題目

寫一支 `crawler.py`，完成下面 5 件事：

1. **先讀 robots.txt**，確認可以抓 `https://www.sanmin.com.tw/promote/top`。
2. 用 `requests` 抓排行榜頁面，要設定 `User-Agent` 和 `timeout`。
3. 用 `BeautifulSoup` 找出每一本書的 **排名、書名、作者、出版社、書的網址**。
4. 存進 MariaDB 的 `books` 資料表（`crawler_course` 資料庫）。**同一天執行兩次，不能變成 80 本**。
5. 從資料庫查回今天的資料，印出共幾本，以及前 10 名的書名。

### 延伸題

6. 排行榜有 3 頁（`?id=wbyy&pi=1`、`pi=2`、`pi=3`）。用 `for` 迴圈抓完 3 頁，每頁之間等 1 秒，印出每頁幾本、共幾本。

---

## 準備

```bash
git clone https://github.com/4-learn/books-crawler.git
cd books-crawler
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

資料庫沿用第 16 節建好的 `crawler_course` 和 `crawler` 帳號。還沒建的話，照〈[16 附錄：MariaDB 一步一步做](https://github.com/4-learn/python-web-crawler-demo/blob/main/docs/16-mariadb-setup.md)〉第 1–6 步做。

```bash
export DB_USER=crawler DB_PASS='crawler-db-2026' DB_NAME=crawler_course
```

`schema.sql` 已經寫好，執行一次就會建出 `books` 資料表：

```bash
mariadb -u $DB_USER -p$DB_PASS $DB_NAME < schema.sql
```

---

## 提示

### 提示 1：先用瀏覽器看網頁長怎樣

打開排行榜頁，在第一本書的書名上按右鍵 →「檢查」。你會看到每一本書都包在一個 `<div class="sProduct">` 裡面：

```html
<div class="sProduct" id="Prod015911594">
  ...
  <div class="Title">
    <a href="/product/index/015911594">1.<h3>萬相天后：臺灣媽祖信仰文化特展展覽專刊</h3></a>
  </div>
  <div class="Attribute">
    <span class="Author"><b>作者：</b><span class="text-green"><a href="...">廖伯豪</a></span></span>
    <span class="Publisher"><b>出版社：</b><span class="text-green"><a href="...">國立臺灣歷史博物館</a></span></span>
  </div>
  ...
</div>
```

（書名和排名每天會變，你看到的不一定是這本。）

| 要的資料 | 在哪裡 |
|---|---|
| 一本書 | `div.sProduct` |
| 書名 | 裡面的 `h3` |
| 作者 | 裡面的 `span.Author`（文字前面有「作者：」要拿掉） |
| 出版社 | 裡面的 `span.Publisher`（文字前面有「出版社：」要拿掉） |
| 網址 | 裡面第一個 `a` 的 `href`，前面要加上 `https://www.sanmin.com.tw` |

### 提示 2：讀 robots.txt

```python
r = requests.get("https://www.sanmin.com.tw/robots.txt", headers=HEADERS, timeout=10)
robots = RobotFileParser()
robots.parse(r.text.splitlines())
allowed = robots.can_fetch(HEADERS["User-Agent"], URL)
print("robots.txt 允許嗎？", allowed)      # True 才可以抓
```

`crawler.py` 已經寫好 `if allowed:`：`allowed` 是 `True` 才會去抓排行榜；`False` 就什麼都不抓。

### 提示 3：找出所有書

`crawler.py` 已經寫好抓網頁和 `soup = BeautifulSoup(r.text, "html.parser")`。先試試看一頁有幾本：

```python
items = soup.select("div.sProduct")
print(len(items))             # 一頁有幾本？
```

`狀態碼` 印出 200 才是成功。

### 提示 4：從一本書裡拿出書名

```python
for item in items:
    title = item.select_one("h3").get_text(strip=True)
    print(title)
```

- `select("…")`：找出**全部**符合的，得到一個 list。
- `select_one("…")`：只找**第一個**。
- `get_text(strip=True)`：拿出文字，去掉前後空白。
- 排名：在 `for` 外面放一個 `rank = 0`，迴圈裡每次 `rank = rank + 1`。

### 提示 5：存進 MariaDB

```python
import os
import mariadb

conn = mariadb.connect(
    host="localhost",
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASS"],
    database=os.environ["DB_NAME"],
)
cur = conn.cursor()

sql = "INSERT INTO books (rank_date, rank_no, title, author, publisher, url) VALUES (?, ?, ?, ?, ?, ?)"
cur.execute(sql, (today, rank, title, author, publisher, link))
conn.commit()      # 沒有 commit，資料不會真的存進去
```

- SQL 裡的值一律用 `?`，不要自己用 `+` 把書名拼進 SQL（書名裡可能有引號）。
- `today` 用 `datetime.date.today()`。
- **同一天跑兩次不能重複**：`books` 表的 `(rank_date, rank_no)` 是唯一鍵。想想看第 16 節的 `ON DUPLICATE KEY UPDATE` 怎麼用。

### 提示 6：查回來確認

```python
cur.execute("SELECT COUNT(*) FROM books WHERE rank_date = ?", (today,))
print(cur.fetchone()[0])
```

---

## 預期輸出

```text
robots.txt 允許嗎？ True
狀態碼： 200
抓到 40 本
資料庫裡 2026-11-02 共 40 本
1 （第 1 名的書名）
2 （第 2 名的書名）
...
10 （第 10 名的書名）
```

同一天再執行一次，「資料庫裡 … 共 40 本」**還是 40**，不會變成 80。

延伸題：

```text
第 1 頁： 40 本
第 2 頁： 40 本
第 3 頁： 20 本
共 100 本
```

第 3 頁只有 20 本：暢銷總榜是「前 100 名」，不是每頁都剛好 40 本。所以程式**不要寫死** `3 × 40 = 120`，要用實際抓到的數字。

---

## 要遵守的事

- 只抓排行榜頁；`robots.txt` 禁止的路徑（例如 `/member/`、`/shopping/`、`/promote/vip`）不要碰。
- 每次請求之間至少等 1 秒（`time.sleep(1)`）。
- User-Agent 寫上你的名字，讓網站知道是誰在抓。
- 密碼放在環境變數，不要寫進程式、不要 commit。
