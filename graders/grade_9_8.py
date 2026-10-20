# ==============================================================================
# 🧪 《PythAPCS123》單元 9-8：網格射線掃描（Raycasting）與連線阻擋（APCS g596 專題） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_9_8.py
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
NOTEBOOK_FILE = "PythAPCS123_9-8_grid_raycasting_and_apcs_g596.ipynb"

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


def auto_grade_unit_9_8(env=None):
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
        # 9-8-1 沿單一方向連續推進模型 (while 迴圈) (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-8-1", "填空題", "射線連續步進 while 邊界條件", 5, (),
         lambda g: (
             (True, "射線步進 while 條件填空正確！")
             if ("while 0 <= curr_r < R" in history_str or "while 0<=curr_r<R" in history_clean or
                 "0 <= curr_r < R and 0 <= curr_c < C" in history_str)
             else (False, "請在 9-8-1 填空題填入 while 邊界守護推進條件！")
         )),

        ("9-8-1", "練習題", "朝右方射線掃描直至出界並印出軌跡", 6, (),
         lambda g: (
             (True, "單向射線掃描軌跡正確！")
             if ("curr_c += 1" in history_str or "curr_c+=1" in history_clean) and "while" in history_str
             else (False, "請使用 while 迴圈連續向右推進並印出經由座標！")
         )),

        ("9-8-1", "挑戰題", "射線行進步數累加統計", 5, (),
         lambda g: (
             (True, "射線步數累加正確！")
             if ("steps += 1" in history_str or "steps+=1" in history_clean or "step_count" in history_str)
             else (False, "請統計射線自起點出發至出界前的總步數！")
         )),

        # ----------------------------------------------------------------------
        # 9-8-2 射線撞牆邊界終止條件 (Boundary Stop) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-8-2", "填空題", "撞牆判定與終止條件", 5, (),
         lambda g: (
             (True, "撞牆終止條件填空正確！")
             if ("not (0 <= next_r < R and 0 <= next_c < C)" in history_str or "break" in history_str or
                 "0 <= next_r < R" in history_str)
             else (False, "請在 9-8-2 填空題填入撞牆終止防禦！")
         )),

        ("9-8-2", "練習題", "朝指定方向射線掃描回傳撞牆前最後合法座標", 6, (),
         lambda g: (
             (True, "撞牆極限座標鎖定正確！")
             if ("last_r" in history_str or "last_c" in history_str or "curr_r" in history_str) and "while" in history_str
             else (False, "請掃描並回傳撞牆前的最後一個合法內部座標！")
         )),

        ("9-8-2", "挑戰題", "四方向撞牆距離計算 (上下左右距邊界長度)", 6, (),
         lambda g: (
             (True, "四向撞牆距離計算正確！")
             if ("r" in history_str and "R - 1 - r" in history_str or "c" in history_str and "C - 1 - c" in history_str)
             else (False, "請計算當前點至上下左右四面牆壁的步數距離！")
         )),

        # ----------------------------------------------------------------------
        # 9-8-3 射線遇障礙物阻擋機制 (Obstacle Stop) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-8-3", "填空題", "障礙物阻擋中斷 if grid[r][c] == '#': break", 5, (),
         lambda g: (
             (True, "障礙物阻擋中斷填空正確！")
             if ("grid[curr_r][curr_c] == '#'" in history_str or "grid[curr_r][curr_c]=='#'" in history_clean or
                 "grid[curr_r][curr_c] == 1" in history_str) and "break" in history_str
             else (False, "請在 9-8-3 填空題填入遇障礙物 break 中斷！")
         )),

        ("9-8-3", "練習題", "射線搜尋最近障礙物座標與距離", 6, (),
         lambda g: (
             (True, "最近障礙物搜尋正確！")
             if ("==" in history_str and "break" in history_str and "while" in history_str)
             else (False, "請沿射線推進，回傳遭遇的第一個障礙物座標與距離！")
         )),

        ("9-8-3", "挑戰題", "被障礙物阻擋後將沿途格子染為指定符號", 6, (),
         lambda g: (
             (True, "射線沿途染色正確！")
             if ("grid[r][c] =" in history_str or "board[r][c] =" in history_str or "=" in history_str) and "while" in history_str
             else (False, "請將射線前進路徑上的所有空格染色！")
         )),

        # ----------------------------------------------------------------------
        # 9-8-4 十字四方向雷射掃描器 (Cross Laser Scanner) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-8-4", "填空題", "十字四方向雷射掃描外層 for d in range(4)", 5, (),
         lambda g: (
             (True, "十字四方向雷射掃描填空正確！")
             if ("for d in range(4)" in history_str or "for d in range(4):" in history_str or
                 "range(4)" in history_clean)
             else (False, "請在 9-8-4 填空題填入 for d in range(4) 驅動四向射線！")
         )),

        ("9-8-4", "練習題", "在 (r, c) 放置雷射塔並向四向射擊染色", 6, (),
         lambda g: (
             (True, "四向十字雷射染色正確！")
             if ("range(4)" in history_str and "while" in history_str and ("+" in history_str or "*" in history_str))
             else (False, "請以 (r, c) 為中心向四個方向發射雷射並標記軌跡！")
         )),

        ("9-8-4", "挑戰題", "多座雷射塔同時照射之覆蓋格子總數統計", 6, (),
         lambda g: (
             (True, "多塔覆蓋面積統計正確！")
             if ("towers" in history_str or "tower" in history_str or "for" in history_str) and "count" in history_str
             else (False, "請統計多座雷射塔共同覆蓋的所有不重複格子數！")
         )),

        # ----------------------------------------------------------------------
        # 9-8-5 雙柱連線與網格區間染色 (Line Segment Marking) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("9-8-5", "填空題", "同列水平連線染色 for c in range(c1 + 1, c2)", 5, (),
         lambda g: (
             (True, "水平區間染色填空正確！")
             if ("range(c1 + 1, c2)" in history_str or "range(c1+1,c2)" in history_clean or
                 "range(min(c1, c2) + 1, max(c1, c2))" in history_str)
             else (False, "請在 9-8-5 填空題填入連線區間 range(c1 + 1, c2)！")
         )),

        ("9-8-5", "練習題", "給定兩柱座標，若在同行或同列則連線染色", 6, (),
         lambda g: (
             (True, "同行同列雙柱連線判斷正確！")
             if ("r1 == r2" in history_str or "c1 == c2" in history_str) and "range" in history_str
             else (False, "請判斷兩柱是否在同一行或同一直列，若是則將其中間格子染色！")
         )),

        ("9-8-5", "挑戰題", "若兩柱中間夾有障礙物則阻斷連線", 6, (),
         lambda g: (
             (True, "障礙物阻斷連線模擬正確！")
             if ("blocked" in history_str or "break" in history_str or "is_blocked" in history_str)
             else (False, "請檢查兩柱之間是否有障礙物，有障礙物時不可連線！")
         )),

        # ----------------------------------------------------------------------
        # 9-8-6 APCS g596 骨牌遊戲：柱子拔除與連線阻擋動態模擬 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("9-8-6", "填空題", "APCS g596 跨距限制 steps <= K", 5, (),
         lambda g: (
             (True, "APCS g596 跨距限制填空正確！")
             if ("steps <= K" in history_str or "steps<=K" in history_clean or "step <= K" in history_str)
             else (False, "請在 9-8-6 填空題填入 steps <= K！")
         )),

        ("9-8-6", "練習題", "APCS g596 單次加柱與四向連線模擬", 6, (),
         lambda g: (
             (True, "APCS g596 加柱連線模擬正確！")
             if ("posts[r][c] = True" in history_str or "posts" in history_str) and "range(4)" in history_str
             else (False, "請實作 APCS g596 加柱後的四向射線搜尋並連線！")
         )),

        ("9-8-6", "挑戰題", "APCS g596 柱子拔除與全地圖連線覆蓋結算", 5, (),
         lambda g: (
             (True, "APCS g596 拔柱與全地圖連線結算正確！")
             if ("posts[r][c] = False" in history_str or "posts" in history_str) and "sum" in history_str
             else (False, "請實作拔柱後重新連線並統計全圖被連線覆蓋的格子總數！")
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
    print(" 📊 《PythAPCS123》單元 9-8：網格射線掃描（Raycasting）與連線阻擋（APCS g596 專題） —— 自動評分報告")
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
        "unit": "9-8",
        "unit_title": "網格射線掃描（Raycasting）與連線阻擋（APCS g596 專題）",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_9_8.py",
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
auto_grade_unit_9_8()
