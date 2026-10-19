# ==============================================================================
# 🧪 《PythAPCS123》單元 9-3：二維陣列初始化與參照共用致命陷阱 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_9_3.py
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
NOTEBOOK_FILE = "PythAPCS123_9-3_2d_array_initialization_and_reference_pitfall.ipynb"

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


def auto_grade_unit_9_3():
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
        # 9-3-1 淺拷貝參照共用致命陷阱 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-3-1", "填空題", "觀察 trap_grid 參照連動現象", 5, ("trap_grid",),
         lambda g: (
             (True, "trap_grid 參照共用現象填空正確！")
             if ("trap_grid" in history_str and "[0]" in history_str) or ("trap_grid" in g)
             else (False, "請在 9-3-1 填空題執行並觀察 trap_grid 的參照連動！")
         )),

        ("9-3-1", "練習題", "刻意使用乘號建立 2x3 trap_matrix 並修改驗證", 6, ("trap_matrix",),
         lambda g: (
             (True, "trap_matrix 乘法陷阱驗證正確！")
             if ("trap_matrix" in history_str and "* 2" in history_str) or ("trap_matrix" in g)
             else (False, "請故意使用 [[0]*3]*2 建立 trap_matrix 並修改第 0 列元素觀察連動！")
         )),

        ("9-3-1", "挑戰題", "預測 trap[3][0] 數值", 5, (),
         lambda g: (
             (True, "trap 連動預測正確！")
             if ("15" in history_str or "trap[3][0]" in history_clean)
             else (False, "請預測執行 trap[0][0] += 5 後 trap[3][0] 的數值（為 15）！")
         )),

        # ----------------------------------------------------------------------
        # 9-3-2 正確初始化黃金法則 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-3-2", "填空題", "列表生成式建立全 0 陣列 [[0]*C for _ in range(R)]", 5, (),
         lambda g: (
             (True, "二維全 0 陣列正確生成式填空正確！")
             if ("[[0]*Cfor_inrange(R)]" in history_clean or "[[0] * C for _ in range(R)]" in history_str)
             else (False, "請在 9-3-2 填空題填入 [[0] * C for _ in range(R)]！")
         )),

        ("9-3-2", "練習題", "正確建立 3x3 全 0 陣列並將 (1, 1) 改為 999", 6, (),
         lambda g: (
             (True, "獨立網格建立與單點修改驗證正確！")
             if ("999" in history_str and "for _ in range(R)" in history_str) or
                ("grid[1][1] = 999" in history_str or "grid[1][1]=999" in history_clean)
             else (False, "請使用生成式建立 3x3 全 0 網格，將 (1, 1) 改為 999，並確認其他列未被影響！")
         )),

        ("9-3-2", "挑戰題", "動態讀入 R, C 建立全 0 陣列並解包輸出", 6, (),
         lambda g: (
             (True, "動態建立全 0 陣列與解包輸出正確！")
             if ("print(*row)" in history_str and "for _ in range(R)" in history_str)
             else (False, "請動態讀入 R, C，使用列表生成式建立全 0 矩陣並逐列解包輸出！")
         )),

        # ----------------------------------------------------------------------
        # 9-3-3 記憶體指標探測：id() 與 is (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-3-3", "填空題", "使用 id() 比對第 0 列與第 1 列記憶體", 5, (),
         lambda g: (
             (True, "id() 比對填空正確！")
             if ("id(my_grid[0])" in history_clean and "id(my_grid[1])" in history_clean)
             else (False, "請在 9-3-3 填空題填入 id(my_grid[0]) 與 id(my_grid[1])！")
         )),

        ("9-3-3", "練習題", "使用 is 運算子判斷 row 0 is row 1", 6, (),
         lambda g: (
             (True, "is 運算子判斷邏輯正確！")
             if (" is " in history_str and "test_grid[0]" in history_str) or ("False" in history_str)
             else (False, "請使用 is 運算子比對第 0 列與第 1 列是否為同一個物件！")
         )),

        ("9-3-3", "挑戰題", "迴圈巡檢所有相鄰列獨立性", 6, (),
         lambda g: (
             (True, "相鄰列 id 比對巡檢正確！")
             if ("is not" in history_str or "is" in history_str or "!=" in history_str) and "range" in history_str
             else (False, "請用迴圈巡檢相鄰各列是否全為獨立記憶體位址！")
         )),

        # ----------------------------------------------------------------------
        # 9-3-4 布林標記地圖與符號地圖 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-3-4", "填空題", "初始化 visited 布林陣列全為 False", 5, (),
         lambda g: (
             (True, "visited 布林陣列初始化填空正確！")
             if ("[[False]*Cfor_inrange(R)]" in history_clean or "[[False] * C for _ in range(R)]" in history_str)
             else (False, "請在 9-3-4 填空題填入 [[False] * C for _ in range(R)]！")
         )),

        ("9-3-4", "練習題", "3x3 字元陣列 '.'，對角線改為 'O'", 6, (),
         lambda g: (
             (True, "符號地圖初始化與對角線修改正確！")
             if ("'O'" in history_str or '"O"' in history_str) and ("grid[0][0]" in history_clean or "i == j" in history_str or "range(3)" in history_str)
             else (False, "請初始化 3x3 '.' 網格，並將對角線三格原地修改為 'O'！")
         )),

        ("9-3-4", "挑戰題", "4x5 布林陣列最外圍一圈設為 True", 6, (),
         lambda g: (
             (True, "外圍邊界布林標記設定正確！")
             if ("True" in history_str and "False" in history_str) and ("visited" in history_str or "range" in history_str)
             else (False, "請將 4x5 布林陣列外圍邊界一圈設為 True，內部維持 False！")
         )),

        # ----------------------------------------------------------------------
        # 9-3-5 動態規律填值 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-3-5", "填空題", "棋盤交錯網格公式 (r + c) % 2", 5, (),
         lambda g: (
             (True, "棋盤奇偶交錯公式填空正確！")
             if ("(r+c)%2" in history_clean or "(r + c) % 2" in history_str)
             else (False, "請在 9-3-5 填空題填入 (r + c) % 2！")
         )),

        ("9-3-5", "練習題", "2x3 規律填值 r * C + c + 1", 6, (),
         lambda g: (
             (True, "連續編號矩陣規律填值正確！")
             if ("r * C + c + 1" in history_str or "r*C+c+1" in history_clean or "r * 3 + c + 1" in history_str)
             else (False, "請建立 2x3 網格，每格填入 r * C + c + 1 並解包印出！")
         )),

        ("9-3-5", "挑戰題", "NxN 座標和矩陣 r + c", 6, (),
         lambda g: (
             (True, "NxN 座標和矩陣建立正確！")
             if ("r + c" in history_str or "r+c" in history_clean) and "print(*row)" in history_str
             else (False, "請建立 N x N 矩陣，每格值為 r + c 並解包印出！")
         )),

        # ----------------------------------------------------------------------
        # 9-3-6 二維獨立深拷貝：[row[:] for row in grid] (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-3-6", "填空題", "切片深拷貝 [row[:] for row in base_grid]", 5, (),
         lambda g: (
             (True, "切片深拷貝語法填空正確！")
             if ("[row[:] for row in base_grid]" in history_str or "[row[:]forrowinbase_grid]" in history_clean or
                 "row[:]" in history_clean)
             else (False, "請在 9-3-6 填空題填入 [row[:] for row in base_grid]！")
         )),

        ("9-3-6", "練習題", "複製 src 至 dst 並修改驗證獨立性", 6, (),
         lambda g: (
             (True, "深拷貝獨立副本與修改驗證正確！")
             if ("dst = [row[:] for row in src]" in history_str or "[row[:] for row in src]" in history_str or
                 "dst[0][0]" in history_clean)
             else (False, "請深拷貝 dst = [row[:] for row in src]，修改 dst[0][0] 並確認 src 不受影響！")
         )),

        ("9-3-6", "挑戰題", "深拷貝迷宮並替換 'S' 與 'E' 為 '*'", 5, (),
         lambda g: (
             (True, "迷宮深拷貝與字元替換正確！")
             if ("maze_copy" in history_str and "*" in history_str and ("S" in history_str or "E" in history_str))
             else (False, "請深拷貝迷宮為 maze_copy，並將 'S' 與 'E' 替換為 '*'！")
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
    print(" 📊 《PythAPCS123》單元 9-3：二維陣列初始化與參照共用致命陷阱 —— 自動評分報告")
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
        "unit": "9-3",
        "unit_title": "二維陣列初始化與參照共用致命陷阱",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_9_3.py",
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
auto_grade_unit_9_3()
