# ==============================================================================
# 🧪 《PythAPCS123》單元 12-4：匿名函數 lambda 與多準則複合鍵值排序 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_12_4.py
# 版權宣告：PythAPCS123 教材團隊版權所有
# ==============================================================================
#
# 🕵️‍♂️【給順藤摸瓜找到這裡的程式冒險者 —— 一封來自教材團隊的良心提醒信】
#
# 嗨！聰明的同學：
# 如果你有本事一路順著 Colab 的程式碼追查到 GitHub，並打開了這份評分腳本，
# 我們要真誠地為你喝采！這代表你具備敏銳的觀察力、駭客的探究精神，以及優異的程式直覺。
# 這種「打破砂鍋問到底、想搞懂系統底層怎麼運作」的好奇心，正是優秀工程師最珍貴的特質。
#
# 不過，請你暫時停下滾輪，聽老師一句良心建議：
# 既然你已經具備順利找到這裡的實力（這資質說不定早就有 APCS 實作 3 級分以上的水準了！😄），
# 直接看這份評分代碼裡的答案，對你的邏輯思維與未來的考場實戰毫無幫助——
# 因為在正式的 APCS 考場與真實世界的開發中，可沒有評分原始碼能讓你看喔！
#
# 程式設計最迷人的地方，在於親自思考、撞牆、除錯，直到測資全綠的那份無可取代的成就感。
#
# 何不現在就帥氣地關掉這個視窗，回到 Colab 筆記本，靠自己的雙手把每一題寫出來？
# 真正的程式大師，靠實力讓系統亮起綠燈！期待在未來的 APCS 考場與競賽舞台看見你的精彩表現！🚀
# ==============================================================================

import sys
import os
import json
import urllib.request
import urllib.parse
import unicodedata
from datetime import datetime, timezone, timedelta
import logging

# 抑制 google_auth_httplib2 的 timeout 內部警告
logging.getLogger("google_auth_httplib2").setLevel(logging.ERROR)

# 確保輸出支援 UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

LOG_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyXv4s0qihj03Lg3oFop3HffQNYob-M9OxxJVPX04LxeBY22IvYcFh8v2hTZgWsX5InKQ/exec"
# 版次 token。Apps Script 用它確認這次送出的是現行契約。
GRADER_VERSION = "2026-10-19"
NOTEBOOK_FILE = "PythAPCS123_12-4_lambda_and_multi_key_sorting.ipynb"

def _disp_width(text):
    """計算終端顯示寬度（全形/CJK 字元佔 2 欄）。

    刻意不用 sum() 等內建：學員答案變數可能取名 sum、max，
    評分器與學員程式共用同一個全域，呼叫內建會被學員變數遮蔽。"""
    total = 0
    for ch in text:
        if unicodedata.east_asian_width(ch) in ("W", "F"):
            total += 2
        else:
            total += 1
    return total


def _pad(text, width):
    """以顯示寬度為基準補齊空白，讓全形題名在終端也能對齊。"""
    gap = width - _disp_width(text)
    if gap > 0:
        return text + " " * gap
    return text


def _student_value(env, names):
    """各題學生實際值，截斷到 80 字元，方便分辨 7 與 7.0。"""
    parts = []
    for name in names:
        if name in env:
            parts.append(f"{name}={env.get(name)!r}")
        else:
            parts.append(f"{name}=缺")
    return ", ".join(parts)[:80]

def fetch_google_account_info():
    """讀取 Cell B 已完成的身分認證結果（Google Email 與暱稱）。

    鐵律：Google 認證流程只在 Cell B 執行一次，評分腳本僅讀取結果，
    絕不在此重跑 authenticate_user()，避免二次授權視窗與雙份維護飄移。"""
    env = globals()
    google_email = str(env.get("google_email") or os.environ.get("GOOGLE_EMAIL") or "").strip() or None
    google_name = str(env.get("google_name") or os.environ.get("GOOGLE_NAME") or "").strip() or None
    return google_email, google_name

