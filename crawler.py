# 三民書局暢銷總榜 → MariaDB
# 題目和提示見 README.md
# 執行前先設定帳密：
#   export DB_USER=crawler DB_PASS='crawler-db-2026' DB_NAME=crawler_course
# 執行：python crawler.py

import datetime
import os
import time
from urllib.robotparser import RobotFileParser

import mariadb
import requests
from bs4 import BeautifulSoup

URL = "https://www.sanmin.com.tw/promote/top"
HEADERS = {"User-Agent": "course-crawler/1.0 (你的名字)"}

# 1. 先看 robots.txt 允不允許（提示 2）
#    把結果（True 或 False）存在 allowed
allowed = False

books = []
if allowed:
    time.sleep(1)

    # 2. 抓排行榜頁面
    r = requests.get(URL, headers=HEADERS, timeout=10)
    print("狀態碼：", r.status_code)

    # 3. 用 BeautifulSoup 找出每一本書（提示 3、4）
    soup = BeautifulSoup(r.text, "html.parser")
    rank = 0
    # 在這裡寫 for 迴圈：每一本書做成 [rank, title, author, publisher, link]，用 books.append(...) 加進 books

print("抓到", len(books), "本")

if len(books) > 0:
    # 4. 存進 MariaDB，同一天跑兩次不能重複（提示 5）

    # 5. 從資料庫查回來，印出共幾本、前 10 名（提示 6）
    print("（第 4、5 步還沒寫）")
else:
    print("一本都沒抓到，不寫資料庫")
