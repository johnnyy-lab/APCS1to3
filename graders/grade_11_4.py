# ==============================================================================
# 🧪 《PythAPCS123》單元 11-4：變數作用域：區域變數與同名遮蔽 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_11_4.py
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
NOTEBOOK_FILE = "PythAPCS123_11-4_variable_scope_local_and_shadowing.ipynb"

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


def auto_grade_unit_11_4(env=None):
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
        # 11-4-1 區域作用域 (Local Scope) 獨立王國 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-4-1", "填空題", "三角形面積區域變數封裝 get_triangle_area(b, h)", 5, ("result_area", "get_triangle_area"),
         lambda g: (
             (True, "get_triangle_area 區域變數填空正確！")
             if (callable(g.get("get_triangle_area")) and g.get("get_triangle_area")(10, 6) == 30.0) or
                (g.get("result_area") == 30.0) or
                ("b * h / 2" in history_str)
             else (False, "請在 get_triangle_area 內定義區域變數計算面積並 return！")
         )),

        ("11-4-1", "練習題", "金額格式化區域變數封裝 format_currency(amount)", 6, ("format_currency",),
         lambda g: (
             (True, "format_currency 金額格式化實作正確！")
             if (callable(g.get("format_currency")) and
                 g.get("format_currency")(1000).startswith("$") and
                 g.get("format_currency")(2500000).startswith("$")) or
                ("format_currency" in history_str and "formatted_str" in history_str)
             else (False, "請定義 format_currency 在區域變數中格式化金額並回傳！")
         )),

        ("11-4-1", "挑戰題", "多步驟密碼加密區域變數封裝 encode_pin(pin_code)", 6, ("encode_pin",),
         lambda g: (
             (True, "encode_pin 多步驟密碼加密實作正確！")
             if (callable(g.get("encode_pin")) and
                 g.get("encode_pin")("1234") == "5432") or
                ("encode_pin" in history_str and "temp_reversed" in history_str)
             else (False, "請定義 encode_pin 透過區域變數反轉字串並位移數值回傳！")
         )),

        # ----------------------------------------------------------------------
        # 11-4-2 區域變數生命週期：呼叫誕生、結束消亡 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-4-2", "填空題", "問候訊息生命週期驗證 greet_guest 與 msg 釋放", 5, ("greet_guest",),
         lambda g: (
             (True, "greet_guest 生命週期填空正確！")
             if (callable(g.get("greet_guest"))) or
                ("greet_guest" in history_str and "msg1" in history_str)
             else (False, "請呼叫 greet_guest 驗證其內部區域變數在函數結束後不殘留！")
         )),

        ("11-4-2", "練習題", "購物車小計區域變數生命週期 calc_cart_total(prices)", 6, ("calc_cart_total",),
         lambda g: (
             (True, "calc_cart_total 購物車小計實作正確！")
             if (callable(g.get("calc_cart_total"))) or
                ("calc_cart_total" in history_str and "subtotal" in history_str)
             else (False, "請定義 calc_cart_total 以區域變數 subtotal 累加並回傳總額！")
         )),

        ("11-4-2", "挑戰題", "區域變數外部不可見之 NameError 邊界驗證", 6, (),
         lambda g: (
             (True, "NameError 生命週期邊界驗證正確！")
             if ("try:" in history_str and "except NameError" in history_str) or
                ("NameError" in history_str and "temp_list" in history_str)
             else (False, "請使用 try-except NameError 驗證區域變數在外部無法被存取！")
         )),

        # ----------------------------------------------------------------------
        # 11-4-3 變數遮蔽 (Shadowing) 與就近原則 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-4-3", "填空題", "免稅商店同名遮蔽 tax_free_shop 與 tax_rate", 5, ("tax_free_shop",),
         lambda g: (
             (True, "tax_free_shop 同名遮蔽填空正確！")
             if (callable(g.get("tax_free_shop"))) or
                ("tax_rate = 0.0" in history_str or "tax_rate = 0" in history_str)
             else (False, "請在 tax_free_shop 內宣告區域 tax_rate = 0.0 遮蔽外部稅率！")
         )),

        ("11-4-3", "練習題", "同名區域變數遮蔽計算 calc_group_score(base_score, bonus)", 6, ("calc_group_score",),
         lambda g: (
             (True, "calc_group_score 同名區域變數遮蔽實作正確！")
             if (callable(g.get("calc_group_score")) and
                 g.get("calc_group_score")(60, 25) == 85) or
                ("calc_group_score" in history_str and "score =" in history_str)
             else (False, "請定義 calc_group_score 宣告同名區域變數 score 並回傳！")
         )),

        ("11-4-3", "挑戰題", "全域、區域與參數同名遮蔽就近原則驗證", 6, (),
         lambda g: (
             (True, "就近原則遮蔽驗證正確！")
             if (("scope_tag" in history_str or "val" in history_str) and "shadow" in history_str) or
                ("shadow" in history_str or "scope_tag = " in history_str or "val = 10" in history_str)
             else (False, "請設計範例驗證同名變數依據就近原則優先採用區域變數！")
         )),

        # ----------------------------------------------------------------------
        # 11-4-4 函數內部「唯讀」存取全域變數 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-4-4", "填空題", "及格門檻唯讀全域變數 check_pass 與 PASS_STANDARD", 5, ("check_pass",),
         lambda g: (
             (True, "check_pass 唯讀全域填空正確！")
             if (callable(g.get("check_pass"))) or
                ("PASS_STANDARD" in history_str)
             else (False, "請在 check_pass 內直接讀取全域常數 PASS_STANDARD 進行比較！")
         )),

        ("11-4-4", "練習題", "匯率轉換唯讀全域常數 exchange_to_twd(usd_amount)", 6, ("exchange_to_twd",),
         lambda g: (
             (True, "exchange_to_twd 唯讀全域常數轉換正確！")
             if (callable(g.get("exchange_to_twd")) and
                 g.get("exchange_to_twd")(100) == 3200) or
                ("exchange_to_twd" in history_str and "USD_TO_TWD" in history_str)
             else (False, "請定義 exchange_to_twd 唯讀存取 USD_TO_TWD 並回傳整數金額！")
         )),

        ("11-4-4", "挑戰題", "唯讀全域方向向量走訪 get_neighbors(r, c)", 6, ("get_neighbors",),
         lambda g: (
             (True, "get_neighbors 唯讀存取方向常數正確！")
             if (callable(g.get("get_neighbors")) and
                 len(g.get("get_neighbors")(0, 0)) == 4) or
                ("get_neighbors" in history_str and "DIRS" in history_str)
             else (False, "請定義 get_neighbors 走訪全域常數 DIRS 回傳相鄰座標！")
         )),

        # ----------------------------------------------------------------------
        # 11-4-5 UnboundLocalError 經典報錯陷阱 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-4-5", "填空題", "點數累計未宣告 global 引發 UnboundLocalError 剖析", 5, (),
         lambda g: (
             (True, "UnboundLocalError 陷阱分析填空正確！")
             if ("UnboundLocalError" in history_str) or
                ("accumulate_points" in history_str)
             else (False, "請剖析 accumulate_points 內部 += 賦值為何被視為未初始化區域變數！")
         )),

        ("11-4-5", "練習題", "日誌追加純函數重構 append_log(current_log, new_msg)", 6, ("append_log",),
         lambda g: (
             (True, "append_log 日誌追加純函數實作正確！")
             if (callable(g.get("append_log")) and
                 g.get("append_log")("", "Start") == "Start" and
                 g.get("append_log")("Start", "Run") == "Start -> Run") or
                ("append_log" in history_str and "current_log" in history_str)
             else (False, "請定義 append_log 以參數進、return 出安全組裝日誌！")
         )),

        ("11-4-5", "挑戰題", "修復 UnboundLocalError 之兩種正解方案實作", 5, (),
         lambda g: (
             (True, "修復 UnboundLocalError 方案實作正確！")
             if ("global" in history_str or "return" in history_str) and ("UnboundLocalError" in history_str or "fix" in history_str)
             else (False, "請以 (1) 宣告 global 或 (2) 透過參數傳入 return 傳出修復報錯！")
         )),

        # ----------------------------------------------------------------------
        # 11-4-6 純函數設計原則：依賴參數與回傳 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-4-6", "填空題", "矩形周長純函數重構 calc_perimeter(w, h)", 5, ("rect1_p", "calc_perimeter"),
         lambda g: (
             (True, "calc_perimeter 純函數填空正確！")
             if (callable(g.get("calc_perimeter")) and g.get("calc_perimeter")(5, 3) == 16) or
                (g.get("rect1_p") == 16) or
                ("return (w + h) * 2" in history_str or "return 2 * (w + h)" in history_str)
             else (False, "請在 calc_perimeter 透過傳入的 w, h 計算周長並回傳！")
         )),

        ("11-4-6", "練習題", "曼哈頓距離純函數 manhattan_distance(p1, p2)", 6, ("manhattan_distance",),
         lambda g: (
             (True, "manhattan_distance 曼哈頓距離純函數正確！")
             if (callable(g.get("manhattan_distance")) and
                 g.get("manhattan_distance")((0, 0), (3, 4)) == 7) or
                ("manhattan_distance" in history_str and "abs(" in history_str)
             else (False, "請定義無副作用純函數 manhattan_distance(p1, p2) 回傳整數距離！")
         )),

        ("11-4-6", "挑戰題", "重構依賴全域的髒代碼為無副作用純函數", 5, (),
         lambda g: (
             (True, "純函數重構挑戰成功！")
             if ("pure" in history_str or "def " in history_str) and ("return" in history_str)
             else (False, "請將依賴全域狀態的邏輯改寫為獨立可測試的純函數！")
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
    print(" 📊 《PythAPCS123》單元 11-4：變數作用域：區域變數與同名遮蔽 —— 自動評分報告")
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
        "unit": "11-4",
        "unit_title": "變數作用域：區域變數與同名遮蔽",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_11_4.py",
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
auto_grade_unit_11_4()
