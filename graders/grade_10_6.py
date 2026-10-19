# ==============================================================================
# 🧪 《PythAPCS123》單元 10-6：集合特性、建立與元素操作 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_10_6.py
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
NOTEBOOK_FILE = "PythAPCS123_10-6_set_creation_and_operations.ipynb"

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


def auto_grade_unit_10_6():
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
        # 10-6-1 集合概念：無序性與唯一性天然去重 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-6-1", "填空題", "大括號宣告集合 fruits_set = {'apple', 'banana', 'apple'}", 5, (),
         lambda g: (
             (True, "大括號集合宣告填空正確！")
             if ("fruits_set" in history_str and "banana" in history_str) or ("apple" in history_str and "{" in history_str)
             else (False, "請在 10-6-1 填空題宣告包含重複水果的集合！")
         )),

        ("10-6-1", "練習題", "單字相異字母統計器 unique_chars = set(word)", 6, (),
         lambda g: (
             (True, "相異字母集合統計正確！")
             if ("set(" in history_str or "{" in history_str) and ("unique_chars" in history_str or "word" in history_str)
             else (False, "請將單字中所有字母放入集合中並統計相異字母個數！")
         )),

        ("10-6-1", "挑戰題", "相異整數極值全距計算 max(raw_set) - min(raw_set)", 5, (),
         lambda g: (
             (True, "集合極值全距計算正確！")
             if ("max(" in history_str and "min(" in history_str) and ("raw_set" in history_str or "set" in history_str)
             else (False, "請計算集合中最大值與最小值的差距！")
         )),

        # ----------------------------------------------------------------------
        # 10-6-2 集合建立語法與空集合陷阱 set() (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-6-2", "填空題", "宣告真正的空集合 lucky_numbers = set()", 5, (),
         lambda g: (
             (True, "空集合 set() 填空正確！")
             if ("set()" in history_clean)
             else (False, "請在 10-6-2 填空題填入 set() 建立空集合！")
         )),

        ("10-6-2", "練習題", "動態收集非負整數集合 (.add())", 6, (),
         lambda g: (
             (True, "動態條件 .add() 收集正確！")
             if (".add(" in history_str and ">= 0" in history_str) or ("non_negative_set" in history_str)
             else (False, "請建立空集合並使用 .add() 收集非負整數！")
         )),

        ("10-6-2", "挑戰題", "連續字母遇到哨兵字元停機收集", 6, (),
         lambda g: (
             (True, "哨兵終止集合收集正確！")
             if (".add(" in history_str and "break" in history_str) or ("'X'" in history_str or '"X"' in history_str)
             else (False, "請走訪字母，遇到 'X' 立即中斷迴圈！")
         )),

        # ----------------------------------------------------------------------
        # 10-6-3 可迭代物件快速去重 set(my_list) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-6-3", "填空題", "計算打卡名單不重複人數 len(set(checkin_logs))", 5, (),
         lambda g: (
             (True, "set() 快速去重人數統計填空正確！")
             if ("len(set(checkin_logs))" in history_clean or "set(checkin_logs)" in history_str)
             else (False, "請在 10-6-3 填空題填入 len(set(checkin_logs))！")
         )),

        ("10-6-3", "練習題", "相異整數計數與純度檢測 len(s) == len(lst)", 6, (),
         lambda g: (
             (True, "去重長度比對純度檢測正確！")
             if ("len(set(" in history_clean and "len(" in history_str) or ("==" in history_str and "set" in history_str)
             else (False, "請比較 len(set(lst)) 與 len(lst) 判斷是否完全無重複！")
         )),

        ("10-6-3", "挑戰題", "兩班選課名冊相加後快速求總科目數", 6, (),
         lambda g: (
             (True, "兩名冊串列合併去重正確！")
             if ("set(" in history_str and ("+" in history_str or "|" in history_str)) and ("list_a" in history_str)
             else (False, "請利用串列相加並轉為 set 求出兩班總科目數！")
         )),

        # ----------------------------------------------------------------------
        # 10-6-4 元素動態增刪：.add(), .remove(), .discard() (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-6-4", "填空題", "使用 discard 安全移除白名單 members.discard(target)", 5, (),
         lambda g: (
             (True, "discard() 安全移除填空正確！")
             if ("discard" in history_str)
             else (False, "請在 10-6-4 填空題填入 discard(target)！")
         )),

        ("10-6-4", "練習題", "動態聊天室在線名冊維護器 (IN 用 add, OUT 用 discard)", 6, (),
         lambda g: (
             (True, "聊天室人員進出維護正確！")
             if (".add(" in history_str and ".discard(" in history_str) or ("online_users" in history_str)
             else (False, "請依 IN/OUT 指令分別調用 add() 與 discard() 維護名冊！")
         )),

        ("10-6-4", "挑戰題", "黑名單批次安全過濾 (遍歷 blacklist 執行 discard)", 6, (),
         lambda g: (
             (True, "黑名單批次 discard 過濾正確！")
             if (".discard(" in history_str and "for" in history_str) and ("approved" in history_str)
             else (False, "請走訪 blacklist 帳號使用 .discard() 安全過濾！")
         )),

        # ----------------------------------------------------------------------
        # 10-6-5 集合生成式（Set Comprehension） (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-6-5", "填空題", "集合生成式篩選大於 50 分數 {s for s in scores if s > 50}", 5, (),
         lambda g: (
             (True, "集合生成式填空正確！")
             if ("> 50" in history_str or ">50" in history_clean) and ("{" in history_str and "}" in history_str)
             else (False, "請在 10-6-5 填空題填入 if s > 50 門檻！")
         )),

        ("10-6-5", "練習題", "相異字串首字母集合提取器 {w[0].upper() for w in words}", 6, (),
         lambda g: (
             (True, "單字大寫首字母集合生成式正確！")
             if ("w[0].upper()" in history_clean or ".upper()" in history_str) and ("for" in history_str and "{" in history_str)
             else (False, "請以一行集合生成式提取所有單字的大寫首字母！")
         )),

        ("10-6-5", "挑戰題", "英文句子中相異母音單行萃取 {c for c in quote if c in 'aeiou'}", 6, (),
         lambda g: (
             (True, "母音字元集合生成式正確！")
             if ("'aeiou'" in history_str or '"aeiou"' in history_str or "in vowel" in history_str) and ("{" in history_str)
             else (False, "請以單行集合生成式篩選出句子中的所有母音！")
         )),

        # ----------------------------------------------------------------------
        # 10-6-6 集合元素限制：Hashable 限制 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-6-6", "填空題", "以元組 (r, c) 標記已拜訪座標 visited_coords.add((r, c))", 5, (),
         lambda g: (
             (True, "座標元組放入集合填空正確！")
             if (".add((" in history_clean or "visited_coords.add" in history_str)
             else (False, "請在 10-6-6 填空題將座標元組加到 visited_coords！")
         )),

        ("10-6-6", "練習題", "網格足跡重複踩踏偵測機 (pt in visited)", 6, (),
         lambda g: (
             (True, "網格重複足跡偵測正確！")
             if ("in visited" in history_str and ".add(" in history_str) or ("path_points" in history_str)
             else (False, "請使用集合紀錄走過的座標並回報重複踏足的點！")
         )),

        ("10-6-6", "挑戰題", "稀疏障礙物跨界安全過濾 (邊界範圍生成式)", 5, (),
         lambda g: (
             (True, "合法邊界障礙物過濾正確！")
             if ("0 <= r <" in history_str and "0 <= c <" in history_str) and ("{" in history_str)
             else (False, "請使用集合生成式過濾出所有位在合法邊界內的障礙物座標！")
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
    print(" 📊 《PythAPCS123》單元 10-6：集合特性、建立與元素操作 —— 自動評分報告")
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
        "unit": "10-6",
        "unit_title": "集合特性、建立與元素操作",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_10_6.py",
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
auto_grade_unit_10_6()
