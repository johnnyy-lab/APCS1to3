# ==============================================================================
# 🧪 《PythAPCS123》單元 10-1：元組特性、建立與不可變保護機制 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_10_1.py
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
NOTEBOOK_FILE = "PythAPCS123_10-1_tuple_creation_and_immutability.ipynb"

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


def auto_grade_unit_10_1(env=None):
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
        # 10-1-1 為什麼需要不可變容器？ (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-1-1", "填空題", "安全讀取伺服器設定 server_config[0] 與 server_config[-1]", 5, ("port", "status"),
         lambda g: (
             (True, "元組安全讀取填空完全正確！")
             if (g.get("port") == 8080 and g.get("status") == "ONLINE") or
                ("server_config[0]" in history_clean and "server_config[-1]" in history_clean)
             else (False, "請在 10-1-1 填空題填入索引 0 與 -1 安全讀取元組！")
         )),

        ("10-1-1", "練習題", "不可變常數守護者 (a, b, c) 打包乘數", 6, (),
         lambda g: (
             (True, "三常數元組打包與倍率運算正確！")
             if ("tuple" in history_str or "(" in history_str) and ("multiplier" in history_str or "*" in history_str)
             else (False, "請將三個整數打包為元組並乘以 multiplier！")
         )),

        ("10-1-1", "挑戰題", "四科成績極值守門員與全距計算", 5, (),
         lambda g: (
             (True, "元組極值與全距計算正確！")
             if ("max(" in history_str and "min(" in history_str) and ("scores" in history_str or "tuple" in history_str)
             else (False, "請輸入四科成績存入元組，並計算 max(scores) - min(scores)！")
         )),

        # ----------------------------------------------------------------------
        # 10-1-2 單元素逗號陷阱 (x,) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-1-2", "填空題", "修復單元素元組宣告 (num_val,)", 5, ("single_t",),
         lambda g: (
             (True, "單元素元組逗號修復正確！")
             if (isinstance(g.get("single_t"), tuple) and len(g.get("single_t")) == 1) or
                ("(num_val,)" in history_clean or "(88,)" in history_clean)
             else (False, "請在 10-1-2 填空題小括號內補上逗號 `(num_val,)`！")
         )),

        ("10-1-2", "練習題", "純括號整數 vs 單元素元組型態與長度檢驗", 6, (),
         lambda g: (
             (True, "元組型態與長度量測正確！")
             if ("type(" in history_str and "len(" in history_str) and ("," in history_str)
             else (False, "請比較 (N) 與 (N,) 的 type 與 len！")
         )),

        ("10-1-2", "挑戰題", "動態構造空元組 () 與單元素元組", 6, (),
         lambda g: (
             (True, "空元組與單元素動態構造正確！")
             if ("() " in history_str or "()" in history_clean or "tuple()" in history_str) and ("k ==" in history_str or "k==" in history_clean)
             else (False, "請依 K == 0 建立空元組 ()，K == 1 建立單元素元組！")
         )),

        # ----------------------------------------------------------------------
        # 10-1-3 正負索引存取與切片操作 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-1-3", "填空題", "週末切片 days[-2:] 與平日反轉 days[:5][::-1]", 5, ("weekend",),
         lambda g: (
             (True, "元組切片提取與反轉填空正確！")
             if (g.get("weekend") == ("六", "日")) or
                ("days[-2:]" in history_clean or "days[5:]" in history_clean or "::-1" in history_str)
             else (False, "請在 10-1-3 填空題填入 days[-2:] 與 days[:5][::-1]！")
         )),

        ("10-1-3", "練習題", "數列頭尾裁切與中間反轉 (t[1:-1][::-1])", 6, (),
         lambda g: (
             (True, "頭尾裁切與中間反轉切片正確！")
             if ("t[1:-1]" in history_clean and "::-1" in history_str) or ("tuple" in history_str and "print" in history_str)
             else (False, "請去除首尾兩數後將中間元素反轉輸出！")
         )),

        ("10-1-3", "挑戰題", "迴文元組檢測器 (t == t[::-1])", 6, (),
         lambda g: (
             (True, "迴文元組檢測邏輯正確！")
             if ("t == t[::-1]" in history_clean or "t==t[::-1]" in history_clean) and ("YES" in history_str and "NO" in history_str)
             else (False, "請以 t == t[::-1] 判斷是否為迴文元組並輸出 YES 或 NO！")
         )),

        # ----------------------------------------------------------------------
        # 10-1-4 tuple(list) 與 list(tuple) 型態互轉 (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-1-4", "填空題", "元組轉串列排序後重新封裝 tuple(sorted_list)", 5, ("sorted_t",),
         lambda g: (
             (True, "元組與串列互轉填空正確！")
             if (g.get("sorted_t") == (10, 20, 30, 40, 50)) or
                ("list(raw_t)" in history_clean and "tuple(" in history_clean)
             else (False, "請在 10-1-4 填空題填入 list(raw_t) 與 tuple(sorted_list)！")
         )),

        ("10-1-4", "練習題", "黑名單數值過濾與元組重新封印", 6, (),
         lambda g: (
             (True, "黑名單過濾與元組封印正確！")
             if ("list(" in history_str and "tuple(" in history_str) and ("bad_val" in history_str or "!=" in history_str)
             else (False, "請將元組轉為串列剔除 bad_val 後重新轉為元組！")
         )),

        ("10-1-4", "挑戰題", "元組指定位置就地替換模擬器", 6, (),
         lambda g: (
             (True, "元組單點替換模擬正確！")
             if ("list(" in history_str and "tuple(" in history_str) and ("idx" in history_str and "new_val" in history_str)
             else (False, "請將元組轉為串列替換指定索引數值後封印回元組！")
         )),

        # ----------------------------------------------------------------------
        # 10-1-5 元組解包賦值 (Tuple Unpacking) (共 17 分: 5 + 6 + 6)
        # ----------------------------------------------------------------------
        ("10-1-5", "填空題", "三維座標解包與曼哈頓距離計算", 5, ("manhattan_dist",),
         lambda g: (
             (True, "三維曼哈頓座標解包填空正確！")
             if (g.get("manhattan_dist") == 22) or
                ("px, py, pz = coord_3d" in history_str or "px,py,pz=coord_3d" in history_clean or
                 "x, y, z = coord_3d" in history_str or "x,y,z=coord_3d" in history_clean)
             else (False, "請在 10-1-5 填空題完成座標解包！")
         )),

        ("10-1-5", "練習題", "選手四項成績解包與總分計算", 6, (),
         lambda g: (
             (True, "選手成績解包與加總正確！")
             if ("name, run, jump, shoot" in history_str or "name,run,jump,shoot" in history_clean or
                 "parts" in history_str)
             else (False, "請將選手資料解包給 name, run, jump, shoot 並計算總分！")
         )),

        ("10-1-5", "挑戰題", "兩人對戰成績解包與勝負判定", 6, (),
         lambda g: (
             (True, "兩人對戰解包判定正確！")
             if ("p1" in history_str and "p2" in history_str) and (">" in history_str and "sum" in history_str)
             else (False, "請各自解包兩人成績，計算三局總分並判定勝負！")
         )),

        # ----------------------------------------------------------------------
        # 10-1-6 二維座標封裝：以 (r, c) 表示平面點 (共 16 分: 5 + 6 + 5)
        # ----------------------------------------------------------------------
        ("10-1-6", "填空題", "座標元組走訪 for r, c in points", 5, (),
         lambda g: (
             (True, "座標元組走訪填空正確！")
             if ("for r, c in points" in history_str or "for r, c in points:" in history_str or
                 "forr,cinpoints" in history_clean)
             else (False, "請在 10-1-6 填空題填入 for r, c in points！")
         )),

        ("10-1-6", "練習題", "曼哈頓兩點距離元組計算機 abs(r1-r2) + abs(c1-c2)", 6, (),
         lambda g: (
             (True, "曼哈頓兩點距離計算正確！")
             if ("abs(" in history_str and "+" in history_str) and ("r1" in history_str and "r2" in history_str)
             else (False, "請計算兩座標元組之間的曼哈頓距離 abs(r1 - r2) + abs(c1 - c2)！")
         )),

        ("10-1-6", "挑戰題", "多點軌跡中心點座標計算 (sum_r//N, sum_c//N)", 5, (),
         lambda g: (
             (True, "多點軌跡中心座標計算正確！")
             if ("sum(" in history_str or "sum_r" in history_str) and ("// n" in history_str or "//n" in history_clean or "// N" in history_str)
             else (False, "請計算所有點的平均座標 (sum_r // N, sum_c // N)！")
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
    print(" 📊 《PythAPCS123》單元 10-1：元組特性、建立與不可變保護機制 —— 自動評分報告")
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
        "unit": "10-1",
        "unit_title": "元組特性、建立與不可變保護機制",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_10_1.py",
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
auto_grade_unit_10_1()
