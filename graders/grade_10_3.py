# ==============================================================================
# 🧪 《PythAPCS123》單元 10-3：字典概念、建立與鍵值對存取（Key-Value） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_10_3.py
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
NOTEBOOK_FILE = "PythAPCS123_10-3_dictionary_concept_creation_and_access.ipynb"

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


def auto_grade_unit_10_3():
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
        # 10-3-1 為什麼需要字典？名牌索引 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-3-1", "填空題", "機場代碼字典查詢 airports['TPE']", 5, (),
         lambda g: (
             (True, "機場代碼查詢填空正確！")
             if ("airports['TPE']" in history_str or 'airports["TPE"]' in history_str or
                 "airports['KHH']" in history_str)
             else (False, "請在 10-3-1 填空題填入鍵值 'TPE' 取出城市！")
         )),

        ("10-3-1", "練習題", "電話簿快速查號台 phone_book[name]", 6, (),
         lambda g: (
             (True, "電話簿字典建立與查號正確！")
             if ("phone_book" in history_str or "phone" in history_str) and ("[" in history_str and "]" in history_str)
             else (False, "請建立 phone_book 字典並完成電話號碼查詢！")
         )),

        ("10-3-1", "挑戰題", "單字英翻中對照小辭典", 5, (),
         lambda g: (
             (True, "英中辭典動態建置與查詢正確！")
             if ("dict" in history_str or "{}" in history_str) and ("for" in history_str and "input" in history_str)
             else (False, "請建立英翻中字典並查詢指定單字！")
         )),

        # ----------------------------------------------------------------------
        # 10-3-2 大括號鍵值對語法與空字典 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-3-2", "填空題", "商品價格字典宣告 {'book': 250, 'pen': 30}", 5, ("item_prices",),
         lambda g: (
             (True, "商品價格字典宣告填空正確！")
             if (g.get("item_prices") and g.get("item_prices").get("book") == 250) or
                ("250" in history_str and "30" in history_str and ":" in history_str)
             else (False, "請在 10-3-2 填空題填入價格 250 與 30！")
         )),

        ("10-3-2", "練習題", "學生學號登錄卡 (學號為 Key，姓名為 Value)", 6, (),
         lambda g: (
             (True, "學號姓名登錄字典正確！")
             if ("{}" in history_str or "dict()" in history_str) and ("[" in history_str and "=" in history_str)
             else (False, "請以學號為 Key、姓名為 Value 存入字典！")
         )),

        ("10-3-2", "挑戰題", "重複鍵覆蓋歷史追蹤器", 6, (),
         lambda g: (
             (True, "重複鍵覆蓋特性驗證正確！")
             if ("len(" in history_str or "print" in history_str) and ("=" in history_str)
             else (False, "請模擬相同 Key 重複賦值，觀察字典長度維持 1 且值被更新！")
         )),

        # ----------------------------------------------------------------------
        # 10-3-3 鍵的合法型態：Hashable 限制 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-3-3", "填空題", "使用座標元組作為鍵 board[(1, 3)] = 'QUEEN'", 5, (),
         lambda g: (
             (True, "座標元組做為字典鍵填空正確！")
             if ("(1, 3)" in history_str or "(1,3)" in history_clean) and ("QUEEN" in history_str or "KNIGHT" in history_str)
             else (False, "請在 10-3-3 填空題填入座標元組 (1, 3) 與 (2, 2)！")
         )),

        ("10-3-3", "練習題", "網格寶物定位查詢機 treasure_map[(r, c)]", 6, (),
         lambda g: (
             (True, "網格寶物座標元組字典正確！")
             if ("(r, c)" in history_str or "(r,c)" in history_clean or "treasure" in history_str)
             else (False, "請以 (r, c) 元組為 Key 記錄各座標點的寶物！")
         )),

        ("10-3-3", "挑戰題", "座標點重疊價值累加器 (+= val)", 6, (),
         lambda g: (
             (True, "重複座標價值累加正確！")
             if ("+=" in history_str or "get(" in history_str) and ("(r, c)" in history_str or "(r,c)" in history_clean)
             else (False, "請在座標重複時將數值累加至該格字典中！")
         )),

        # ----------------------------------------------------------------------
        # 10-3-4 鍵值存取與 KeyError 防範 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-3-4", "填空題", "使用 in 運算子安全防禦 target_country in capitals", 5, (),
         lambda g: (
             (True, "in 運算子安全檢查填空正確！")
             if ("in capitals" in history_str)
             else (False, "請在 10-3-4 填空題填入 target_country in capitals！")
         )),

        ("10-3-4", "練習題", "圖書館借閱安全查詢機", 6, (),
         lambda g: (
             (True, "安全借閱書籍查詢正確！")
             if ("in books" in history_str or "not in" in history_str or "get(" in history_str)
             else (False, "請在查詢前檢查書籍是否存在於 books 中！")
         )),

        ("10-3-4", "挑戰題", "多鍵連續查詢與未命中計數器", 6, (),
         lambda g: (
             (True, "連續查詢與未命中統計正確！")
             if ("NONE" in history_str or "miss" in history_str or "count" in history_str) and ("in" in history_str)
             else (False, "請查詢代碼，查不到輸出 NONE 並統計未命中總次數！")
         )),

        # ----------------------------------------------------------------------
        # 10-3-5 新增與修改鍵值對 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-3-5", "填空題", "開票計數初值設定與 counts[cand] += 1 累加", 5, (),
         lambda g: (
             (True, "計數初值設定與累加填空正確！")
             if ("counts[cand] = 1" in history_str or "counts[cand] += 1" in history_str or
                 "+= 1" in history_str)
             else (False, "請在 10-3-5 填空題補齊初值設定與 += 1 累加！")
         )),

        ("10-3-5", "練習題", "動態商品庫存管理員 (進出貨累加扣減)", 6, (),
         lambda g: (
             (True, "動態庫存加減更新正確！")
             if ("+=" in history_str or "stock" in history_str) and ("in" in history_str)
             else (False, "請以字典動態維護商品進出貨後的庫存量！")
         )),

        ("10-3-5", "挑戰題", "字串單字出現次數統計與最高票", 6, (),
         lambda g: (
             (True, "單字出現頻率統計與極值正確！")
             if ("max(" in history_str or "count" in history_str) and ("+=" in history_str or "get(" in history_str)
             else (False, "請統計每個單字出現次數並找出最高票得主！")
         )),

        # ----------------------------------------------------------------------
        # 10-3-6 刪除鍵值對：del 與 pop() (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-3-6", "填空題", "安全彈出過期用戶 users.pop('user3', 'NOT_FOUND')", 5, (),
         lambda g: (
             (True, "pop 安全彈出預設值填空正確！")
             if ("NOT_FOUND" in history_str)
             else (False, "請在 10-3-6 填空題填入預設回傳值 'NOT_FOUND'！")
         )),

        ("10-3-6", "練習題", "會員登出與註銷系統 (pop 安全剔除)", 6, (),
         lambda g: (
             (True, "會員帳號安全註銷正確！")
             if (".pop(" in history_str or "del " in history_str) and ("members" in history_str)
             else (False, "請使用 pop() 或 del 註銷會員帳號並防範 KeyError！")
         )),

        ("10-3-6", "挑戰題", "黑名單安全過濾清理器 (防崩潰)", 5, (),
         lambda g: (
             (True, "批次黑名單安全過濾正確！")
             if (".pop(" in history_str or "in players" in history_str or "discard" in history_str)
             else (False, "請批次自 players 中剔除作弊者，且不因重複不存在而崩潰！")
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
    print(" 📊 《PythAPCS123》單元 10-3：字典概念、建立與鍵值對存取（Key-Value） —— 自動評分報告")
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
        "unit": "10-3",
        "unit_title": "字典概念、建立與鍵值對存取（Key-Value）",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_10_3.py",
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
auto_grade_unit_10_3()
