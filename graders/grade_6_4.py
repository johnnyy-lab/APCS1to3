# ==============================================================================
# 🧪 《PythAPCS123》單元 6-4：迴圈流程跳轉控制（break, continue 與 for...else） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_6_4.py
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
NOTEBOOK_FILE = "PythAPCS123_6-4_loop_break_and_continue.ipynb"

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


def auto_grade_unit_6_4(env=None):
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

    input_history = env.get("_ih", env.get("In", []))
    history_str = "\n".join(input_history) if isinstance(input_history, list) else ""
    history_clean = history_str.replace(" ", "")

    test_cases = [
        # ----------------------------------------------------------------------
        # 6-4-1 break：緊急煞車與提前終止 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-4-1", "填空題", "電梯超重煞車中斷 (total_weight > 300, break)", 4, (),
         lambda g: (
             (True, "電梯超重 break 緊急煞車關鍵字填寫正確！")
             if ("total_weight>300" in history_clean or "total_weight > 300" in history_str) and
                ("break" in history_str)
             else (False, "請在 6-4-1 填空題空格填入緊急煞車關鍵字 break！")
         )),

        ("6-4-1", "練習題", "目標幸運數字搜尋 (target = 37, found = True, steps)", 4, ("found", "steps"),
         lambda g: (
             (True, "幸運數字搜尋旗標與終止步數記錄正確！")
             if (("found" in g or "found" in history_str) and
                 ("steps" in g or "steps" in history_str) and
                 ("break" in history_str))
             else (False, "請在搜尋到 target 時將 found 設為 True，記錄 steps 並 break！")
         )),

        ("6-4-1", "挑戰題", "最小公倍數走訪搜尋 (lcm = 36)", 5, ("lcm",),
         lambda g: (
             (True, "最小公倍數 (36) 首次整除命中與終止成功！")
             if (("lcm" in g or "lcm" in history_str) and
                 ("36" in history_str or g.get("lcm") == 36) and
                 ("break" in history_str))
             else (False, "請走訪候選數，找到第一個能同時整除 12 與 18 的數 (36) 並 break！")
         )),

        # ----------------------------------------------------------------------
        # 6-4-2 continue：跨步換輪與跳過當前 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-4-2", "填空題", "指定數值跳步換輪 (val == 4 or val == 7, continue)", 4, (),
         lambda g: (
             (True, "條件過濾跳步關鍵字 continue 填寫正確！")
             if ("val==4orval==7" in history_clean or "4" in history_str and "7" in history_str) and
                ("continue" in history_str)
             else (False, "請在 6-4-2 填空題填入跳步關鍵字 continue！")
         )),

        ("6-4-2", "練習題", "跳過 5 的倍數累加總和 (sum_filtered = 160)", 4, ("sum_filtered",),
         lambda g: (
             (True, "排除 5 的倍數之 continue 累加 (160) 輸出正確！")
             if (("sum_filtered" in g or "sum_filtered" in history_str) and
                 ("% 5 == 0" in history_str or "%5==0" in history_clean) and
                 ("continue" in history_str))
             else (False, "請走訪 1 到 20，若為 5 的倍數則 continue，其餘累加到 sum_filtered！")
         )),

        ("6-4-2", "挑戰題", "while 迴圈安全 continue 奇數和 (total_odd = 25)", 5, ("total_odd",),
         lambda g: (
             (True, "while 安全步進防空轉與奇數累加 (25) 成功！")
             if (("total_odd" in g or "total_odd" in history_str) and
                 ("25" in history_str or g.get("total_odd") == 25) and
                 ("continue" in history_str))
             else (False, "請在 while 迴圈確保步進在 continue 之前，計算奇數和 25！")
         )),

        # ----------------------------------------------------------------------
        # 6-4-3 break vs continue 深度對比與執行軌跡追蹤 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-4-3", "填空題", "煞車 vs 跳步次數追蹤 (count_break, count_continue)", 4, (),
         lambda g: (
             (True, "break 與 continue 兩段式對比填寫正確！")
             if ("count_break" in history_str and "count_continue" in history_str and
                 "break" in history_str and "continue" in history_str)
             else (False, "請在 6-4-3 填空題分別填入 break 與 continue！")
         )),

        ("6-4-3", "練習題", "特殊符號過濾與終止 (result = 'APCSPYTHON')", 4, ("result",),
         lambda g: (
             (True, "字串掃描跳過 '#' 並於 '*' 終止之串接結果正確！")
             if (("result" in g or "result" in history_str) and
                 ("APCSPYTHON" in history_str or g.get("result") == "APCSPYTHON") and
                 ("continue" in history_str and "break" in history_str))
             else (False, "請遇 '#' continue、遇 '*' break，其餘串接為 APCSPYTHON！")
         )),

        ("6-4-3", "挑戰題", "雙指標篩選跳步與上限終止 (total = 106, last_add = 15)", 5, ("total", "last_add"),
         lambda g: (
             (True, "排除 4 的倍數且突破 100 終止雙指標運算成功！")
             if (("total" in g or "total" in history_str) and
                 ("last_add" in g or "last_add" in history_str) and
                 ("106" in history_str or g.get("total") == 106))
             else (False, "請逢 4 的倍數 continue，total > 100 時 break，求出 106 與 15！")
         )),

        # ----------------------------------------------------------------------
        # 6-4-4 旗標搜尋與質數檢驗：break 的經典應用模式 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-4-4", "填空題", "質數檢驗整除判定與煞車 (test_val % factor == 0, break)", 4, (),
         lambda g: (
             (True, "質數檢驗整除 == 0 與 break 煞車填寫精確！")
             if ("test_val%factor==0" in history_clean or "== 0" in history_str) and
                ("break" in history_str)
             else (False, "請在 6-4-4 填空題填入整除 0 與煞車關鍵字 break！")
         )),

        ("6-4-4", "練習題", "質數判定旗標 (result_prime = True / False)", 4, ("result_prime",),
         lambda g: (
             (True, "任意數質數檢驗與布林旗標正確！")
             if (("result_prime" in g or "result_prime" in history_str) and
                 ("break" in history_str))
             else (False, "請走訪因數檢驗 candidate_num，若整除則立旗並 break！")
         )),

        ("6-4-4", "挑戰題", "區間質數計數器 (10 到 50 之間共有 11 個質數)", 5, ("prime_count",),
         lambda g: (
             (True, "巢狀質數走訪與區間計數 (11 個質數) 成功！")
             if (("prime_count" in g or "prime_count" in history_str) and
                 ("11" in history_str or g.get("prime_count") == 11))
             else (False, "請統計 10 到 50 之間的質數個數（共 11 個）！")
         )),

        # ----------------------------------------------------------------------
        # 6-4-5 衛語句（Guard Clauses）心法：用 continue 消除多層巢狀 (共 12 分)
        # ----------------------------------------------------------------------
        ("6-4-5", "填空題", "偶數過濾衛語句 (if num % 2 == 0: continue)", 4, (),
         lambda g: (
             (True, "偶數衛語句 continue 填寫正確！")
             if ("num%2==0" in history_clean or "num % 2 == 0" in history_str) and
                ("continue" in history_str)
             else (False, "請在 6-4-5 填空題填入跳步關鍵字 continue！")
         )),

        ("6-4-5", "練習題", "水庫進水量雜訊清洗 (effective_water = 150, valid_readings = 3)", 4, ("effective_water", "valid_readings"),
         lambda g: (
             (True, "感測器負數與零雜訊過濾清洗輸出正確！")
             if (("effective_water" in g or "effective_water" in history_str) and
                 ("valid_readings" in g or "valid_readings" in history_str) and
                 ("continue" in history_str))
             else (False, "請過濾非正數（continue），統計有效水量 150 與筆數 3！")
         )),

        ("6-4-5", "挑戰題", "字串數字過濾器 (letters_only = 'ABCDE')", 4, ("letters_only",),
         lambda g: (
             (True, "字元數字衛語句過濾為純字母 (ABCDE) 成功！")
             if (("letters_only" in g or "letters_only" in history_str) and
                 ("ABCDE" in history_str or g.get("letters_only") == "ABCDE") and
                 ("continue" in history_str))
             else (False, "請使用 continue 跳過數字字元，串接純字母 ABCDE！")
         )),

        # ----------------------------------------------------------------------
        # 6-4-6 Python 獨家利器：for...else 與 while...else 結構 (共 12 分)
        # ----------------------------------------------------------------------
        ("6-4-6", "填空題", "for...else 質數檢驗結構對齊 (else:)", 4, (),
         lambda g: (
             (True, "與 for 對齊之 else 關鍵字填寫正確！")
             if ("for d in range" in history_str or "for" in history_str) and
                ("else:" in history_clean)
             else (False, "請在 6-4-6 填空題填入與 for 對齊的 else: 關鍵字！")
         )),

        ("6-4-6", "練習題", "密碼違規字元搜尋與 for...else 驗收", 4, ("status",),
         lambda g: (
             (True, "for...else 完整走完未中斷判定正確！")
             if (("status" in g or "status" in history_str) and
                 ("ALL_VALID" in history_str or "INVALID" in history_str) and
                 ("else:" in history_clean))
             else (False, "請遇 '!' break 設 INVALID，未中斷進入 else 設 ALL_VALID！")
         )),

        ("6-4-6", "挑戰題", "while...else 倒數正常停機驗證", 4, ("else_executed", "count"),
         lambda g: (
             (True, "while...else 倒數停機進入 else 區塊成功！")
             if (("else_executed" in g or "else_executed" in history_str) and
                 ("火箭發射" in history_str or g.get("else_executed") is True or g.get("count") == 0))
             else (False, "請撰寫 while...else 倒數，正常停機進入 else 輸出發射！")
         )),

        # ----------------------------------------------------------------------
        # 6-4-7 while True 自由出口模式（Free-Exit Loop） (共 12 分)
        # ----------------------------------------------------------------------
        ("6-4-7", "填空題", "while True 骰子擲點最大值退出 (while True:, break)", 4, (),
         lambda g: (
             (True, "while True 引擎與擲出 6 點 break 退出填寫正確！")
             if ("whileTrue:" in history_clean or "while True" in history_str) and
                ("break" in history_str)
             else (False, "請在 6-4-7 填空題填入 while True 與 break！")
         )),

        ("6-4-7", "練習題", "倍數逼近突破門檻 (val = 1024, steps = 10)", 4, ("val", "steps"),
         lambda g: (
             (True, "while True 乘 2 逼近 1000 門檻終止輸出正確！")
             if (("val" in g or "val" in history_str) and
                 ("steps" in g or "steps" in history_str) and
                 ("1024" in history_str or g.get("val") == 1024) and
                 ("break" in history_str))
             else (False, "請在 while True 中每輪 val *= 2，>= 1000 時 break！")
         )),

        ("6-4-7", "挑戰題", "烏龜追兔子動態追逐遊戲 (rounds = 5, turtle = 25)", 4, ("rounds", "turtle"),
         lambda g: (
             (True, "動態追逐追上中斷 (5 輪，位置 25) 成功！")
             if (("rounds" in g or "rounds" in history_str) and
                 ("turtle" in g or "turtle" in history_str) and
                 ("25" in history_str or (g.get("rounds") == 5 and g.get("turtle") == 25)))
             else (False, "請以 while True 模擬烏龜追兔子，turtle >= rabbit 時 break！")
         )),

        # ----------------------------------------------------------------------
        # 6-4-8 break 與 continue 的常見天坑與除錯心法 (共 12 分)
        # ----------------------------------------------------------------------
        ("6-4-8", "填空題", "修正過早中斷天坑 (char == 'O': break)", 4, ("found_o",),
         lambda g: (
             (True, "搜尋目標命中煞車邏輯填寫正確！")
             if ("found_o" in history_str or "found_o" in g) and
                ("break" in history_str)
             else (False, "請在 6-4-8 填空題填入尋獲時的煞車指令 break！")
         )),

        ("6-4-8", "練習題", "等差數列首個大於 20 之項 (target_val = 23)", 4, ("target_val",),
         lambda g: (
             (True, "等差數列首個突破 20 搜尋終止正確！")
             if (("target_val" in g or "target_val" in history_str) and
                 ("23" in history_str or g.get("target_val") == 23) and
                 ("break" in history_str))
             else (False, "請搜尋首個大於 20 的等差項 (23)，記錄並 break！")
         )),

        ("6-4-8", "挑戰題", "密碼三次重試安全驗證 (第 3 次成功登入)", 4, ("is_login",),
         lambda g: (
             (True, "密碼有限次數重試與命中 break 邏輯成功！")
             if (("is_login" in g or "is_login" in history_str) and
                 ("break" in history_str) and
                 (g.get("is_login") is True or "登入成功" in history_str))
             else (False, "請模擬密碼重試，正確才 break，驗證第 3 次登入成功！")
         )),
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
        badge = '🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通 break、continue 與 for...else 之流程跳轉藝術，控速如賽車手般精準！'
    elif total_score >= 80:
        badge = '🥈 卓越冒險者（銀牌徽章 🥈）—— 表現優異，衛語句心法與 while True 自由出口駕輕就熟！'
    elif total_score >= 60:
        badge = '🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目微調中斷條件或跳步位置！'
    else:
        badge = '🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 6-4：迴圈流程跳轉控制（break, continue 與 for...else） —— 自動評分報告")
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
        "unit": "6-4",
        "unit_title": "迴圈流程跳轉控制（break, continue 與 for...else）",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_6_4.py",
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
auto_grade_unit_6_4()
