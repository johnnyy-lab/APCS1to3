# ==============================================================================
# 🧪 《PythAPCS123》單元 6-6：幾何圖形與星號排版演算法 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_6_6.py
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
NOTEBOOK_FILE = "PythAPCS123_6-6_geometric_patterns_and_asterisk_formatting.ipynb"

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


def auto_grade_unit_6_6(env=None):
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
    history_clean_all = history_clean.replace("\n", "")

    test_cases = [
        # ----------------------------------------------------------------------
        # 6-6-1 幾何圖形排版心智模型：代數映射與行列雙重走訪 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-6-1", "填空題", "等差階梯星號內層範圍 (range(stars_count))", 4, (),
         lambda g: (
             (True, "等差階梯星號內層計數範圍填寫正確！")
             if ("range(stars_count)" in history_clean or "stars_count" in history_str)
             else (False, "請在 6-6-1 填空題填入 range(stars_count)！")
         )),

        ("6-6-1", "練習題", "三倍速階梯星號總數統計 (total_stars = 9/18)", 4, ("total_stars",),
         lambda g: (
             (True, "三倍速階梯星號排版與顆數累加正確！")
             if (g.get("total_stars") in [9, 18] or
                 (("total_stars" in g or "total_stars" in history_str) and
                  ("3 * r" in history_str or "3*r" in history_clean)))
             else (False, "請每列印出 3 * r 顆星號並累加總星號數至 total_stars！")
         )),

        ("6-6-1", "挑戰題", "平方倍增星號排版 (total_stars = 30)", 5, ("total_stars",),
         lambda g: (
             (True, "平方倍增星號排版與總顆數 (30 顆) 驗證成功！")
             if (g.get("total_stars") == 30 or
                 (("total_stars" in g or "total_stars" in history_str) and
                  ("r ** 2" in history_str or "r**2" in history_clean or "30" in history_str)))
             else (False, "請每列印出 r ** 2 顆星號，4 列總星號應為 30 顆！")
         )),

        # ----------------------------------------------------------------------
        # 6-6-2 矩形與空心方框排版：邊框條件判定式 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-6-2", "填空題", "空心方框邊界條件 (r == H-1, c == W-1)", 4, (),
         lambda g: (
             (True, "空心方框末列與末欄邊界條件填寫正確！")
             if ("H-1" in history_clean or "H - 1" in history_str) and
                ("W-1" in history_clean or "W - 1" in history_str)
             else (False, "請在 6-6-2 填空題填入 H - 1 與 W - 1 邊界！")
         )),

        ("6-6-2", "練習題", "主對角線空心方陣 (star_count = 14/19)", 4, ("star_count",),
         lambda g: (
             (True, "四邊框與主對角線星號方陣排版輸出正確！")
             if (g.get("star_count") in [14, 19] or
                 (("star_count" in g or "star_count" in history_str) and
                  ("r == c" in history_str or "r==c" in history_clean)))
             else (False, "請在四邊框或 r == c 處印星號，並統計 star_count！")
         )),

        ("6-6-2", "挑戰題", "田字窗格空心矩陣 (plus_count = 21)", 5, ("plus_count",),
         lambda g: (
             (True, "田字窗格中央十字與外框排版 (21 個 +) 成功！")
             if (g.get("plus_count") == 21 or
                 (("plus_count" in g or "plus_count" in history_str) and
                  ("N // 2" in history_str or "N//2" in history_clean or "21" in history_str)))
             else (False, "請排版四邊框與正中央水平垂直十字加號，總計 21 個！")
         )),

        # ----------------------------------------------------------------------
        # 6-6-3 直角三角形系列（一）：靠左正直角三角形 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-6-3", "填空題", "靠左直角三角形內層走訪與換行 (range(r), print())", 4, (),
         lambda g: (
             (True, "靠左直角三角形內層 range(r) 與列尾換行填寫正確！")
             if ("range(r)" in history_clean or "range( r )" in history_str) and
                ("print()" in history_clean)
             else (False, "請在 6-6-3 填空題填入 range(r) 與列尾換行 print()！")
         )),

        ("6-6-3", "練習題", "靠左數字階梯總和 (number_sum = 14/30)", 4, ("number_sum",),
         lambda g: (
             (True, "數字階梯三角形排版與數值總和輸出正確！")
             if (g.get("number_sum") in [14, 30] or
                 (("number_sum" in g or "number_sum" in history_str) and
                  ("number_sum +=" in history_str or "number_sum+=" in history_clean)))
             else (False, "請每列印出 r 個數字 r，並累加總和至 number_sum！")
         )),

        ("6-6-3", "挑戰題", "弗洛伊德流水號三角形 (last_num = 10)", 5, ("last_num", "cur_num"),
         lambda g: (
             (True, "弗洛伊德連續流水號直角三角形 (last_num = 10) 成功！")
             if (g.get("last_num") == 10 or
                 (("cur_num" in g or "cur_num" in history_str) and
                  ("10" in history_str or "cur_num += 1" in history_str)))
             else (False, "請排版 4 層弗洛伊德三角形，最後一個數字應為 10！")
         )),

        # ----------------------------------------------------------------------
        # 6-6-4 直角三角形系列（二）：靠左倒直角三角形 (共 13 分)
        # ----------------------------------------------------------------------
        ("6-6-4", "填空題", "負步進倒直角三角形外層邊界 (range(N, 0, -1))", 4, (),
         lambda g: (
             (True, "倒直角三角形負步進外層邊界填寫正確！")
             if ("range(N,0,-1)" in history_clean or "range(N, 0, -1)" in history_str)
             else (False, "請在 6-6-4 填空題填入 range(N, 0, -1)！")
         )),

        ("6-6-4", "練習題", "倒數字三角形數字 1 出現次數 (one_count = 1)", 4, ("one_count",),
         lambda g: (
             (True, "倒直角數字排版與數字 1 計數輸出正確！")
             if (g.get("one_count") == 1 or
                 (("one_count" in g or "one_count" in history_str) and
                  ("num_val == 1" in history_str or "num_val==1" in history_clean or "val == 1" in history_str or "val==1" in history_clean)))
             else (False, "請排版倒數字圖形並統計數字 1 出現次數為 1！")
         )),

        ("6-6-4", "挑戰題", "倒階梯連續數列總和 (total_val = 20)", 5, ("total_val",),
         lambda g: (
             (True, "倒階梯連續數列走訪與總和 (20) 驗證成功！")
             if (g.get("total_val") == 20 or
                 (("total_val" in g or "total_val" in history_str) and
                  ("20" in history_str or "total_val +=" in history_str)))
             else (False, "請排版每列由 1 起跑的倒階梯，N=4 時總和應為 20！")
         )),

        # ----------------------------------------------------------------------
        # 6-6-5 直角三角形系列（三）：靠右直角三角形（前置空白） (共 12 分)
        # ----------------------------------------------------------------------
        ("6-6-5", "填空題", "靠右直角三角形雙內迴圈 (N - r, r)", 4, (),
         lambda g: (
             (True, "前置空格 N - r 與星號 r 填寫正確！")
             if ("N-r" in history_clean or "N - r" in history_str) and
                ("range(r)" in history_clean or "range( r )" in history_str)
             else (False, "請在 6-6-5 填空題填入空格 N - r 與星號 r！")
         )),

        ("6-6-5", "練習題", "靠右倒直角三角形總空格數 (total_spaces = 3/6)", 4, ("total_spaces",),
         lambda g: (
             (True, "靠右倒直角三角形排版與總空格累加正確！")
             if (g.get("total_spaces") in [3, 6] or
                 (("total_spaces" in g or "total_spaces" in history_str) and
                  ("total_spaces +=" in history_str or "total_spaces+=" in history_clean)))
             else (False, "請排版靠右倒三角形並累加空格數至 total_spaces！")
         )),

        ("6-6-5", "挑戰題", "靠右數字直角三角形數字總和 (sum_all_digits = 20)", 4, ("sum_all_digits",),
         lambda g: (
             (True, "靠右對齊數字階梯排版與數字總和 (20) 成功！")
             if (g.get("sum_all_digits") == 20 or
                 (("sum_all_digits" in g or "sum_all_digits" in history_str) and
                  ("20" in history_str or "sum_all_digits +=" in history_str)))
             else (False, "請排版靠右數字階梯，N=4 時所有數字總和應為 20！")
         )),

        # ----------------------------------------------------------------------
        # 6-6-6 正金字塔與等腰三角形：奇數星號與對稱空格 (共 12 分)
        # ----------------------------------------------------------------------
        ("6-6-6", "填空題", "正金字塔空格與奇數星號公式 (N - i, 2 * i - 1)", 4, (),
         lambda g: (
             (True, "金字塔前置空格 N - i 與奇數星號 2*i - 1 填寫精確！")
             if ("N-i" in history_clean or "N - i" in history_str) and
                ("2*i-1" in history_clean or "2 * i - 1" in history_str)
             else (False, "請在 6-6-6 填空題填入空格 N - i 與奇數星號 2 * i - 1！")
         )),

        ("6-6-6", "練習題", "倒金字塔星號總數統計 (total_pyramid_stars)", 4, ("total_pyramid_stars",),
         lambda g: (
             (True, "倒金字塔排版與星號總數統計輸出正確！")
             if (("total_stars_pyramid" in g or "total_stars_pyramid" in history_str or "total_stars" in g) and
                 ("2 * i - 1" in history_str or "2*i-1" in history_clean))
             else (False, "請排版倒金字塔並統計星號總數！")
         )),

        ("6-6-6", "挑戰題", "迴文數字金字塔每層尖頂和 (peak_sum = 10)", 4, ("peak_sum",),
         lambda g: (
             (True, "迴文對稱數字金字塔與尖頂數字和 (10) 成功！")
             if (g.get("peak_sum") == 10 or
                 (("peak_sum" in g or "peak_sum" in history_str) and
                  ("10" in history_str or "peak_sum +=" in history_str)))
             else (False, "請排版迴文數字金字塔，尖頂 1+2+3+4 總和為 10！")
         )),

        # ----------------------------------------------------------------------
        # 6-6-7 菱形與沙漏形排版：對稱拼接模型 (共 12 分)
        # ----------------------------------------------------------------------
        ("6-6-7", "填空題", "菱形下半部倒數邊界 (range(N - 1, 0, -1))", 4, (),
         lambda g: (
             (True, "菱形下半部倒數邊界 range(N - 1, 0, -1) 填寫正確！")
             if ("range(N-1,0,-1)" in history_clean or "N - 1" in history_str and "-1" in history_str)
             else (False, "請在 6-6-7 填空題填入 N - 1、0 以及步進 -1！")
         )),

        ("6-6-7", "練習題", "計時沙漏形星號總數 (total_hourglass_stars = 17/31)", 4, ("total_hourglass_stars",),
         lambda g: (
             (True, "沙漏形上下拼接排版與星號總數輸出正確！")
             if (g.get("total_hourglass_stars") in [17, 31] or
                 (("total_hourglass_stars" in g or "total_hourglass_stars" in history_str) and
                  ("17" in history_str or "31" in history_str)))
             else (False, "請排版倒正金字塔拼接之沙漏，統計星號總數！")
         )),

        ("6-6-7", "挑戰題", "空心鑽石菱形邊框星號總數 (border_stars = 12)", 4, ("border_stars",),
         lambda g: (
             (True, "鏤空中間空心鑽石排版 (12 顆邊框星號) 成功！")
             if (g.get("border_stars") == 12 or
                 (("border_stars" in g or "border_stars" in history_str) and
                  ("12" in history_str or "border_stars +=" in history_str)))
             else (False, "請排版空心鑽石圖形，N=4 時邊框總星號應為 12 顆！")
         )),

        # ----------------------------------------------------------------------
        # 6-6-8 二維坐標條件判斷綜合應用 (共 12 分)
        # ----------------------------------------------------------------------
        ("6-6-8", "填空題", "棋盤交錯模除條件判斷 ((r + c) % 2 == 0)", 4, (),
         lambda g: (
             (True, "棋盤交錯奇偶判斷 (r + c) % 2 填寫正確！")
             if ("(r+c)%2==0" in history_clean or "% 2" in history_str)
             else (False, "請在 6-6-8 填空題填入取餘數運算子 2！")
         )),

        ("6-6-8", "練習題", "乘法方陣內部元素極值查找 (inner_max = 9/16)", 4, ("inner_max",),
         lambda g: (
             (True, "非邊框內部元素擂台極值查找輸出正確！")
             if (g.get("inner_max") in [9, 16] or
                 (("inner_max" in g or "inner_max" in history_str) and
                  ("1 < r < N" in history_str or "inner_max = val" in history_str)))
             else (False, "請排版乘法方陣並找出非邊框內部元素最大值！")
         )),

        ("6-6-8", "挑戰題", "中心曼哈頓距離總和 (total_dist_sum = 60)", 4, ("total_dist_sum",),
         lambda g: (
             (True, "中心曼哈頓距離漸變方陣總和 (60) 成功！")
             if (g.get("total_dist_sum") == 60 or
                 (("total_dist_sum" in g or "total_dist_sum" in history_str) and
                  ("abs(r - center)" in history_str or "60" in history_str)))
             else (False, "請計算 5x5 中心曼哈頓距離方陣之距離總和（60）！")
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
        badge = '🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通幾何圖形代數映射與星號排版演算法，對稱拼接與曼哈頓方陣游刃有餘！'
    elif total_score >= 80:
        badge = '🥈 卓越冒險者（銀牌徽章 🥈）—— 表現優異，直角三角形、金字塔與空心邊框控制嫻熟！'
    elif total_score >= 60:
        badge = '🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目微調空格或星號代數式！'
    else:
        badge = '🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 6-6：幾何圖形與星號排版演算法 —— 自動評分報告")
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
        "unit": "6-6",
        "unit_title": "幾何圖形與星號排版演算法",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_6_6.py",
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
auto_grade_unit_6_6()
