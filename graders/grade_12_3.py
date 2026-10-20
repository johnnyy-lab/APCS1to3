# ==============================================================================
# 🧪 《PythAPCS123》單元 12-3：自訂排序鍵值基礎：key 參數與具名函數（Named Functions） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_12_3.py
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
NOTEBOOK_FILE = "PythAPCS123_12-3_custom_sort_key_and_named_functions.ipynb"

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


def auto_grade_unit_12_3(env=None):
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
        # 12-3-1 什麼是 key= 參數？投射轉換比喻 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("12-3-1", "填空題", "定義 word_len 回傳長度並以 key=word_len 排序口號", 5, ("sorted_slogans",),
         lambda g: (
             (True, "sorted_slogans 依長度排序正確！特徵投射模型理解深刻！")
             if (g.get("sorted_slogans") == ['Hi', 'Go!', 'Never give up', 'Keep learning python']) or
                ("key=word_len" in history_clean and "return len(s)" in history_str)
             else (False, "尚未找到符合預期的 sorted_slogans，請定義 word_len 回傳 len(s) 並傳入 key=word_len！")
         )),

        ("12-3-1", "練習題", "定義 text_length 依長度升序排列 phrases 並標註最長字串", 6, ("sorted_phrases",),
         lambda g: (
             (True, "練習題 12.3.1 phrases 依長度排序正確！最長字串標註無誤！")
             if (g.get("sorted_phrases") == ['pie', 'fig', 'apple', 'banana', 'watermelon']) or
                ("text_length" in history_str and "sorted_phrases" in history_str)
             else (False, "請定義 text_length(text) 回傳 len(text)，配合 sorted(phrases, key=text_length) 排序！")
         )),

        ("12-3-1", "挑戰題", "結合 key 函數與 reverse=True 依文章標題長度降序排列", 6, ("long_to_short",),
         lambda g: (
             (True, "挑戰題 12.3.1 文章標題依長度降序排列正確！")
             if (isinstance(g.get("long_to_short"), list) and g.get("long_to_short") and g.get("long_to_short")[0] == "AI Revolution in Modern World") or
                ("titles" in history_str and "reverse=True" in history_str and ("len" in history_str or "get_len" in history_str))
             else (False, "請定義長度特徵函數並搭配 reverse=True，將文章標題 titles 依長度由長到短排序！")
         )),

        # ----------------------------------------------------------------------
        # 12-3-2 內建函數作為鍵值：key=abs 與 key=len (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("12-3-2", "填空題", "內建 key=abs 絕對值排序與 key=len 標籤降序排序", 5, ("sorted_deviations", "sorted_tags"),
         lambda g: (
             (False, "⚠️ 偵測到 key=abs() 或 key=len() 帶有括號！內建函數作為鍵值只傳名牌，千萬不要加小括號呼叫！")
             if ("key=abs()" in history_clean or "key=len()" in history_clean)
             else (
                 (True, "sorted_deviations (key=abs) 與 sorted_tags (key=len) 填空皆完全正確！")
                 if (g.get("sorted_deviations") == [-1, 3, -4, 12, 18, -25] and g.get("sorted_tags") == ['programming', 'algorithm', 'python', 'ai', 'it']) or
                    ("key=abs" in history_clean and "key=len" in history_clean)
                 else (False, "請分別填入 key=abs 進行離原點距離排序，與 key=len, reverse=True 進行標籤降序排序！")
             )
         )),

        ("12-3-2", "練習題", "errors.sort(key=abs) 原地依絕對值排序誤差數值", 6, ("errors",),
         lambda g: (
             (True, "練習題 12.3.2 errors.sort(key=abs) 原地絕對值排序正確！")
             if (g.get("errors") == [-0.1, 0.2, 0.5, -0.8, 1.2, -1.5]) or
                ("errors.sort(key=abs)" in history_clean or "errors.sort(key = abs)" in history_str)
             else (False, "請使用 errors.sort(key=abs) 對電壓誤差數值進行原地絕對值排序，並輸出最小與最大誤差！")
         )),

        ("12-3-2", "挑戰題", "使用 key=len 找出最短與最長候選密碼並計算字數差", 6, ("min_pw", "max_pw"),
         lambda g: (
             (True, "挑戰題 12.3.2 成功使用 key=len 定位極值密碼並計算字元差距！")
             if ("passwords" in history_str and "key=len" in history_clean and ("max_pw" in history_str or "29" in history_str or "sorted_pw" in history_str)) or
                (g.get("min_pw") == "a" and g.get("max_pw") == "super_secret_master_key_2026")
             else (False, "請使用 sorted(passwords, key=len) 找出長度最短與最長的密碼，並計算字數差距！")
         )),

        # ----------------------------------------------------------------------
        # 12-3-3 自訂具名函數作為鍵值：def get_feature(x) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("12-3-3", "填空題", "count_vowels 回傳母音總次數並依母音數量排序單字", 5, ("vowel_order",),
         lambda g: (
             (True, "count_vowels 函數與 vowel_order 母音數量排序完全正確！")
             if (g.get("vowel_order") == ['sky', 'python', 'tea', 'queue', 'beautiful']) or
                ("count_vowels" in history_str and "key=count_vowels" in history_clean)
             else (False, "請在 count_vowels 函數中 return cnt，並傳入 key=count_vowels 排序單字！")
         )),

        ("12-3-3", "練習題", "定義 distance_from_50 排序離 50 距離並找出最接近數值", 6, ("sorted_near_50",),
         lambda g: (
             (True, "練習題 12.3.3 distance_from_50 距離排序與最接近數值輸出正確！")
             if (g.get("sorted_near_50") == [48, 53, 42, 65, 20, 80]) or
                ("distance_from_50" in history_str and "raw_vals" in history_str)
             else (False, "請定義 distance_from_50(x) 回傳 abs(x - 50)，對 raw_vals 進行排序！")
         )),

        ("12-3-3", "挑戰題", "定義 calc_digit_sum 依數字各位數之和升序排序", 6, ("sorted_by_digit_sum",),
         lambda g: (
             (True, "挑戰題 12.3.3 calc_digit_sum 各位數和計算與升序排序正確！")
             if (g.get("sorted_by_digit_sum") == [11, 123, 204, 45, 90]) or
                ("calc_digit_sum" in history_str and "numbers" in history_str and "sorted(" in history_str)
             else (False, "請定義 calc_digit_sum(num) 計算各位數和，將 numbers 依數位和由小到大排序！")
         )),

        # ----------------------------------------------------------------------
        # 12-3-4 元組第二欄位排序：def get_second(item): return item[1] (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("12-3-4", "填空題", "定義 get_y 回傳 pt[1] 依 Y 軸座標升序排序 points", 5, ("sorted_by_y",),
         lambda g: (
             (True, "sorted_by_y 依 Y 軸高度排序正確！第二欄位索引 item[1] 運用精準！")
             if (g.get("sorted_by_y") == [(3, 1), (2, 4), (10, 5), (8, 9)]) or
                ("pt[1]" in history_clean and "key=get_y" in history_clean)
             else (False, "請在 get_y(pt) 中回傳 pt[1]，並傳入 key=get_y 依 Y 軸排序點座標！")
         )),

        ("12-3-4", "練習題", "定義 get_seniority 依年資降序排序 records 並輸出最資深代號", 6, ("sorted_emp",),
         lambda g: (
             (True, "練習題 12.3.4 get_seniority 員工年資降序排序與資深代號輸出正確！")
             if (g.get("sorted_emp") == [('E02', 12), ('E03', 7), ('E01', 3), ('E04', 1)]) or
                ("get_seniority" in history_str and "records" in history_str and "E02" in history_str)
             else (False, "請定義 get_seniority(rec) 回傳 rec[1]，將 records 依年資由高到低降序排序！")
         )),

        ("12-3-4", "挑戰題", "定義 get_total_value 計算水果庫存總價值並降序排序", 6, ("sorted_inv",),
         lambda g: (
             (True, "挑戰題 12.3.4 水果庫存總資產計算與降序排序正確！")
             if (isinstance(g.get("sorted_inv"), list) and g.get("sorted_inv") and g.get("sorted_inv")[0][0] in ["香蕉", "櫻桃"]) or
                ("get_total_value" in history_str and "inventory" in history_str and ("price * qty" in history_str or "item[1] * item[2]" in history_clean))
             else (False, "請定義 get_total_value(item) 回傳單價乘數量，將 inventory 依總價值由大到小排序！")
         )),

        # ----------------------------------------------------------------------
        # 12-3-5 字典走訪排序：以 sorted(d.items(), key=...) 依 Value 排序 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("12-3-5", "填空題", "定義 get_price 提取 item_pair[1] 將 cart.items() 依價格排序", 5, ("sorted_items",),
         lambda g: (
             (True, "sorted_items 成功將購物車品項依價格由便宜到貴排序！")
             if (g.get("sorted_items") == [('Eraser', 20), ('Pen', 45), ('Book', 350), ('Headphones', 1200)]) or
                ("cart.items()" in history_clean and "key=get_price" in history_clean)
             else (False, "請在 get_price 中回傳 item_pair[1]，並使用 sorted(cart.items(), key=get_price)！")
         )),

        ("12-3-5", "練習題", "定義 get_frequency 依詞頻降序排序 freq.items() 並印出最高頻單字", 6, ("sorted_freq",),
         lambda g: (
             (True, "練習題 12.3.5 詞頻字典降序排行與最高頻單字輸出正確！")
             if (g.get("sorted_freq") == [('the', 42), ('is', 30), ('python', 15), ('code', 8)]) or
                ("get_frequency" in history_str and "freq.items()" in history_clean)
             else (False, "請定義 get_frequency 並以 reverse=True 對 freq.items() 降序排序！")
         )),

        ("12-3-5", "挑戰題", "線上商店 VIP 顧客前兩大消費金額合計與營業額佔比分析", 5, ("top2_sum",),
         lambda g: (
             (True, "挑戰題 12.3.5 VIP 顧客消費排序與營業額佔比計算正確！")
             if ("customers.items()" in history_clean and ("sorted_customers" in history_str or "top2_sum" in history_str or "ratio" in history_str)) or
                (g.get("top2_sum") == 13800)
             else (False, "請將 customers.items() 依消費金額由高到低排序，並計算前兩大 VIP 消費總和之全體佔比！")
         )),

        # ----------------------------------------------------------------------
        # 12-3-6 排序除錯心法：如何單獨測試 key 函數確認特徵值抽取無誤 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("12-3-6", "填空題", "修復 safe_second_char 長度不足 2 防禦並安全排序", 5, ("safe_sorted",),
         lambda g: (
             (True, "safe_second_char 防禦修復正確！邊界極端測資單獨檢驗與排序成功！")
             if (g.get("safe_sorted") == ['a', '', 'banana', 'cat', 'dog'] or (isinstance(g.get("safe_sorted"), list) and len(g.get("safe_sorted")) == 5)) or
                ("len(s) < 2" in history_str and "key=safe_second_char" in history_clean)
             else (False, "當長度不足 2 時請 return \"\" 空字串，並傳入 key=safe_second_char 進行安全排序！")
         )),

        ("12-3-6", "練習題", "定義 get_month 提取月份整數、單獨印出驗證並排序 dates", 6, ("sorted_dates",),
         lambda g: (
             (True, "練習題 12.3.6 get_month 月份提取、單獨除錯驗證與 dates 排序正確！")
             if (g.get("sorted_dates") == ['2026-01-30', '2026-03-21', '2026-08-14', '2026-11-05']) or
                ("get_month" in history_str and "dates" in history_str)
             else (False, "請實作 get_month(date_str) 取出月份整數，單獨印出驗證後將 dates 依月份排序！")
         )),

        ("12-3-6", "挑戰題", "time_to_seconds 時間轉秒數、單獨測試驗證並評選賽車冠軍", 5, ("ranked_racers",),
         lambda g: (
             (True, "挑戰題 12.3.6 賽車時間轉秒數、單獨樣本驗證與冠軍定位正確！")
             if (isinstance(g.get("ranked_racers"), list) and g.get("ranked_racers") and g.get("ranked_racers")[0][0] == "Mario") or
                ("time_to_seconds" in history_str and "racer_data" in history_str and "125" in history_str)
             else (False, "請定義 time_to_seconds 轉換總秒數，單獨驗證 ('Luigi', '2:05') 為 125 秒後排序找出冠軍！")
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
        badge = '🏆 完美滿分！你已經徹底精通自訂鍵值與特徵抽取技術，具備駕馭複雜多維資料排序的強悍實力！'
    elif total_score >= 80:
        badge = '🌟 優秀！具名函數特徵投射與字典走訪排序掌握極佳，單獨除錯意識非常出色！'
    elif total_score >= 60:
        badge = '👍 及格！基本 key 參數概念已建立，請留意元組索引對齊與 key 函數傳名牌不加括號的鐵律！'
    else:
        badge = '💪 請再接再厲！建議回到上方各微階梯儲存格逐題點擊播放鍵執行代碼！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 12-3：自訂排序鍵值基礎：key 參數與具名函數（Named Functions） —— 自動評分報告")
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
        "unit": "12-3",
        "unit_title": "自訂排序鍵值基礎：key 參數與具名函數（Named Functions）",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_12_3.py",
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
auto_grade_unit_12_3()
