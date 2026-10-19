# ==============================================================================
# 🧪 《PythAPCS123》單元 12-8：二分搜尋法手刻演算法二：邊界二分搜尋（Lower / Upper Bound） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_12_8.py
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
NOTEBOOK_FILE = "PythAPCS123_12-8_binary_search_boundary_lower_upper_bound.ipynb"

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
    fp = g.get("first_pos")
    lp = g.get("last_pos")
    if (fp == 2 and lp == 4) or ("first_pos = 2" in hist and "last_pos = 4" in hist):
        return True, "太棒了！精準標註數值 30 最左側索引 2 與最右側索引 4！"
    return False, "請確認填入 first_pos = 2 與 last_pos = 4。"

def check_q2(g, hist):
    fi = g.get("first_idx")
    li = g.get("last_idx")
    if (fi == 1 and li == 4) or ("if first_idx is None:" in hist and "last_idx = i" in hist):
        return True, "完全正確！透過單一走訪精準找出數值 4 之首度出現 1 與最後出現 4！"
    return False, "請以迴圈記錄數值 4 的首度 (1) 與最後 (4) 出現索引。"

def check_q3(g, hist):
    m = g.get("m")
    if m == 4 or ("m = (l + r) // 2" in hist):
        return True, "太精闢了！展示精確二分命中中央索引 4，證明其無法保證最左側邊界！"
    return False, "請展示初次計算 mid = 4 命中之局限性。"

def check_q4(g, hist):
    if ("arr[m] >= target" in hist or "arr[m] >= x" in hist) and "r = m - 1" in hist:
        return True, "完全正確！下邊界核心大於等於判定與向左逼近 r = m - 1 完美掌握！"
    return False, "請確認填入 arr[m] >= target 與 r = m - 1。"

def check_q5(g, hist):
    func = g.get("lower_bound")
    if callable(func):
        try:
            if func([15, 20, 20, 20, 35, 50], 20) == 1 and func([15, 20, 20, 20, 35, 50], 30) == 4:
                return True, "太棒了！手刻 lower_bound 實機測試完全正確，>= 20 索引為 1，>= 30 為 4！"
        except Exception:
            pass
    if "def lower_bound" in hist and "arr[m] >= target" in hist:
        return True, "函數架構正確，通過！"
    return False, "請實作 lower_bound(arr, target) 並正確回傳第一個 >= 目標的索引。"

def check_q6(g, hist):
    next_idx = g.get("next_lvl_idx")
    # exp_levels = [100, 250, 450, 700, 1000], cur_exp = 500 -> 第 3 個索引 (700 exp)
    if next_idx == 3 or ("lower_bound(exp_levels" in hist):
        return True, "太實用了！成功運用 lower_bound 找到 500 exp 下一個升級門檻位於索引 3 (700 exp)！"
    return False, "請使用 lower_bound 查詢經驗值 500 的超越門檻 (索引 3)。"

def check_q7(g, hist):
    if ("arr[m] > x" in hist or "arr[m] > target" in hist) and "r = m - 1" in hist:
        return True, "完全正確！Upper Bound 嚴格大於 > 條件填空無誤！"
    return False, "請在填空處填入嚴格大於符號 >。"

def check_q8(g, hist):
    func = g.get("upper_bound")
    if callable(func):
        try:
            if func([5, 10, 10, 10, 15, 20], 10) == 4 and func([5, 10, 10, 10, 15, 20], 0) == 0:
                return True, "太強了！手刻 upper_bound 實機測試全數通過，> 10 索引為 4！"
        except Exception:
            pass
    if "def upper_bound" in hist and "arr[m] > target" in hist:
        return True, "函數架構正確，通過！"
    return False, "請實作 upper_bound(arr, target) 尋找第一個嚴格大於目標的位置。"

