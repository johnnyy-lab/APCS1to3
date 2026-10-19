# ==============================================================================
# 🧪 《PythAPCS123》單元 2-1：數值型態分類（整數與浮點數） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_2_1.py
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
    """計算終端顯示寬度（全形/CJK 字元佔 2 欄）。"""
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in text)


def _pad(text, width):
    """以顯示寬度為基準補齊空白，讓全形題名在終端也能對齊。"""
    return text + " " * max(0, width - _disp_width(text))


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
NOTEBOOK_FILE = "PythAPCS123_2-1_numeric_types_int_and_float.ipynb"

def fetch_google_account_info():
    """讀取 Cell B 已完成的身分認證結果（Google Email 與暱稱）。

    鐵律：Google 認證流程只在 Cell B 執行一次，評分腳本僅讀取結果，
    絕不在此重跑 authenticate_user()，避免二次授權視窗與雙份維護飄移。"""
    env = globals()
    google_email = str(env.get("google_email") or os.environ.get("GOOGLE_EMAIL") or "").strip() or None
    google_name = str(env.get("google_name") or os.environ.get("GOOGLE_NAME") or "").strip() or None
    return google_email, google_name


def auto_grade_unit_2_1():
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

    # 題目檢驗清單：(子單元, 題型, 題目說明, 配分, 檢驗邏輯)
    test_cases = [
        # ----------------------------------------------------------------------
        # 2-1-1 數字世界的兩大宗族——整數積木（int）與浮點果汁（float） (共 24 分)
        # ----------------------------------------------------------------------
        ("2-1-1", "填空題", "整數與浮點數外觀宣告 (my_int, my_float)", 7, ("my_int", "my_float"),
         lambda g: (
             (True, "成功建立整數積木 my_int=10 與浮點果汁 my_float=10.0！")
             if (g.get("my_int") == 10 and type(g.get("my_int")) is int and
                 g.get("my_float") == 10.0 and type(g.get("my_float")) is float)
             else (
                 (False, "my_float 必須是帶有小數點的浮點數 10.0，目前型態為整數 int 喔！")
                 if (g.get("my_int") == 10 and type(g.get("my_float")) is int)
                 else (False, "找不到變數 my_int=10 或 my_float=10.0，請在底線填入 10.0 並點擊播放鍵執行！")
             )
         )),

        ("2-1-1", "練習題", "價格與重量變數 (price_int, wt_float)", 10, ("price_int", "wt_float"),
         lambda g: (
             (True, f"型態正確：price_int={g.get('price_int')} (int), wt_float={g.get('wt_float')} (float)")
             if ("price_int" in g and "wt_float" in g and
                 type(g.get("price_int")) is int and type(g.get("wt_float")) is float and
                 (g.get("price_int") in [85, 120] or g.get("price_int") > 0) and
                 (g.get("wt_float") in [2.5, 0.75] or g.get("wt_float") > 0))
             else (
                 (False, "price_int 必須是純整數（int），請勿加上小數點！")
                 if ("price_int" in g and type(g.get("price_int")) is float)
                 else (
                     (False, "wt_float 必須是帶有小數點的浮點數（float）！")
                     if ("wt_float" in g and type(g.get("wt_float")) is int)
                     else (False, "找不到變數 price_int 或 wt_float，請依練習題說明宣告並設定數值！")
                 )
             )
         )),

        ("2-1-1", "挑戰題", "圓周率與半徑宣告 (pi, r)", 7, ("pi", "r"),
         lambda g: (
             (True, f"常數宣告正確：pi={g.get('pi')} (float), r={g.get('r')} (int)")
             if ("pi" in g and "r" in g and
                 type(g.get("pi")) is float and 3.14 <= g.get("pi") <= 3.1416 and
                 type(g.get("r")) is int and g.get("r") == 5)
             else (
                 (False, "半徑 r 題目指定為整數 5，請勿寫成浮點數 5.0！")
                 if ("r" in g and type(g.get("r")) is float)
                 else (
                     (False, "圓周率 pi 必須是浮點數（如 3.14159）！")
                     if ("pi" in g and type(g.get("pi")) is int)
                     else (False, "找不到變數 pi=3.14159 或 r=5，請依挑戰題說明宣告並執行！")
                 )
             )
         )),

        # ----------------------------------------------------------------------
        # 2-1-2 查驗身分的照妖鏡——認識內建型態檢查工具 type() (共 24 分)
        # ----------------------------------------------------------------------
        ("2-1-2", "填空題", "type() 照妖鏡檢驗浮點數 num", 7, ("num",),
         lambda g: (
             (True, f"照妖鏡檢驗成功：num={g.get('num')} 身分型態為 <class 'float'>！")
             if ("num" in g and g.get("num") == 99.9 and type(g.get("num")) is float)
             else (False, "找不到變數 num=99.9，請確認在填空處填入 type 並執行！")
         )),

        ("2-1-2", "練習題", "自訂數值型態檢驗 sample_val", 10, ("sample_val",),
         lambda g: (
             (True, f"成功建立數值 sample_val={g.get('sample_val')}，其型態為 {type(g.get('sample_val')).__name__}！")
             if ("sample_val" in g and type(g.get("sample_val")) in [int, float])
             else (False, "找不到數值變數 sample_val，請建立整數或浮點數 sample_val（如 7 或 7.0）！")
         )),

        ("2-1-2", "挑戰題", "三數型態對比 (v1=0, v2=0.0, v3=-50)", 7, ("v1", "v2", "v3"),
         lambda g: (
             (True, f"三數型態透視成功：v1=0 (int), v2=0.0 (float), v3=-50 (int)！")
             if ("v1" in g and "v2" in g and "v3" in g and
                 g.get("v1") == 0 and type(g.get("v1")) is int and
                 g.get("v2") == 0.0 and type(g.get("v2")) is float and
                 g.get("v3") == -50 and type(g.get("v3")) is int)
             else (
                 (False, "v2 必須是帶小數點的浮點數 0.0，不可省略小數點！")
                 if ("v2" in g and type(g.get("v2")) is int)
                 else (
                     (False, "v1 必須是純整數 0，請勿寫成 0.0！")
                     if ("v1" in g and type(g.get("v1")) is float)
                     else (False, "找不到變數 v1=0, v2=0.0, v3=-50，請依挑戰題說明宣告並執行！")
                 )
             )
         )),

        # ----------------------------------------------------------------------
        # 2-1-3 染紅效應——整數與浮點數混合運算自動晉升為浮點數 (共 26 分)
        # ----------------------------------------------------------------------
        ("2-1-3", "填空題", "整數乘以 1.0 自動染紅晉升 (up_float = 8.0)", 7, ("up_float",),
         lambda g: (
             (True, "染紅成功！8 * 1.0 晉升為浮點數 up_float = 8.0（<class 'float'>）")
             if ("up_float" in g and g.get("up_float") == 8.0 and type(g.get("up_float")) is float)
             else (
                 (False, "up_float 目前是整數 8，請在填空處乘以浮點數 1.0 觸發晉升為 8.0！")
                 if ("up_float" in g and g.get("up_float") == 8 and type(g.get("up_float")) is int)
                 else (False, "找不到變數 up_float，請在填空處填入 1.0 並點擊播放鍵執行！")
             )
         )),

        ("2-1-3", "練習題", "整數與浮點數混合相加 mix_sum", 11, ("mix_int", "mix_float", "mix_sum"),
         lambda g: (
             (True, f"混合相加染紅成功：mix_sum = {g.get('mix_sum')}（<class 'float'>）")
             if ("mix_sum" in g and type(g.get("mix_sum")) is float and
                 "mix_int" in g and "mix_float" in g and type(g.get("mix_int")) is int and type(g.get("mix_float")) is float and
                 abs(g.get("mix_sum") - (g.get("mix_int") + g.get("mix_float"))) < 1e-9)
             else (
                 (False, "變數 mix_float 必須是浮點數（例如 0.5 或 5.0），才能示範染紅晉升效應喔！")
                 if ("mix_float" in g and type(g.get("mix_float")) is int)
                 else (
                     (False, "變數 mix_int 必須是純整數（int，例如 10 或 20）！")
                     if ("mix_int" in g and type(g.get("mix_int")) is float)
                     else (False, "找不到變數 mix_int, mix_float 或 mix_sum，請宣告 mix_int 與 mix_float 並將 mix_int + mix_float 存入 mix_sum！")
                 )
             )
         )),

        ("2-1-3", "挑戰題", "三數混合連加染紅 (ans_float = 10.0)", 8, ("ans_float", "ans"),
         lambda g: (
             (True, "三數連加染紅成功：ans_float = 10.0（整數 5 與 3 被 2.0 染紅為 float）！")
             if ("ans_float" in g and g.get("ans_float") == 10.0 and type(g.get("ans_float")) is float)
             else (
                 (False, "偵測到變數 ans = 10.0！本題已鎖定專屬變數 ans_float，請改用 ans_float = 5 + 3 + 2.0 並重新點擊播放鍵，避免變數撞名被覆蓋！")
                 if ("ans" in g and g.get("ans") == 10.0 and type(g.get("ans")) is float)
                 else (
                     (False, "計算結果目前是純整數 10，算式中請包含 2.0 浮點數讓結果自動晉升為 10.0！")
                     if (g.get("ans_float") == 10)
                     else (False, "找不到變數 ans_float，請寫出 5 + 3 + 2.0 計算並存入 ans_float！")
                 )
             )
         )),

        # ----------------------------------------------------------------------
        # 2-1-4 APCS 考場的致命失分陷阱——4.0 與 4 大不相同 (共 26 分)
        # ----------------------------------------------------------------------
        ("2-1-4", "填空題", "修正 3.0 為純整數 3 避免 WA (pure_int = 5)", 7, ("pure_int",),
         lambda g: (
             (True, "修正成功！pure_int = 3 + 2 得到純整數 5（<class 'int'>），成功避開 5.0 WA 陷阱！")
             if ("pure_int" in g and g.get("pure_int") == 5 and type(g.get("pure_int")) is int)
             else (
                 (False, "變數 pure_int 目前為浮點數 5.0！請將 3.0 修改為純整數 3，確保輸出為純整數 5！")
                 if ("pure_int" in g and (g.get("pure_int") == 5.0 or (g.get("pure_int") == 5 and type(g.get("pure_int")) is float)))
                 else (False, "找不到變數 pure_int 或數值不為 5，請填入純整數 3 並點擊播放鍵執行！")
             )
         )),

        ("2-1-4", "練習題", "長寬與周長純整數運算 (length, width)", 11, ("length", "width"),
         lambda g: (
             (True, f"長寬與周長計算正確：length={g.get('length')}, width={g.get('width')}（周長 {(g.get('length')+g.get('width'))*2}，純整數）")
             if ("length" in g and "width" in g and
                 type(g.get("length")) is int and type(g.get("width")) is int and
                 g.get("length") > 0 and g.get("width") > 0 and
                 not any(isinstance(g.get(k), float) for k in ["perimeter", "peri", "perim"] if k in g))
             else (
                 (False, "題目要求輸入都是整數，length 與 width 必須是純整數（int），請勿加上小數點！")
                 if (("length" in g and type(g.get("length")) is float) or ("width" in g and type(g.get("width")) is float))
                 else (
                     (False, "檢測到周長變數為浮點數，在 APCS 輸出帶小數點會被判 WA 喔！請確保計算過程不使用浮點數！")
                     if any(isinstance(g.get(k), float) for k in ["perimeter", "peri", "perim"] if k in g)
                     else (False, "找不到變數 length 或 width，請依題目宣告長度與寬度純整數！")
                 )
             )
         )),

        ("2-1-4", "挑戰題", "破除 100.0 浮點陷阱維持整數 score", 8, ("score",),
         lambda g: (
             (True, "完美修正！score = 100 為純正整數（<class 'int'>），成功避開 APCS 考場的 100.0 WA 陷阱！")
             if ("score" in g and g.get("score") == 100 and type(g.get("score")) is int)
             else (
                 (False, "變數 score 目前仍是浮點數 100.0！請不要乘以 1.0，改用純整數 100 * 1 或 score = 100，確保輸出為純整數！")
                 if ("score" in g and (g.get("score") == 100.0 or (g.get("score") == 100 and type(g.get("score")) is float)))
                 else (False, "找不到變數 score 或數值不為 100，請設定純整數 score = 100 並點擊播放鍵執行！")
             )
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
        badge = "🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通整數與浮點數本質，考場零 WA！"
    elif total_score >= 80:
        badge = "🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，型態觀念清晰扎實！"
    elif total_score >= 60:
        badge = "🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作微調！"
    else:
        badge = "🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！"

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 2-1：數值型態分類（整數與浮點數） —— 自動評分報告")
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
        for l in lines:
            print(l)
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
    # --------------------------------------------------------------------------
    log_data = {
        "unit": "2-1",
        "unit_title": "數值型態分類（整數與浮點數）",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_2_1.py",
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
auto_grade_unit_2_1()
