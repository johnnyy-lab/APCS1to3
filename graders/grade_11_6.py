# ==============================================================================
# 🧪 《PythAPCS123》單元 11-6：線性遞迴：呼叫堆疊展開與終止條件 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_11_6.py
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
NOTEBOOK_FILE = "PythAPCS123_11-6_linear_recursion_and_call_stack.ipynb"

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


def auto_grade_unit_11_6():
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
        # 11-6-1 遞迴第一步：認識函數呼叫自己 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-6-1", "填空題", "遞迴倒數記數 rec_count 與終止條件 if n == 0", 5, ("rec_count",),
         lambda g: (
             (True, "rec_count 遞迴倒數填空正確！")
             if (callable(g.get("rec_count"))) or
                ("def rec_count" in history_str and "rec_count(n - 1)" in history_str)
             else (False, "請定義 rec_count 並在 n == 0 時終止，其餘呼叫 rec_count(n - 1)！")
         )),

        ("11-6-1", "練習題", "發射倒數線性遞迴 countdown_launch(n)", 6, ("countdown_launch",),
         lambda g: (
             (True, "countdown_launch 線性遞迴實作正確！")
             if (callable(g.get("countdown_launch"))) or
                ("countdown_launch" in history_str and "發射" in history_str)
             else (False, "請定義 countdown_launch 遞迴倒數至 1 並在終止時輸出發射！")
         )),

        ("11-6-1", "挑戰題", "遞迴連續區間印出 rec_print_range(start, end)", 6, ("rec_print_range",),
         lambda g: (
             (True, "rec_print_range 區間遞迴實作正確！")
             if (callable(g.get("rec_print_range"))) or
                ("rec_print_range" in history_str)
             else (False, "請定義 rec_print_range 從 start 印至 end 遞迴推進！")
         )),

        # ----------------------------------------------------------------------
        # 11-6-2 呼叫堆疊 (Call Stack) 模型：前序與後序 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-6-2", "填空題", "對稱鏡像遞迴 mirror_box 與堆疊推入彈出", 5, ("mirror_box",),
         lambda g: (
             (True, "mirror_box 鏡像堆疊填空正確！")
             if (callable(g.get("mirror_box"))) or
                ("mirror_box" in history_str and "進盒" in history_str or "出盒" in history_str)
             else (False, "請在遞迴呼叫前後分別印出標記，觀察堆疊先進後出對稱性！")
         )),

        ("11-6-2", "練習題", "視覺化堆疊層級 trace visualize_stack(n)", 6, ("visualize_stack",),
         lambda g: (
             (True, "visualize_stack 堆疊追蹤實作正確！")
             if (callable(g.get("visualize_stack"))) or
                ("visualize_stack" in history_str and "Push" in history_str or "Pop" in history_str)
             else (False, "請定義 visualize_stack 顯示堆疊深度的進入與返回時序！")
         )),

        ("11-6-2", "挑戰題", "遞迴巢狀方框符號包裹 nested_boxes(size)", 6, ("nested_boxes",),
         lambda g: (
             (True, "nested_boxes 巢狀符號包裹正確！")
             if (callable(g.get("nested_boxes"))) or
                ("nested_boxes" in history_str and "[" in history_str)
             else (False, "請定義 nested_boxes 遞迴產出巢狀對稱括號或符號！")
         )),

        # ----------------------------------------------------------------------
        # 11-6-3 終止條件 (Base Case)：煞車皮機制 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-6-3", "填空題", "連續折半次數計算 count_halves 與煞車條件", 5, ("count_halves",),
         lambda g: (
             (True, "count_halves 煞車條件填空正確！")
             if (callable(g.get("count_halves")) and g.get("count_halves")(16) == 4) or
                ("count_halves" in history_str and "// 2" in history_str)
             else (False, "請定義 count_halves 在 n <= 1 時回傳 0，否則 1 + count_halves(n // 2)！")
         )),

        ("11-6-3", "練習題", "安全階梯減法遞迴 subtract_step(n, step)", 6, ("subtract_step",),
         lambda g: (
             (True, "subtract_step 減法遞迴正確！")
             if (callable(g.get("subtract_step"))) or
                ("subtract_step" in history_str and "step" in history_str)
             else (False, "請定義 subtract_step 每次扣除 step 直到 <= 0 停止！")
         )),

        ("11-6-3", "挑戰題", "純手工遞迴求餘數 rec_mod(a, b)", 6, ("rec_mod",),
         lambda g: (
             (True, "rec_mod 遞迴取餘數實作正確！")
             if (callable(g.get("rec_mod")) and g.get("rec_mod")(17, 5) == 2) or
                ("rec_mod" in history_str and "a < b" in history_str)
             else (False, "請實作 rec_mod：若 a < b 則回傳 a，否則回傳 rec_mod(a - b, b)！")
         )),

        # ----------------------------------------------------------------------
        # 11-6-4 線性遞迴累計：次方與數列 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-6-4", "填空題", "遞迴計算 2 的次方 power_of_two(n)", 5, ("ans", "power_of_two"),
         lambda g: (
             (True, "power_of_two 填空正確！")
             if (callable(g.get("power_of_two")) and g.get("power_of_two")(5) == 32) or
                (g.get("ans") == 32) or
                ("power_of_two(n - 1)" in history_str and "2 *" in history_str)
             else (False, "請實作 power_of_two：n == 0 回傳 1，其餘回傳 2 * power_of_two(n - 1)！")
         )),

        ("11-6-4", "練習題", "遞迴計算連續奇數和 sum_odd(n)", 6, ("sum_odd",),
         lambda g: (
             (True, "sum_odd 奇數累加遞迴正確！")
             if (callable(g.get("sum_odd")) and g.get("sum_odd")(4) == 16) or
                ("sum_odd" in history_str and "2 * n - 1" in history_str)
             else (False, "請定義 sum_odd 遞迴計算前 n 個奇數總和 (1 + 3 + ... + 2n-1)！")
         )),

        ("11-6-4", "挑戰題", "遞迴等比數列總和 geometric_series(a, r, n)", 6, ("geometric_series",),
         lambda g: (
             (True, "geometric_series 等比數列遞迴正確！")
             if (callable(g.get("geometric_series"))) or
                ("geometric_series" in history_str)
             else (False, "請實作 geometric_series(a, r, n) 遞迴計算首項 a 公比 r 前 n 項和！")
         )),

        # ----------------------------------------------------------------------
        # 11-6-5 串列與字串的線性遞迴：切片縮小 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-6-5", "填空題", "遞迴串列加總 rec_sum_list(arr) 與 arr[1:]", 5, ("rec_sum_list",),
         lambda g: (
             (True, "rec_sum_list 串列遞迴加總填空正確！")
             if (callable(g.get("rec_sum_list")) and g.get("rec_sum_list")([1, 2, 3, 4, 5]) == 15) or
                ("rec_sum_list(arr[1:])" in history_str or "arr[0] +" in history_str)
             else (False, "請在 rec_sum_list 使用 arr[0] + rec_sum_list(arr[1:]) 推進！")
         )),

        ("11-6-5", "練習題", "字元間插入連字號 insert_hyphens(s)", 6, ("insert_hyphens",),
         lambda g: (
             (True, "insert_hyphens 字串遞迴處理正確！")
             if (callable(g.get("insert_hyphens")) and g.get("insert_hyphens")("APCS") == "A-P-C-S") or
                ("insert_hyphens" in history_str and "'-'" in history_str)
             else (False, "請定義 insert_hyphens 遞迴在每對相鄰字元間插入 '-'！")
         )),

        ("11-6-5", "挑戰題", "遞迴母音字元清洗 remove_vowels(s)", 5, ("remove_vowels",),
         lambda g: (
             (True, "remove_vowels 遞迴母音清洗正確！")
             if (callable(g.get("remove_vowels")) and g.get("remove_vowels")("apple") == "ppl") or
                ("remove_vowels" in history_str and "aeiou" in history_str)
             else (False, "請實作 remove_vowels 遞迴去除字串中所有的英文母音字母！")
         )),

        # ----------------------------------------------------------------------
        # 11-6-6 遞迴深度限制與防爆防禦 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-6-6", "填空題", "安全深度下潛 safe_dive 與深度上限檢查", 5, ("safe_dive",),
         lambda g: (
             (True, "safe_dive 深度限制填空正確！")
             if (callable(g.get("safe_dive"))) or
                ("depth >= max_safe_depth" in history_str or "safe_dive" in history_str)
             else (False, "請在 safe_dive 內於達到上限時提早煞車，杜絕無限遞迴！")
         )),

        ("11-6-6", "練習題", "遞迴累加安全防禦器 safe_rec_sum(n, limit=500)", 6, ("safe_rec_sum",),
         lambda g: (
             (True, "safe_rec_sum 安全防禦器實作正確！")
             if (callable(g.get("safe_rec_sum")) and g.get("safe_rec_sum")(1000) == -1) or
                ("safe_rec_sum" in history_str and "limit" in history_str)
             else (False, "請定義 safe_rec_sum：當 n > limit 時提早攔截回傳 -1！")
         )),

        ("11-6-6", "挑戰題", "遞迴與迴圈空間效能實測對比 loop_sum 與 rec_sum", 5, (),
         lambda g: (
             (True, "遞迴迴圈對比實驗完成！")
             if ("loop_sum" in history_str and "rec_sum" in history_str) or
                ("RecursionError" in history_str or "sys.getrecursionlimit" in history_str)
             else (False, "請分別實作 loop_sum 與 rec_sum 並比較極限深度下的表現！")
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
    print(" 📊 《PythAPCS123》單元 11-6：線性遞迴：呼叫堆疊展開與終止條件 —— 自動評分報告")
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
        "unit": "11-6",
        "unit_title": "線性遞迴：呼叫堆疊展開與終止條件",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_11_6.py",
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
auto_grade_unit_11_6()
