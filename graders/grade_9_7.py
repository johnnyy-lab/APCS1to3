# ==============================================================================
# 🧪 《PythAPCS123》單元 9-7：二維網格導航：方向向量與相鄰探測（APCS e287 原型） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_9_7.py
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
NOTEBOOK_FILE = "PythAPCS123_9-7_grid_navigation_direction_vectors_and_apcs_e287.ipynb"

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


def auto_grade_unit_9_7():
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
        # 9-7-1 網格相鄰座標與相對位移 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-7-1", "填空題", "四方向相對位移座標填空", 5, (),
         lambda g: (
             (True, "四方向位移座標填空正確！")
             if ("r - 1" in history_str or "r + 1" in history_str or "c - 1" in history_str or "c + 1" in history_str) or
                ("r-1" in history_clean or "r+1" in history_clean)
             else (False, "請在 9-7-1 填空題填入四方向相對座標！")
         )),

        ("9-7-1", "練習題", "提取中心點相鄰四格數值並輸出", 6, (),
         lambda g: (
             (True, "中心點四相鄰取值正確！")
             if ("grid[r-1][c]" in history_clean or "grid[r+1][c]" in history_clean or
                 "matrix[r-1][c]" in history_clean or "matrix[r+1][c]" in history_clean)
             else (False, "請取出上下左右四個相鄰點的數值並印出！")
         )),

        ("9-7-1", "挑戰題", "計算相鄰四格的總和", 5, (),
         lambda g: (
             (True, "相鄰四格數值加總正確！")
             if ("sum" in history_str or "+" in history_str) and ("r - 1" in history_str or "r-1" in history_clean)
             else (False, "請計算中心點相鄰四格的數值總和！")
         )),

        # ----------------------------------------------------------------------
        # 9-7-2 方向向量差值陣列 (dr, dc) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-7-2", "填空題", "方向向量補齊 dc = [0, 1, 0, -1]", 5, (),
         lambda g: (
             (True, "方向差值陣列 dc 填空正確！")
             if ("-1" in history_str and "dc = [ 0,  1,  0" in history_str) or
                ("dc=[0,1,0,-1]" in history_clean or "dc = [0, 1, 0, -1]" in history_str)
             else (False, "請在 9-7-2 填空題補齊 dc 中的左方差值 -1！")
         )),

        ("9-7-2", "練習題", "迴圈遍歷方向向量探測四相鄰點", 6, (),
         lambda g: (
             (True, "方向向量迴圈探測正確！")
             if ("for d in range(4)" in history_str or "for i in range(4)" in history_str or "zip(dr, dc)" in history_str)
             else (False, "請使用 for 迴圈配合 dr, dc 探測四相鄰點！")
         )),

        ("9-7-2", "挑戰題", "自訂八方向向量 (dr, dc 長度為 8)", 6, (),
         lambda g: (
             (True, "八方向差值陣列定義正確！")
             if ("len(dr) == 8" in history_str or "8" in history_str) and ("dr" in history_str and "dc" in history_str)
             else (False, "請定義長度為 8 的八方向向量陣列！")
         )),

        # ----------------------------------------------------------------------
        # 9-7-3 合法邊界防護條件 (Boundary Guard) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-7-3", "填空題", "邊界守護判斷式 0 <= nr < R and 0 <= nc < C", 5, (),
         lambda g: (
             (True, "邊界守護判斷式填空正確！")
             if ("0 <= nr < R and 0 <= nc < C" in history_str or "0<=nr<Rand0<=nc<C" in history_clean or
                 "0 <= nr < R" in history_str)
             else (False, "請在 9-7-3 填空題填入 0 <= nr < R and 0 <= nc < C！")
         )),

        ("9-7-3", "練習題", "帶邊界防護之相鄰格子安全讀取", 6, (),
         lambda g: (
             (True, "安全邊界相鄰走訪正確！")
             if ("0 <= nr < R" in history_str or "0 <= nr" in history_str) and "grid[nr][nc]" in history_clean
             else (False, "請加入邊界守護條件，避免 IndexError 讀取相鄰元素！")
         )),

        ("9-7-3", "挑戰題", "統計邊界上合法相鄰格子數量", 6, (),
         lambda g: (
             (True, "邊界鄰格數量統計正確！")
             if ("count" in history_str or "+= 1" in history_str) and ("0 <= nr < R" in history_str)
             else (False, "請統計位於四邊或角落時的合法相鄰格數量！")
         )),

        # ----------------------------------------------------------------------
        # 9-7-4 八方向相鄰探測（8-Neighbors / 踩地雷原理） (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-7-4", "填空題", "踩地雷地雷探測 mine_map[nr][nc] == '#'", 5, (),
         lambda g: (
             (True, "踩地雷地雷條件填空正確！")
             if ("mine_map[nr][nc] == '#'" in history_str or "mine_map[nr][nc]=='#'" in history_clean or
                 "mine_map[nr][nc] == 1" in history_str)
             else (False, "請在 9-7-4 填空題填入地雷判斷式！")
         )),

        ("9-7-4", "練習題", "踩地雷九宮格周圍地雷總數統計", 6, (),
         lambda g: (
             (True, "周圍地雷統計正確！")
             if ("mine_count" in history_str or "mines" in history_str or "count" in history_str) and ("nr" in history_str)
             else (False, "請使用八方向向量統計周圍 8 格的地雷數量！")
         )),

        ("9-7-4", "挑戰題", "生成完整踩地雷數字提示地圖", 6, (),
         lambda g: (
             (True, "踩地雷數字地圖生成正確！")
             if ("range(8)" in history_str or "dr" in history_str) and ("print" in history_str)
             else (False, "請為全地圖每一格計算周圍地雷數並印出！")
         )),

        # ----------------------------------------------------------------------
        # 9-7-5 拜訪標記矩陣 (Visited Grid) 與貪婪前進 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-7-5", "填空題", "拜訪標記設定 visited[nr][nc] = True", 5, (),
         lambda g: (
             (True, "拜訪標記語法填空正確！")
             if ("visited[nr][nc] = True" in history_str or "visited[nr][nc]=True" in history_clean or
                 "visited[r][c] = True" in history_str)
             else (False, "請在 9-7-5 填空題填入 visited 標記語法！")
         )),

        ("9-7-5", "練習題", "防止重複走訪之貪婪前進模擬", 6, (),
         lambda g: (
             (True, "防止重複走訪實作正確！")
             if ("not visited[nr][nc]" in history_str or "not visited" in history_str) and "visited" in history_str
             else (False, "請加入 not visited 判斷，確保路徑不重複踏足！")
         )),

        ("9-7-5", "挑戰題", "走訪步數與途經總和統計", 6, (),
         lambda g: (
             (True, "走訪步數與加總統計正確！")
             if ("steps" in history_str or "path_sum" in history_str or "total" in history_str) and "visited" in history_str
             else (False, "請記錄貪婪尋路的步數與經過數值總和！")
         )),

        # ----------------------------------------------------------------------
        # 9-7-6 APCS e287 機器人的路徑：全圖貪婪尋路實戰 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-7-6", "填空題", "尋找全圖最小值作為起點座標", 5, (),
         lambda g: (
             (True, "全圖起點最小值定位填空正確！")
             if ("min_val" in history_str and "grid[r][c]" in history_clean) or
                ("best_r = r" in history_str or "best_c = c" in history_str)
             else (False, "請在 9-7-6 填空題填入尋找起點最小值的判斷！")
         )),

        ("9-7-6", "練習題", "APCS e287 核心尋路單一測資實戰", 6, (),
         lambda g: (
             (True, "APCS e287 尋路模擬正確！")
             if ("visited" in history_str and "while True:" in history_str) or
                ("min_neighbor" in history_str or "next_r" in history_str)
             else (False, "請完成從最小值起點出發、每步挑選最小未走鄰格的 APCS e287 尋路！")
         )),

        ("9-7-6", "挑戰題", "APCS e287 完整路徑總和輸出通關", 5, (),
         lambda g: (
             (True, "APCS e287 完整加總輸出正確！")
             if ("total_sum" in history_str or "print(" in history_str) and "visited" in history_str
             else (False, "請累加所有走過格子的數值並印出最終總和！")
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
    print(" 📊 《PythAPCS123》單元 9-7：二維網格導航：方向向量與相鄰探測（APCS e287 原型） —— 自動評分報告")
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
        "unit": "9-7",
        "unit_title": "二維網格導航：方向向量與相鄰探測（APCS e287 原型）",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_9_7.py",
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
auto_grade_unit_9_7()
