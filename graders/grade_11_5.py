# ==============================================================================
# 🧪 《PythAPCS123》單元 11-5：全域變數在 APCS 競賽中的使用準則與除錯防禦 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_11_5.py
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
NOTEBOOK_FILE = "PythAPCS123_11-5_global_variable_and_debugging.ipynb"

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


def auto_grade_unit_11_5(env=None):
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
        # 11-5-1 global 關鍵字在函數內改寫全域變數 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-5-1", "填空題", "計程車里程累計 add_mileage 與 global fare", 5, ("add_mileage",),
         lambda g: (
             (True, "add_mileage global 關鍵字填空正確！")
             if (callable(g.get("add_mileage"))) or
                ("global fare" in history_str)
             else (False, "請在 add_mileage 內加入 global fare 以便修改全域車資變數！")
         )),

        ("11-5-1", "練習題", "網站點擊計數器 record_clicks 與 global total_clicks", 6, ("record_clicks",),
         lambda g: (
             (True, "click_counter 全域計數實作正確！")
             if (callable(g.get("record_clicks"))) or
                ("record_clicks" in history_str and "total_clicks" in history_str)
             else (False, "請定義 record_clicks 使用 global total_clicks 每次累加！")
         )),

        ("11-5-1", "挑戰題", "護盾能量扣減 take_damage(damage)", 6, ("take_damage",),
         lambda g: (
             (True, "modify_shield_energy 全域能量更新正確！")
             if (callable(g.get("take_damage"))) or
                ("take_damage" in history_str and "shield_energy" in history_str)
             else (False, "請使用 global shield_energy 實作能量安全扣減！")
         )),

        # ----------------------------------------------------------------------
        # 11-5-2 APCS 場景一：全域最佳解累計計數器 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-5-2", "填空題", "跳高冠軍紀錄 record_jump 與 global highest_jump", 5, ("record_jump",),
         lambda g: (
             (True, "record_jump 最佳解填空正確！")
             if (callable(g.get("record_jump"))) or
                ("global highest_jump" in history_str and "max(" in history_str)
             else (False, "請在 record_jump 內使用 global highest_jump 維護全域最高紀錄！")
         )),

        ("11-5-2", "練習題", "最低報價評估器 submit_quote(cost)", 6, ("submit_quote",),
         lambda g: (
             (True, "update_min_cost 最小成本維護正確！")
             if (callable(g.get("submit_quote"))) or
                ("submit_quote" in history_str and "min_cost" in history_str)
             else (False, "請定義 submit_quote 以 min_cost = min(min_cost, cost) 更新全域解！")
         )),

        ("11-5-2", "挑戰題", "全域極端氣溫監控 record_temperature(temp)", 6, ("record_temperature",),
         lambda g: (
             (True, "氣溫極值雙指標追蹤實作正確！")
             if (callable(g.get("record_temperature"))) or
                ("record_temperature" in history_str and "max_temp" in history_str and "min_temp" in history_str)
             else (False, "請同時維護 global max_temp, min_temp 兩項全域極值指標！")
         )),

        # ----------------------------------------------------------------------
        # 11-5-3 APCS 場景二：大型地圖全域共享存取 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-5-3", "填空題", "網格障礙物計數 count_adjacent_walls 與全域 board", 5, ("count_adjacent_walls",),
         lambda g: (
             (True, "count_adjacent_walls 全域網格讀取填空正確！")
             if (callable(g.get("count_adjacent_walls"))) or
                ("board[nr][nc]" in history_str or "count_adjacent_walls" in history_str)
             else (False, "請在 count_adjacent_walls 直接唯讀存取全域二維地圖 board！")
         )),

        ("11-5-3", "練習題", "全域路徑總分計算器 score_grid 累加", 6, (),
         lambda g: (
             (True, "query_matrix_sum 全域矩陣查詢正確！")
             if ("score_grid" in history_str and "path" in history_str) or
                ("score_grid" in history_str and "+=" in history_str)
             else (False, "請直接走訪全域 score_grid 矩陣並累加路徑總分！")
         )),

        ("11-5-3", "挑戰題", "全域網格高低起伏探測 find_local_peaks()", 6, ("find_local_peaks",),
         lambda g: (
             (True, "global_flood_fill 全域網格染色實作正確！")
             if (callable(g.get("find_local_peaks"))) or
                ("find_local_peaks" in history_str and "elevation_map" in history_str)
             else (False, "請走訪全域地形矩陣 elevation_map 找出區域極值點！")
         )),

        # ----------------------------------------------------------------------
        # 11-5-4 可變物件免 global 原理 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("11-5-4", "填空題", "佇列原地追加 add_job 免宣告 global 原理", 5, ("add_job",),
         lambda g: (
             (True, "add_job 免 global 原地修改填空正確！")
             if (callable(g.get("add_job"))) or
                ("print_queue.append" in history_str)
             else (False, "請直接在 add_job 呼叫 print_queue.append(job) 體驗可變物件免 global！")
         )),

        ("11-5-4", "練習題", "購物車清單免 global 原處修改 add_item", 6, ("add_item",),
         lambda g: (
             (True, "add_to_cart 免 global 串列操作正確！")
             if (callable(g.get("add_item"))) or
                ("add_item" in history_str and "cart.append" in history_str)
             else (False, "請在 add_item 直接對全域 cart 串列進行 append 操作！")
         )),

        ("11-5-4", "挑戰題", "全域成績字典就地登錄 update_grade", 6, ("update_grade",),
         lambda g: (
             (True, "update_grade_book 免 global 字典更新正確！")
             if (callable(g.get("update_grade"))) or
                ("update_grade" in history_str and "grade_book" in history_str)
             else (False, "請直接對全域 grade_book 字典賦值，體驗字典就地修改無須 global！")
         )),

        # ----------------------------------------------------------------------
        # 11-5-5 濫用 global 的狀態污染隱患 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-5-5", "填空題", "跨測資未清空慘劇剖析 process_daily_batch", 5, (),
         lambda g: (
             (True, "狀態污染剖析填空正確！")
             if ("process_daily_batch" in history_str and "visitor_log" in history_str) or
                ("visitor_log" in history_str)
             else (False, "請觀察 process_daily_batch 未清空全域 visitor_log 所導致的跨日污染！")
         )),

        ("11-5-5", "練習題", "字元出現次數統計與歸零重置 count_letter", 6, ("count_letter",),
         lambda g: (
             (True, "reset_and_count_chars 重置清空正確！")
             if (callable(g.get("count_letter"))) or
                ("char_count = 0" in history_str or "char_count" in history_str)
             else (False, "請在 count_letter 開頭重置全域 char_count，杜絕殘留狀態！")
         )),

        ("11-5-5", "挑戰題", "跨多筆測資偶數和安全累加模擬", 5, (),
         lambda g: (
             (True, "跨多筆測資安全累加模擬正確！")
             if ("even_sum" in history_str and "clear" in history_str or "even_sum = 0" in history_str)
             else (False, "請在每筆測資迴圈開頭將全域累計變數歸零！")
         )),

        # ----------------------------------------------------------------------
        # 11-5-6 競賽除錯守則：多筆測資迴圈開頭重置 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("11-5-6", "填空題", "競賽重置標準框架 reset_contest 與 solve_case", 5, ("reset_contest", "solve_case"),
         lambda g: (
             (True, "reset_contest 競賽重置框架填空正確！")
             if (callable(g.get("reset_contest")) and callable(g.get("solve_case"))) or
                ("reset_contest" in history_str and "solve_case" in history_str)
             else (False, "請定義 reset_contest 歸零全域變數，並在 solve_case 前呼叫！")
         )),

        ("11-5-6", "練習題", "最大溫差分析器重置與計算 reset_day 與 analyze_day", 6, ("reset_day", "analyze_day"),
         lambda g: (
             (True, "reset_weather_station 每季重置實作正確！")
             if (callable(g.get("reset_day")) and callable(g.get("analyze_day"))) or
                ("reset_day" in history_str and "analyze_day" in history_str)
             else (False, "請實作 reset_day 與 analyze_day 歸零並分析極值！")
         )),

        ("11-5-6", "挑戰題", "APCS 多筆測資迴圈開頭重置除錯模擬", 5, (),
         lambda g: (
             (True, "多筆測資迴圈重置模擬挑戰成功！")
             if ("reset" in history_str and "for" in history_str and "solve" in history_str) or
                ("solve_case" in history_str)
             else (False, "請撰寫外層迴圈遍歷多組測資，並在每次迴圈開頭呼叫 reset 函數！")
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
    print(" 📊 《PythAPCS123》單元 11-5：全域變數在 APCS 競賽中的使用準則與除錯防禦 —— 自動評分報告")
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
        "unit": "11-5",
        "unit_title": "全域變數在 APCS 競賽中的使用準則與除錯防禦",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_11_5.py",
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
auto_grade_unit_11_5()
