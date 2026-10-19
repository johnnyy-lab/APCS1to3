# ==============================================================================
# 🧪 《PythAPCS123》單元 6-5：雙重與多重巢狀迴圈（時鐘模型與維度展開） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_6_5.py
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
NOTEBOOK_FILE = "PythAPCS123_6-5_nested_loops_and_clock_model.ipynb"

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


def auto_grade_unit_6_5():
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

    input_history = env.get("_ih", env.get("In", []))
    history_str = "\n".join(input_history) if isinstance(input_history, list) else ""
    history_clean = history_str.replace(" ", "")

    test_cases = [
        # ----------------------------------------------------------------------
        # 6-5-1 雙重迴圈心智模型：時鐘的分針與時針 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-5-1", "填空題", "雙重集訓週數與天數走訪 (for week, for day)", 4, ("total_training_days",),
         lambda g: (
             (True, "雙重迴圈外層週數與內層天數填寫正確！")
             if (g.get("total_training_days") == 6 or
                 ("forweekinrange" in history_clean and "fordayinrange" in history_clean))
             else (False, "請在 6-5-1 填空題填入外層 for week 與內層 for day 迴圈！")
         )),

        ("6-5-1", "練習題", "巡邏大樓房間二維走訪 (F{floor}-R{room})", 4, ("inspected_count",),
         lambda g: (
             (True, "大樓樓層與房間雙層巡查累加輸出正確！")
             if (("inspected_count" in g or "inspected_count" in history_str) and
                 ("F{floor}-R{room}" in history_str or "floor" in history_str and "room" in history_str))
             else (False, "請走訪 total_floors 與 rooms_per_floor，累加 inspected_count！")
         )),

        ("6-5-1", "挑戰題", "投籃訓練條件得分結算 (total_shots = 15, score = 16)", 5, ("total_shots", "score"),
         lambda g: (
             (True, "雙重迴圈模擬投籃條件判定與得分累加成功！")
             if (("total_shots" in g or "total_shots" in history_str) and
                 ("score" in g or "score" in history_str) and
                 ("(set_idx + shot_idx) % 2 == 0" in history_str or "16" in history_str or g.get("score") == 16))
             else (False, "請模擬 3 組各 5 球投籃，偶數得分累加，驗證 score = 16！")
         )),

        # ----------------------------------------------------------------------
        # 6-5-2 變數命名鐵律與常見命名天坑（遮蔽同名 Bug） (共 13 分)
        # ----------------------------------------------------------------------
        ("6-5-2", "填空題", "內層變數獨立命名避免衝突 (for j in range(1, 4))", 4, ("pair_count",),
         lambda g: (
             (True, "內層計數器獨立命名 j 填寫正確，9 組配對無誤！")
             if (g.get("pair_count") == 9 or "forjinrange" in history_clean or "({i}, {j})" in history_str)
             else (False, "請在 6-5-2 填空題將內層變數更正為 j！")
         )),

        ("6-5-2", "練習題", "二維座標乘積合格篩選 (qualified_cells)", 4, ("qualified_cells",),
         lambda g: (
             (True, "二維網格座標乘積門檻篩選統計正確！")
             if (("qualified_cells" in g or "qualified_cells" in history_str) and
                 ("product >= threshold" in history_str or "qualified_cells +=" in history_str))
             else (False, "請走訪 r 與 c，統計 product >= threshold 的合格格子數！")
         )),

        ("6-5-2", "挑戰題", "西洋棋盤黑白染色統計 (white_count = 10, black_count = 10)", 5, ("white_count", "black_count"),
         lambda g: (
             (True, "棋盤黑白染色雙重走訪與總格數驗證成功！")
             if (("white_count" in g or "white_count" in history_str) and
                 ("black_count" in g or "black_count" in history_str) and
                 ("(r + c) % 2 == 0" in history_str or "(r+c)%2==0" in history_clean))
             else (False, "請以 (r + c) % 2 == 0 分類統計 4x5 棋盤之白格與黑格！")
         )),

        # ----------------------------------------------------------------------
        # 6-5-3 end 參數與 print() 換行節奏控制（矩陣視覺化排版） (共 13 分)
        # ----------------------------------------------------------------------
        ("6-5-3", "填空題", "矩陣水平輸出與列尾換行 (end=' ', print())", 4, (),
         lambda g: (
             (True, "矩陣 end=' ' 水平排版與列尾換行填寫正確！")
             if ('end=" "' in history_str or "end=' '" in history_str) and
                ("print()" in history_clean)
             else (False, "請在 6-5-3 填空題填入 end=' ' 以及列尾換行 print()！")
         )),

        ("6-5-3", "練習題", "乘積矩陣排版與總和累加 (sum_val = 18)", 4, ("sum_val",),
         lambda g: (
             (True, "乘積矩陣排版與數值總和累加輸出正確！")
             if (("sum_val" in g or "sum_val" in history_str) and
                 ("18" in history_str or g.get("sum_val") == 18))
             else (False, "請排版 r * c 矩陣並累加數值總和至 sum_val！")
         )),

        ("6-5-3", "挑戰題", "斑馬線條紋矩陣排版 (hash_count = 12)", 5, ("hash_count",),
         lambda g: (
             (True, "奇偶欄位交錯斑馬線條紋矩陣輸出成功！")
             if (g.get("hash_count") == 12 or
                 (("hash_count" in g or "hash_count" in history_str) and
                  ("12" in history_str or ("#" in history_str and "-" in history_str))))
             else (False, "請依欄位奇偶排版 # 與 -，統計 4x5 矩陣中井字號為 12！")
         )),

        # ----------------------------------------------------------------------
        # 6-5-4 九九乘法表排版藝術與對齊格式化 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-5-4", "填空題", "乘法表內層邊界與列尾換行 (range(1, 6), print())", 4, (),
         lambda g: (
             (True, "九九乘法表內層 range(1, 6) 與換行填寫精確！")
             if ("range(1,6)" in history_clean or "range(1, 6)" in history_str) and
                ("print()" in history_clean)
             else (False, "請在 6-5-4 填空題填入內層 1 到 6 與換行指令 print()！")
         )),

        ("6-5-4", "練習題", "取餘數矩陣排版與整除次數 (zero_count = 5)", 4, ("zero_count",),
         lambda g: (
             (True, "模運算矩陣排版與整除個數 (zero_count = 5) 正確！")
             if (g.get("zero_count") == 5 or
                 (("zero_count" in g or "zero_count" in history_str) and
                  ("5" in history_str or "a % b" in history_str or "a%b" in history_clean)))
             else (False, "請排版 a % b 矩陣並統計餘數為 0 的整除次數！")
         )),

        ("6-5-4", "挑戰題", "加法方陣與主對角線和 (total = 80, diag_sum = 20)", 5, ("total_matrix_sum", "diag_sum"),
         lambda g: (
             (True, "方陣全元素總和 (80) 與主對角線和 (20) 計算成功！")
             if ((g.get("total_matrix_sum") == 80 and g.get("diag_sum") == 20) or
                 (("total_matrix_sum" in g or "total_matrix_sum" in history_str) and
                  ("diag_sum" in g or "diag_sum" in history_str) and
                  ("80" in history_str or "20" in history_str or "i == j" in history_str)))
             else (False, "請計算 4x4 加法方陣全元素總和與 i == j 對角線和！")
         )),

        # ----------------------------------------------------------------------
        # 6-5-5 內層邊界依賴外層變數（三角形與階梯模型） (共 12 分)
        # ----------------------------------------------------------------------
        ("6-5-5", "填空題", "同數階梯內層上限與換行 (range(1, row + 1), print())", 4, (),
         lambda g: (
             (True, "同數階梯內層依賴 row 與換行填寫正確！")
             if ("row+1" in history_clean or "row + 1" in history_str) and
                ("print()" in history_clean)
             else (False, "請在 6-5-5 填空題填入 row + 1 與換行 print()！")
         )),

        ("6-5-5", "練習題", "階梯數列總和計算 (grand_total = 10)", 4, ("grand_total",),
         lambda g: (
             (True, "階梯數列雙重走訪累加總和 (10) 輸出正確！")
             if (("grand_total" in g or "grand_total" in history_str) and
                 ("10" in history_str or g.get("grand_total") == 10))
             else (False, "請使用階梯雙重迴圈累加出現的所有數字至 grand_total！")
         )),

        ("6-5-5", "挑戰題", "倒階梯遞減走訪與奇數統計 (odd_count = 9)", 4, ("odd_count",),
         lambda g: (
             (True, "倒階梯遞減圖形排版與奇數次數統計 (9) 成功！")
             if (("odd_count" in g or "odd_count" in history_str) and
                 ("9" in history_str or g.get("odd_count") == 9))
             else (False, "請排版倒階梯圖形並統計奇數出現總次數 (9 次)！")
         )),

        # ----------------------------------------------------------------------
        # 6-5-6 雙重迴圈的雙變數枚舉（窮舉法初步） (共 12 分)
        # ----------------------------------------------------------------------
        ("6-5-6", "填空題", "和為 10 且 a < b 防重複枚舉 (range(a + 1, 10))", 4, (),
         lambda g: (
             (True, "防止重複枚舉之 b 起點 a + 1 填寫正確！")
             if ("a+1" in history_clean or "a + 1" in history_str)
             else (False, "請在 6-5-6 填空題填入內層起點 a + 1！")
         )),

        ("6-5-6", "練習題", "雞兔同籠雙變數窮舉 (chickens = 23, rabbits = 12)", 4, ("chickens", "rabbits"),
         lambda g: (
             (True, "雞兔同籠窮舉命中解 (23 雞 12 兔) 正確！")
             if (("chickens" in g or "chickens" in history_str) and
                 ("rabbits" in g or "rabbits" in history_str) and
                 ("23" in history_str and "12" in history_str))
             else (False, "請以雙重迴圈窮舉雞兔數量，求出 23 雞與 12 兔！")
         )),

        ("6-5-6", "挑戰題", "邊長 20 內畢氏三元組枚舉 (pythagorean_count = 6)", 4, ("pythagorean_count",),
         lambda g: (
             (True, "畢氏三元整數組枚舉統計 (6 組) 成功！")
             if (("pythagorean_count" in g or "pythagorean_count" in history_str) and
                 ("6" in history_str or g.get("pythagorean_count") == 6))
             else (False, "請枚舉 a < b <= 20 找出滿足 a^2 + b^2 = c^2 的 6 組畢氏三元組！")
         )),

        # ----------------------------------------------------------------------
        # 6-5-7 雙重迴圈的中斷控制：旗標變數連鎖跳出 (共 12 分)
        # ----------------------------------------------------------------------
        ("6-5-7", "填空題", "雙重中斷旗標連鎖跳出 (found = True; break; if found: break)", 4, (),
         lambda g: (
             (True, "布林旗標更新與外層連鎖 break 填寫精確！")
             if (("found=True" in history_clean or "found = True" in history_str) and
                 ("iffound:break" in history_clean.replace("\n", "") or "if found" in history_str))
             else (False, "請在 6-5-7 填空題填入 found = True、break 以及外層 if found: break！")
         )),

        ("6-5-7", "練習題", "二維搜尋目標和與步數統計 (found 連鎖跳出)", 4, ("steps", "found"),
         lambda g: (
             (True, "二維搜尋目標和連鎖中斷與步數統計正確！")
             if (("steps" in g or "steps" in history_str) and
                 ("found" in g or "found" in history_str) and
                 ("break" in history_str))
             else (False, "請搜尋 a + b == target_sum，記錄 steps 並以旗標連鎖 break！")
         )),

        ("6-5-7", "挑戰題", "半質數拆解密碼鎖 (77 = 7 * 11 旗標連鎖中斷)", 4, ("ans_p", "ans_q"),
         lambda g: (
             (True, "半質數分解 (77 = 7 * 11) 雙重迴圈旗標鎖定成功！")
             if (("ans_p" in g or "ans_p" in history_str) and
                 ("ans_q" in g or "ans_q" in history_str) and
                 ("7" in history_str and "11" in history_str))
             else (False, "請以雙重迴圈枚舉 p * q == 77，找到 7 與 11 並連鎖 break！")
         )),

        # ----------------------------------------------------------------------
        # 6-5-8 三重與多重巢狀迴圈：空間維度展開與效能警示 (共 12 分)
        # ----------------------------------------------------------------------
        ("6-5-8", "填空題", "三重座標盒子枚舉次數 (total_runs = 24)", 4, ("total_runs",),
         lambda g: (
             (True, "三重迴圈層次與執行次數 (24 次) 填寫正確！")
             if (g.get("total_runs") == 24 or "range(1, 4)" in history_str or "range(1, 5)" in history_str)
             else (False, "請在 6-5-8 填空題填入中層 1 到 4 與內層 1 到 5 範圍！")
         )),

        ("6-5-8", "練習題", "三角形三邊長整數解枚舉 (valid_triangles)", 4, ("valid_triangles",),
         lambda g: (
             (True, "周長 P 之三角形不等式三重枚舉輸出正確！")
             if (("valid_triangles" in g or "valid_triangles" in history_str) and
                 ("a + b > c" in history_str or "a+b>c" in history_clean))
             else (False, "請三重枚舉 a, b, c，統計滿足 a + b + c == P 且 a + b > c 的個數！")
         )),

        ("6-5-8", "挑戰題", "湊 25 元零錢硬幣枚舉 (coin_ways = 12)", 4, ("coin_ways",),
         lambda g: (
             (True, "硬幣面額湊錢方案枚舉 (12 種) 成功！")
             if (("coin_ways" in g or "coin_ways" in history_str) and
                 ("12" in history_str or g.get("coin_ways") == 12))
             else (False, "請枚舉 10元、5元、1元湊出 25 元，方案數為 12 種！")
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
        badge = '🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通雙重與多重巢狀迴圈之時鐘模型，二維矩陣排版與旗標連鎖跳出登峰造極！'
    elif total_score >= 80:
        badge = '🥈 卓越冒險者（銀牌徽章 🥈）—— 表現優異，變數命名嚴謹，階梯依賴與雙變數窮舉架構清晰！'
    elif total_score >= 60:
        badge = '🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目微調排版換行或連鎖旗標！'
    else:
        badge = '🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 6-5：雙重與多重巢狀迴圈（時鐘模型與維度展開） —— 自動評分報告")
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
        "unit": "6-5",
        "unit_title": "雙重與多重巢狀迴圈（時鐘模型與維度展開）",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_6_5.py",
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
auto_grade_unit_6_5()
