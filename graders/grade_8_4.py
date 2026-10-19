# ==============================================================================
# 🧪 《PythAPCS123》單元 8-4：串列統計函數與極值維護 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_8_4.py
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
NOTEBOOK_FILE = "PythAPCS123_8-4_list_statistics_and_extrema.ipynb"

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


def auto_grade_unit_8_4():
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
        # 8-4-1 len() 函數與容量狀態 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-4-1", "填空題", "呼叫 len(items) 檢查安全庫存 (status)", 6, ("status",),
         lambda g: (
             (True, "len(items) >= 3 判定庫存狀態成功！")
             if g.get("status") == "STOCK ADEQUATE" or
                ("len(items)" in history_clean and "STOCK ADEQUATE" in history_str)
             else (False, "請在 8-4-1 填空題空格填入函數名稱 len！")
         )),

        ("8-4-1", "練習題", "購物車空滿狀態通報 (CART IS EMPTY / CONTAINS)", 9, (),
         lambda g: (
             (True, "購物車長度 len(cart) 狀態分支通報正確！")
             if ("len(cart)" in history_clean and ("CART IS EMPTY" in history_str or "CART CONTAINS:" in history_str)) or
                ("CART CONTAINS: 5 ITEMS" in history_str or "CART IS EMPTY" in history_str)
             else (False, "請依 len(cart) 判定並輸出 CART IS EMPTY 或 CART CONTAINS: [數量] ITEMS！")
         )),

        ("8-4-1", "挑戰題", "串列尺寸等級分類器 (LEVEL: NONE / SMALL / MEDIUM / LARGE)", 5, (),
         lambda g: (
             (True, "串列長度四級別門檻分類正確！")
             if ("LEVEL:" in history_str and "len(" in history_str) or
                ("LEVEL: MEDIUM (8)" in history_str)
             else (False, "請使用 len() 依題意劃分 NONE, SMALL, MEDIUM, LARGE 四種等級輸出！")
         )),

        # ----------------------------------------------------------------------
        # 8-4-2 sum() 總和函數 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-4-2", "填空題", "呼叫 sum(pocket_money) 計算總金額 (total_money == 300)", 6, ("total_money",),
         lambda g: (
             (True, "sum(pocket_money) 總和計算完全正確！")
             if g.get("total_money") == 300 or
                ("sum(pocket_money)" in history_clean)
             else (False, "請在 8-4-2 填空題空格填入函數名稱 sum！")
         )),

        ("8-4-2", "練習題", "籃球比賽總分比對儀 (sum(host) vs sum(guest))", 9, (),
         lambda g: (
             (True, "兩隊四節總分 sum() 比對與差值勝負判定正確！")
             if ("sum(host)" in history_clean and "sum(guest)" in history_clean and
                 ("HOST WINS" in history_str or "GUEST WINS" in history_str or "TIE" in history_str)) or
                ("HOST WINS 18" in history_str or "TIE" in history_str)
             else (False, "請使用 sum(host) 與 sum(guest) 比對兩隊總分並輸出勝負結果！")
         )),

        ("8-4-2", "挑戰題", "高於平均分人數統計器 (sum // n 搭配大於平均統計)", 5, (),
         lambda g: (
             (True, "平均計算與高於平均人數走訪統計正確！")
             if ("sum(scores)" in history_clean and ("Average:" in history_str or "Above count:" in history_str)) or
                ("Average: 70, Above count: 2" in history_str)
             else (False, "請計算整數平均值並走訪統計大於平均人數，依格式印出！")
         )),

        # ----------------------------------------------------------------------
        # 8-4-3 max() 與 min() 極值函數 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-4-3", "填空題", "呼叫 max 與 min 鎖定極值 (top_score, low_score)", 6, ("top_score", "low_score"),
         lambda g: (
             (True, "max(scores) 與 min(scores) 極值提取成功！")
             if (g.get("top_score") == 95 and g.get("low_score") == 60) or
                ("max(scores)" in history_clean and "min(scores)" in history_clean)
             else (False, "請在 8-4-3 填空題分別填入函數名稱 max 與 min！")
         )),

        ("8-4-3", "練習題", "股市最高價與最低價通報 (Highest 與 Lowest)", 9, (),
         lambda g: (
             (True, "5 天股價最高最低極值通報輸出正確！")
             if ("Highest:" in history_str and "Lowest:" in history_str and
                 ("max(" in history_str and "min(" in history_str)) or
                ("Highest: 530, Lowest: 480" in history_str or "Highest: 101, Lowest: 99" in history_str)
             else (False, "請使用 max() 與 min() 找出最高最低價並依格式輸出！")
         )),

        ("8-4-3", "挑戰題", "最高分與次高分 (max(a) 搭配 remove 與二次 max)", 5, (),
         lambda g: (
             (True, "冠軍與亞軍兩階段極值定位輸出正確！")
             if ("Champion:" in history_str and "Runner-up:" in history_str and "max(" in history_str) or
                ("Champion: 95, Runner-up: 88" in history_str)
             else (False, "請找出最高分 champion 後移除，再找出次高分 runner_up 並印出！")
         )),

        # ----------------------------------------------------------------------
        # 8-4-4 全距（Range）與極端價差計算 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-4-4", "填空題", "全距價差計算 max(prices) - min(prices) (price_diff == 320)", 6, ("price_diff",),
         lambda g: (
             (True, "max(prices) - min(prices) 算式完全正確！")
             if g.get("price_diff") == 320 or
                ("max(prices)-min(prices)" in history_clean or "max(prices) - min(prices)" in history_str)
             else (False, "請在 8-4-4 填空題空格分別填入 max 與 min！")
         )),

        ("8-4-4", "練習題", "購買力價差篩選器 (APCS f605 核心邏輯)", 9, (),
         lambda g: (
             (True, "價差波動 >= 20 與平均值 ALERT / NORMAL 判定正確！")
             if (("ALERT:" in history_str or "NORMAL:" in history_str) and
                 ("max(" in history_str and "min(" in history_str and "sum(" in history_str)) or
                ("ALERT: diff=50, avg=123" in history_str or "NORMAL: avg=55" in history_str)
             else (False, "請依 max(p)-min(p) 是否 >= 20 輸出 ALERT 或 NORMAL 警報！")
         )),

        ("8-4-4", "挑戰題", "全距門檻合格名單過濾 (diff <= D)", 5, (),
         lambda g: (
             (True, "全距門檻 D 與數列價差 PASS / FAIL 判斷正確！")
             if ("max(" in history_str and "min(" in history_str and
                 ("PASS:" in history_str or "FAIL:" in history_str or "EMPTY" in history_str)) or
                ("PASS: 12" in history_str)
             else (False, "請計算數列全距 diff，比對是否 <= 門檻 D 並輸出 PASS 或 FAIL！")
         )),

        # ----------------------------------------------------------------------
        # 8-4-5 歌唱與裁判評分：去頭去尾去極值 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-4-5", "填空題", "極值剔除加總 sum - max - min (core_sum == 175)", 6, ("core_sum",),
         lambda g: (
             (True, "sum(scores) - max(scores) - min(scores) 公式正確！")
             if g.get("core_sum") == 175 or
                ("sum(scores)-max(scores)-min(scores)" in history_clean)
             else (False, "請在 8-4-5 填空題依序填入函數 sum, max, min！")
         )),

        ("8-4-5", "練習題", "跳水大賽選手最終得分計算機 (去除最高最低 // 3)", 9, (),
         lambda g: (
             (True, "扣除最高最低並除以 3 計算最終分數正確！")
             if ("Final Score:" in history_str and
                 ("sum(" in history_str and "max(" in history_str and "min(" in history_str)) or
                ("Final Score: 85" in history_str or "Final Score: 60" in history_str)
             else (False, "請扣除 1 個最高分與 1 個最低分，求剩餘 3 評審平均分數並依格式輸出！")
         )),

        ("8-4-5", "挑戰題", "動態裁判評分器 (通用除以 len - 2 與極值通報)", 5, (),
         lambda g: (
             (True, "動態人數裁判評分去頭去尾平均計算完整！")
             if ("Highest:" in history_str and "Lowest:" in history_str and "Trimmed Average:" in history_str and
                 ("max(" in history_str and "min(" in history_str)) or
                ("Trimmed Average: 85" in history_str)
             else (False, "請通報最高分、最低分與扣除兩極值後的平均分數！")
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
        badge = '🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通 len()、sum()、max()、min() 四大統計神器與去極值演算法，數據分析戰神！'
    elif total_score >= 80:
        badge = '🥈 卓越冒險者（銀牌徽章 🥈）—— 表現優異，串列統計與極值篩選邏輯精準敏銳！'
    elif total_score >= 60:
        badge = '🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目微調全距運算與整數平均！'
    else:
        badge = '🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 8-4：串列統計函數與極值維護 —— 自動評分報告")
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
        "unit": "8-4",
        "unit_title": "串列統計函數與極值維護",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_8_4.py",
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
auto_grade_unit_8_4()
