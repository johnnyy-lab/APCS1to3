# ==============================================================================
# 🧪 《PythAPCS123》單元 1-3：多變數同時賦值與變數交換（Swap） —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_1_3.py
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
NOTEBOOK_FILE = "PythAPCS123_1-3_multiple_assignment_and_swap.ipynb"

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


def auto_grade_unit_1_3():
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

    test_cases = test_cases = [
        # 1-3-1 多變數同時賦值——雙手齊發的打包與解包 (共 19 分)
        ("1-3-1", "填空題", "雙變數同時賦值 x, y = 10, 20", 6, ("x", "y"),
         lambda g: (True, "雙變數同時賦值成功：x=10, y=20") if g.get("x") in [10, 20] and g.get("y") in [20, 30]
         else (False, "找不到變數 x, y 或數值不正確，請在 1-3-1 填空題設定 x, y = 10, 20")),

        ("1-3-1", "練習題", "一行宣告寬高 width, height", 8, ("width", "height"),
         lambda g: (True, f"寬高設定正確：width={g.get('width')}, height={g.get('height')}")
         if (g.get("width") in [40, 15] and g.get("height") in [30, 25])
         else (False, "找不到變數 width 或 height，請依練習題說明使用一行多重賦值設定數值")),

        ("1-3-1", "挑戰題", "RGB三原色同時賦值 (red, green, blue)", 5, ("red", "green", "blue"),
         lambda g: (True, f"RGB色彩代碼設定成功：({g.get('red')}, {g.get('green')}, {g.get('blue')})")
         if (g.get("red") == 255 and g.get("green") == 128 and g.get("blue") == 0)
         else (False, "請在一行中同時設定 red, green, blue 為 255, 128, 0")),

        # 1-3-2 等號兩側天平必須對稱——個數不符的 ValueError 警報 (共 19 分)
        ("1-3-2", "填空題", "天平平衡補齊三數 p, q, r", 6, ("p", "q", "r"),
         lambda g: (True, "三變數對稱賦值完成：p=100, q=200, r=300")
         if (g.get("p") == 100 and g.get("q") == 200 and g.get("r") == 300)
         else (False, "變數 p, q, r 未正確設定為 100, 200, 300，請補齊右側數值")),

        ("1-3-2", "練習題", "修復 ValueError (x1, x2, x3)", 8, ("x1", "x2", "x3"),
         lambda g: (True, f"三變數對稱修復正確：({g.get('x1')}, {g.get('x2')}, {g.get('x3')})")
         if (g.get("x1") in [5, 1] and g.get("x2") in [10, 2] and g.get("x3") in [15, 3])
         else (False, "請修正 x1, x2, x3 的賦值，確認等號兩側均為 3 個元素")),

        ("1-3-2", "挑戰題", "四季代號一行四變數 (a, b, c, d)", 5, ("a", "b", "c", "d"),
         lambda g: (True, f"四變數對稱宣告成功：a={g.get('a')}, b={g.get('b')}, c={g.get('c')}, d={g.get('d')}")
         if (g.get("a") in [1, 4] and g.get("b") in [2, 1] and g.get("c") in [3, 2] and g.get("d") in [4, 3])
         else (False, "請在一行中宣告 a, b, c, d 分別對應 1, 2, 3, 4")),

        # 1-3-3 傳統變數交換的慘痛悲劇——為什麼需要第三個空杯子 temp？ (共 19 分)
        ("1-3-3", "填空題", "第三空杯備份交換 m 與 n", 6, ("m", "n", "temp"),
         lambda g: (True, "傳統暫存變數交換正確：m=99, n=88, temp=88")
         if (g.get("m") == 99 and g.get("n") == 88 and g.get("temp") == 88)
         else (False, "請在 ___ 填入 n，完成 m=n 與 n=temp 的三步驟交換")),

        ("1-3-3", "練習題", "卡牌交換 card1 與 card2 (透過 t)", 8, ("card1", "card2"),
         lambda g: (True, f"卡牌交換完成：card1={g.get('card1')}, card2={g.get('card2')}")
         if ((g.get("card1") == 2 and g.get("card2") == 7) or (g.get("card1") == 4 and g.get("card2") == 9))
         else (False, "卡牌數值未成功對調，請透過暫存變數 t 將 card1 與 card2 數值互換")),

        ("1-3-3", "挑戰題", "金銀蘋果守衛交換 guard_temp", 5, ("gold_apple", "silver_apple", "guard_temp"),
         lambda g: (True, f"金銀蘋果對調成功：gold={g.get('gold_apple')}, silver={g.get('silver_apple')}")
         if (g.get("gold_apple") == 2 and g.get("silver_apple") == 1 and g.get("guard_temp") == 1)
         else (False, "請宣告 guard_temp 備份，將 gold_apple (1->2) 與 silver_apple (2->1) 成功交換")),

        # 1-3-4 Python 專屬的瞬間乾坤大挪移——`a, b = b, a` 變數交換 (共 20 分)
        ("1-3-4", "填空題", "乾坤大挪移 u, v = v, u", 6, ("u", "v"),
         lambda g: (True, "單行交換成功：u=555, v=111")
         if (g.get("u") == 555 and g.get("v") == 111)
         else (False, "請填入 u, v = v, u 實現一行變數乾坤大挪移")),

        ("1-3-4", "練習題", "左右數值對調 left, right", 8, ("left", "right"),
         lambda g: (True, f"左右交換正確：left={g.get('left')}, right={g.get('right')}")
         if ((g.get("left") == 200 and g.get("right") == 100) or (g.get("left") == 50 and g.get("right") == 10))
         else (False, "請使用 left, right = right, left 將左右變數數值對調")),

        ("1-3-4", "挑戰題", "大小號碼牌對調 small, big", 6, ("small", "big"),
         lambda g: (True, f"大小牌對調成功：small={g.get('small')}, big={g.get('big')}")
         if (g.get("small") == 10 and g.get("big") == 50)
         else (False, "請使用一行交換語法，讓原本 50 與 10 的 small 與 big 數值對調")),

        # 1-3-5 三人傳球大輪替——多變數循環交換（Cyclic Swap） (共 23 分)
        ("1-3-5", "填空題", "三變數循環輪替 x, y, z = y, z, x", 7, ("x", "y", "z"),
         lambda g: (True, "三變數輪替完成：x=20, y=30, z=10")
         if (g.get("x") == 20 and g.get("y") == 30 and g.get("z") == 10)
         else (False, "請填入 x, y, z = y, z, x 完成循環輪替")),

        ("1-3-5", "練習題", "隊員分數循環傳球 p1, p2, p3", 9, ("p1", "p2", "p3"),
         lambda g: (True, f"隊員分數輪替正確：({g.get('p1')}, {g.get('p2')}, {g.get('p3')})")
         if ((g.get("p1") == 200 and g.get("p2") == 300 and g.get("p3") == 100) or
             (g.get("p1") == 60 and g.get("p2") == 70 and g.get("p3") == 50))
         else (False, "請透過一行語法將 p1, p2, p3 循環輪替（p1拿p2, p2拿p3, p3拿p1）")),

        ("1-3-5", "挑戰題", "四變數逆向大輪替 a, b, c, d", 7, ("a", "b", "c", "d"),
         lambda g: (True, f"四變數逆向輪替成功：({g.get('a')}, {g.get('b')}, {g.get('c')}, {g.get('d')})")
         if (g.get("a") == 4 and g.get("b") == 1 and g.get("c") == 2 and g.get("d") == 3)
         else (False, "請以 a, b, c, d = d, a, b, c 完成逆向輪替（a=4, b=1, c=2, d=3）")),
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
        badge = '🏆 傳奇大師（金牌徽章 🥇）—— 變數交換與多重賦值神乎其技！'
    elif total_score >= 80:
        badge = '🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，僅少數細節需微調！'
    elif total_score >= 60:
        badge = '🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作檢查！'
    else:
        badge = '🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 1-3：多變數同時賦值與變數交換（Swap） —— 自動評分報告")
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
        "unit": "1-3",
        "unit_title": "多變數同時賦值與變數交換（Swap）",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_1_3.py",
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
auto_grade_unit_1_3()