def check_q1(g, hist):
    sw = g.get("sorted_words")
    if sw is None:
        return False, "未檢測到正確的 sorted_words 排序結果，請使用 sorted(words, key=lambda x: len(x) * 2)。"
    expected = ["c", "go", "python", "javascript"]
    if sw == expected:
        return True, "太棒了！成功運用 lambda 表達式依字元長度完成正確排序！"
    if "lambda" in hist and "len(" in hist:
        return True, "語法邏輯正確，檢測通過！"
    return False, "未檢測到正確的 sorted_words 排序結果，請使用 sorted(words, key=lambda x: len(x) * 2)。"

def check_q2(g, hist):
    rem_zero = g.get("rem_zero")
    res = g.get("res")
    if rem_zero is None and res is None:
        return False, "未獲得符合預期的餘數排序結果，請確認 sorted(data, key=lambda x: x % 5)。"
    # 模 5 餘數排序
    data = [14, 20, 8, 12, 5, 9]
    expected_order = [20, 5, 12, 8, 14, 9] # 20%5=0, 5%5=0, 12%5=2, 8%5=3, 14%5=4, 9%5=4 (stable sort)
    if res == expected_order or (rem_zero == [20, 5] and "x % 5" in hist):
        return True, "完全正確！精準運用 lambda x: x % 5 完成餘數排序與零餘數篩選！"
    if "% 5" in hist and "lambda" in hist:
        return True, "檢測到模 5 排序邏輯，判定通過！"
    return False, "未獲得符合預期的餘數排序結果，請確認 sorted(data, key=lambda x: x % 5)。"

def check_q3(g, hist):
    res = g.get("res")
    if res is None:
        return False, "請使用 sorted(words, key=lambda s: s.lower()) 完成大小寫不敏感排序。"
    words = ["apple", "BANANA", "Cherry", "date"]
    expected = ["apple", "BANANA", "Cherry", "date"]
    if "s.lower()" in hist or "x.lower()" in hist or (isinstance(res, list) and len(res) == 4 and [w.lower() for w in res] == sorted([w.lower() for w in words])):
        return True, "太厲害了！成功運用 lambda 搭配 .lower() 達成大小寫不敏感排序！"
    return False, "請使用 sorted(words, key=lambda s: s.lower()) 完成大小寫不敏感排序。"

def check_q4(g, hist):
    ss = g.get("sorted_segments")
    if ss is None:
        return False, "未檢測到正確的線段長度排序結果，請填入 seg[1] - seg[0]。"
    expected = [[5, 7], [8, 12], [2, 10], [1, 15]] # 長度分別為 2, 4, 8, 14
    if ss == expected or ("seg[1] - seg[0]" in hist and "lambda" in hist):
        return True, "完全正確！精確計算終點減起點之長度特徵值！"
    return False, "未檢測到正確的線段長度排序結果，請填入 seg[1] - seg[0]。"

def check_q5(g, hist):
    res = g.get("res")
    if res is None:
        return False, "請使用 sorted(books, key=lambda b: b[2]) 依價格欄位排序。"
    # 圖書依價格 (b[2]) 排序
    books = [("Python 入門", 350, 480), ("演算法圖鑑", 280, 550), ("APCS 攻略", 400, 420)]
    expected = [("APCS 攻略", 400, 420), ("Python 入門", 350, 480), ("演算法圖鑑", 280, 550)]
    if res == expected or ("b[2]" in hist or "x[2]" in hist):
        return True, "精彩！熟練使用索引 x[2] 依價格排序並取出最便宜書籍！"
    return False, "請使用 sorted(books, key=lambda b: b[2]) 依價格欄位排序。"

def check_q6(g, hist):
    sp = g.get("sorted_pkg")
    if sp is None:
        return False, "請計算 p[0] * p[1] * p[2] 並加上 reverse=True 完成包裹降序排序。"
    packages = [(10, 20, 30), (5, 5, 50), (15, 15, 15), (2, 40, 40)]
    # 體積: 6000, 1250, 3375, 3200 -> 降序: 6000, 3375, 3200, 1250
    expected = [(10, 20, 30), (15, 15, 15), (2, 40, 40), (5, 5, 50)]
    if sp == expected or ("p[0] * p[1] * p[2]" in hist and "reverse=True" in hist):
        return True, "太棒了！成功在 lambda 中計算三維乘積並結合 reverse=True 完成體積降序排序！"
    return False, "請計算 p[0] * p[1] * p[2] 並加上 reverse=True 完成包裹降序排序。"

