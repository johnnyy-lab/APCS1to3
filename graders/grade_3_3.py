# ==============================================================================
# 🧪 《PythAPCS123》單元 3-3：極值比較函數（max, min） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_3_3.py
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
NOTEBOOK_FILE = "PythAPCS123_3-3_extremum_functions_max_min.ipynb"

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


def auto_grade_unit_3_3(env=None):
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

    test_cases = [
        # ----------------------------------------------------------------------
        # 3-3-1 max() 與 min() 多參數比大小——誰是擂台冠軍與墊底守門員 (共 34 分)
        # ----------------------------------------------------------------------
        ("3-3-1", "填空題", "max/min 求三回合最佳與最低分 (best, worst)", 11, ("best", "worst"),
         lambda g: (
             (True, "極值計算成功：best=95, worst=76！")
             if (g.get("best") == 95 and g.get("worst") == 76)
             else (False, "找不到 best 或 worst（預期最高 95、最低 76），請在空格填入 max 與 min！")
         )),

        ("3-3-1", "練習題", "三個整數極大與極小值求值 (num1, num2, num3)", 12, ("num1", "num2", "num3"),
         lambda g: (
             (True, "三數極大值與極小值計算正確！")
             if ("num1" in g and "num2" in g and "num3" in g and
                 isinstance(g.get("num1"), (int, float)) and
                 isinstance(g.get("num2"), (int, float)) and
                 isinstance(g.get("num3"), (int, float)) and
                 (any(v == max(g.get("num1"), g.get("num2"), g.get("num3")) for v in g.values() if isinstance(v, (int, float))) or
                  any(v == min(g.get("num1"), g.get("num2"), g.get("num3")) for v in g.values() if isinstance(v, (int, float)))))
             else (False, "找不到 num1, num2, num3，請宣告三整數並使用 max() 與 min() 印出極值！")
         )),

        ("3-3-1", "挑戰題", "跳遠成績全距計算 (max - min ≈ 0.70)", 11, ("d1", "d2", "d3", "d4"),
         lambda g: (
             (True, "跳遠全距計算正確：5.30 - 4.60 = 0.70 公尺！")
             if any(isinstance(v, (int, float)) and abs(v - 0.70) < 1e-4 for v in g.values()) or
                (all(k in g for k in ["d1", "d2", "d3", "d4"]) and
                 any(isinstance(v, (int, float)) and abs(v - (max(g['d1'], g['d2'], g['d3'], g['d4']) - min(g['d1'], g['d2'], g['d3'], g['d4']))) < 1e-4 for v in g.values()))
             else (False, "請宣告四位選手成績，以 max() - min() 計算全距（約 0.70）並印出！")
         )),

        # ----------------------------------------------------------------------
        # 3-3-2 巢狀合成函數運算——由內而外的同心圓求值順序 (共 33 分)
        # ----------------------------------------------------------------------
        ("3-3-2", "填空題", "由內而外巢狀求值 (nested_result = 15)", 11, ("nested_result",),
         lambda g: (
             (True, "巢狀合成計算成功：max(12, min(8*2, 15)) = 15！")
             if (g.get("nested_result") == 15)
             else (False, "找不到 nested_result 或數值不為 15，請在空格依序填入 max 與 min！")
         )),

        ("3-3-2", "練習題", "多層合成運算式求值 (p, q, r)", 12, ("p", "q", "r"),
         lambda g: (
             (True, "巢狀合成運算式計算正確！")
             if ("p" in g and "q" in g and "r" in g and
                 isinstance(g.get("p"), (int, float)) and
                 isinstance(g.get("q"), (int, float)) and
                 isinstance(g.get("r"), (int, float)) and
                 (any(v == max(g['p'] + 2, min(g['q'] * 3, g['r'] - 4)) for v in g.values() if isinstance(v, (int, float))) or
                  any(v == 12 for v in g.values() if isinstance(v, (int, float)))))
             else (False, "找不到 p, q, r，請計算 max(p + 2, min(q * 3, r - 4)) 並印出！")
         )),

        ("3-3-2", "挑戰題", "Clamp 數值安全限幅閥演算法 (clamped = 100)", 10, ("raw_speed",),
         lambda g: (
             (True, "Clamp 數值限幅成功：角色速度被安全限制在上限 100！")
             if any(isinstance(v, (int, float)) and v == 100 for k, v in g.items() if "clamp" in k or "speed" in k) or
                (g.get("raw_speed") == 120 and any(isinstance(v, (int, float)) and v == 100 for v in g.values()))
             else (False, "請以 min(max_limit, max(min_limit, raw_speed)) 限制速度在 [0, 100] 內並印出 100！")
         )),

        # ----------------------------------------------------------------------
        # 3-3-3 三數排序中間值技巧——總和扣除極值的數學巧思 (共 33 分)
        # ----------------------------------------------------------------------
        ("3-3-3", "填空題", "三數扣除極值求中間值 (low=78, mid=85, high=92)", 11, ("low", "mid", "high"),
         lambda g: (
             (True, "總和扣除極值法成功：low=78, mid=85, high=92！")
             if ((g.get("low") == 78 and g.get("mid") == 85 and g.get("high") == 92) or
                 (g.get("low") == 7 and g.get("mid") == 19 and g.get("high") == 24))
             else (False, "找不到 low, mid, high（預期 78, 85, 92），請在空格填入 min, max 與 low, high！")
         )),

        ("3-3-3", "練習題", "三商品價格由小到大三數排序 (price1, price2, price3)", 12, ("price1", "price2", "price3"),
         lambda g: (
             (True, "三價格排序計算正確！")
             if (all(k in g for k in ["price1", "price2", "price3"]) and
                 isinstance(g.get("price1"), (int, float)) and
                 isinstance(g.get("price2"), (int, float)) and
                 isinstance(g.get("price3"), (int, float)) and
                 (any(isinstance(v, (int, float)) and v == (g["price1"] + g["price2"] + g["price3"] - min(g["price1"], g["price2"], g["price3"]) - max(g["price1"], g["price2"], g["price3"])) for v in g.values()) or
                  any(v in [280, 60, 80] for v in g.values() if isinstance(v, (int, float))) or
                  any(all(s in str(v) for s in ["120", "280", "350"]) for v in g.values()) or
                  any(all(s in str(v) for s in ["50", "60", "90"]) for v in g.values()) or
                  any("45" in str(v) and "80" in str(v) and "120" in str(v) for v in g.values())))
             else (False, "找不到 price1, price2, price3，請以總和扣除極值法計算中間值並依序印出！")
         )),

        ("3-3-3", "挑戰題", "買三件特惠促銷結帳總額 (total_pay = 860)", 10, ("total_pay",),
         lambda g: (
             (True, "促銷結帳總額計算成功：860 元（原價總和 770 + 最低價半價 90）！")
             if (g.get("total_pay") == 860) or
                any(isinstance(v, (int, float)) and v == 860 for v in g.values())
             else (False, "請找出最低價 cheapest，計算 other_sum + cheapest // 2 得總額 860 並印出！")
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
        badge = '🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通 max/min 多參數與巢狀合成，三數中間值巧思融會貫通！'
    elif total_score >= 80:
        badge = '🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，極值比較與合成求值邏輯清晰！'
    elif total_score >= 60:
        badge = '🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作微調！'
    else:
        badge = '🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 3-3：極值比較函數（max, min） —— 自動評分報告")
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
        "unit": "3-3",
        "unit_title": "極值比較函數（max, min）",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_3_3.py",
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
auto_grade_unit_3_3()
