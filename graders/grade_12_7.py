# ==============================================================================
# 🧪 《PythAPCS123》單元 12-7：二分搜尋法手刻演算法一：猜數字模型與精確匹配 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_12_7.py
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
import math
# 抑制 google_auth_httplib2 的 timeout 內部警告
logging.getLogger("google_auth_httplib2").setLevel(logging.ERROR)

# 確保輸出支援 UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

LOG_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyXv4s0qihj03Lg3oFop3HffQNYob-M9OxxJVPX04LxeBY22IvYcFh8v2hTZgWsX5InKQ/exec"
# 版次 token。Apps Script 用它確認這次送出的是現行契約。
GRADER_VERSION = "2026-10-19"
NOTEBOOK_FILE = "PythAPCS123_12-7_binary_search_exact_match.ipynb"

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

def check_q1(g, hist):
    ui = g.get("usr_inpt")
    if ui is None:
        return False, "請呼叫 usr_inpt.sort() 進行升序排序。"
    if (ui == [12, 34, 60, 78, 95]) or ("usr_inpt.sort()" in hist):
        return True, "太棒了！原地 sort() 成功賦予串列單調性，二分搜尋前提成立！"
    return False, "請呼叫 usr_inpt.sort() 進行升序排序。"

def check_q2(g, hist):
    is_sorted = g.get("is_sorted")
    nums_chk = g.get("ns_chck")
    if is_sorted is None and nums_chk is None:
        return False, "請檢驗 ns_chck 單調性，若未排序則進行修復排序。"
    if is_sorted is not None and isinstance(nums_chk, list) and nums_chk == sorted(nums_chk):
        return True, "完全正確！精準檢驗排序單調性並完成自動修復排序！"
    if "is_sorted" in hist and "ns_chck.sort()" in hist:
        return True, "檢驗邏輯正確，通過！"
    return False, "請檢驗 ns_chck 單調性，若未排序則進行修復排序。"

def check_q3(g, hist):
    mid_word = g.get("mid_word")
    if mid_word is None:
        return False, "請對 wrds127 排序並取得正中間單字 (應為 'grape')。"
    # wrds127 = ["orange", "apple", "banana", "watermelon", "grape"]
    # 排序後: ['apple', 'banana', 'grape', 'orange', 'watermelon'] -> mid_idx127 = 2, mid_word = 'grape'
    if mid_word == "grape" or ("wrds127.sort()" in hist and "len(wrds127) // 2" in hist):
        return True, "太厲害了！單字字典序排序後，正確鎖定正中間單字 'grape'！"
    return False, "請對 wrds127 排序並取得正中間單字 (應為 'grape')。"

def check_q4(g, hist):
    lft = g.get("lft")
    rght = g.get("rght")
    if lft is None and rght is None:
        return False, "請確認填入 lft = 0 與 len(srt_ns) - 1。"
    if (lft == 0 and rght == 5) or ("lft = 0" in hist and "len(srt_ns) - 1" in hist):
        return True, "完全正確！閉區間起點 0 與終點 len(srt_ns) - 1 初始化無誤！"
    return False, "請確認填入 lft = 0 與 len(srt_ns) - 1。"

def check_q5(g, hist):
    if g.get('srt_dt127') is None:
        return False, "請模擬第一回合區間並判斷下一步更新邊界。"
    if "mid127 = (l + r127) // 2" in hist and ("right = mid127 - 1" in hist or "left = mid127 + 1" in hist):
        return True, "精彩！準確模擬第一回合中間點數值與下一步縮小方向！"
    return False, "請模擬第一回合區間並判斷下一步更新邊界。"

def check_q6(g, hist):
    stps127 = g.get("stps127")
    if stps127 is None:
        return False, "請記錄搜尋收斂總回合數 (預期為 4 回合)。"
    # ns127 = list(range(10, 160, 10)) -> 15 個元素
    # tg13 = 75 (不在數列中)
    # len=15, 每次折半，步數通常為 4 次 (log2(15) ~ 3.9 -> 4)
    if stps127 == 4 or ("stps127 += 1" in hist and "while l <= r127" in hist):
        return True, "太強了！完整追蹤 15 筆資料收斂過程，精準確認 4 回合後退出！"
    return False, "請記錄搜尋收斂總回合數 (預期為 4 回合)。"

def check_q7(g, hist):
    mi = g.get("mid_index")
    if mi is None:
        return False, "請以 (crrn_lft + crrn_rght) // 2 計算中間索引。"
    # crrn_lft = 6, crrn_rght = 11 -> (6 + 11) // 2 = 8
    if mi == 8 or ("(crrn_lft + crrn_rght) // 2" in hist):
        return True, "完全正確！(6 + 11) // 2 = 8，整數除法掌握無誤！"
    return False, "請以 (crrn_lft + crrn_rght) // 2 計算中間索引。"