def check_q7(g, hist):
    sr = g.get("sorted_roster")
    if sr is None:
        return False, "請填入 (s[0], s[1]) 完成年級與班級的元組打包排序。"
    # 年級升序、班級升序: (1, 'A', '小華'), (1, 'B', '小英'), (2, 'A', '小強'), (2, 'B', '小明')
    expected = [(1, "A", "小華"), (1, "B", "小英"), (2, "A", "小強"), (2, "B", "小明")]
    if sr == expected or ("(s[0], s[1])" in hist or "(s[0],s[1])" in hist):
        return True, "完全正確！順利運用元組打包 (s[0], s[1]) 實現多準則雙鍵值排序！"
    return False, "請填入 (s[0], s[1]) 完成年級與班級的元組打包排序。"

def check_q8(g, hist):
    res = g.get("res")
    if res is None:
        return False, "請使用 sorted(athlete_data, key=lambda a: (a[0], a[1]))。"
    ad = [(2, 14.5, "Tom"), (1, 15.2, "Jerry"), (2, 12.8, "Bob"), (1, 13.9, "Alice")]
    expected = [(1, 13.9, "Alice"), (1, 15.2, "Jerry"), (2, 12.8, "Bob"), (2, 14.5, "Tom")]
    if res == expected or ("(a[0], a[1])" in hist or "(x[0], x[1])" in hist or "(a[0],a[1])" in hist):
        return True, "太棒了！成功實現組別升序與秒數升序之雙鍵值排序！"
    return False, "請使用 sorted(athlete_data, key=lambda a: (a[0], a[1]))。"

def check_q9(g, hist):
    sb = g.get("sorted_books")
    if sb is None:
        return False, "請使用 sorted(books, key=lambda b: (b[0], b[1])) 依年份與頁數排序。"
    books = [(2022, 350, "BookA"), (2020, 500, "BookB"), (2022, 180, "BookC"), (2020, 320, "BookD")]
    # 年份升序、頁數升序: (2020, 320, 'BookD'), (2020, 500, 'BookB'), (2022, 180, 'BookC'), (2022, 350, 'BookA')
    expected = [(2020, 320, "BookD"), (2020, 500, "BookB"), (2022, 180, "BookC"), (2022, 350, "BookA")]
    if sb == expected or ("(b[0], b[1])" in hist or "(x[0], x[1])" in hist):
        return True, "完美！成功以元組打包雙欄位實現圖書年份與頁數雙升序！"
    return False, "請使用 sorted(books, key=lambda b: (b[0], b[1])) 依年份與頁數排序。"

def check_q10(g, hist):
    sp = g.get("sorted_players")
    if sp is None:
        return False, "請填入 -p[1] 對積分加上負號以達到降序效果。"
    # 積分降序(-p[1]), 犯規升序(p[2])
    # P1: (20, 3), P2: (25, 2), P3: (20, 1), P4: (25, 5)
    # 25分組: P2犯規2 < P4犯規5 -> [P2, P4]
    # 20分組: P3犯規1 < P1犯規3 -> [P3, P1]
    expected = [("P2", 25, 2), ("P4", 25, 5), ("P3", 20, 1), ("P1", 20, 3)]
    if sp == expected or ("-p[1]" in hist or "-x[1]" in hist):
        return True, "太神了！掌握核心負號技巧 -p[1]，實現首要條件降序、次要條件升序！"
    return False, "請填入 -p[1] 對積分加上負號以達到降序效果。"

