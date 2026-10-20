# ==============================================================================
# 🧪 《PythAPCS123》單元 11-7：樹狀分支遞迴與數論演算法 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_11_7.py
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
NOTEBOOK_FILE = "PythAPCS123_11-7_tree_recursion_and_number_theory.ipynb"

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


def auto_grade_unit_11_7(env=None):
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
        # 11-7-1 雙分支遞迴：一分二的展開樹 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-7-1", "填空題", "二元樹葉節點計數 count_leaves(depth)", 5, ("count_leaves",),
         lambda g: (
             (True, "count_leaves 雙分支填空正確！")
             if (callable(g.get("count_leaves")) and g.get("count_leaves")(3) == 8) or
                ("2 * count_leaves" in history_str or "count_leaves(depth - 1) + count_leaves" in history_str)
             else (False, "請完成 count_leaves：depth == 0 回傳 1，否則分支呼叫兩側子樹！")
         )),

        ("11-7-1", "練習題", "雙分支印出符號樹 branch_shapes(n)", 6, ("branch_shapes",),
         lambda g: (
             (True, "branch_shapes 符號樹實作正確！")
             if (callable(g.get("branch_shapes"))) or
                ("branch_shapes" in history_str)
             else (False, "請定義 branch_shapes 展開雙分支結構並印出分支型態！")
         )),

        ("11-7-1", "挑戰題", "雙分支金幣累加樹 tree_coins(level)", 6, ("tree_coins",),
         lambda g: (
             (True, "tree_coins 金幣累加樹正確！")
             if (callable(g.get("tree_coins")) and g.get("tree_coins")(3) == 7) or
                ("tree_coins" in history_str and "2 *" in history_str)
             else (False, "請實作 tree_coins：level == 1 回傳 1，其餘回傳 1 + 2 * tree_coins(level - 1)！")
         )),

        # ----------------------------------------------------------------------
        # 11-7-2 經典費氏數列與爬樓梯 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-7-2", "填空題", "經典費氏數列 get_fib(n) 雙遞迴呼叫", 5, ("fib_val", "get_fib"),
         lambda g: (
             (True, "get_fib 費氏數列填空正確！")
             if (callable(g.get("get_fib")) and g.get("get_fib")(6) == 8) or
                (g.get("fib_val") == 8) or
                ("get_fib(n - 1) + get_fib(n - 2)" in history_str)
             else (False, "請在 get_fib 填入 get_fib(n - 1) + get_fib(n - 2)！")
         )),

        ("11-7-2", "練習題", "三分支變形數列 trib(n)", 6, ("trib",),
         lambda g: (
             (True, "trib 三分支變形數列實作正確！")
             if (callable(g.get("trib")) and g.get("trib")(4) == 7) or
                ("trib" in history_str and "trib(n - 1) + trib(n - 2) + trib(n - 3)" in history_str)
             else (False, "請定義 trib 遞迴加總前三項 trib(n-1) + trib(n-2) + trib(n-3)！")
         )),

        ("11-7-2", "挑戰題", "爬樓梯問題遞迴解 count_stair_ways(n)", 6, ("count_stair_ways",),
         lambda g: (
             (True, "count_stair_ways 爬樓梯遞迴正確！")
             if (callable(g.get("count_stair_ways")) and g.get("count_stair_ways")(4) == 5) or
                ("count_stair_ways" in history_str)
             else (False, "請定義 count_stair_ways：n == 1 回傳 1，n == 2 回傳 2，其餘兩項相加！")
         )),

        # ----------------------------------------------------------------------
        # 11-7-3 重疊子問題與記憶化查表 Memoization (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-7-3", "填空題", "記憶化查表消除重複計算 memo_fib(n, memo)", 5, ("memo_fib",),
         lambda g: (
             (True, "memo_fib 記憶化填空正確！")
             if (callable(g.get("memo_fib"))) or
                ("if n in memo:" in history_str or "memo[n] = " in history_str)
             else (False, "請在 memo_fib 檢查若 n in memo 則直接回傳，否則算完存入 memo！")
         )),

        ("11-7-3", "練習題", "統計特定數值被重複計算次數 count_target_calls", 6, ("count_target_calls",),
         lambda g: (
             (True, "count_target_calls 重複呼叫統計正確！")
             if (callable(g.get("count_target_calls"))) or
                ("count_target_calls" in history_str and "target" in history_str)
             else (False, "請定義 count_target_calls 統計指定值在遞迴樹中出現的次數！")
         )),

        ("11-7-3", "挑戰題", "極限對抗：樸素費氏 vs 記憶化查表效能評比", 6, (),
         lambda g: (
             (True, "記憶化極限對抗實驗完成！")
             if ("memo" in history_str and "fib" in history_str) or
                ("time" in history_str or "call_count" in history_str)
             else (False, "請比較 slow_fib 與 memo_fib 計算大數時的呼叫次數與速度差異！")
         )),

        # ----------------------------------------------------------------------
        # 11-7-4 歐幾里得輾轉相除法 GCD (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-7-4", "填空題", "輾轉相除法求最大公因數 fast_gcd(a, b)", 5, ("fast_gcd",),
         lambda g: (
             (True, "fast_gcd 輾轉相除填空正確！")
             if (callable(g.get("fast_gcd")) and g.get("fast_gcd")(48, 18) == 6) or
                ("fast_gcd(b, a % b)" in history_str)
             else (False, "請在 fast_gcd 填入 fast_gcd(b, a % b) 遞迴求公因數！")
         )),

        ("11-7-4", "練習題", "分數約分化簡器 simplify_fraction(num, den)", 6, ("simplify_fraction",),
         lambda g: (
             (True, "simplify_fraction 分數約分實作正確！")
             if (callable(g.get("simplify_fraction")) and g.get("simplify_fraction")(12, 18) == (2, 3)) or
                ("simplify_fraction" in history_str and "// g" in history_str)
             else (False, "請使用 gcd 求出最大公因數 g 並回傳 (num // g, den // g)！")
         )),

        ("11-7-4", "挑戰題", "三個整數的最大公因數 gcd_three(a, b, c)", 6, ("gcd_three",),
         lambda g: (
             (True, "gcd_three 三數最大公因數正確！")
             if (callable(g.get("gcd_three")) and g.get("gcd_three")(24, 36, 60) == 12) or
                ("gcd_three" in history_str and "fast_gcd" in history_str)
             else (False, "請運用結合律實作 gcd_three(a, b, c) = gcd(gcd(a, b), c)！")
         )),

        # ----------------------------------------------------------------------
        # 11-7-5 快速冪運算遞迴版 (Fast Power) (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-7-5", "填空題", "遞迴快速冪折半平方 rec_pow(base, exp)", 5, ("rec_pow",),
         lambda g: (
             (True, "rec_pow 快速冪填空正確！")
             if (callable(g.get("rec_pow")) and g.get("rec_pow")(2, 10) == 1024) or
                ("rec_pow(base, exp // 2)" in history_str and "half * half" in history_str)
             else (False, "請在 rec_pow 計算 half = rec_pow(base, exp // 2) 並依奇偶平方！")
         )),

        ("11-7-5", "練習題", "取模快速冪運算 modular_pow(base, exp, mod)", 6, ("modular_pow",),
         lambda g: (
             (True, "modular_pow 取模快速冪正確！")
             if (callable(g.get("modular_pow")) and g.get("modular_pow")(2, 10, 1000) == 24) or
                ("modular_pow" in history_str and "% mod" in history_str)
             else (False, "請定義 modular_pow 在每次乘法後皆 % mod，防止大數溢位！")
         )),

        ("11-7-5", "挑戰題", "快速冪與樸素累乘運算次數與耗時對比", 5, (),
         lambda g: (
             (True, "快速冪對比實驗挑戰成功！")
             if ("rec_pow" in history_str or "power" in history_str) and ("//" in history_str or "time" in history_str)
             else (False, "請對比 2^100 在迴圈 100 次乘法 vs 快速冪 7 次乘法之巨大落差！")
         )),

        # ----------------------------------------------------------------------
        # 11-7-6 遞迴與迴圈選型思維 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-7-6", "填空題", "平方和選型對比 square_sum_loop 與 square_sum_rec", 5, ("square_sum_loop", "square_sum_rec"),
         lambda g: (
             (True, "平方和雙模式選型填空正確！")
             if (callable(g.get("square_sum_loop")) and callable(g.get("square_sum_rec"))) or
                ("square_sum_loop" in history_str and "square_sum_rec" in history_str)
             else (False, "請分別完成迴圈版與遞迴版平方和函數實作！")
         )),

        ("11-7-6", "練習題", "二分折半步數計算器 count_steps_loop 與 count_steps_rec", 6, ("count_steps_loop", "count_steps_rec"),
         lambda g: (
             (True, "折半查詢步數計算實作正確！")
             if (callable(g.get("count_steps_loop")) or callable(g.get("count_steps_rec"))) or
                ("count_steps" in history_str and "// 2" in history_str)
             else (False, "請實作折半次數計算器，計算長度 N 降至 1 的次數！")
         )),

        ("11-7-6", "挑戰題", "演算法選型診斷器 algorithm_advisor", 5, ("algorithm_advisor",),
         lambda g: (
             (True, "algorithm_advisor 選型診斷器正確！")
             if (callable(g.get("algorithm_advisor"))) or
                ("algorithm_advisor" in history_str and "RECURSION" in history_str or "LOOP" in history_str)
             else (False, "請定義 algorithm_advisor 依問題類型與資料規模給出適當演算法建議！")
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
        badge = '🏆 完美滿分！你已經徹底攻克自訂函數與作用域核心技術，具備 APCS 實戰高手水準！'
    elif total_score >= 80:
        badge = '🌟 優秀！模組化概念與函數傳參掌握非常扎實，稍微細心檢查即可登峰造極！'
    elif total_score >= 60:
        badge = '👍 及格！基本函數已建立，建議複習未通過的題目加強熟悉度！'
    else:
        badge = '💪 請再接再厲！建議回到上方微型階梯逐題操作並執行程式碼！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 11-7：樹狀分支遞迴與數論演算法 —— 自動評分報告")
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
        "unit": "11-7",
        "unit_title": "樹狀分支遞迴與數論演算法",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_11_7.py",
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
auto_grade_unit_11_7()
