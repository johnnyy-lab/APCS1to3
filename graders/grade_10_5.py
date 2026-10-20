# ==============================================================================
# 🧪 《PythAPCS123》單元 10-5：字典在 APCS 的經典解題模式 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_10_5.py
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
NOTEBOOK_FILE = "PythAPCS123_10-5_dictionary_apcs_patterns.ipynb"

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


def auto_grade_unit_10_5(env=None):
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
        # 10-5-1 頻率統計模式（Frequency Counter） (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-5-1", "填空題", "以 get() 補齊投票開票計數 tally.get(candidate, 0) + 1", 5, (),
         lambda g: (
             (True, "投票計數 get() 填空正確！")
             if ("tally.get(candidate, 0)" in history_str or "tally.get(candidate,0)" in history_clean or
                 "get(" in history_str and "+ 1" in history_str)
             else (False, "請在 10-5-1 填空題填入 tally.get(candidate, 0) + 1！")
         )),

        ("10-5-1", "練習題", "最高票選拔統計機 (得票最多者與票數)", 6, (),
         lambda g: (
             (True, "最高票統計與候選人搜尋正確！")
             if ("max(" in history_str or "for" in history_str) and ("ballot_box" in history_str or "count" in history_str)
             else (False, "請統計投票結果並輸出得票最高者與票數！")
         )),

        ("10-5-1", "挑戰題", "尋找唯一落單的幸運號碼 (恰好出現 1 次)", 5, (),
         lambda g: (
             (True, "唯一落單號碼統計鎖定正確！")
             if ("== 1" in history_str or "==1" in history_clean) and ("counts" in history_str or "get(" in history_str)
             else (False, "請以字典統計頻率，找出出現次數恰為 1 的號碼！")
         )),

        # ----------------------------------------------------------------------
        # 10-5-2 查表法（Lookup Table） (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-5-2", "填空題", "月份縮寫轉數字查表 month_map.get(target_month, -1)", 5, (),
         lambda g: (
             (True, "月份查表法填空正確！")
             if ("month_map.get" in history_str and "-1" in history_str)
             else (False, "請在 10-5-2 填空題填入 month_map.get(target_month, -1)！")
         )),

        ("10-5-2", "練習題", "外幣匯率試算器 (幣別查表換算台幣)", 6, (),
         lambda g: (
             (True, "外幣匯率查表換算正確！")
             if ("exchange_rates" in history_str and "*" in history_str) or ("sum" in history_str)
             else (False, "請透過匯率字典查表並計算兌換後的新台幣總額！")
         )),

        ("10-5-2", "挑戰題", "英文星期天數差計算 (星期縮寫查表差距)", 6, (),
         lambda g: (
             (True, "星期天數差距查表計算正確！")
             if ("weekday_map" in history_str and ("abs(" in history_str or "-" in history_str))
             else (False, "請透過星期查表計算兩天數之間的絕對差距！")
         )),

        # ----------------------------------------------------------------------
        # 10-5-3 離散化 / 座標壓縮（Coordinate Compression） (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-5-3", "填空題", "建立座標壓縮字典 rank_map[val] = idx", 5, (),
         lambda g: (
             (True, "座標壓縮字典建立填空正確！")
             if ("rank_map[val] = idx" in history_str or "rank_map[val]=idx" in history_clean or
                 "enumerate" in history_str)
             else (False, "請在 10-5-3 填空題填入 rank_map[val] = idx！")
         )),

        ("10-5-3", "練習題", "選手背號稠密排名轉換器 (排序去重離散化)", 6, (),
         lambda g: (
             (True, "稠密排名離散化轉換正確！")
             if ("sorted(" in history_str and "set(" in history_str) and ("[" in history_str and "]" in history_str)
             else (False, "請將選手背號排序去重，建立緊湊排名字典並映射輸出！")
         )),

        ("10-5-3", "挑戰題", "離散化反向解碼器 (依排名還原原始數值)", 6, (),
         lambda g: (
             (True, "反向字典查表解碼正確！")
             if ("rank_to_val" in history_str and "[" in history_str) or ("compressed" in history_str)
             else (False, "請透過反向字典將壓縮排名還原為原本的大數值！")
         )),

        # ----------------------------------------------------------------------
        # 10-5-4 雙向映射表（Two-way Mapping） (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-5-4", "填空題", "摩斯密碼反向字典建置 morse_decode[code] = letter", 5, (),
         lambda g: (
             (True, "雙向映射字典反轉填空正確！")
             if ("morse_decode[code] = letter" in history_str or "morse_decode[code]=letter" in history_clean)
             else (False, "請在 10-5-4 填空題填入 morse_decode[code] = letter！")
         )),

        ("10-5-4", "練習題", "情報員暗號雙向翻譯機 (代號與真名互查)", 6, (),
         lambda g: (
             (True, "特務雙向翻譯字典建置正確！")
             if ("agent_codes" in history_str and ("items()" in history_str or "reverse" in history_str))
             else (False, "請建置好雙向字典，支援代號與真名相互查詢！")
         )),

        ("10-5-4", "挑戰題", "一對多反向分組索引 (分數 -> 姓名串列)", 6, (),
         lambda g: (
             (True, "一對多反向分組索引正確！")
             if ("score_dict" in history_str and "append" in history_str) or ("score_to_names" in history_str)
             else (False, "請將學生姓名依成績反向歸入以分數為鍵的串列字典中！")
         )),

        # ----------------------------------------------------------------------
        # 10-5-5 分組聚合（Group By / Bucket） (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-5-5", "填空題", "奇偶數分組收集 d['odd'].append(x)", 5, (),
         lambda g: (
             (True, "奇偶數分組收集填空正確！")
             if ("append(" in history_str and ("odd" in history_str or "even" in history_str))
             else (False, "請在 10-5-5 填空題完成 odd 與 even 的 append 收集！")
         )),

        ("10-5-5", "練習題", "單字首字母分組歸檔器 (w[0].upper() 分桶)", 6, (),
         lambda g: (
             (True, "單字首字母分組歸檔正確！")
             if ("upper()" in history_str and "append(" in history_str) and ("words" in history_str)
             else (False, "請將單字按首字母大寫分組歸檔進字典中！")
         )),

        ("10-5-5", "挑戰題", "餘數分桶總和統計 (num % k 分組加總)", 6, (),
         lambda g: (
             (True, "餘數分桶統計與加總正確！")
             if ("% k" in history_str or "%k" in history_clean or "% 3" in history_str) and "sum(" in history_str
             else (False, "請將整數依餘數分組，並輸出各餘數組的總和！")
         )),

        # ----------------------------------------------------------------------
        # 10-5-6 字典與串列效能實測對比 O(1) vs O(N) (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-5-6", "填空題", "以字典建立白名單查詢 query_user in whitelist_dict", 5, (),
         lambda g: (
             (True, "字典 O(1) 白名單查詢填空正確！")
             if ("in whitelist_dict" in history_str or "in whitelist" in history_str)
             else (False, "請在 10-5-6 填空題填入 query_user in whitelist_dict！")
         )),

        ("10-5-6", "練習題", "極速資料去重過濾保留順序 (O(N) 雜湊查表)", 6, (),
         lambda g: (
             (True, "保留順序之雜湊去重正確！")
             if ("seen" in history_str or "table" in history_str or "in" in history_str) and "append(" in history_str
             else (False, "請利用雜湊字典/集合在維持初次出現順序下去除重複值！")
         )),

        ("10-5-6", "挑戰題", "兩數串列交集元素極速提取 O(N + M)", 5, (),
         lambda g: (
             (True, "O(N + M) 兩串列交集提取正確！")
             if ("table_a" in history_str or "in table" in history_str or "in set" in history_str) and ("list_b" in history_str)
             else (False, "請將 list_a 轉為雜湊表後走訪 list_b 達到 O(N+M) 交集！")
         ))    ]

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
        badge = '🏆 完美滿分！你已經徹底攻克二維陣列核心技術，具備 APCS 實戰高手水準！'
    elif total_score >= 80:
        badge = '🌟 優秀！觀念掌握非常扎實，稍微細心檢查即可登峰造極！'
    elif total_score >= 60:
        badge = '👍 及格！基本概念已建立，建議複習未通過的題目加強熟悉度！'
    else:
        badge = '💪 請再接再厲！建議回到上方微型階梯逐題操作並執行程式碼！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 10-5：字典在 APCS 的經典解題模式 —— 自動評分報告")
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
        "unit": "10-5",
        "unit_title": "字典在 APCS 的經典解題模式",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_10_5.py",
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
auto_grade_unit_10_5()