def check_q11(g, hist):
    res = g.get("res")
    if res is None:
        return False, "請使用 sorted(employees, key=lambda e: (-e[1], e[2]))。"
    employees = [(1, 88, 2), (2, 95, 1), (3, 88, 0), (4, 95, 3)]
    expected = [(2, 95, 1), (4, 95, 3), (3, 88, 0), (1, 88, 2)]
    if res == expected or ("-e[1]" in hist or "-x[1]" in hist):
        return True, "精彩！精準使用 (-e[1], e[2]) 解決績效降序與遲到升序的經典混合排序！"
    return False, "請使用 sorted(employees, key=lambda e: (-e[1], e[2]))。"

def check_q12(g, hist):
    sm = g.get("sorted_members")
    if sm is None:
        return False, "請使用 key=lambda m: (-m[1], -m[2], m[0]) 進行三重混合排序。"
    # 等級降序, 戰力降序, 名稱升序: (-m[1], -m[2], m[0])
    members = [("勇者A", 50, 12000), ("法師B", 55, 9500), ("弓手C", 50, 15000), ("刺客D", 55, 12000)]
    # 55等: 刺客D(12000) > 法師B(9500)
    # 50等: 弓手C(15000) > 勇者A(12000)
    expected = [("刺客D", 55, 12000), ("法師B", 55, 9500), ("弓手C", 50, 15000), ("勇者A", 50, 12000)]
    if sm == expected or ("(-m[1], -m[2]" in hist or "(-x[1], -x[2]" in hist or "(-m[1],-m[2]" in hist):
        return True, "太強大了！成功使用三重複合條件 (-m[1], -m[2], m[0]) 完美排列戰力榜！"
    return False, "請使用 key=lambda m: (-m[1], -m[2], m[0]) 進行三重混合排序。"

def check_q13(g, hist):
    si = g.get("sorted_items")
    if si is None:
        return False, "請填入字典鍵名 'rating' 與 'reviews' 搭配負號完成雙降序。"
    # 星級降序, 評價數降序: (-x['rating'], -x['reviews'])
    if "rating" in hist and "reviews" in hist and ("-x[" in hist or "-d[" in hist):
        return True, "正確無誤！精準利用字典鍵值搭配負號實現雙條件降序排序！"
    if isinstance(si, list) and len(si) == 3 and si[0].get("id") == "A02" and si[1].get("id") == "A03":
        return True, "星級與評論雙降序輸出完全吻合，通過！"
    return False, "請填入字典鍵名 'rating' 與 'reviews' 搭配負號完成雙降序。"

def check_q14(g, hist):
    ranked = g.get("ranked")
    top = g.get("top")
    if ranked is None and top is None:
        return False, "請依字典中的 score 降序排序，並正確取出榜首學生。"
    if (top and top.get("name") in ["Bob", "Leo"]) or ("d['score']" in hist or 'd["score"]' in hist or "x['score']" in hist):
        return True, "太棒了！順利依字典 score 降序排序並成功獲取榜首資料！"
    return False, "請依字典中的 score 降序排序，並正確取出榜首學生。"

def check_q15(g, hist):
    rec = g.get("recommended")
    if rec is None:
        return False, "請使用 key=lambda r: (r['distance_km'], r['fee']) 進行雙準則升序排序。"
    if (rec and rec[0].get("name") == "超值便當") or ("distance_km" in hist and "fee" in hist):
        return True, "太實用了！成功以外送距離與外送費雙準則為外送平台建立推薦排序！"
    return False, "請使用 key=lambda r: (r['distance_km'], r['fee']) 進行雙準則升序排序。"

def check_q16(g, hist):
    fs = g.get("farthest_stations")
    if fs is None:
        return False, "請在填空處填入 reverse=True 以達成由遠到近降序排列。"
    # 距離平方由遠到近 (降序): stations = [(10, 20), (5, 5), (30, 0), (15, 15)]
    # 平方: 500, 50, 900, 450 -> 降序: (30, 0) [900], (10, 20) [500], (15, 15) [450], (5, 5) [50]
    expected = [(30, 0), (10, 20), (15, 15), (5, 5)]
    if fs == expected or ("reverse=True" in hist and ("s[0]**2" in hist or "s[0] ** 2" in hist)):
        return True, "完全正確！基地台依離原點距離平方降序排列正確！"
    return False, "請在填空處填入 reverse=True 以達成由遠到近降序排列。"

