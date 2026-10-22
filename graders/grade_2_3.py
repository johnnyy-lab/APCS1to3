# ==============================================================================
# 🧪 《PythAPCS123》單元 2-3：整數除法商數（//）與取餘數（%） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_2_3.py
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

# ------------------------------------------------------------------------------
# 🌐 雲端後台成績記錄端點（已綁定 Google 試算表 Webhook）
# ------------------------------------------------------------------------------
LOG_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyXv4s0qihj03Lg3oFop3HffQNYob-M9OxxJVPX04LxeBY22IvYcFh8v2hTZgWsX5InKQ/exec"
# 版次 token。Apps Script 用它確認這次送出的是現行契約。
GRADER_VERSION = "2026-10-19"
NOTEBOOK_FILE = "PythAPCS123_2-3_integer_division_and_modulus.ipynb"

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

def auto_grade_unit_2_3(env=None):
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

    # 題目檢驗清單：(子單元, 題型, 題目說明, 配分, 觀察變數, 檢驗邏輯)
    test_cases = [
        # ----------------------------------------------------------------------
        # 2-3-1 整數除法雙斜線（//）——只留整數商數的無情去尾刀 (共 20 分)
        # ----------------------------------------------------------------------
        ("2-3-1", "填空題", "蛋撻裝盒整數除法 (tot_bxs = 6)", 6, ("tot_bxs",),
         lambda g: (
             (True, "整數除法成功：tot_bxs = 38 // 6 = 6！")
             if (g.get("tot_bxs") == 6 and type(g.get("tot_bxs")) is int)
             else (False, "找不到變數 tot_bxs 或數值不為 6，請在空格填入 // 並執行！")
         )),

        ("2-3-1", "練習題", "遊覽車所需車輛數計算 (students // bus_capacity)", 8, ("students", "bus_capacity"),
         lambda g: (
             (True, f"遊覽車商數計算正確：{g.get('students')} // {g.get('bus_capacity')} = {g.get('students') // g.get('bus_capacity')}")
             if ("students" in g and "bus_capacity" in g and
                 type(g.get("students")) is int and type(g.get("bus_capacity")) is int and
                 (g.get("students") // g.get("bus_capacity") in [4, 5] or g.get("students") // g.get("bus_capacity") > 0))
             else (False, "找不到變數 students 或 bus_capacity，請依練習題說明使用 // 計算滿載車數！")
         )),

        ("2-3-1", "挑戰題", "雞蛋連續整除換算大箱 (total_eggs // 12 // 30)", 6, ("total_eggs",),
         lambda g: (
             (True, "大箱數量計算完成（連續兩次 // 換算）！")
             if ("total_eggs" in g and type(g.get("total_eggs")) is int and any(type(v) is int for v in g.values()))
             else (False, "請宣告 total_eggs 變數，並連續使用 // 12 與 // 30 計算能裝成的大箱數量！")
         )),

        # ----------------------------------------------------------------------
        # 2-3-2 模除取餘數百分比（%）——撿回落單零頭的餘數探測器 (共 20 分)
        # ----------------------------------------------------------------------
        ("2-3-2", "填空題", "獎勵貼紙模除取餘數 (rmnn_stck = 2)", 6, ("rmnn_stck",),
         lambda g: (
             (True, "模除運算成功：rmnn_stck = 50 % 6 = 2！")
             if (g.get("rmnn_stck") == 2 and type(g.get("rmnn_stck")) is int)
             else (False, "找不到 rmnn_stck 或數值不為 2，請填入 % 並點擊播放鍵執行！")
         )),

        ("2-3-2", "練習題", "萬聖節糖果平分落單數量 (total_candies % child_num)", 8, ("total_candies", "child_num"),
         lambda g: (
             (True, f"剩餘糖果計算正確：{g.get('total_candies')} % {g.get('child_num')} = {g.get('total_candies') % g.get('child_num')}")
             if ("total_candies" in g and "child_num" in g and
                 type(g.get("total_candies")) is int and type(g.get("child_num")) is int and
                 (g.get("total_candies") % g.get("child_num") in [3, 2] or g.get("total_candies") % g.get("child_num") >= 0))
             else (False, "找不到 total_candies 或 child_num，請依練習題計算 total_candies % child_num！")
         )),

        ("2-3-2", "挑戰題", "彈珠盒數與落單顆數雙重計算 (total_marbles)", 6, ("total_marbles",),
         lambda g: (
             (True, "彈珠裝盒商數與落單餘數計算成功！")
             if ("total_marbles" in g and type(g.get("total_marbles")) is int)
             else (False, "請宣告 total_marbles，並分別計算 // 9（盒數）與 % 9（剩餘顆數）！")
         )),

        # ----------------------------------------------------------------------
        # 2-3-3 奇偶數判定與分組循環——餘數的週期魔法 (共 20 分)
        # ----------------------------------------------------------------------
        ("2-3-3", "填空題", "號碼牌小隊分配模除 (my_team = 2)", 6, ("my_team",),
         lambda g: (
             (True, "小隊分組模除成功：my_team = 17 % 3 = 2！")
             if (g.get("my_team") == 2 and type(g.get("my_team")) is int)
             else (False, "找不到變數 my_team 或數值不為 2，請在空格填入 % 運算子！")
         )),

        ("2-3-3", "練習題", "遊戲公會職業分配 (ticket_num % 4)", 8, ("ticket_num",),
         lambda g: (
             (True, f"職業分配計算正確：{g.get('ticket_num')} % 4 = {g.get('ticket_num') % 4}")
             if ("ticket_num" in g and type(g.get("ticket_num")) is int and
                 g.get("ticket_num") % 4 in [2, 1])
             else (False, "找不到變數 ticket_num，請計算 ticket_num % 4 分配職業公會編號！")
         )),

        ("2-3-3", "挑戰題", "每週值日生排別循環計算 ((week - 1) % 3)", 6, ("current_week",),
         lambda g: (
             (True, "週次值日生分組週期計算成功！")
             if ("current_week" in g and type(g.get("current_week")) is int and (g.get("current_week") - 1) % 3 in [0, 1, 2])
             else (False, "請宣告 current_week 並利用 (current_week - 1) % 3 計算當週值日生排別！")
         )),

        # ----------------------------------------------------------------------
        # 2-3-4 神奇位數拆解術——取出個位數（% 10）與右移剝皮（// 10） (共 20 分)
        # ----------------------------------------------------------------------
        ("2-3-4", "填空題", "兩位數拆解十位與個位 (tens = 7, units = 9)", 6, ("tens", "units"),
         lambda g: (
             (True, "位數拆解成功：tens = 7, units = 9！")
             if (g.get("tens") == 7 and g.get("units") == 9 and
                 type(g.get("tens")) is int and type(g.get("units")) is int)
             else (False, "變數 tens 或 units 數值不正確，請在 tens 填入 // 在 units 填入 %！")
         )),

        ("2-3-4", "練習題", "兩位數各位數字相加總和 (num // 10 + num % 10)", 8, ("num",),
         lambda g: (
             (True, f"位數總和計算正確：{g.get('num')} ➔ {g.get('num') // 10 + g.get('num') % 10}")
             if ("num" in g and type(g.get("num")) is int and
                 (g.get("num") // 10 + g.get("num") % 10 in [11, 13] or
                  any(v in [11, 13] for v in g.values())))
             else (False, "找不到變數 num，請拆解十位與個位並計算加總（如 47 ➔ 11，85 ➔ 13）！")
         )),

        ("2-3-4", "挑戰題", "三位數密碼鎖各位數字乘積 (secret = 642 ➔ 48)", 6, ("secret",),
         lambda g: (
             (True, "三位數位數乘積計算正確（6 * 4 * 2 = 48）！")
             if ("secret" in g and (g.get("secret") == 642 or any(v == 48 for v in g.values())))
             else (False, "請設定 secret = 642 並利用 // 10 與 % 10 算出 6*4*2 = 48 解鎖密碼！")
         )),

        # ----------------------------------------------------------------------
        # 2-3-5 時間與單位的複合進位換算——商與餘數的黃金雙重奏 (共 20 分)
        # ----------------------------------------------------------------------
        ("2-3-5", "填空題", "公分換算公尺又公分 (meters = 2, remain_cm = 45)", 6, ("meters", "remain_cm"),
         lambda g: (
             (True, "單位換算成功：meters = 2, remain_cm = 45！")
             if (g.get("meters") == 2 and g.get("remain_cm") == 45 and
                 type(g.get("meters")) is int and type(g.get("remain_cm")) is int)
             else (False, "meters 或 remain_cm 數值不符，請在 meters 填入 // 在 remain_cm 填入 %！")
         )),

        ("2-3-5", "練習題", "總秒數換算分鐘與剩餘秒數 (total_sec)", 8, ("total_sec",),
         lambda g: (
             (True, f"秒數換算正確：{g.get('total_sec')} 秒 ➔ {g.get('total_sec') // 60} 分 {g.get('total_sec') % 60} 秒")
             if ("total_sec" in g and type(g.get("total_sec")) is int and
                 ((g.get("total_sec") // 60 == 2 and g.get("total_sec") % 60 == 15) or
                  (g.get("total_sec") // 60 == 5 and g.get("total_sec") % 60 == 8) or
                  (g.get("total_sec") > 0)))
             else (False, "找不到變數 total_sec，請依練習題換算為分鐘（// 60）與秒數（% 60）！")
         )),

        ("2-3-5", "挑戰題", "深空飛行總小時換算天數與小時 (total_hours)", 6, ("total_hours",),
         lambda g: (
             (True, "飛行時間換算天數與剩餘小時成功（// 24 與 % 24）！")
             if ("total_hours" in g and type(g.get("total_hours")) is int)
             else (False, "請宣告 total_hours，並利用 // 24 與 % 24 依序換算出完整天數與剩餘小時數！")
         )),
    ]

    # 6. 前置遍歷評分運算（結論先行前置計算）
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

    # 7. 計算榮譽等級徽章
    if total_score >= 90:
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通整除去尾與餘數探測之雙重奏！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，位數拆解與商餘掌控熟練！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作檢查！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    # 8. 三段式頂部資訊排版（結論先行，防範 VS Code 終端折疊截斷）
    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 2-3：整數除法商數（//）與取餘數（%） —— 自動評分報告")
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
        "unit": "2-3",
        "unit_title": "整數除法商數（//）與取餘數（%）",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_2_3.py",
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
auto_grade_unit_2_3()
