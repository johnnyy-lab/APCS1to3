# ==============================================================================
# 🧪 《PythAPCS123》單元 12-2：降序排序、字串字典序與數值轉型陷阱 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_12_2.py
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
NOTEBOOK_FILE = "PythAPCS123_12-2_reverse_sort_and_lexicographical_order.ipynb"

def _disp_width(text):
    """計算終端顯示寬度（全形/CJK 字元佔 2 欄）。

    刻意不用 sum() 等內建：學員答案變數可能取名 sum、max。
    直接執行腳本時答案與評分器在同一個全域，呼叫內建會被遮蔽。"""
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

def _student_env(env=None):
    """學員變數所在的命名空間。

    Cell B 隔離載入時讀 __STUDENT_ENV__。直接執行腳本，或測試把答案
    放在同一個全域時，改讀 globals()。"""
    if isinstance(env, dict):
        return env
    snapshot = globals().get("__STUDENT_ENV__")
    if isinstance(snapshot, dict):
        return snapshot
    return globals()


def fetch_google_account_info(env=None):
    """讀取 Cell B 已完成的身分認證結果（Google Email 與暱稱）。

    鐵律：Google 認證流程只在 Cell B 執行一次，評分腳本僅讀取結果，
    絕不在此重跑 authenticate_user()，避免二次授權視窗與雙份維護飄移。"""
    env = _student_env(env)
    google_email = str(env.get("google_email") or os.environ.get("GOOGLE_EMAIL") or "").strip() or None
    google_name = str(env.get("google_name") or os.environ.get("GOOGLE_NAME") or "").strip() or None
    return google_email, google_name

def get_submission_env():
    """取得學員全域與執行歷史。Cell B 隔離載入時優先讀 __STUDENT_ENV__。"""
    snapshot = globals().get("__STUDENT_ENV__")
    if isinstance(snapshot, dict):
        history_cells = snapshot.get("_ih", snapshot.get("In", []))
        if not isinstance(history_cells, list):
            history_cells = []
        return snapshot, history_cells
    try:
        import IPython
        ipython_inst = IPython.get_ipython()
        if ipython_inst is not None:
            user_ns = ipython_inst.user_ns
            history_cells = getattr(ipython_inst, 'user_ns', {}).get('_ih', [])
            return user_ns, history_cells
    except Exception:
        pass
    
    # 備用機制：若不在 IPython 環境，從呼叫棧主模組獲取
    try:
        import __main__
        return __main__.__dict__, []
    except Exception:
        return {}, []