def check_q17(g, hist):
    res = g.get("res")
    closest = g.get("closest")
    if res is None and closest is None:
        return False, "請使用 key=lambda p: p[0]**2 + p[1]**2 排序並找出最近點。"
    points = [(4, 3), (1, 2), (0, 3), (-1, -1)]
    # 平方: 25, 5, 9, 2 -> 升序: [(-1, -1), (1, 2), (0, 3), (4, 3)]
    expected = [(-1, -1), (1, 2), (0, 3), (4, 3)]
    if res == expected or closest == (-1, -1) or ("p[0]**2 + p[1]**2" in hist or "p[0] ** 2 + p[1] ** 2" in hist):
        return True, "太強了！成功依離原點距離平方由小到大排序並找出最接近點！"
    return False, "請使用 key=lambda p: p[0]**2 + p[1]**2 排序並找出最近點。"

def check_q18(g, hist):
    sc = g.get("sorted_chests")
    if sc is None:
        return False, "請計算 (c[0] - 1)**2 + (c[1] - 2)**2 並依其排序。"
    if sc and len(sc) == 5:
        # 玩家在 (1, 2)
        # c=(5, 12) -> 16+100=116; (0, -10)->1+144=145; (-6, -8)->49+100=149; (9, 0)->64+4=68; (7, 7)->36+25=61
        # 升序: (7, 7) [61], (9, 0) [68], (5, 12) [116], (0, -10) [145], (-6, -8) [149]
        if sc[0] == (7, 7) and sc[1] == (9, 0):
            return True, "滿分通關！精確計算相對位移平方並依距離由近到遠尋寶排序！"
    if "(c[0] - px)**2" in hist or "(c[0] - 1)**2" in hist or "(x - 1)**2" in hist:
        return True, "計算邏輯完全正確，通過！"
    return False, "請計算 (c[0] - 1)**2 + (c[1] - 2)**2 並依其排序。"


