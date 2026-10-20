# ==============================================================================
# 🧪 《PythAPCS123》單元 9-1：二維陣列概念與座標元素存取 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_9_1.py
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
NOTEBOOK_FILE = "PythAPCS123_9-1_2d_array_concept_and_coordinate_access.ipynb"

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


def auto_grade_unit_9_1(env=None):
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
        # 9-1-1 二維陣列物理模型與座位宣告 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-1-1", "填空題", "宣告 3x2 座位表 seating", 5, ("seating",),
         lambda g: (
             (True, "seating 3x2 陣列宣告正確！")
             if ("seating" in g and isinstance(g.get("seating"), list) and len(g.get("seating")) == 3 and
                 len(g.get("seating")[0]) == 2 and "小明" in str(g.get("seating"))) or
                ("seating" in history_str and "小明" in history_str and "小強" in history_str)
             else (False, "請在 9-1-1 填空題完成 seating 3x2 座位表宣告！")
         )),

        ("9-1-1", "練習題", "手動宣告 2x3 整數陣列 grid 並印出兩列", 6, ("grid",),
         lambda g: (
             (True, "grid 2x3 整數陣列建立與兩列輸出正確！")
             if ("grid" in g and isinstance(g.get("grid"), list) and len(g.get("grid")) == 2 and
                 g.get("grid")[0] == [1, 2, 3] and g.get("grid")[1] == [4, 5, 6]) or
                ("[1, 2, 3]" in history_str and "[4, 5, 6]" in history_str) or
                ("grid[0]" in history_clean and "grid[1]" in history_clean)
             else (False, "請建立 2x3 整數陣列 grid = [[1, 2, 3], [4, 5, 6]] 並分別印出第 0 與 1 列！")
         )),

        ("9-1-1", "挑戰題", "2x4 巴士座位分佈 bus_seats", 5, ("bus_seats",),
         lambda g: (
             (True, "2x4 巴士座位陣列宣告與印出正確！")
             if ("bus_seats" in g and isinstance(g.get("bus_seats"), list) and len(g.get("bus_seats")) == 2 and len(g.get("bus_seats")[0]) == 4) or
                ("bus_seats" in history_str and ("Empty" in history_str or "empty" in history_str or "print" in history_str))
             else (False, "請宣告 2x4 的字串陣列 bus_seats 並依序印出兩排座位！")
         )),

        # ----------------------------------------------------------------------
        # 9-1-2 網格尺寸掌握：R 與 C (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-1-2", "填空題", "長度函式計算 R, C 與 total_cells", 5, ("R", "C", "total_cells"),
         lambda g: (
             (True, "尺寸測量與總格子數計算正確！")
             if (g.get("R") == 3 and g.get("C") == 4 and g.get("total_cells") == 12) or
                ("len(map_data)" in history_clean and "len(map_data[0])" in history_clean)
             else (False, "請在 9-1-2 填空題填入 len(map_data) 與 len(map_data[0])！")
         )),

        ("9-1-2", "練習題", "計算矩陣維度 R, C 與格式化輸出", 6, (),
         lambda g: (
             (True, "矩陣維度 R, C 計算與格式化字串輸出正確！")
             if ("維度:" in history_str or ("R = len(matrix)" in history_str and "C = len(matrix[0])" in history_str)) or
                ("3列2行" in history_str or "6" in history_str)
             else (False, "請計算 matrix 的 R 與 C，並輸出『維度: R列C行, 總數: 總數值』！")
         )),

        ("9-1-2", "挑戰題", "棋盤方陣判定 (R == C)", 6, (),
         lambda g: (
             (True, "方陣網格判定邏輯正確！")
             if ("方陣網格: True" in history_str or "R == C" in history_clean or "R==C" in history_clean)
             else (False, "請測量 8x8 棋盤尺寸，判斷 R == C 並輸出『方陣網格: True』！")
         )),

        # ----------------------------------------------------------------------
        # 9-1-3 整列提取 vs 單格存取 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-1-3", "填空題", "整列提取 row_1 與單格 student", 5, ("row_1", "student"),
         lambda g: (
             (True, "整列 row_1 與單格 student 存取正確！")
             if (g.get("row_1") == ["David", "Eva", "Frank"] and g.get("student") == "Frank") or
                ("classroom[1]" in history_clean and "classroom[1][2]" in history_clean)
             else (False, "請在 9-1-3 填空題填入 classroom[1] 與 classroom[1][2]！")
         )),

        ("9-1-3", "練習題", "成績矩陣第 0 列總和與單格提取", 6, (),
         lambda g: (
             (True, "第 0 列總和與 grades[2][1] 取值正確！")
             if ("sum(grades[0])" in history_clean or "60" in history_str) and
                ("grades[2][1]" in history_clean or "80" in history_str)
             else (False, "請計算 sum(grades[0]) 並取出 grades[2][1] 印出！")
         )),

        ("9-1-3", "挑戰題", "水果清單第 1 列長度與成員檢查", 6, (),
         lambda g: (
             (True, "第 1 列長度統計與 in 關鍵字檢查正確！")
             if ("芭樂" in history_str and ("in items[1]" in history_clean or "len(items[1])" in history_clean or "True" in history_str))
             else (False, "請印出 items[1] 的長度，並檢查 '芭樂' 是否在 items[1] 中！")
         )),

        # ----------------------------------------------------------------------
        # 9-1-4 座標定位存取：grid[r][c] (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-1-4", "填空題", "井字棋盤四個角落 corners", 5, ("corners",),
         lambda g: (
             (True, "井字棋盤四角座標取值正確！")
             if (g.get("corners") == ["X", "O", "O", "X"]) or
                ("board[0][0]" in history_clean and "board[0][2]" in history_clean and
                 "board[2][0]" in history_clean and "board[2][2]" in history_clean)
             else (False, "請在 9-1-4 填空題填入四個角落座標 (0,0), (0,2), (2,0), (2,2)！")
         )),

        ("9-1-4", "練習題", "數值矩陣四角加總 corner_sum", 6, ("corner_sum",),
         lambda g: (
             (True, "四角落元素加總計算正確！")
             if (g.get("corner_sum") == 20 or "四角總和: 20" in history_str or
                 ("matrix_data[0][0]" in history_clean and "matrix_data[2][2]" in history_clean) or
                 ("data[0][0]" in history_clean and "data[2][2]" in history_clean))
             else (False, "請計算 matrix_data 四個角落元素的總和（預期為 20）！")
         )),

        ("9-1-4", "挑戰題", "十字中心五格數值總和", 6, (),
         lambda g: (
             (True, "十字中心與上下左右五格加總正確！")
             if ("(1, 1)" in history_str or "matrix[1][1]" in history_clean or
                 ("matrix[0][1]" in history_clean and "matrix[2][1]" in history_clean))
             else (False, "請加總中心點 (1,1) 與上下左右四格的數值！")
         )),

        # ----------------------------------------------------------------------
        # 9-1-5 網格元素原地修改：grid[r][c] = val (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-1-5", "填空題", "庫存網格修改 inventory[0][1] = 50", 5, ("inventory",),
         lambda g: (
             (True, "庫存單格原地修改正確！")
             if (g.get("inventory") and g.get("inventory")[0][1] == 50) or
                ("inventory[0][1]=50" in history_clean or "inventory[0][1] = 50" in history_str)
             else (False, "請在 9-1-5 填空題完成 inventory[0][1] = 50！")
         )),

        ("9-1-5", "練習題", "3x3 全 0 矩陣三點原地修改 (0,0), (1,1), (2,2)", 6, ("grid",),
         lambda g: (
             (True, "三處座標原地賦值正確！")
             if (g.get("grid") and g.get("grid")[0][0] == 1 and g.get("grid")[1][1] == 5 and g.get("grid")[2][2] == 9) or
                ("grid[0][0]=1" in history_clean and "grid[1][1]=5" in history_clean and "grid[2][2]=9" in history_clean) or
                ("[1, 0, 0]" in history_str and "[0, 5, 0]" in history_str and "[0, 0, 9]" in history_str)
             else (False, "請將 grid 的 (0,0) 改為 1、(1,1) 改為 5、(2,2) 改為 9！")
         )),

        ("9-1-5", "挑戰題", "打地鼠地圖三處冒頭原地替換為 'M'", 6, (),
         lambda g: (
             (True, "打地鼠地圖三處座標原地修改為 'M' 正確！")
             if ("grid[0][3] = 'M'" in history_str or 'grid[0][3] = "M"' in history_str or
                 'grid[1][1] = "M"' in history_str or "M" in history_str)
             else (False, "請將 (0,3), (1,1), (2,0) 原地修改為 'M' 並印出地圖！")
         )),

        # ----------------------------------------------------------------------
        # 9-1-6 負向索引定位與維度混淆防禦 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-1-6", "填空題", "負向索引存取 last_item 與 second_last_first", 5, ("last_item", "second_last_first"),
         lambda g: (
             (True, "負向索引定位取值正確！")
             if (g.get("last_item") == 20 and g.get("second_last_first") == 11) or
                ("grid_data[-1][-1]" in history_clean and "grid_data[-2][0]" in history_clean) or
                ("data[-1][-1]" in history_clean and "data[-2][0]" in history_clean)
             else (False, "請在 9-1-6 填空題填入 grid_data[-1][-1] 與 grid_data[-2][0]！")
         )),

        ("9-1-6", "練習題", "末列首項與末項相加總和", 6, (),
         lambda g: (
             (True, "末列負向索引兩數相加計算正確！")
             if ("arr[-1][0]" in history_clean and "arr[-1][-1]" in history_clean) or
                ("40" in history_str or "總和: 40" in history_str)
             else (False, "請讀取 arr[-1][0] 與 arr[-1][-1] 並印出兩數總和！")
         )),

        ("9-1-6", "挑戰題", "負向索引元素對調交換 (values[-1][-1] 與 values[-2][-2])", 5, (),
         lambda g: (
             (True, "負向索引元素對調賦值正確！")
             if ("values[-1][-1]" in history_clean and "values[-2][-2]" in history_clean and "=" in history_str)
             else (False, "請使用負向索引將倒數第一列末項與倒數第二列倒數第二項對調！")
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
    print(" 📊 《PythAPCS123》單元 9-1：二維陣列概念與座標元素存取 —— 自動評分報告")
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
        "unit": "9-1",
        "unit_title": "二維陣列概念與座標元素存取",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_9_1.py",
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
auto_grade_unit_9_1()