def auto_grade_unit_12_2(env=None):
    env = _student_env(env)
    total_score = 0
    max_score = 100

    # 1. 讀取學生姓名與學號座號（分開獨立欄位，支援全域變數與環境變數）
    declared_name = str(env.get("student_name", "")).strip() or os.environ.get("STUDENT_NAME", "").strip() or "自學冒險者"
    declared_id = str(env.get("student_id", "")).strip() or os.environ.get("STUDENT_ID", "").strip() or "無座號"

    # 2. 自動嘗試獲取 Google 帳號 Email 與 Google 暱稱
    google_email, google_name = fetch_google_account_info(env)

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

    env, history = get_submission_env()
    history_str = "\n".join(history)
    history_clean = history_str.replace(" ", "").replace("\t", "")

    test_cases = [
        # ----------------------------------------------------------------------
        # 12-2-1 參數 reverse=True：從大到小反向降序排列 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("12-2-1", "填空題", "sorted(..., reverse=True) 降序排序與最高出價取值", 5, ("ranked_bids",),
         lambda g: (
             (True, "ranked_bids 降序排序正確，且最高出價取值無誤！")
             if (g.get("ranked_bids") == [950, 620, 480, 230, 150]) or
                ("sorted(bids,reverse=True)" in history_clean or "sorted(bids, reverse=True)" in history_str)
             else (False, "尚未找到符合預期的 ranked_bids，請在 sorted() 中指定 reverse=True 降序排列！")
         )),

        ("12-2-1", "練習題", "scores.sort(reverse=True) 原地降序與前三名得分總和", 6, ("scores",),
         lambda g: (
             (True, "練習題 12.2.1 scores 原地降序排序與前三名總和計算正確！")
             if (g.get("scores") == [35, 28, 24, 18, 12]) or
                ("scores.sort(reverse=True)" in history_str and ("87" in history_str or "scores[:3]" in history_str))
             else (False, "請使用 scores.sort(reverse=True) 進行原地由大到小排序，並計算前三名總和！")
         )),

        ("12-2-1", "挑戰題", "貪婪硬幣面額由大到小排序與前兩大金額合計", 6, ("sorted_coins", "first_two_sum"),
         lambda g: (
             (True, "挑戰題 12.2.1 硬幣面額降序排序與前二大面額合計正確！")
             if (g.get("sorted_coins") == [50, 20, 10, 5, 1] or g.get("first_two_sum") == 70) or
                ("reverse=True" in history_str and ("coins" in history_str or "70" in history_str))
             else (False, "請將硬幣面額 coins 由大到小排序，並取出前兩大面額合計（50 + 20 = 70）！")
         )),

        # ----------------------------------------------------------------------
        # 12-2-2 數值排序 vs 字串字典序（Lexicographical Order） (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("12-2-2", "填空題", "單字清單字典序排序 alpha_order 與首位語言", 5, ("alpha_order",),
         lambda g: (
             (True, "alpha_order 字母字典序排序正確！首位語言為 'basic'！")
             if (g.get("alpha_order") == ['basic', 'c', 'java', 'pascal', 'python']) or
                ("sorted(languages)" in history_str and "alpha_order" in history_str)
             else (False, "請使用 alpha_order = sorted(languages) 依字母字典序排列程式語言名稱！")
         )),

        ("12-2-2", "練習題", "raw_words 字典序排序與末位單字首字元及長度", 6, ("sorted_animals",),
         lambda g: (
             (True, "練習題 12.2.2 單字字典序排序與末位單字特徵擷取正確！")
             if (g.get("sorted_animals") == ['ant', 'bear', 'dog', 'monkey', 'zebra']) or
                ("sorted(raw_words)" in history_str and ("len(" in history_str or "zebra" in history_str))
             else (False, "請將 raw_words 進行字典序升序排序，並輸出排序結果與最後一個單字的首字與長度！")
         )),

        ("12-2-2", "挑戰題", "逐字元 ASCII 比對驗證器找出勝負索引", 6, ("diff_found",),
         lambda g: (
             (True, "挑戰題 12.2.2 逐字元比對驗證器實作正確！成功定位相異字元索引！")
             if ("wordA" in history_str and "wordB" in history_str and ("range(" in history_str or "!=" in history_str)) or
                (g.get("diff_found") is not None)
             else (False, "請撰寫迴圈逐字比對 wordA 與 wordB，找出首個相異字元之索引位置！")
         )),

        # ----------------------------------------------------------------------
        # 12-2-3 考場世紀大陷阱：字串 '100' 小於 '2' 的成因與數值轉型 int 必要性 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("12-2-3", "填空題", "文字數字轉型 clean_numbers = [int(x) for x in ...] 防禦", 5, ("clean_numbers",),
         lambda g: (
             (False, "⚠️ 偵測到 clean_numbers 仍包含文字型態！踩到了文字數字字典序陷阱（'120' < '3'）！請使用 int(x) 進行轉型！")
             if (isinstance(g.get("clean_numbers"), list) and any(isinstance(x, str) for x in g.get("clean_numbers", [])))
             else (
                 (True, "clean_numbers 數值轉型防禦正確！數值由小到大排列無誤！")
                 if (g.get("clean_numbers") == [3, 9, 45, 88, 120]) or
                    ("int(x)" in history_str and "clean_numbers" in history_str)
                 else (False, "請使用列表生成式 [int(x) for x in raw_input_data] 將文字數字轉為整數後排序！")
             )
         )),

        ("12-2-3", "練習題", "token_list 字串轉型整數後進行由大到小降序排列", 6, ("nums",),
         lambda g: (
             (False, "⚠️ 偵測到排序結果仍為字串！請務必先透過 int() 轉為整數再排序！")
             if (isinstance(g.get("nums"), list) and any(isinstance(x, str) for x in g.get("nums", [])))
             else (
                 (True, "練習題 12.2.3 成功將字串數字轉為整數並完成降序排序！")
                 if (g.get("nums") == [100, 25, 12, 7, 3]) or
                    ("int(" in history_str and "reverse=True" in history_str and ("100" in history_str or "nums" in history_str))
                 else (False, "請將 token_list 內項目轉型為整數，並進行由大到小（reverse=True）降序排序！")
             )
         )),

        ("12-2-3", "挑戰題", "對比未轉型字串排序與整數排序之首位數值差距", 6, (),
         lambda g: (
             (True, "挑戰題 12.2.3 成功對比字串排序與數值排序之首位差距！")
             if ("wrong_sorted" in history_str and "right_sorted" in history_str) or
                ("105" in history_str and ("diff" in history_str or "100" in history_str or "abs(" in history_str))
             else (False, "請分別印出 records 未轉型排序與轉型整數排序結果，並計算第 0 個位置元素差距！")
         )),

        # ----------------------------------------------------------------------
        # 12-2-4 大小寫混合字串排序規則：大寫字母永遠排在小寫前面 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("12-2-4", "填空題", "標準 ASCII 排序大寫字母優先 sorted_tags = sorted(tags)", 5, ("sorted_tags",),
         lambda g: (
             (True, "sorted_tags 標準 ASCII 排序正確！大寫字母開頭者成功排在最前方！")
             if (g.get("sorted_tags") == ['AI', 'Data', 'algorithm', 'python']) or
                ("sorted(tags)" in history_str and "sorted_tags" in history_str)
             else (False, "請以 sorted(tags) 進行標準 ASCII 排序，觀察大寫字母優先排序的特性！")
         )),

        ("12-2-4", "練習題", "code_names 排序並統計大寫開頭國家名稱個數", 6, ("upper_count", "sorted_names"),
         lambda g: (
             (True, "練習題 12.2.4 國家名稱排序與大寫開頭個數統計正確！")
             if (g.get("upper_count") == 3 or g.get("sorted_names") == ['Canada', 'UK', 'USA', 'japan', 'taiwan']) or
                ("sorted(code_names)" in history_str and ("isupper()" in history_str or "<= 'Z'" in history_str))
             else (False, "請對 code_names 進行排序，並計算大寫字母開頭的國家名稱數量（'Canada', 'UK', 'USA' 共 3 個）！")
         )),

        ("12-2-4", "挑戰題", "帳號清單依大寫與小寫分層獨立排序後合併", 6, ("combined",),
         lambda g: (
             (True, "挑戰題 12.2.4 大小寫帳號分層排序並合併成功！")
             if (g.get("combined") == ['Alice', 'Charlie', 'bob', 'david', 'john']) or
                ("isupper()" in history_str and "islower()" in history_str and "sorted(" in history_str)
             else (False, "請分別挑出大寫與小寫開頭帳號並各自排序，最後合併為大寫在前、小寫在後的名冊！")
         )),

        # ----------------------------------------------------------------------
        # 12-2-5 負號取反技巧：利用 -x 進行降序快速切換 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("12-2-5", "填空題", "定義 invert_sign(t) 回傳 -t 實現氣溫降序 hot_to_cold", 5, ("hot_to_cold",),
         lambda g: (
             (True, "invert_sign 負號取反函數與 hot_to_cold 降序排列正確！")
             if (g.get("hot_to_cold") == [31.0, 29.8, 24.5, 22.0, 18.2]) or
                ("return -t" in history_str and "key=invert_sign" in history_str)
             else (False, "請定義 invert_sign(t) 回傳 -t，並傳入 key=invert_sign 將氣溫由高到低排序！")
         )),

        ("12-2-5", "練習題", "negative_key 高度降序排序與最高次高差距", 6, ("sorted_altitudes",),
         lambda g: (
             (True, "練習題 12.2.5 negative_key 高度降序排序與最高次高差距計算正確！")
             if (g.get("sorted_altitudes") == [4200, 3500, 2100, 1200, 800]) or
                ("negative_key" in history_str and "altitudes" in history_str)
             else (False, "請定義負號函式 negative_key 並配合 sorted() 將 altitudes 降序排序，計算前兩名差距！")
         )),

        ("12-2-5", "挑戰題", "利用負號取反函數排序利潤並找出最大虧損金額", 5, ("desc_profits",),
         lambda g: (
             (True, "挑戰題 12.2.5 利潤降序排序與最大虧損金額確認正確！")
             if (g.get("desc_profits") == [4500, 2800, 1200, 0, -100, -300]) or
                ("return -x" in history_str and "profits" in history_str and "-300" in history_str)
             else (False, "請定義負號取反函數將 profits 降序排列，並印出虧損最多（數值最小者 -300）！")
         )),

        # ----------------------------------------------------------------------
        # 12-2-6 字母大小寫不敏感排序初探：初探 key=str.lower (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("12-2-6", "填空題", "key=str.lower 不加括號實現姓名大小寫不敏感排序", 5, ("sorted_names",),
         lambda g: (
             (False, "⚠️ 偵測到 key=str.lower() 帶有括號！傳入 key 的必須是函數名牌，請去掉小括號改寫為 key=str.lower！")
             if ("key=str.lower()" in history_clean or "key = str.lower()" in history_str)
             else (
                 (True, "sorted_names 成功使用 key=str.lower 實現大小寫不敏感排序！")
                 if (isinstance(g.get("sorted_names"), list) and [x.lower() for x in g.get("sorted_names", [])] == ['alice', 'alice', 'bob', 'charlie', 'dave']) or
                    ("key=str.lower" in history_clean)
                 else (False, "請使用 sorted(names, key=str.lower) 進行大小寫不敏感排序（請勿加括號）！")
             )
         )),

        ("12-2-6", "練習題", "城市名單大小寫不敏感升序排序與首個城市輸出", 6, ("sorted_cities",),
         lambda g: (
             (True, "練習題 12.2.6 城市名單大小寫不敏感排序正確！首個城市為 amsterdam！")
             if (g.get("sorted_cities") == ['amsterdam', 'Berlin', 'London', 'paris', 'tokyo']) or
                ("cities" in history_str and "str.lower" in history_str)
             else (False, "請使用 key=str.lower 對 cities 進行大小寫不敏感排序，並輸出首個城市！")
         )),

        ("12-2-6", "挑戰題", "結合 key=str.lower 與 reverse=True 實現反向降序不分大小寫排序", 5, ("desc_words",),
         lambda g: (
             (True, "挑戰題 12.2.6 成功結合 key=str.lower 與 reverse=True 實現反向不分大小寫排序！")
             if (isinstance(g.get("desc_words"), list) and [w.lower() for w in g.get("desc_words", [])] == ['zebra', 'dog', 'cat', 'bear', 'ant']) or
                ("key=str.lower" in history_str and "reverse=True" in history_str and "vocabulary" in history_str)
             else (False, "請結合 key=str.lower 與 reverse=True 兩個參數，產出由 Z 到 A 的反向不分大小寫單字表！")
         ))
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
        badge = '🏆 完美滿分！你已經徹底識破字串字典序天坑與大小寫陷阱，具備極致敏銳的考場防禦力！'
    elif total_score >= 80:
        badge = '🌟 優秀！逆序排列與數值轉型技巧掌握純熟，細心防禦即可在 APCS 考場百戰百勝！'
    elif total_score >= 60:
        badge = "👍 及格！基本字典序與 reverse 概念已建立，請特別小心文字數字 '100' < '2' 的世紀地雷！"
    else:
        badge = '💪 請再接再厲！建議回到上方各微階梯儲存格逐題點擊播放鍵執行代碼！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 12-2：降序排序、字串字典序與數值轉型陷阱 —— 自動評分報告")
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
        "unit": "12-2",
        "unit_title": "降序排序、字串字典序與數值轉型陷阱",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_12_2.py",
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
auto_grade_unit_12_2()
