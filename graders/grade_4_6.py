# ==============================================================================
# 🧪 《PythAPCS123》單元 4-6：單行多筆輸入 split() 與 map() —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_4_6.py
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
NOTEBOOK_FILE = "PythAPCS123_4-6_single_line_multiple_inputs_split_map.ipynb"

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


def auto_grade_unit_4_6(env=None):
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
        # 4-6-1 字串拆解 split() 與多變數解包 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-6-1", "填空題", "雙人飛行員代號解包 (input().split())", 6, ("pilot1", "pilot2"),
         lambda g: (
             (True, "split() 解包設定正確：成功存入 pilot1 與 pilot2！")
             if (("split()" in history_str or "split" in history_str) and
                 ("pilot1" in g or "pilot2" in g or "pilot1" in history_str))
             else (False, "請在 4-6-1 填空題空格填入 split 方法並在 print 印出 pilot2！")
         )),

        ("4-6-1", "練習題", "超商進貨單行雙物品輸入與變數交換 (Swap)", 8, ("item1", "item2"),
         lambda g: (
             (True, "單行雙物品讀入與交換輸出成功！")
             if (("item1" in g and "item2" in g) and
                 ("split" in history_str) and
                 ("➔" in history_str or "->" in history_str or "," in history_str))
             else (False, "請使用 item1, item2 = input().split() 讀入並交換後輸出！")
         )),

        ("4-6-1", "挑戰題", "台灣高鐵三站名單行輸入與路線圖播報", 6, ("station1", "station2", "station3"),
         lambda g: (
             (True, "高鐵三站名單行讀入與路線排版成功！")
             if (("station1" in g and "station2" in g and "station3" in g) or
                 ("station1" in history_str and "split" in history_str))
             else (False, "請在同一行讀入三個站名，並以箭頭符號輸出路線！")
         )),

        # ----------------------------------------------------------------------
        # 4-6-2 map(int, input().split()) 單行多個整數轉換 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-6-2", "填空題", "文具店單價與數量整數映射 (map, int)", 6, ("price",),
         lambda g: (
             (True, "map 與 int 整數映射填寫正確！")
             if (("map(int" in history_str.replace(" ", "") or "price" in g) and
                 ("total_price" in history_str or "結帳明細" in history_str))
             else (False, "請在 4-6-2 填空題空格填入 map 與 int 進行整數轉換！")
         )),

        ("4-6-2", "練習題", "矩形長寬單行讀取與周長面積計算 (length, width)", 8, ("length", "width"),
         lambda g: (
             (True, f"矩形幾何數值計算完成：length={g.get('length')}, width={g.get('width')}！")
             if (("length" in g and "width" in g) and
                 ("map(int" in history_str.replace(" ", "") or "map" in history_str))
             else (False, "請使用 map(int, input().split()) 讀入長寬，並印出周長與面積！")
         )),

        ("4-6-2", "挑戰題", "射擊大賽選手得分分差分析 (score1, score2, abs)", 6, ("score1", "score2"),
         lambda g: (
             (True, "選手得分單行整數讀入與分差計算完成！")
             if (("score1" in g and "score2" in g) or
                 ("map(int" in history_str.replace(" ", "") and "abs" in history_str))
             else (False, "請在同一行讀入 score1 與 score2，並使用 abs 計算分差！")
         )),

        # ----------------------------------------------------------------------
        # 4-6-3 三個及以上整數的單行讀取 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-6-3", "填空題", "段考三科成績解包與總分平均計算 (math, total_score)", 6, ("chinese", "total_score"),
         lambda g: (
             (True, "三科成績映射與計算設定正確！")
             if (("chinese" in g or "total_score" in g or "math" in history_str) and
                 ("map(int" in history_str.replace(" ", "") or "map" in history_str))
             else (False, "請在 4-6-3 填空題補齊變數 math 與總分算式！")
         )),

        ("4-6-3", "練習題", "單行三整數讀入與全距計算 (max - min)", 8, (),
         lambda g: (
             (True, "單行三整數讀入與全距計算成功！")
             if (("map(int" in history_str.replace(" ", "")) and
                 ("max" in history_str and "min" in history_str))
             else (False, "請使用 map(int, input().split()) 讀入三整數，並印出全距 max - min！")
         )),

        ("4-6-3", "挑戰題", "APCS 座標曼哈頓距離計算 (x1, y1, x2, y2)", 6, ("x1", "x2"),
         lambda g: (
             (True, "曼哈頓距離四座標讀入與計算完成！")
             if (("x1" in g or "x2" in g or "map(int" in history_str.replace(" ", "")) and
                 ("abs(" in history_str.replace(" ", "")))
             else (False, "請在同一行讀入四個座標，並利用 abs() 計算曼哈頓距離！")
         )),

        # ----------------------------------------------------------------------
        # 4-6-4 浮點數轉換 map(float, input().split()) (共 20 分)
        # ----------------------------------------------------------------------
        ("4-6-4", "填空題", "雙裁判評分浮點數映射 (map(float, ...))", 6, ("score1",),
         lambda g: (
             (True, "浮點數映射設定正確：map(float, ...)！")
             if (("map(float" in history_str.replace(" ", "") or "score1" in g) and
                 ("avg_score" in history_str or "官方計分板" in history_str))
             else (False, "請在 4-6-4 填空題空格填入 float 與相加算式！")
         )),

        ("4-6-4", "練習題", "健康檢查站單行 BMI 計算 (height, weight)", 8, ("height", "weight"),
         lambda g: (
             (True, "單行浮點數身高體重讀入與 BMI 計算完成！")
             if (("height" in g and "weight" in g) and
                 ("map(float" in history_str.replace(" ", "") or "float" in history_str))
             else (False, "請使用 map(float, input().split()) 讀入身高體重並輸出 BMI！")
         )),

        ("4-6-4", "挑戰題", "幾何同心圓環面積計算 (R, r)", 6, (),
         lambda g: (
             (True, "同心圓環兩半徑讀取與面積計算完成！")
             if (("map(float" in history_str.replace(" ", "")) and
                 ("3.14" in history_str or "**2" in history_str or "** 2" in history_str))
             else (False, "請在同一行讀入大圓與小圓半徑，並計算圓環面積！")
         )),

        # ----------------------------------------------------------------------
        # 4-6-5 實戰 APCS / OJ 考題情境與除錯 (共 20 分)
        # ----------------------------------------------------------------------
        ("4-6-5", "填空題", "三數乘積程式除錯特訓 (map(int, ...))", 6, ("n1",),
         lambda g: (
             (True, "map(int, ...) 除錯修復完成！")
             if (("map(int" in history_str.replace(" ", "") or "n1" in g) and
                 ("乘積結果" in history_str or "result" in history_str))
             else (False, "請在 4-6-5 填空題空格填入 map 與 int 修復型態錯誤！")
         )),

        ("4-6-5", "練習題", "APCS 基礎模擬實作：均分糖果問題 (candies, students)", 8, ("candies", "students"),
         lambda g: (
             (True, "糖果均分問題單行輸入與商數餘數輸出正確！")
             if (("candies" in g and "students" in g) or
                 ("map(int" in history_str.replace(" ", "") and ("//" in history_str and "%" in history_str)))
             else (False, "請使用 map(int, input().split()) 讀入糖果與人數，並輸出 // 與 %！")
         )),

        ("4-6-5", "挑戰題", "APCS 基礎模擬實作：三角形邊長極端差 (max - min)", 6, (),
         lambda g: (
             (True, "三角形三邊長讀入與極端差計算完成！")
             if (("map(int" in history_str.replace(" ", "")) and
                 ("max(" in history_str and "min(" in history_str))
             else (False, "請單行讀入三角形三邊長，並輸出最長邊與最短邊差值！")
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
        badge = '🏆 滿分榮譽大師（王者金牌 🥇）—— 恭喜完全降伏 split() 與 map()，解鎖 APCS 核心輸入技法！'
    elif total_score >= 80:
        badge = '🥈 卓越進階工程師（銀牌徽章 🥈）—— 表現相當亮眼，只差一點點就滿分囉！'
    elif total_score >= 60:
        badge = '🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作微調！'
    else:
        badge = '🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 4-6：單行多筆輸入 split() 與 map() —— 自動評分報告")
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
        "unit": "4-6",
        "unit_title": "單行多筆輸入 split() 與 map()",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_4_6.py",
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
auto_grade_unit_4_6()