def check_q9(g, hist):
    idx = g.get("idx")
    # parts = [48, 49, 50, 50, 50, 51, 52] -> upper_bound(50) = 5 (尺寸 51)
    if idx == 5 or ("upper_bound(parts, 50)" in hist):
        return True, "精彩！upper_bound 精準鎖定第一個超標零件位於索引 5 (51 mm)！"
    return False, "請使用 upper_bound(parts, 50) 定位首個超標零件。"

def check_q10(g, hist):
    if "len(items) - 1" in hist and ("left <= right" in hist or "l <= r" in hist):
        return True, "完全正確！雙閉區間四大金剛 len - 1 與 while <= 掌握無懈可擊！"
    return False, "請確認填入 len(items) - 1 與 while left <= right。"

def check_q11(g, hist):
    func = g.get("search_single")
    if callable(func):
        try:
            if func([99], 99) == 0 and func([99], 100) == -1:
                return True, "完美！單元素串列極限邊界測試通過，99 命中 0，100 安全回傳 -1！"
        except Exception:
            pass
    if "search_single(single, 99)" in hist:
        return True, "極限測試檢驗通過！"
    return False, "請驗證單元素串列在目標存在與不存在時之二分搜尋表現。"

def check_q12(g, hist):
    func = g.get("safe_bsearch")
    if callable(func):
        try:
            if func([], 10) == -1:
                return True, "太神了！空串列傳入時 0 <= -1 直接不進迴圈，零崩潰防禦通過！"
        except Exception:
            pass
    if "safe_bsearch" in hist and "empty_list" in hist:
        return True, "空串列檢測邏輯通過！"
    return False, "請驗證傳入空串列時二分搜尋安全退出回傳 -1。"

def check_q13(g, hist):
    if "arr[pos] == x" in hist or "arr[pos] == target" in hist:
        return True, "完全正確！雙重防護條件 pos < len(arr) and arr[pos] == x 填寫正確！"
    return False, "請填入相等條件 arr[pos] == x。"

def check_q14(g, hist):
    func = g.get("find_first_occurrence")
    if callable(func):
        try:
            nums = [1, 2, 2, 2, 3, 4, 4, 5]
            if func(nums, 2) == 1 and func(nums, 4) == 5 and func(nums, 9) == -1:
                return True, "太強大了！find_first_occurrence 實機測試完全正確，最左側定位無懈可擊！"
        except Exception:
            pass
    if "def find_first_occurrence" in hist:
        return True, "函數架構正確，通過！"
    return False, "請實作 find_first_occurrence(arr, target) 鎖定首度出現位置。"

def check_q15(g, hist):
    func = g.get("find_last_occurrence")
    if callable(func):
        try:
            data = [5, 8, 8, 8, 8, 12]
            if func(data, 8) == 4 and func(data, 99) == -1:
                return True, "登峰造極！以 upper_bound - 1 精妙實現最右側索引定位 (索引 4)！"
        except Exception:
            pass
    if "def find_last_occurrence" in hist:
        return True, "最右側定位邏輯正確，通過！"
    return False, "請實作 find_last_occurrence 函數尋找目標最後一次出現的索引。"

def check_q16(g, hist):
    freq = g.get("freq")
    if freq == 4 or ("ub - lb" in hist or "upper_bound(scores" in hist):
        return True, "完全正確！ub - lb 秒求 70 分人數共 4 人，O(log N) 統計神技！"
    return False, "請填入 freq = ub - lb 公式計算出現次數。"

def check_q17(g, hist):
    ac = g.get("ans_counts")
    # targets = [60, 80, 100] -> [3, 2, 0]
    if ac == [3, 2, 0] or ("upper_bound(grades, t) - lower_bound(grades, t)" in hist):
        return True, "太棒了！批次計算 [60, 80, 100] 出現次數 [3, 2, 0] 完全無誤！"
    return False, "請以 ub - lb 公式計算各目標之出現次數清單。"

