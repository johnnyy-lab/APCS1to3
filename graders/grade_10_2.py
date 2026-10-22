# ==============================================================================
# 🧪 《PythAPCS123》單元 10-2：元組進階操作與可雜湊特性（Hashable） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_10_2.py
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
NOTEBOOK_FILE = "PythAPCS123_10-2_tuple_advanced_and_hashable.ipynb"

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


def auto_grade_unit_10_2(env=None):
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
        # 10-2-1 記憶體行為本質與 id() (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-2-1", "填空題", "使用 id() 驗證元組重賦值產生新位址", 5, (),
         lambda g: (
             (True, "id() 記憶體探測填空正確！")
             if ("id(base_t)" in history_clean or "id(a)" in history_clean)
             else (False, "請在 10-2-1 填空題填入 id(base_t) 觀察位址變化！")
         )),

        ("10-2-1", "練習題", "不可變字串與元組位址驗證儀 (id1 != id2)", 6, (),
         lambda g: (
             (True, "元組加法新物件位址驗證正確！")
             if ("id(" in history_str and "!=" in history_str) or ("id1" in history_str and "id2" in history_str)
             else (False, "請記錄 t1 與 t2 的 id 並驗證兩者位址相異！")
         )),

        ("10-2-1", "挑戰題", "純淨不可變容器檢測 (isinstance int/float/str/tuple)", 5, (),
         lambda g: (
             (True, "不可變純淨型態檢測正確！")
             if ("isinstance" in history_str and ("tuple" in history_str or "list" in history_str)) or ("SAFE" in history_str)
             else (False, "請檢驗清單中各元素是否全為不可變型態！")
         )),

        # ----------------------------------------------------------------------
        # 10-2-2 可雜湊（Hashable）本質 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-2-2", "填空題", "計算不可變元組雜湊指紋 hash(coord)", 5, (),
         lambda g: (
             (True, "hash() 函式填空正確！")
             if ("hash(coord)" in history_clean)
             else (False, "請在 10-2-2 填空題填入 hash(coord)！")
         )),

        ("10-2-2", "練習題", "元組雜湊一致性驗證 hash(t1) == hash(t2)", 6, (),
         lambda g: (
             (True, "雜湊一致性比對正確！")
             if ("hash(t1) == hash(t2)" in history_str or "hash(t1)==hash(t2)" in history_clean or "hash(" in history_str)
             else (False, "請驗證內容相同的兩個元組其 hash 值完全相等！")
         )),

        ("10-2-2", "挑戰題", "動態輸入資料可雜湊性整數檢驗", 6, (),
         lambda g: (
             (True, "可雜湊性檢測正確！")
             if ("isinstance(hash(" in history_clean or "hash(" in history_str)
             else (False, "請驗證 tuple 輸入的雜湊值為整數型態！")
         )),

        # ----------------------------------------------------------------------
        # 10-2-3 巢狀元組與結構化資料打包 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-2-3", "填空題", "巢狀解包 sid, nm, (math, eng, sci) = rcrd102", 5, (),
         lambda g: (
             (True, "多層巢狀解包填空正確！")
             if ("sid, nm" in history_str and "math" in history_str) or ("rcrd102" in history_str)
             else (False, "請在 10-2-3 填空題填入多層解包變數！")
         )),

        ("10-2-3", "練習題", "學生卡成績統計器 (sid, nm, (s1, s2, s3))", 6, (),
         lambda g: (
             (True, "學生卡巢狀打包與統計正確！")
             if ("(" in history_str and "sum(" in history_str) and ("nm" in history_str or "sid" in history_str)
             else (False, "請打包為 (sid, nm, (s1, s2, s3)) 並計算成績總和！")
         )),

        ("10-2-3", "挑戰題", "二維多線段長度統計 ((r1, c1), (r2, c2))", 6, (),
         lambda g: (
             (True, "巢狀線段長度統計正確！")
             if ("abs(" in history_str and "((" in history_str)
             else (False, "請將線段儲存為 ((r1, c1), (r2, c2)) 並計算曼哈頓長度！")
         )),

        # ----------------------------------------------------------------------
        # 10-2-4 座標位移向量應用 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-2-4", "填空題", "八方向對角向量補齊 (-1, -1) 與 (1, 1)", 5, (),
         lambda g: (
             (True, "八方向位移向量填空正確！")
             if ("(-1, -1)" in history_str or "(-1,-1)" in history_clean) and ("(1, 1)" in history_str or "(1,1)" in history_clean)
             else (False, "請在 10-2-4 填空題補齊對角線位移向量！")
         )),

        ("10-2-4", "練習題", "網格安全位移探測器 (r + dr, c + dc)", 6, (),
         lambda g: (
             (True, "向量位移與邊界判定正確！")
             if ("r + dr" in history_str or "c + dc" in history_str or "0 <= nr < R" in history_str)
             else (False, "請使用位移向量計算新座標並加入邊界保護！")
         )),

        ("10-2-4", "挑戰題", "連續向量步進路徑生成", 6, (),
         lambda g: (
             (True, "連續步進軌跡計算正確！")
             if ("for" in history_str and ("dr" in history_str or "dc" in history_str or "DRCT" in history_str))
             else (False, "請連續執行 M 步移動並輸出最終座標！")
         )),

        # ----------------------------------------------------------------------
        # 10-2-5 多傳回值模擬打包 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-2-5", "填空題", "奇偶數總和打包為 (odd_sum102, evn_sum102)", 5, (),
         lambda g: (
             (True, "多值統計元組打包填空正確！")
             if ("(odd_sum102, evn_sum102)" in history_str or "(odd_sum102,evn_sum102)" in history_clean)
             else (False, "請在 10-2-5 填空題填入 (odd_sum102, evn_sum102)！")
         )),

        ("10-2-5", "練習題", "四合一數據分析打包 (len, sum, max, min)", 6, (),
         lambda g: (
             (True, "四項統計指標打包正確！")
             if ("len(" in history_str and "sum(" in history_str and "max(" in history_str and "min(" in history_str)
             else (False, "請將長度、總和、最大值、最小值打包為四元組！")
         )),

        ("10-2-5", "挑戰題", "正負數與零計數三元組 (pos, neg, zero)", 6, (),
         lambda g: (
             (True, "正負零計數三元組打包正確！")
             if ("> 0" in history_str and "< 0" in history_str and "== 0" in history_str)
             else (False, "請統計正數、負數與 0 的個數並打包輸出！")
         )),

        # ----------------------------------------------------------------------
        # 10-2-6 元組字典序排序原則 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-2-6", "填空題", "雙條件排序鍵值 (-score, penalties)", 5, (),
         lambda g: (
             (True, "多條件排序元組填空正確！")
             if ("-p1_score" in history_str or "-score" in history_str or "-p" in history_clean)
             else (False, "請在 10-2-6 填空題填入 (-score, penalties)！")
         )),

        ("10-2-6", "練習題", "兩位選手多條件勝負判定 (-solved, penalty, id)", 6, (),
         lambda g: (
             (True, "多準則勝負比對正確！")
             if ("-s" in history_clean or "p1" in history_str) and ("<" in history_str or ">" in history_str)
             else (False, "請使用元組 (-solved, penalty, id) 比較兩位選手高下！")
         )),

        ("10-2-6", "挑戰題", "三點距離原點多準則排序", 5, (),
         lambda g: (
             (True, "座標多準則排序正確！")
             if ("abs(" in history_str and "sort" in history_str) or ("sorted(" in history_str)
             else (False, "請依照曼哈頓距離與座標字典序對三點進行排序！")
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
    print(" 📊 《PythAPCS123》單元 10-2：元組進階操作與可雜湊特性（Hashable） —— 自動評分報告")
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
        "unit": "10-2",
        "unit_title": "元組進階操作與可雜湊特性（Hashable）",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_10_2.py",
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
auto_grade_unit_10_2()
