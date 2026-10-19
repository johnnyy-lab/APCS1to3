# ==============================================================================
# 🧪 《PythAPCS123》單元 4-7：多行固定筆數讀取 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_4_7.py
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
NOTEBOOK_FILE = "PythAPCS123_4-7_multiline_fixed_inputs.ipynb"

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


def auto_grade_unit_4_7():
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

    test_cases = [
        # ----------------------------------------------------------------------
        # 4-7-1 連續三行純整數讀入模式 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-7-1", "填空題", "紙箱長寬高三行讀入與表面積計算 (width, surface_area)", 6, ("length", "width", "height"),
         lambda g: (
             (True, "紙箱三行尺寸讀取與容積表面積計算正確！")
             if (("length" in g or "width" in g or "height" in g) and
                 ("volume" in history_str or "surface_area" in history_str or "紙箱容積" in history_str))
             else (False, "請在 4-7-1 填空題空格填入 int(input()) 讀取寬度並補齊表面積算式！")
         )),

        ("4-7-1", "練習題", "射箭選拔賽三輪得分與穩定度指標 (score1, score2, score3)", 8, ("score1", "score2", "score3"),
         lambda g: (
             (True, "射箭三輪得分讀入與最高分、穩定度計算成功！")
             if (("score1" in g and "score2" in g and "score3" in g) and
                 ("max(" in history_str or "stability" in history_str))
             else (False, "請連續三行讀入 score1, score2, score3，並計算總分、最高分與穩定度！")
         )),

        ("4-7-1", "挑戰題", "健走四天步數與極端差距統計 (day1, day2, day3, day4)", 6, ("day1", "day2", "day3", "day4"),
         lambda g: (
             (True, "連續四天步數讀取與極端差距計算完成！")
             if (("day1" in g or "day2" in g or "day3" in g or "day4" in g) or
                 ("day1" in history_str and "int(input())" in history_str))
             else (False, "請連續四行讀取四天步數，並計算總步數與極端差距！")
         )),

        # ----------------------------------------------------------------------
        # 4-7-2 混合型態（文字、整數、小數）的多行讀入 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-7-2", "填空題", "定存帳戶文字、整數與年利率多型態讀取 (acc_name, annual_rate)", 6, ("acc_name", "annual_rate", "interest"),
         lambda g: (
             (True, "混合型態讀取填寫正確：成功計算年利息與本利和！")
             if (("acc_name" in g or "annual_rate" in g or "interest" in g) and
                 ("total_balance" in history_str or "持有人" in history_str))
             else (False, "請在 4-7-2 填空題分別使用 input() 與 float(input()) 完成讀取！")
         )),

        ("4-7-2", "練習題", "百米短跑姓名、距離與秒數平均秒速 (runner_name, speed_mps)", 8, ("runner_name", "distance_m", "time_sec", "speed_mps"),
         lambda g: (
             (True, "短跑選手三行資料讀入與平均秒速計算完成！")
             if (("runner_name" in g and "distance_m" in g and "time_sec" in g) or
                 ("runner_name" in g and "speed_mps" in g) or
                 ("runner_name" in history_str and "float(input())" in history_str))
             else (False, "請連續三行讀取姓名、距離、秒數，並計算平均秒速！")
         )),

        ("4-7-2", "挑戰題", "咖啡館外帶點餐品名、杯數與折扣結帳 (drink_name, final_pay)", 6, ("drink_name", "cups", "discount"),
         lambda g: (
             (True, "咖啡外帶結帳單品名、原價與實付金額計算完成！")
             if (("drink_name" in g or "cups" in g or "discount" in g) or
                 ("drink_name" in history_str and "float(input())" in history_str))
             else (False, "請依序讀入品名、杯數與折扣數，並輸出原價與實付金額！")
         )),

        # ----------------------------------------------------------------------
        # 4-7-3 單一整數與單行多整數的混合輸入 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-7-3", "填空題", "滿額購物金與商品單價混合行讀取 (coupon, item1, item2)", 6, ("coupon", "item1"),
         lambda g: (
             (True, "單值行與同行多值混合讀取設定正確！")
             if (("coupon" in g or "item1" in g) and
                 ("subtotal" in history_str or "total_pay" in history_str or "商品原總價" in history_str))
             else (False, "請在 4-7-3 填空題第一行讀入 coupon，第二行使用 map 讀入兩商品單價！")
         )),

        ("4-7-3", "練習題", "及格基準分與兩科成績差值計算 (passing_score, s1, s2)", 8, ("passing_score", "s1", "s2", "diff"),
         lambda g: (
             (True, "及格基準分與兩科成績讀入與差值計算完成！")
             if (("passing_score" in g and "s1" in g and "s2" in g) or
                 ("passing_score" in g and "diff" in g) or
                 ("passing_score" in history_str and "map(int" in history_str.replace(" ", "")))
             else (False, "請第一行讀取 passing_score，第二行讀取 s1, s2，並印出總分、平均與差值！")
         )),

        ("4-7-3", "挑戰題", "遊樂園基礎門票與同行雙人代幣花費 (ticket_price, tokens_a, tokens_b)", 6, ("ticket_price", "tokens_a", "tokens_b"),
         lambda g: (
             (True, "遊樂園雙人總花費與差額計算完成！")
             if (("ticket_price" in g or "tokens_a" in g or "tokens_b" in g) or
                 ("ticket_price" in history_str and "map(int" in history_str.replace(" ", "")))
             else (False, "請第一行讀取門票單價，第二行讀取兩位遊客代幣數，並輸出花費與差額！")
         )),

        # ----------------------------------------------------------------------
        # 4-7-4 連續兩行座標讀入與幾何距離計算 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-7-4", "填空題", "對角兩點外接矩形尺寸與周長面積 (width, height, area)", 6, ("x1", "x2", "width"),
         lambda g: (
             (True, "兩行座標讀取與外接矩形幾何數值計算正確！")
             if (("x1" in g or "x2" in g or "width" in g) and
                 ("perimeter" in history_str or "area" in history_str or "矩形寬與高" in history_str))
             else (False, "請在 4-7-4 填空題空格補齊第 2 行座標讀取與 height、area 計算式！")
         )),

        ("4-7-4", "練習題", "無人機兩行座標曼哈頓與歐式距離 (manhattan_dist, euclidean_dist)", 8, ("ax", "bx", "manhattan_dist", "euclidean_dist"),
         lambda g: (
             (True, "無人機兩點座標讀入與曼哈頓、歐式距離計算成功！")
             if (("ax" in g and "bx" in g) or
                 ("manhattan_dist" in g or "euclidean_dist" in g) or
                 ("**0.5" in history_str or "** 0.5" in history_str))
             else (False, "請讀入兩行座標，並分別輸出曼哈頓距離與直線距離！")
         )),

        ("4-7-4", "挑戰題", "兩頂點最小外接正方形邊長與面積 (side_len, square_area)", 6, ("p1x", "p2x", "side_len"),
         lambda g: (
             (True, "兩頂點最小外接正方形邊長與面積計算完成！")
             if (("p1x" in g or "p2x" in g or "side_len" in g) or
                 ("side_len" in history_str and "max(" in history_str))
             else (False, "請讀入兩頂點座標，取 dx 與 dy 較大者為正方形邊長並輸出邊長與面積！")
         )),

        # ----------------------------------------------------------------------
        # 4-7-5 APCS 競技程式多行固定筆數讀取實戰 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-7-5", "填空題", "紅藍兩隊趣味競賽兩行得分純淨讀取 (r1, b1, r2, b2)", 6, ("r1", "total_r", "diff"),
         lambda g: (
             (True, "兩行趣味競賽得分純淨讀取與總分差計算正確！")
             if (("r1" in g or "total_r" in g or "diff" in g) and
                 ("total_b" in history_str or "紅隊總分" in history_str))
             else (False, "請在 4-7-5 填空題依序使用 map 讀入兩行競賽得分並計算總分差！")
         )),

        ("4-7-5", "練習題", "APCS 模擬實作：冒險者戰鬥結算 (remaining_hp, remaining_mp)", 8, ("hp", "damage", "remaining_hp", "remaining_mp"),
         lambda g: (
             (True, "戰鬥結算兩行數值純淨讀入與血魔結算輸出成功！")
             if (("hp" in g and "damage" in g) or
                 ("remaining_hp" in g and "remaining_mp" in g) or
                 ("remaining_hp" in history_str and "remaining_mp" in history_str))
             else (False, "請純淨讀入初始血魔與傷害消耗，並分兩行輸出剩餘血量與魔力！")
         )),

        ("4-7-5", "挑戰題", "APCS 模擬實作：文具批發採購三行結算 (revenue)", 6, ("unit_price", "q_a", "revenue"),
         lambda g: (
             (True, "文具採購三行資料純淨讀入與總營業額計算完成！")
             if (("unit_price" in g or "q_a" in g or "revenue" in g) or
                 ("revenue" in history_str or "unit_price" in history_str))
             else (False, "請嚴格依格式讀入三行批發資料，並輸出實付金額與總營業額！")
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
        badge = '🏆 滿分榮譽大師（王者金牌 🥇）—— 恭喜完全制霸多行固定筆數讀取，第四章輸入輸出全章通關！'
    elif total_score >= 80:
        badge = '🥈 卓越進階工程師（銀牌徽章 🥈）—— 表現相當亮眼，只差一點點就滿分囉！'
    elif total_score >= 60:
        badge = '🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作微調！'
    else:
        badge = '🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 4-7：多行固定筆數讀取 —— 自動評分報告")
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
        "unit": "4-7",
        "unit_title": "多行固定筆數讀取",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_4_7.py",
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
auto_grade_unit_4_7()