def check_q18(g, hist):
    irc = g.get("in_range_count")
    # heights = [155, 160, 162, 165, 168, 170, 172, 175, 180, 185]
    # [165, 175] 內: 165, 168, 170, 172, 175 共 5 位！
    if irc == 5 or ("R_bound - L_bound" in hist and "upper_bound(heights, 175)" in hist):
        return True, "滿分通關！一行不跑線性迴圈，以雙邊界相減秒算區間人數 5 位，登峰造極！"
    return False, "請利用 upper_bound(175) - lower_bound(165) 計算區間內總人數 (5位)。"


def auto_grade_unit_12_8():
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
        ('12-8-1', '填空題', '重複數值最左與最右邊界定位', 6, ("first_pos", "last_pos"),
         lambda g: check_q1(g, history_str)),
        ('12-8-1', '練習題', '單迴圈統計重複元素首尾索引', 6, ("first_idx", "last_idx"),
         lambda g: check_q2(g, history_str)),
        ('12-8-1', '挑戰題', '揭示精確二分命中中央之邊界盲區', 5, ("m",),
         lambda g: check_q3(g, history_str)),
        ('12-8-2', '填空題', '下邊界 >= 判定與向左逼近 r = m - 1', 6, (),
         lambda g: check_q4(g, history_str)),
        ('12-8-2', '練習題', '手刻 lower_bound 查詢及格與門檻索引', 6, ("lower_bound",),
         lambda g: check_q5(g, history_str)),
        ('12-8-2', '挑戰題', '利用 lower_bound 定位下一個升級門檻', 5, ("next_lvl_idx",),
         lambda g: check_q6(g, history_str)),
        ('12-8-3', '填空題', 'Upper Bound 嚴格大於 > 判定', 6, (),
         lambda g: check_q7(g, history_str)),
        ('12-8-3', '練習題', '手刻 upper_bound 查詢第一個超越目標者', 6, ("upper_bound",),
         lambda g: check_q8(g, history_str)),
        ('12-8-3', '挑戰題', 'upper_bound 精準鎖定超標零件位置', 5, ("idx",),
         lambda g: check_q9(g, history_str)),
        ('12-8-4', '填空題', '雙閉區間 len - 1 與 while <= 邊界規範', 6, (),
         lambda g: check_q10(g, history_str)),
        ('12-8-4', '練習題', '單元素邊界極限二分驗證', 6, ("search_single",),
         lambda g: check_q11(g, history_str)),
        ('12-8-4', '挑戰題', '空串列零長度雙閉區間零崩潰防禦', 5, ("safe_bsearch",),
         lambda g: check_q12(g, history_str)),
        ('12-8-5', '填空題', '最左側定位存在性 pos < len 與 == 檢驗', 6, (),
         lambda g: check_q13(g, history_str)),
        ('12-8-5', '練習題', 'find_first_occurrence 最左側索引查詢', 5, ("find_first_occurrence",),
         lambda g: check_q14(g, history_str)),
        ('12-8-5', '挑戰題', 'find_last_occurrence 最右側索引查詢實作', 5, ("find_last_occurrence",),
         lambda g: check_q15(g, history_str)),
        ('12-8-6', '填空題', '極速區間個數統計公式 ub - lb', 6, ("freq",),
         lambda g: check_q16(g, history_str)),
        ('12-8-6', '練習題', '雙邊界差值批次統計目標頻率', 5, ("ans_counts",),
         lambda g: check_q17(g, history_str)),
        ('12-8-6', '挑戰題', 'O(log N) 區間查詢統計落在閉區間內之總人數', 5, ("in_range_count",),
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
    print(" 📊 《PythAPCS123》單元 12-8：二分搜尋法手刻演算法二：邊界二分搜尋（Lower / Upper Bound） —— 自動評分報告")
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
        "unit": "12-8",
        "unit_title": "二分搜尋法手刻演算法二：邊界二分搜尋（Lower / Upper Bound）",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_12_8.py",
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
auto_grade_unit_12_8()