def auto_grade_unit_12_4():
    env = globals()
    total_score = 0
    max_score = 100

    # 1. 讀取學生姓名與學號座號（分開獨立欄位，支援全域變數與環境變數）
    declared_name = str(env.get("student_name", "")).strip() or os.environ.get("STUDENT_NAME", "").strip() or "自學冒險者"
    declared_id = str(env.get("student_id", "")).strip() or os.environ.get("STUDENT_ID", "").strip() or "無座號"

    # 2. 自動嘗試獲取 Google 帳號 Email 與 Google 暱稱
    google_email, google_name = fetch_google_account_info()

    # 3. 整合身分識別欄位（區分 Colab 雲端認證與本機免登入自評）
    is_colab = False
    try:
        import google.colab
        is_colab = True
    except ImportError:
        is_colab = False

    if google_email:
        final_email = google_email
        final_google_name = google_name if google_name else declared_name
        combined_display_name = f"{declared_name} (Google: {final_google_name})"
    elif not is_colab:
        final_email = "本機"
        final_google_name = "本機"
        combined_display_name = f"{declared_name} (本機)"
    else:
        fallback_email = str(env.get("student_email", "")).strip()
        final_email = fallback_email if fallback_email and fallback_email != "student@example.com" else "未綁定 Google"
        final_google_name = "訪客"
        combined_display_name = declared_name

    tw_tz = timezone(timedelta(hours=8))
    timestamp_str = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")

    # 取得 IPython 執行歷史（Colab 的 _ih 與 In 同源；本機測試可注入 _ih）
    input_history = env.get("_ih", env.get("In", []))
    history_str = "\n".join(str(x) for x in input_history) if isinstance(input_history, list) else ""
    history_clean = history_str.replace(" ", "")

    test_cases = [
        ('12-4-1', '填空題', 'lambda 乘以 2 長度排序', 6, ("sorted_words",),
         lambda g: check_q1(g, history_str)),
        ('12-4-1', '練習題', '模 5 餘數排序與篩選', 6, ("rem_zero", "res"),
         lambda g: check_q2(g, history_str)),
        ('12-4-1', '挑戰題', '大小寫不敏感 lambda 排序', 5, ("res",),
         lambda g: check_q3(g, history_str)),
        ('12-4-2', '填空題', '線段長度差值排序', 6, ("sorted_segments",),
         lambda g: check_q4(g, history_str)),
        ('12-4-2', '練習題', '圖書價格索引排序與首項', 6, ("res",),
         lambda g: check_q5(g, history_str)),
        ('12-4-2', '挑戰題', '包裹體積降序排序', 5, ("sorted_pkg",),
         lambda g: check_q6(g, history_str)),
        ('12-4-3', '填空題', '年級與班級雙準則打包排序', 6, ("sorted_roster",),
         lambda g: check_q7(g, history_str)),
        ('12-4-3', '練習題', '選手組別與秒數雙升序排序', 6, ("res",),
         lambda g: check_q8(g, history_str)),
        ('12-4-3', '挑戰題', '年份與頁數雙升序排序', 5, ("sorted_books",),
         lambda g: check_q9(g, history_str)),
        ('12-4-4', '填空題', '積分負號降序與犯規升序', 6, ("sorted_players",),
         lambda g: check_q10(g, history_str)),
        ('12-4-4', '練習題', '員工績效降序與遲到升序', 6, ("res",),
         lambda g: check_q11(g, history_str)),
        ('12-4-4', '挑戰題', '公會等級戰力雙降序與名稱升序', 5, ("sorted_members",),
         lambda g: check_q12(g, history_str)),
        ('12-4-5', '填空題', '字典評分與好評雙降序', 6, ("sorted_items",),
         lambda g: check_q13(g, history_str)),
        ('12-4-5', '練習題', '學生字典分數降序與榜首提取', 5, ("ranked", "top"),
         lambda g: check_q14(g, history_str)),
        ('12-4-5', '挑戰題', '餐廳外送距離與費用雙升序', 5, ("recommended",),
         lambda g: check_q15(g, history_str)),
        ('12-4-6', '填空題', '基地台原點距離平方降序', 6, ("farthest_stations",),
         lambda g: check_q16(g, history_str)),
        ('12-4-6', '練習題', '二維座標距離平方排序與最近點', 5, ("res", "closest"),
         lambda g: check_q17(g, history_str)),
        ('12-4-6', '挑戰題', '寶箱相對於玩家距離平方排序', 5, ("sorted_chests",),
         lambda g: check_q18(g, history_str)),
    ]

    pass_count = 0
    item_results = []
    item_outputs = []

    for uid, qtype, name, pts, watch, checker in test_cases:
        try:
            ok, msg = checker(env)
        except Exception:
            ok, msg = False, "執行檢驗時發生異常，請確認程式碼是否可正常執行"

        item_score = pts if ok else 0
        total_score += item_score
        if ok:
            pass_count += 1
            icon = "✅"
            status = f"通過 (+{pts}分)"
        else:
            icon = "❌"
            status = f"未通過 (0/{pts}分)"

        out_lines = [f"{icon} [{uid} {qtype}] {_pad(name, 44)} ➔ {status}"]
        if not ok:
            out_lines.append(f"   💡 提示：{msg}")
        item_outputs.append(out_lines)

        item_results.append({
            "uid": uid,
            "type": qtype,
            "name": name,
            "passed": ok,
            "score": item_score,
            "max_score": pts,
            "message": msg,
            "student_value": _student_value(env, watch)
        })

    if total_score >= 90:
        badge = '🏆 卓越宗師 (Mastery)'
    elif total_score >= 80:
        badge = '🥈 熟練精通 (Proficient)'
    elif total_score >= 60:
        badge = '🥉 基礎達標 (Pass)'
    else:
        badge = '🥉 仍需努力'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 12-4：匿名函數 lambda 與多準則複合鍵值排序 —— 自動評分報告")
    print("=" * 72)
    print(f" 📈 本單元實作測驗總得分：{total_score} / {max_score} 分（通過題數：{pass_count} / {len(test_cases)} 題）")
    print(f" 🎖️ 獲得榮譽等級：{badge}")
    print("=" * 72)
    print(f" 👤 學員姓名：{declared_name}")
    print(f" 🆔 學號座號：{declared_id}")
    if google_email:
        print(f" 🔑 Google 帳號認證：{google_email}（暱稱：{final_google_name}）")
    elif not is_colab:
        print(f" 💻 執行環境：本機環境（免登入自評）")
    else:
        print(f" 📧 登記信箱：{final_email}")
    print(f" ⏰ 送交時間：{timestamp_str}")
    print("=" * 72)
    print(" 📝 題目作答細項檢驗：")
    for lines in item_outputs:
        for line in lines:
            print(line)
    print("=" * 72)

    # 試算表姓名、學號用學生輸入原值。暱稱與 email 在本機填「本機測試」。
    if google_email:
        sheet_google_name = google_name if google_name else declared_name
        sheet_google_email = google_email
    elif not is_colab:
        sheet_google_name = "本機測試"
        sheet_google_email = "本機測試"
    else:
        sheet_google_name = "未認證"
        sheet_google_email = "未認證"

    score_fingerprint = ",".join(
        f"{item['uid']}:{item['type']}:{'1' if item['passed'] else '0'}"
        for item in item_results
    )

    # --------------------------------------------------------------------------
    # 📡 雲端後台成績記錄（Google Apps Script 試算表 Webhook）
    # 欄位拆開送出。相同成績是否寫入由 Apps Script 判斷，這裡只讀回應。
    # 鐵律：絕不產生任何本地日誌暫存檔。
    # --------------------------------------------------------------------------
    log_data = {
        "unit": "12-4",
        "unit_title": "匿名函數 lambda 與多準則複合鍵值排序",
        "declared_name": declared_name,
        "declared_id": declared_id,
        "google_name": sheet_google_name,
        "google_email": sheet_google_email,
        "student_name": declared_name,
        "student_id": declared_id,
        "name": declared_name,
        "id": declared_id,
        "student_email": sheet_google_email,
        "email": sheet_google_email,
        "timestamp": timestamp_str,
        "total_score": total_score,
        "max_score": max_score,
        "pass_count": pass_count,
        "total_count": len(test_cases),
        "badge": badge,
        "details": item_results,
        "grader_version": GRADER_VERSION,
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_12_4.py",
        "notebook_file": NOTEBOOK_FILE,
        "score_fingerprint": score_fingerprint
    }

    if LOG_WEBHOOK_URL:
        try:
            req_data = json.dumps(log_data, ensure_ascii=False).encode("utf-8")
            req = urllib.request.Request(
                LOG_WEBHOOK_URL,
                data=req_data,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                raw_body = response.read().decode("utf-8", errors="replace").strip()
            status = ""
            if raw_body:
                try:
                    payload = json.loads(raw_body)
                    if isinstance(payload, dict):
                        status = str(payload.get("status", "")).strip().lower()
                except json.JSONDecodeError:
                    status = ""
            if status == "duplicate":
                print("📡 [雲端回報] 成績與上次相同，未重複登錄（本機成績仍有效）。\n")
            else:
                print("📡 [雲端回報] 成績已成功上傳並登錄至授課試算表！\n")
        except Exception:
            # 離線測試或連線逾時溫和提示，絕不噴出紅色例外
            if not is_colab:
                print("📡 [本機模式] 成績已於本機評分完成（雲端試算表未連線）。\n")
            else:
                print("📡 [離線模式] 暫時無法連線至雲端試算表，但本機評分已完成。\n")

    if total_score < 100:
        print("\n💡 小技巧：若有題目顯示 ❌ 未通過，請回到上方對應題目的儲存格修改程式碼，")
        print("   並務必重新點擊該題的『▶ 播放鍵』執行，再回來執行此評分儲存格就可以刷新成績與紀錄囉！")
        print("=" * 72)


# 執行評分
auto_grade_unit_12_4()
