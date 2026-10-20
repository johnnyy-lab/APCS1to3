# ==============================================================================
# 🧪 《PythAPCS123》單元 8-7：列表生成式與動態輸入 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_8_7.py
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
NOTEBOOK_FILE = "PythAPCS123_8-7_list_comprehension_and_dynamic_input.ipynb"

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


def auto_grade_unit_8_7(env=None):
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
        # 8-7-1 列表生成式基礎語法：[運算式 for 變數 in 迭代對象] (共 20 分)
        # ----------------------------------------------------------------------
        ("8-7-1", "填空題", "列表生成式立方數計算 ([x ** 3 for x in range(1, 6)])", 6, ("cubes",),
         lambda g: (
             (True, "列表生成式立方運算式產出成功！")
             if g.get("cubes") == [1, 8, 27, 64, 125] or
                ("[x**3forxinrange(1,6)]" in history_clean or "[x ** 3 for x in range(1, 6)]" in history_str)
             else (False, "請在 8-7-1 填空題填入次方數 3 與 range 終點 6！")
         )),

        ("8-7-1", "練習題", "整數兩倍串列生成 (doubled = [x * 2 for x in nums])", 9, (),
         lambda g: (
             (True, "兩倍數值列表生成式運算正確！")
             if ("[x * 2 for x in nums]" in history_str or "[x*2forxinnums]" in history_clean) or
                ("[4, 10, 16, 20]" in history_str or "[0, -6, 14]" in history_str)
             else (False, "請使用列表生成式產出 doubled = [x * 2 for x in nums] 並印出！")
         )),

        ("8-7-1", "挑戰題", "前 8 個正偶數一行生成 ([2, 4, ... 16])", 5, (),
         lambda g: (
             (True, "前 8 個正偶數列表生成式構思正確！")
             if ("[x for x in range(2, 17, 2)]" in history_str or "[x*2forxinrange(1,9)]" in history_clean or
                 "[x * 2 for x in range(1, 9)]" in history_str) or
                ("[2, 4, 6, 8, 10, 12, 14, 16]" in history_str)
             else (False, "請使用列表生成式搭配 range() 一行產出前 8 個正偶數！")
         )),

        # ----------------------------------------------------------------------
        # 8-7-2 列表生成式搭配條件篩選：[... if 條件] (共 20 分)
        # ----------------------------------------------------------------------
        ("8-7-2", "填空題", "末端 if 篩選不及格分數 ([s for s in scores if s < 60])", 6, ("failed",),
         lambda g: (
             (True, "末端 if 條件過濾不及格分數正確！")
             if g.get("failed") == [48, 59, 30] or
                ("[s for s in scores if s < 60]" in history_str or "[sforsinscoresifs<60]" in history_clean)
             else (False, "請在 8-7-2 填空題空格填入 if 與不及格門檻 60！")
         )),

        ("8-7-2", "練習題", "正整數平方篩選 ([x ** 2 for x in data if x > 0])", 9, (),
         lambda g: (
             (True, "大於 0 正整數平方生成式過濾輸出正確！")
             if ("[x ** 2 for x in data if x > 0]" in history_str or "[x**2forxindataifx>0]" in history_clean) or
                ("[225, 64, 529]" in history_str or "[9, 16]" in history_str)
             else (False, "請使用列表生成式篩選出 x > 0 並計算平方後印出！")
         )),

        ("8-7-2", "挑戰題", "A 開頭名字字首過濾 (a_names 篩選)", 5, (),
         lambda g: (
             (True, "字首 'A' 或 'a' 條件列表生成式篩選輸出正確！")
             if ("for name in names" in history_str and ("in \"Aa\"" in history_str or "startswith(" in history_str or "in 'Aa'" in history_str)) or
                ("['Alice', 'Anna', 'alex']" in history_str)
             else (False, "請使用列表生成式過濾出開頭為 A 或 a 的名字！")
         )),

        # ----------------------------------------------------------------------
        # 8-7-3 APCS 必備同行數值動態輸入 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-7-3", "填空題", "逗號切分浮點數轉型 ([float(x) for x in ...])", 6, ("float_nums",),
         lambda g: (
             (True, "浮點數型態轉換 float(x) 填寫正確！")
             if g.get("float_nums") == [1.5, 2.8, 3.2, 4.0] or
                ("[float(x) for x in raw_text.split" in history_str or "[float(x)forxinraw_text.split" in history_clean)
             else (False, "請在 8-7-3 填空題填入轉型函數 float！")
         )),

        ("8-7-3", "練習題", "同行整數輸入轉換與總和平均 ([int(x) for x in line.split()])", 9, (),
         lambda g: (
             (True, "同行字串轉整數串列與 sum/avg 計算正確！")
             if ("[int(x) for x in line.split()]" in history_str or "[int(x)forxinline.split()]" in history_clean) and
                ("總和:" in history_str and "平均:" in history_str) or
                ("總和: 414 平均: 82" in history_str or "總和: 60 平均: 20" in history_str)
             else (False, "請使用 [int(x) for x in line.split()] 轉換並輸出總和與平均！")
         )),

        ("8-7-3", "挑戰題", "同行輸入正整數過濾與極值總和統計", 5, (),
         lambda g: (
             (True, "同行輸入字串過濾正整數並輸出總和與最大值正確！")
             if ("[int(x) for x in" in history_str and "if" in history_str and ("sum(" in history_str or "max(" in history_str))
             else (False, "請將同行字串轉整數並只保留正整數，印出串列、總和與最大值！")
         )),

        # ----------------------------------------------------------------------
        # 8-7-4 雙重分支與三元運算生成式：[值A if 條件 else 值B for ...] (共 20 分)
        # ----------------------------------------------------------------------
        ("8-7-4", "填空題", "三元運算前置 if-else 奇偶標籤生成 (parity)", 6, ("parity",),
         lambda g: (
             (True, "前置 if-else 三元運算奇偶性標籤正確！")
             if g.get("parity") == ["Odd", "Even", "Odd", "Even", "Odd", "Even"] or
                ('["Even" if' in history_str and 'else "Odd"' in history_str) or
                ("Evenifn%2==0elseOdd" in history_clean)
             else (False, "請在 8-7-4 填空題空格依序填入 if 與 else！")
         )),

        ("8-7-4", "練習題", "滿百折 20 前置三元折扣計算 (discounted_prices)", 9, (),
         lambda g: (
             (True, "滿百折 20 前置 if-else 折扣計算輸出正確！")
             if ("[p - 20 if p >= 100 else p for p in prices]" in history_str or
                 "[p-20ifp>=100elsepforpinprices]" in history_clean) or
                ("[100, 45, 280, 80, 480]" in history_str or "[80, 99]" in history_str)
             else (False, "請使用前置 if-else 生成式：滿百折 20，未滿百維持原價！")
         )),

        ("8-7-4", "挑戰題", "負分歸零與總分加總 (safe_scores 與 sum)", 5, (),
         lambda g: (
             (True, "負分歸零前置三元列表生成式計算正確！")
             if ("if" in history_str and "else 0" in history_str or "else0" in history_clean) and "sum(" in history_str
             else (False, "請使用前置 if-else 將負分替換為 0，並計算 safe_scores 的總得分！")
         )),

        # ----------------------------------------------------------------------
        # 8-7-5 列表生成式實戰綜合特訓 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-7-5", "填空題", "攝氏轉華氏溫度生成式公式填空 (fahrenheit)", 6, ("fahrenheit",),
         lambda g: (
             (True, "華氏轉換公式生成式 [c * 9 // 5 + 32 for c in celsius] 正確！")
             if g.get("fahrenheit") == [32, 59, 77, 86, 104] or
                ("[c * 9 // 5 + 32 for c in celsius]" in history_str or "[c*9//5+32forcincelsius]" in history_clean)
             else (False, "請在 8-7-5 填空題空格填入除數 5 與常數 32！")
         )),

        ("8-7-5", "練習題", "偶數且大於 50 數值過濾與降序排序 (filtered.sort)", 9, (),
         lambda g: (
             (True, "複合條件 (偶數且 > 50) 篩選與降序排序輸出正確！")
             if ("% 2 == 0" in history_str and "> 50" in history_str and
                 ("sort(reverse=True)" in history_str or "reverse=True" in history_clean or "[::-1]" in history_str)) or
                ("[90, 68]" in history_str or "[60, 52]" in history_str)
             else (False, "請以列表生成式篩選出偶數且 > 50 之數值，由大到小排序後輸出！")
         )),

        ("8-7-5", "挑戰題", "APCS 及格人數與及格平均綜合解題", 5, (),
         lambda g: (
             (True, "字串拆分、及格篩選、人數與平均計算綜合通關！")
             if ("split()" in history_str and ">= 60" in history_str and "len(" in history_str and "sum(" in history_str)
             else (False, "請完成整數轉型、及格篩選並計算及格人數與及格平均！")
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
        badge = '🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通基礎列表生成式、末端 if 篩選、同行動態輸入與前置三元運算，Pythonic 代碼藝術家！'
    elif total_score >= 80:
        badge = '🥈 卓越冒險者（銀牌徽章 🥈）—— 表現優異，列表生成式語法架構與條件分支運用自如！'
    elif total_score >= 60:
        badge = '🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目微調 if-else 位置與型態轉型！'
    else:
        badge = '🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 8-7：列表生成式與動態輸入 —— 自動評分報告")
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
        "unit": "8-7",
        "unit_title": "列表生成式與動態輸入",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_8_7.py",
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
auto_grade_unit_8_7()