def check_q8(g, hist):
    mids = g.get("mids")
    if mids is None:
        return False, "請使用列表生成式計算各區間之中間索引。"
    # bounds = [(0, 10), (3, 7), (5, 6), (8, 8)] -> [5, 5, 5, 8]
    if mids == [5, 5, 5, 8] or ("(l + r127) // 2" in hist and "bounds" in hist):
        return True, "太棒了！列表生成式批次計算中間索引 [5, 5, 5, 8] 完全吻合！"
    return False, "請使用列表生成式計算各區間之中間索引。"

def check_q9(g, hist):
    lc = g.get("left_count")
    rc = g.get("rght_cnt")
    if lc is None and rc is None:
        return False, "請計算以 mid3 為界的左半與右半元素個數。"
    # N127 = 9, left=0, right=8, mid3=4 -> left_count: 4, rght_cnt: 4
    if (lc == 4 and rc == 4) or ("mid3 - left" in hist and "right - mid3" in hist):
        return True, "完美！精準計算 mid3 左右兩側對稱區間各自包含 4 個元素！"
    return False, "請計算以 mid3 為界的左半與右半元素個數。"

def check_q10(g, hist):
    if g.get('arr127') is None:
        return False, "請確認填入 while lft127 <= rght127、mid + 1 與 mid - 1。"
    if "while lft127 <= rght127" in hist and "mid + 1" in hist and "mid - 1" in hist:
        return True, "完全正確！閉區間三劍客 while <=、mid + 1、mid - 1 嚴格防禦死結！"
    return False, "請確認填入 while lft127 <= rght127、mid + 1 與 mid - 1。"

def check_q11(g, hist):
    fnd_idx = g.get("fnd_idx")
    if fnd_idx is None:
        return False, "請使用 while lft2 <= rght2: 在質數串列中搜尋 tg15。"
    if fnd_idx == 5 or ("while lft2 <= rght2" in hist and "prms[mid] == tg15" in hist):
        return True, "太棒了！質數二分搜尋實作完全成功，精準命中目標索引 5！"
    return False, "請使用 while lft2 <= rght2: 在質數串列中搜尋 tg15。"

def check_q12(g, hist):
    l = g.get("l")
    r127 = g.get("r127")
    if l is None and r127 is None:
        return False, "請驗證搜尋 25 退出時的 left 與 right 狀態。"
    # data = [10, 20, 30, 40], tg16 = 25
    # 25 介於 20(idx127 1) 與 30(idx127 2) 之間 -> 最終 left=2, right=1 (left == right + 1)
    if (l == 2 and r127 == 1) or ("l == r127 + 1" in hist):
        return True, "太精闢了！親身驗證退出時兩面盾牌交叉錯位（left == right + 1）的物理定律！"
    return False, "請驗證搜尋 25 退出時的 left 與 right 狀態。"

def check_q13(g, hist):
    mc = g.get("max_cmp")
    if mc is None:
        return False, "請使用 math.ceil(math.log2(n)) 計算比對次數上限。"
    # n = 1,000,000 -> ceil(log2(1000000)) = 20
    if mc == 20 or ("math.log2(data_scale)" in hist or "math.log2" in hist):
        return True, "完全正確！一百萬筆資料二分搜尋僅需 20 次比對即可定生死！"
    return False, "請使用 math.ceil(math.log2(n)) 計算比對次數上限。"

def check_q14(g, hist):
    saved = g.get("saved")
    if saved is None:
        return False, "請計算線性搜尋與二分搜尋比對次數的差額 saved。"
    # N49 = 1024 -> linear: 1024, bin: 10 -> saved: 1014
    if saved in [1014, 58] or ("linear_cnt - bin_cnt" in hist):
        return True, "精彩！震撼體驗二分搜尋相比線性搜尋節省了超過 1000 次比對！"
    return False, "請計算線性搜尋與二分搜尋比對次數的差額 saved。"

def check_q15(g, hist):
    qps = g.get("qrs_sec")
    if qps is None:
        return False, "請推算伺服器每秒可承受的二分查詢請求次數。"
    # N50 = 10,000,000 -> log2 = 24. 100000 // 24 = 4166 次
    if (qps is not None and 4000 <= qps <= 4500) or ("srv_cap // cmp_srch" in hist):
        return True, "太神了！一秒內輕鬆處理超過 4,000 次獨立使用者查詢，對數威力震撼體現！"
    return False, "請推算伺服器每秒可承受的二分查詢請求次數。"

def check_q16(g, hist):
    func = g.get("my_bsearch")
    if func is None:
        return False, "請完整默寫 my_bsearch 函數並正確回傳 -1。"
    if callable(func):
        try:
            if func([2, 4, 6, 8, 10], 8) == 3 and func([2, 4, 6, 8, 10], 5) == -1:
                return True, "滿分默寫！標準二分搜尋骨架測試通過，成功回傳正確索引與 -1！"
        except Exception:
            pass
    if "def my_bsearch" in hist and "return -1" in hist:
        return True, "骨架語法正確，通過！"
    return False, "請完整默寫 my_bsearch 函數並正確回傳 -1。"

