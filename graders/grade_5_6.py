# ==============================================================================
# 🧪 《PythAPCS123》單元 5-6：巢狀 if 與短路求值（Short-circuit） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_5_6.py
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
NOTEBOOK_FILE = "PythAPCS123_5-6_nested_if_and_short_circuit.ipynb"

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


def auto_grade_unit_5_6(env=None):
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

    test_cases = [
        # ----------------------------------------------------------------------
        # 5-6-1 巢狀分支結構——多層次縮排 (共 20 分)
        # ----------------------------------------------------------------------
        ("5-6-1", "填空題", "遊樂設施雙重條件巢狀檢驗 (TOO SHORT)", 6, (),
         lambda g: (
             (True, "巢狀 if-else 填寫正確：成功印出 TOO SHORT！")
             if (("if h056 >= 140" in history_str or "if h056>=140" in history_str) and
                 ("else:" in history_str.replace(" ", "")))
             else (False, "請在 5-6-1 填空題空格填入 if 與 else:！")
         )),

        ("5-6-1", "練習題", "帳號密碼雙重登入安全審查 (LOGIN SUCCESS / WRONG)", 8, ("account", "password"),
         lambda g: (
             (True, "帳號密碼巢狀登入審查判定正確！")
             if (("LOGIN SUCCESS" in history_str and "WRONG PASSWORD" in history_str and "WRONG ACCOUNT" in history_str) or
                 ("admin" in history_str and "1234" in history_str and "if" in history_str)) or
                ("account" in g and "password" in g)
             else (False, "請依題意以巢狀 if 判斷帳號 'admin' 與密碼 1234 並印出結果！")
         )),

        ("5-6-1", "挑戰題", "座標象限分類巢狀版 (Q1, Q2, Q3, Q4)", 6, ("pt_x", "pt_y"),
         lambda g: (
             (True, "四象限巢狀判斷輸出成功！")
             if (("Q1" in history_str and "Q2" in history_str and "Q3" in history_str and "Q4" in history_str) or
                 ("pt_x > 0" in history_str and "pt_y > 0" in history_str and "if" in history_str)) or
                ("pt_x" in g and "pt_y" in g)
             else (False, "請讀入 pt_x 與 pt_y，以巢狀 if-else 區分 Q1, Q2, Q3, Q4 象限！")
         )),

        # ----------------------------------------------------------------------
        # 5-6-2 巢狀 if 與 and 複合條件轉換 (共 20 分)
        # ----------------------------------------------------------------------
        ("5-6-2", "填空題", "巢狀扁平化為 and 複合條件 (POSITIVE)", 6, (),
         lambda g: (
             (True, "扁平化 and 複合條件填寫正確！")
             if ("(x > 0) and (y > 0)" in history_str.replace(" ", "") or
                 ("x > 0" in history_str and "y > 0" in history_str and "and" in history_str))
             else (False, "請在 5-6-2 填空題空格填入 and 運算子！")
         )),

        ("5-6-2", "練習題", "週末特惠資格複合檢驗 (DISCOUNT AVAILABLE / NO DISCOUNT)", 8, ("day", "amount"),
         lambda g: (
             (True, "週末特惠複合邏輯判定正確！")
             if (("DISCOUNT AVAILABLE" in history_str and "NO DISCOUNT" in history_str) or
                 ("day == 6 or day == 7" in history_str.replace(" ", "") and "amount >= 1000" in history_str.replace(" ", ""))) or
                ("day" in g and "amount" in g)
             else (False, "請讀入 day 與 amount，以複合條件判斷是否符合週末特惠資格！")
         )),

        ("5-6-2", "挑戰題", "三角形三邊全正且任兩邊和大於第三邊 (VALID / INVALID)", 6, ("side_a", "side_b", "side_c"),
         lambda g: (
             (True, "三角形邊長全正與兩邊和複合判定成功！")
             if (("VALID" in history_str and "INVALID" in history_str) or
                 ("side_a + side_b > side_c" in history_str and "side_b + side_c > side_a" in history_str and "side_c + side_a > side_b" in history_str) or
                 ("side_a" in history_str and "side_b" in history_str and "side_c" in history_str and "VALID" in history_str)) or
                (all(k in g for k in ["side_a", "side_b", "side_c"]))
             else (False, "請讀入 side_a, side_b, side_c，判斷三邊均大於 0 且兩邊和大於第三邊！")
         )),

        # ----------------------------------------------------------------------
        # 5-6-3 and 短路求值機制——除數防零檢查 (共 20 分)
        # ----------------------------------------------------------------------
        ("5-6-3", "填空題", "整除防零檢查器 (dvsb=False)", 6, ("dvsb",),
         lambda g: (
             (True, "除數防零 and 短路保護填寫正確：dvsb=False！")
             if (g.get("dvsb") is False) and
                (("divisor!=0" in history_str.replace(" ", "") or "divisor != 0" in history_str) and "and" in history_str)
             else (False, "請在 5-6-3 填空題填入 divisor != 0 與 and！")
         )),

        ("5-6-3", "練習題", "安全除法比值檢驗 (divisor != 0 and num // divisor >= 5)", 8, ("num", "divisor"),
         lambda g: (
             (True, "安全除法比值 and 短路檢驗正確！")
             if (("divisor != 0 and num // divisor >= 5" in history_str.replace(" ", "") or "divisor!=0 and num//divisor>=5" in history_str.replace(" ", "")) or
                 ("PASS" in history_str and "FAIL" in history_str)) or
                ("num" in g and "divisor" in g)
             else (False, "請讀入 num 與 divisor，使用 (divisor != 0 and num // divisor >= 5) 判斷 PASS 或 FAIL！")
         )),

        ("5-6-3", "挑戰題", "班級平均分防零安全網 (students > 0 and total // students >= 60)", 6, ("total_score", "students"),
         lambda g: (
             (True, "人數防零平均分短路檢驗成功！")
             if (("CLASS PASS" in history_str and "CLASS FAIL" in history_str) or
                 ("students > 0" in history_str and "//" in history_str and "and" in history_str)) or
                ("total_score" in g and "students" in g)
             else (False, "請讀入總分與人數，使用 and 短路求值避免 ZeroDivisionError 崩潰！")
         )),

        # ----------------------------------------------------------------------
        # 5-6-4 or 短路求值機制——前真則後略 (共 20 分)
        # ----------------------------------------------------------------------
        ("5-6-4", "填空題", "預設免死金牌 or 短路防呆 (is_alive=True)", 6, ("is_alive",),
         lambda g: (
             (True, "免死金牌 or 短路保護填寫正確：is_alive=True！")
             if (g.get("is_alive") is True) and
                ("or" in history_str)
             else (False, "請在 5-6-4 填空題空格填入 or 運算子！")
         )),

        ("5-6-4", "練習題", "特權與積分雙軌通關 (has_vip == 1 or points >= 500)", 8, ("has_vip", "points"),
         lambda g: (
             (True, "VIP 特權雙軌 or 短路求值判斷正確！")
             if (("ENTRY APPROVED" in history_str and "ENTRY DENIED" in history_str) or
                 ("has_vip == 1 or points >= 500" in history_str.replace(" ", ""))) or
                ("has_vip" in g and "points" in g)
             else (False, "請讀入 has_vip 與 points，判斷 (has_vip == 1 or points >= 500)！")
         )),

        ("5-6-4", "挑戰題", "特例零值免除 or 短路檢驗 (k == 0 or 120 % k == 0)", 6, ("k",),
         lambda g: (
             (True, "特例零值 or 短路防呆判定成功！")
             if (("VALID" in history_str and "INVALID" in history_str) or
                 ("k == 0 or 120 % k == 0" in history_str.replace(" ", "") or "k==0 or 120%k==0" in history_str.replace(" ", ""))) or
                ("k" in g)
             else (False, "請讀入 k，使用 (k == 0 or 120 % k == 0) 判斷 VALID 或 INVALID！")
         )),

        # ----------------------------------------------------------------------
        # 5-6-5 APCS 邊界條件防崩潰雙重防線 (共 20 分)
        # ----------------------------------------------------------------------
        ("5-6-5", "填空題", "開根號前之非負防禦 (root_num >= 0)", 6, (),
         lambda g: (
             (True, "實數開根號非負防線填寫正確！")
             if (("if root_num >= 0" in history_str or "if root_num>=0" in history_str) and
                 ("else:" in history_str.replace(" ", "")))
             else (False, "請在 5-6-5 填空題空格填入 if root_num >= 0 與 else:！")
         )),

        ("5-6-5", "練習題", "兩數整除性除數防零雙重防線 (DIVISION BY ZERO)", 8, ("num_a", "num_b"),
         lambda g: (
             (True, "除數為 0 邊界防禦與整除性判定正確！")
             if (("DIVISION BY ZERO" in history_str and "DIVISIBLE" in history_str and "NOT DIVISIBLE" in history_str) or
                 ("num_b == 0" in history_str and ("num_a % num_b == 0" in history_str.replace(" ", "") or "num_a % num_b" in history_str))) or
                ("num_a" in g and "num_b" in g)
             else (False, "請讀入 num_a 與 num_b，先防線 num_b == 0，再判定 num_a % num_b == 0！")
         )),

        ("5-6-5", "挑戰題", "梯形面積計算防呆安全審查 (INVALID SHAPE)", 6, ("upper", "lower", "h056"),
         lambda g: (
             (True, "梯形邊長非負防呆與面積計算成功！")
             if (("INVALID SHAPE" in history_str and "// 2" in history_str) or
                 ("upper > 0 and lower > 0 and h056 > 0" in history_str.replace(" ", ""))) or
                (all(k in g for k in ["upper", "lower", "h056"]))
             else (False, "請讀入 upper, lower, h056，三者均大於 0 才計算面積！")
         )),
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
        badge = '🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通巢狀 if 與短路求值機制，邊界防禦堅若磐石！'
    elif total_score >= 80:
        badge = '🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，除數防零與前真則後略短路特性掌握純熟！'
    elif total_score >= 60:
        badge = '🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作微調！'
    else:
        badge = '🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 5-6：巢狀 if 與短路求值（Short-circuit） —— 自動評分報告")
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
        "unit": "5-6",
        "unit_title": "巢狀 if 與短路求值（Short-circuit）",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_5_6.py",
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
auto_grade_unit_5_6()
