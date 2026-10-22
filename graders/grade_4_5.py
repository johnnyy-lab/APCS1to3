# ==============================================================================
# 🧪 《PythAPCS123》單元 4-5：標準輸入 input() 基本讀取 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_4_5.py
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
NOTEBOOK_FILE = "PythAPCS123_4-5_standard_input_input.ipynb"

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


def auto_grade_unit_4_5(env=None):
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
        # 4-5-1 input() 的本質——電腦的靈敏耳朵與「輸入一律為字串」的鐵律 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-5-1", "填空題", "標準輸入 input() 讀入星座名稱 (cnst)", 6, ("cnst",),
         lambda g: (
             (True, "字串輸入設定正確：成功使用 input() 讀取星座！")
             if (("cnst" in g or "cnst = input()" in history_str.replace(" ", "")) and
                 ("觀測日誌" in history_str or "cnst" in history_str))
             else (False, "請在 4-5-1 填空題填入 input() 讀入星座並印出！")
         )),

        ("4-5-1", "練習題", "圖書館智慧借書通知 (book_title)", 8, ("book_title",),
         lambda g: (
             (True, f"借閱書籍讀入成功：book_title='{g.get('book_title')}'！")
             if (("book_title" in g) and
                 ("借閱手續完成" in history_str))
             else (False, "請使用 book_title = input() 讀取書名，並印出借閱成功通知！")
         )),

        ("4-5-1", "挑戰題", "傳奇公會勇者報到系統 (title)", 6, ("title",),
         lambda g: (
             (True, "勇者稱號讀入與公會公告排版成功！")
             if (("title" in g or "title = input()" in history_str.replace(" ", "")) and
                 ("歡迎傳奇勇者" in history_str or "*" in history_str))
             else (False, "請宣告 title = input() 讀入稱號，並印出星號裝飾線與公會公告！")
         )),

        # ----------------------------------------------------------------------
        # 4-5-2 字串轉整數 int(input())——破解 \"10\" + \"20\" = \"1020\" 陷阱 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-5-2", "填空題", "神聖仙丹整數轉型 int(input()) (heal_hp)", 6, ("heal_hp", "initial_hp"),
         lambda g: (
             (True, "整數轉型填寫正確：heal_hp = int(input())！")
             if (("int(input())" in history_str.replace(" ", "") or "heal_hp" in g) and
                 ("神聖仙丹" in history_str or g.get("initial_hp") == 150))
             else (False, "請在 4-5-2 填空題空格填入 int 與 input 讀入整數！")
         )),

        ("4-5-2", "練習題", "正方形農場圍籬與面積計算器 (side)", 8, ("side",),
         lambda g: (
             (True, f"正方形農場計算正確：邊長={g.get('side')}！")
             if (("side" in g and isinstance(g.get("side"), int)) and
                 ("正方形農場邊長" in history_str or "圍籬總長度" in history_str))
             else (False, "請使用 side = int(input()) 讀取邊長，並輸出圍籬長度與土地面積！")
         )),

        ("4-5-2", "挑戰題", "智慧零錢硬幣兌換機 (total_money, coin_50)", 6, ("total_money",),
         lambda g: (
             (True, "零錢硬幣兌換邏輯計算正確！")
             if (("total_money" in g or "total_money = int(input())" in history_str.replace(" ", "")) and
                 ("// 50" in history_str or "//50" in history_str or "50元" in history_str))
             else (False, "請宣告 total_money = int(input())，並計算各面額硬幣數量印出報告！")
         )),

        # ----------------------------------------------------------------------
        # 4-5-3 小數輸入 float(input())——精準量測身高體重與實數幾何計算 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-5-3", "填空題", "身高浮點數 float(input()) 與 BMI 計算 (height_m)", 6, ("height_m", "weight_kg"),
         lambda g: (
             (True, "小數輸入設定正確：height_m = float(input())！")
             if (("float(input())" in history_str.replace(" ", "") or "height_m" in g) and
                 ("BMI" in history_str or g.get("weight_kg") == 55.0))
             else (False, "請在 4-5-3 填空題空格填入 float 與 input 讀入身高！")
         )),

        ("4-5-3", "練習題", "攝氏轉華氏溫標轉換 (c, f)", 8, ("c",),
         lambda g: (
             (True, f"溫標換算完成：攝氏={g.get('c')}°C！")
             if (("c" in g and (isinstance(g.get("c"), float) or isinstance(g.get("c"), int))) and
                 ("9 / 5" in history_str or "9/5" in history_str or "1.8" in history_str or "°F" in history_str))
             else (False, "請使用 c = float(input()) 讀取溫度，並計算華氏溫度 f 印出！")
         )),

        ("4-5-3", "挑戰題", "精品百貨 VIP 折扣收銀計算 (discount_rate)", 6, ("discount_rate", "original_price"),
         lambda g: (
             (True, "VIP 折扣金額計算與排版完成！")
             if (("discount_rate" in g or "discount_rate = float(input())" in history_str.replace(" ", "") or "discount_rate" in history_str) and
                 ("VIP" in history_str or "現省" in history_str or "original_price" in g or "discount_rate" in g))
             else (False, "請使用 discount_rate = float(input()) 讀取折扣，並輸出漂亮帳單！")
         )),

        # ----------------------------------------------------------------------
        # 4-5-4 循序多次調用 input() 讀入多行單一資料 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-5-4", "填空題", "超商商品三行讀取與總額計算 (item_name, prc, cnt045)", 6, ("item_name", "prc", "cnt045"),
         lambda g: (
             (True, "三行資料循序讀取設定正確！")
             if (("item_name" in g or "prc" in g or "cnt045" in g) or
                 ("item_name" in history_str and "input" in history_str))
             else (False, "請在 4-5-4 填空題依序使用 input() 與 int(input()) 讀取三行！")
         )),

        ("4-5-4", "練習題", "雙數四則運算分析儀 (nm1045, nm2045)", 8, ("nm1045", "nm2045"),
         lambda g: (
             (True, f"雙數分析儀運算完成：nm1045={g.get('nm1045')}, nm2045={g.get('nm2045')}！")
             if (("nm1045" in g and "nm2045" in g) and
                 ("兩數為：" in history_str or "商：" in history_str))
             else (False, "請連續兩行讀入 nm1045 與 nm2045 整數，並印出和、差、積、商、餘數！")
         )),

        ("4-5-4", "挑戰題", "競賽選手總分加權計算模組 (theory_score, practical_score)", 6, ("theory_score", "practical_score", "candidate_name"),
         lambda g: (
             (True, "選手四行成績與加權總分計算成功！")
             if (("theory_score" in g or "practical_score" in g or "candidate_name" in g) and
                 ("加權" in history_str or "總成績" in history_str))
             else (False, "請連續四行讀取選手資料，並計算筆試與實作加權總分！")
         )),

        # ----------------------------------------------------------------------
        # 4-5-5 競技程式 APCS / OJ 生死線——嚴禁提示文字的「純淨讀入」 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-5-5", "填空題", "APCS 純淨讀入求較大者 (max(nm1045, nm2045))", 6, ("nm1045",),
         lambda g: (
             (True, "APCS 純淨讀入格式正確：input() 無多餘字串！")
             if (("int(input())" in history_str.replace(" ", "") or "nm1045" in g) and
                 ("max(nm1045" in history_str.replace(" ", "") or "max" in history_str))
             else (False, "請在 4-5-5 填空題使用純淨 int(input()) 讀入兩數並輸出較大者！")
         )),

        ("4-5-5", "練習題", "APCS 規格模擬題：兩數之差的絕對值 (abs(diff_a - diff_b))", 8, ("diff_a", "diff_b"),
         lambda g: (
             (True, f"絕對值純淨計算完成：diff_a={g.get('diff_a')}, diff_b={g.get('diff_b')}！")
             if (("diff_a" in g and "diff_b" in g) and
                 ("abs(diff_a - diff_b)" in history_str.replace(" ", "") or "abs(diff_a-diff_b)" in history_str.replace(" ", "") or "abs" in history_str))
             else (False, "請純淨讀入 diff_a, diff_b 並輸出 abs(diff_a - diff_b)，不印出任何多餘文字！")
         )),

        ("4-5-5", "挑戰題", "APCS 規格模擬題：三數極端全距純淨輸出 (max - min)", 6, ("range_a", "range_b", "range_c"),
         lambda g: (
             (True, "三數全距純淨輸出成功！")
             if (("max(" in history_str and "min(" in history_str) or
                 ("range_a" in g and "range_b" in g and "range_c" in g and ("max" in history_str or "-" in history_str)))
             else (False, "請連續三行純淨讀入 range_a, range_b, range_c，並直接輸出 max(range_a, range_b, range_c) - min(range_a, range_b, range_c)！")
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
        badge = '🏆 滿分榮譽大師（王者金牌 🥇）—— 恭喜完美掌握 input() 標準輸入與 APCS 純淨讀入規範！'
    elif total_score >= 80:
        badge = '🥈 卓越進階工程師（銀牌徽章 🥈）—— 表現相當亮眼，只差一點點就滿分囉！'
    elif total_score >= 60:
        badge = '🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作微調！'
    else:
        badge = '🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 4-5：標準輸入 input() 基本讀取 —— 自動評分報告")
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
        "unit": "4-5",
        "unit_title": "標準輸入 input() 基本讀取",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_4_5.py",
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
auto_grade_unit_4_5()