def check_q17(g, hist):
    idx127 = g.get("idx127")
    if idx127 is None:
        return False, "請利用 binary_search 驗證 member_ids 中的 login_id。"
    if idx127 == 2 or ("binary_search(member_ids, login_id)" in hist):
        return True, "精彩！成功運用二分搜尋模組於會員登入驗證，定位會員序號 2！"
    return False, "請利用 binary_search 驗證 member_ids 中的 login_id。"

def check_q18(g, hist):
    intr127 = g.get("intr127")
    if intr127 is None:
        return False, "請以二分搜尋逐一檢驗轉帳名冊並收集黑名單帳號 [10050, 10900]。"
    # blck127 = [10001, 10050, 10200, 10550, 10900, 11000]
    # transfers = [10050, 10300, 10900, 12000]
    # 黑名單命中: [10050, 10900]
    if intr127 == [10050, 10900] or ("intr127.append" in hist and "binary_search" in hist):
        return True, "登峰造極！以對數級極速精準攔截黑名單危險帳號 [10050, 10900]！"
    return False, "請以二分搜尋逐一檢驗轉帳名冊並收集黑名單帳號 [10050, 10900]。"


def auto_grade_unit_12_7(env=None):
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

    # 取得 IPython 執行歷史（Colab 的 _ih 與 In 同源；本機測試可注入 _ih）
    input_history = env.get("_ih", env.get("In", []))
    history_str = "\n".join(str(x) for x in input_history) if isinstance(input_history, list) else ""
    history_clean = history_str.replace(" ", "")

    test_cases = [
        ('12-7-1', '填空題', '原地升序排序滿足二分前提', 6, ("usr_inpt",),
         lambda g: check_q1(g, history_str)),
        ('12-7-1', '練習題', '檢驗單調性與自動修復排序', 6, ("is_sorted", "ns_chck"),
         lambda g: check_q2(g, history_str)),
        ('12-7-1', '挑戰題', '單字字典序排序與正中間定位', 5, ("mid_word",),
         lambda g: check_q3(g, history_str)),
        ('12-7-2', '填空題', '雙指標初始邊界 lft 與 len - 1', 6, ("lft", "rght"),
         lambda g: check_q4(g, history_str)),
        ('12-7-2', '練習題', '模擬首回合區間與指針更新方向', 6, (),
         lambda g: check_q5(g, history_str)),
        ('12-7-2', '挑戰題', '追蹤無解收斂過程之總回合數', 5, ("stps127",),
         lambda g: check_q6(g, history_str)),
        ('12-7-3', '填空題', '整數除法計算中間索引 (l + r127) // 2', 6, ("mid_index",),
         lambda g: check_q7(g, history_str)),
        ('12-7-3', '練習題', '批次計算多組邊界之中間索引', 6, ("mids",),
         lambda g: check_q8(g, history_str)),
        ('12-7-3', '挑戰題', '驗證中間值左右兩側元素分佈規模', 5, ("left_count", "rght_cnt"),
         lambda g: check_q9(g, history_str)),
        ('12-7-4', '填空題', '閉區間 while 條件與 +1 / -1 跳躍', 6, (),
         lambda g: check_q10(g, history_str)),
        ('12-7-4', '練習題', '質數清單二分搜尋實作', 6, ("fnd_idx",),
         lambda g: check_q11(g, history_str)),
        ('12-7-4', '挑戰題', '驗證退出瞬間 left == right + 1 交叉', 5, ("l", "r127"),
         lambda g: check_q12(g, history_str)),
        ('12-7-5', '填空題', '以 math.log2 推算百萬資料比對次數', 6, ("max_cmp",),
         lambda g: check_q13(g, history_str)),
        ('12-7-5', '練習題', '線性比對與對數比對之節省差額', 5, ("saved",),
         lambda g: check_q14(g, history_str)),
        ('12-7-5', '挑戰題', '高負載伺服器二分搜尋查詢上限評估', 5, ("qrs_sec",),
         lambda g: check_q15(g, history_str)),
        ('12-7-6', '填空題', '默寫標準二分搜尋核心函數模板', 6, ("my_bsearch",),
         lambda g: check_q16(g, history_str)),
        ('12-7-6', '練習題', '會員登入序號精確二分匹配', 5, ("idx127",),
         lambda g: check_q17(g, history_str)),
        ('12-7-6', '挑戰題', '二分搜尋極速攔截黑名單交易帳號', 5, ("intr127",),
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
    print(" 📊 《PythAPCS123》單元 12-7：二分搜尋法手刻演算法一：猜數字模型與精確匹配 —— 自動評分報告")
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
        "unit": "12-7",
        "unit_title": "二分搜尋法手刻演算法一：猜數字模型與精確匹配",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_12_7.py",
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
auto_grade_unit_12_7()
