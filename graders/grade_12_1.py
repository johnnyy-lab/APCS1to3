# ==============================================================================
# 🧪 《PythAPCS123》單元 12-1：就地排序（sort）與新物件排序（sorted） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_12_1.py
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
NOTEBOOK_FILE = "PythAPCS123_12-1_in_place_sort_vs_sorted.ipynb"

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

def get_submission_env():
    """取得 Colab / 本地端全域變數與執行歷史代碼"""
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


def auto_grade_unit_12_1():
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

    env, history = get_submission_env()
    history_str = "\n".join(history)
    history_clean = history_str.replace(" ", "").replace("\t", "")

    test_cases = [
        # ----------------------------------------------------------------------
        # 12-1-1 排序核心概念：升序預設行為 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("12-1-1", "填空題", "sorted() 升序排序與最高身高索引用法", 5, ("sorted_heights",),
         lambda g: (
             (True, "sorted_heights 升序排序正確，且最高身高取值無誤！")
             if (g.get("sorted_heights") == [158, 165, 169, 172, 175, 180]) or
                ("sorted(heights)" in history_str and "sorted_heights" in history_str)
             else (False, "尚未找到符合預期的 sorted_heights，請使用 sorted(heights) 並確認已點擊儲存格播放鍵執行！")
         )),

        ("12-1-1", "練習題", "整數數列升序排序與全距計算", 6, ("res",),
         lambda g: (
             (True, "練習題 12.1.1 raw_data 升序排序與全距計算正確！")
             if (g.get("res") == [12, 34, 45, 67, 89]) or
                ("sorted(raw_data)" in history_str and ("- res[0]" in history_str or "77" in history_str or "res[-1]" in history_str))
             else (False, "請將 raw_data 進行 sorted() 升序排序，並計算最大值與最小值之全距（最大值 - 最小值）！")
         )),

        ("12-1-1", "挑戰題", "浮點數跑步成績排序與前三名切片選取", 6, ("ordered_times",),
         lambda g: (
             (True, "挑戰題 12.1.1 浮點數跑步成績排序與前三名切片成功！")
             if (isinstance(g.get("ordered_times"), list) and len(g.get("ordered_times")) >= 5 and g.get("ordered_times") == sorted(g.get("ordered_times"))) or
                ("sorted(" in history_str and "[:3]" in history_str and ("times" in history_str or "ordered" in history_str))
             else (False, "請宣告至少 5 筆浮點數之跑步秒數串列，使用 sorted() 升序排序後以 [:3] 取出前三名！")
         )),

        # ----------------------------------------------------------------------
        # 12-1-2 原地修改方法 list.sort() (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("12-1-2", "填空題", "避免 a = a.sort() 陷阱，單獨一行呼叫 cards.sort()", 5, ("cards",),
         lambda g: (
             (False, "⚠️ 偵測到 cards 變數值為 None！這是經典的 cards = cards.sort() 陷阱！.sort() 是原地修改且回傳 None，請單獨一行呼叫 cards.sort()！")
             if g.get("cards") is None
             else (
                 (True, "cards.sort() 單獨一行原地排序正確，成功避開 None 陷阱！")
                 if (g.get("cards") == [1, 2, 4, 7, 9]) or ("cards.sort()" in history_str and "cards = cards.sort()" not in history_clean)
                 else (False, "請使用 cards.sort() 原地排序撲克牌串列，切勿覆蓋原變數！")
             )
         )),

        ("12-1-2", "練習題", "data.sort() 原地修改負數與正數串列", 6, ("data",),
         lambda g: (
             (False, "⚠️ 偵測到 data 變數值為 None！請勿對 .sort() 進行賦值（避免 data = data.sort()）！")
             if g.get("data") is None
             else (
                 (True, "練習題 12.1.2 data.sort() 原地排序與首元素取值正確！")
                 if (g.get("data") == [-9, -3, 0, 15, 42]) or ("data.sort()" in history_str and "data = data.sort()" not in history_clean)
                 else (False, "請使用 data.sort() 對 data 進行原地升序排序，並印出排序後內容與第一個元素！")
             )
         )),

        ("12-1-2", "挑戰題", "捕捉 .sort() 回傳值為 None 之防呆警告機制", 6, ("test_list", "ret"),
         lambda g: (
             (True, "挑戰題 12.1.2 成功驗證 .sort() 回傳值為 None 並發出警示！")
             if ("test_list.sort()" in history_str and ("is None" in history_str or "== None" in history_str)) or
                (g.get("ret") is None and "test_list" in g)
             else (False, "請執行 test_list.sort() 並檢查其回傳值是否為 None，若為 None 則印出警告訊息！")
         )),

        # ----------------------------------------------------------------------
        # 12-1-3 內建函數 sorted(iterable) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("12-1-3", "填空題", "sorted() 生成獨立新串列且原串列完好無損", 5, ("leaderboard", "log_order"),
         lambda g: (
             (True, "leaderboard 成功由 sorted(log_order) 生成，且原 log_order 完整保留！")
             if (g.get("leaderboard") == [60, 72, 88, 91, 95] and g.get("log_order") == [88, 95, 72, 60, 91]) or
                ("sorted(log_order)" in history_str and "leaderboard" in history_str)
             else (False, "請使用 leaderboard = sorted(log_order) 產出新排序串列，同時維持 log_order 原樣！")
         )),

        ("12-1-3", "練習題", "raw_temps 溫度計紀錄雙軌保留與排序", 6, ("sorted_temps", "raw_temps"),
         lambda g: (
             (True, "練習題 12.1.3 成功產生 sorted_temps 排序串列並保留原始 raw_temps！")
             if (g.get("sorted_temps") == [19.8, 23.0, 25.4, 28.5, 31.2] and g.get("raw_temps") == [28.5, 23.0, 31.2, 19.8, 25.4]) or
                ("sorted(raw_temps)" in history_str and "sorted_temps" in history_str)
             else (False, "請使用 sorted_temps = sorted(raw_temps) 進行排序，並確認 raw_temps 未受竄改！")
         )),

        ("12-1-3", "挑戰題", "結合 sorted() 極值與原串列 arr.index() 原始索引定位", 6, ("min_val", "max_val", "arr"),
         lambda g: (
             (True, "挑戰題 12.1.3 成功結合 sorted() 與 arr.index() 找出極值原始索引！")
             if ("arr.index" in history_str and "sorted(" in history_str) or
                (isinstance(g.get("arr"), list) and "min_val" in g and "max_val" in g)
             else (False, "請宣告包含至少 5 個整數的 arr，以 sorted() 找出最大與最小值後，透過 arr.index() 找出其原始索引！")
         )),

        # ----------------------------------------------------------------------
        # 12-1-4 記憶體耗損與使用時機對照 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("12-1-4", "填空題", "依場景精準選用 nums1.sort() 與 sorted(nums2)", 5, ("nums1", "sorted_nums2", "nums2"),
         lambda g: (
             (True, "nums1 原地排序與 sorted_nums2 新串列生成填空皆完全正確！")
             if (g.get("nums1") == [1, 3, 7, 9] and g.get("sorted_nums2") == [2, 4, 6, 8] and g.get("nums2") == [8, 4, 6, 2]) or
                ("nums1.sort()" in history_str and "sorted(nums2)" in history_str)
             else (False, "場景 1 請使用 nums1.sort() 原地修改；場景 2 請使用 sorted_nums2 = sorted(nums2)！")
         )),

        ("12-1-4", "練習題", "遊戲戰力排行榜 leaderboard 雙軌維護", 6, ("leaderboard", "power_list"),
         lambda g: (
             (True, "練習題 12.1.4 成功以 sorted(power_list) 建立排行榜並印出首位與戰力天花板！")
             if (g.get("leaderboard") == [1500, 1800, 2400, 2900, 3200] and g.get("power_list") == [2400, 1500, 3200, 1800, 2900]) or
                ("sorted(power_list)" in history_str and "leaderboard" in history_str)
             else (False, "請使用 leaderboard = sorted(power_list) 產生排行榜，並輸出原始第一位與最高戰力者！")
         )),

        ("12-1-4", "挑戰題", "使用 id() 探測驗證原地修改 O(1) 與副本生成 O(N) 記憶體差異", 6, ("id_before", "id_after"),
         lambda g: (
             (True, "挑戰題 12.1.4 成功以 id() 探測驗證原地排序前後 id 相同與 sorted 副本 id 不同！")
             if ("id(items)" in history_str and "items.sort()" in history_str and "sorted(" in history_str) or
                (g.get("id_before") is not None and g.get("id_before") == g.get("id_after"))
             else (False, "請使用 id() 記錄 items 於 items.sort() 前後的記憶體位址，並對比 sorted(items2) 的新位址！")
         )),

        # ----------------------------------------------------------------------
        # 12-1-5 非串列容器的排序 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("12-1-5", "填空題", "字母易位字（Anagram）檢驗神器 is_anagram", 5, ("is_anagram",),
         lambda g: (
             (True, "is_anagram 字母易位字檢驗填空正確！sorted(word1) == sorted(word2)！")
             if (g.get("is_anagram") is True) or
                ("sorted(word1)" in history_str and "sorted(word2)" in history_str and "is_anagram" in history_str)
             else (False, "請使用 is_anagram = sorted(word1) == sorted(word2) 進行易位字驗證！")
         )),

        ("12-1-5", "練習題", "結合 set() 去重與 sorted() 升序輸出 unique_sorted", 6, ("unique_sorted",),
         lambda g: (
             (True, "練習題 12.1.5 集合去重與 sorted() 升序排序整合正確！")
             if (g.get("unique_sorted") == [1, 2, 3, 7, 9]) or
                ("sorted(set(raw_list))" in history_str or "unique_sorted" in history_str)
             else (False, "請使用 unique_sorted = sorted(set(raw_list)) 將 raw_list 先去重後再排序！")
         )),

        ("12-1-5", "挑戰題", "密碼字元 ASCII 排序後首字元數字檢驗", 5, (),
         lambda g: (
             (True, "挑戰題 12.1.5 密碼排序後首字元數字範圍檢驗正確！")
             if ("sorted(password)" in history_str or "sorted_chars" in history_str) and
                (("<= sorted_chars[0] <=" in history_str) or ("isdigit()" in history_str) or ("0" in history_str and "9" in history_str))
             else (False, "請宣告密碼字串 password，以 sorted() 排序後檢查首字元是否介於 '0' 至 '9' 之間！")
         )),

        # ----------------------------------------------------------------------
        # 12-1-6 穩定排序（Stable Sort）特性 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("12-1-6", "填空題", "穩定排序概念檢驗，相等鍵值保留相對順序", 5, ("sorted_data",),
         lambda g: (
             (True, "sorted_data 穩定排序填空正確！相同鍵值項目順序完全保持原樣！")
             if (g.get("sorted_data") == [('B', 5), ('D', 5), ('A', 10), ('C', 10)]) or
                ("sorted(data, key=get_value)" in history_str or "sorted(data,key=get_value)" in history_clean)
             else (False, "請使用 sorted_data = sorted(data, key=get_value) 驗證穩定排序特性！")
         )),

        ("12-1-6", "練習題", "選手同分成績穩定排序保留登記順序", 6, ("res",),
         lambda g: (
             (True, "練習題 12.1.6 選手成績穩定排序正確！同分者登記先後完全維持！")
             if (g.get("res") == [(80, 'T2'), (80, 'T4'), (100, 'T1'), (100, 'T3')]) or
                ("sorted(athletes" in history_str and ("take_score" in history_str or "lambda" in history_str))
             else (False, "請以分數為鍵值對 athletes 進行 sorted 排序，確認同分選手保持原始相對順序！")
         )),

        ("12-1-6", "挑戰題", "商品類別穩定排序示範", 5, ("sorted_products",),
         lambda g: (
             (True, "挑戰題 12.1.6 商品類別穩定排序示範正確！")
             if ("sorted(" in history_str and "category" in history_str) or
                (isinstance(g.get("sorted_products"), list) and len(g.get("sorted_products")) >= 4)
             else (False, "請建立商品清單並依「商品類別」進行穩定排序，展示同類別商品先後順序不變！")
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
        badge = '🏆 完美滿分！你已經徹底攻克就地排序與新物件排序的核心記憶體機制，具備 APCS 演算法高手的穩健實力！'
    elif total_score >= 80:
        badge = '🌟 優秀！對於 sort() 與 sorted() 的使用時機與底層差異掌握非常扎實，稍微細心檢查即可登峰造極！'
    elif total_score >= 60:
        badge = '👍 及格！基本排序概念已建立，請特別注意原地修改回傳 None 的考場經典地雷！'
    else:
        badge = '💪 請再接再厲！建議回到上方各個微階梯儲存格逐題點擊播放鍵執行代碼！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 12-1：就地排序（sort）與新物件排序（sorted） —— 自動評分報告")
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
        "unit": "12-1",
        "unit_title": "就地排序（sort）與新物件排序（sorted）",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_12_1.py",
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
auto_grade_unit_12_1()
