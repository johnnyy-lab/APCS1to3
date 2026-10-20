# ==============================================================================
# 🧪 《PythAPCS123》單元 1-1：變數命名規則與記憶體參照 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_1_1.py
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
NOTEBOOK_FILE = "PythAPCS123_1-1_variable_naming_and_memory.ipynb"

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


def auto_grade_unit_1_1(env=None):
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
        # 1-1-1 變數基本概念
        ("1-1-1", "填空題", "變數建立 score = 95", 5, ("score",),
         lambda g: (True, "置物箱正確貼上名牌 score 並放入 95") if g.get("score") == 95
         else (False, "找不到變數 score 或數值不為 95，請確認已替換 ___ 並點擊播放鍵執行")),

        ("1-1-1", "練習題", "糖果箱 candy 變數與輸出", 8, ("candy", "Candy"),
         lambda g: (True, f"成功建立 candy = {g.get('candy')}") if g.get("candy") in [5, 12]
         else ((False, "檢測到大寫 Candy，但題目要求全小寫 candy（Python 對大小寫很嚴格喔！）") if "Candy" in g
               else (False, "找不到變數 candy，請依照練習題說明建立並賦值 5 或 12"))),

        ("1-1-1", "挑戰題", "幸運數字 my_lucky_number", 4, ("my_lucky_number",),
         lambda g: (True, f"幸運數字已設定為 {g.get('my_lucky_number')}") if isinstance(g.get("my_lucky_number"), (int, float))
         else (False, "找不到名為 my_lucky_number 的數值變數，請自己放進一顆幸運數字！")),

        # 1-1-2 記憶體參照與 NameError
        ("1-1-2", "填空題", "修復 NameError (hp = 100)", 5, ("hp",),
         lambda g: (True, "成功提前宣告變數，hp = 100") if g.get("hp") == 100
         else (False, "找不到變數 hp 或數值不為 100，請先建立 hp 再印出")),

        ("1-1-2", "練習題", "拼字修復 player_level", 8, ("player_level", "player_leval"),
         lambda g: (True, f"拼字修正正確，player_level = {g.get('player_level')}") if g.get("player_level") in [1, 99]
         else ((False, "仍殘留拼錯的 player_leval，請在 1-1-2 練習題更正為 level！") if "player_leval" in g
               else (False, "找不到變數 player_level，請將其設為 1 或 99"))),

        ("1-1-2", "挑戰題", "雙變數宣告 (Alex 與 500 金幣)", 4, ("player_name", "player_gold"),
         lambda g: (True, f"冒險者名牌就緒：{g.get('player_name')}（金幣：{g.get('player_gold')}）")
         if g.get("player_name") == "Alex" and g.get("player_gold") == 500
         else (False, "請確認 player_name 為 'Alex' 且 player_gold 為 500")),

        # 1-1-3 變數命名規則一：字母、數字與底線
        ("1-1-3", "填空題", "底線串接 monster_hp_2", 5, ("monster_hp_2",),
         lambda g: (True, "合法使用底線連接：monster_hp_2 = 350") if g.get("monster_hp_2") == 350
         else (False, "找不到合法的 monster_hp_2 變數，請填入底線連接單字")),

        ("1-1-3", "練習題", "蛇形命名 user_gold_coin", 8, ("user_gold_coin",),
         lambda g: (True, f"蛇形命名正確：user_gold_coin = {g.get('user_gold_coin')}") if g.get("user_gold_coin") in [300, 1500]
         else (False, "找不到 user_gold_coin 變數，請依練習題設為 300 或 1500")),

        ("1-1-3", "挑戰題", "字母+底線+數字自訂變數 (777)", 3, (),
         lambda g: (True, "成功找到符合規則且存放 777 之自訂變數！") if any(v == 777 and '_' in k for k, v in g.items() if not k.startswith('_'))
         else (False, "未檢測到數值為 777 且名稱包含底線的變數（如 item_bag_3 = 777）")),

        # 1-1-4 變數命名規則二：開頭不能是數字
        ("1-1-4", "填空題", "數字移至後方 prize_1", 5, ("prize_1",),
         lambda g: (True, "數字擺在後方正確：prize_1 = 8888") if g.get("prize_1") == 8888
         else (False, "找不到 prize_1 變數，請將 1 移至英文字母後面")),

        ("1-1-4", "練習題", "修改非法變數名 score1 與 score2", 8, ("score1", "score2"),
         lambda g: (True, f"分數變數命名合法：score1={g.get('score1')}, score2={g.get('score2')}")
         if (g.get("score1") in [85, 100] and g.get("score2") in [92, 60])
         else (False, "請將 1score 與 2score 修改為 score1 與 score2 並完成賦值")),

        ("1-1-4", "挑戰題", "三位選手名次 rank1, rank2, rank3", 4, ("rank1", "rank2", "rank3"),
         lambda g: (True, f"三選手排名就緒：({g.get('rank1')}, {g.get('rank2')}, {g.get('rank3')})")
         if (g.get("rank1") == 100 and g.get("rank2") == 90 and g.get("rank3") == 80)
         else (False, "請宣告 rank1=100, rank2=90, rank3=80")),

        # 1-1-5 變數命名規則三：大小寫大不同
        ("1-1-5", "填空題", "平民 hero 與國王 HERO", 5, ("hero", "HERO"),
         lambda g: (True, "大小寫置物箱識別正確：hero=50, HERO=999")
         if (g.get("hero") == 50 and g.get("HERO") == 999)
         else (False, "請確認 hero=50 與 HERO=999 皆已執行宣告")),

        ("1-1-5", "練習題", "大小寫蘋果 apple 與 Apple", 8, ("apple", "Apple"),
         lambda g: (True, f"雙重大小寫蘋果正確：apple={g.get('apple')}, Apple={g.get('Apple')}")
         if (g.get("apple") in [3, 7] and g.get("Apple") in [10, 20])
         else (False, "請建立小寫 apple (3或7) 與大寫 Apple (10或20)")),

        ("1-1-5", "挑戰題", "三重大小寫 data, Data, DATA", 4, ("data", "Data", "DATA"),
         lambda g: (True, "三重大小寫箱子共存成功！(1, 2, 3)")
         if (g.get("data") == 1 and g.get("Data") == 2 and g.get("DATA") == 3)
         else (False, "請分別宣告 data=1, Data=2, DATA=3")),

        # 1-1-6 變數命名規則四：避開保留字
        ("1-1-6", "填空題", "避開保留字改為 pass_code", 5, ("pass_code",),
         lambda g: (True, "安全避開保留字：pass_code = 1234") if g.get("pass_code") == 1234
         else (False, "找不到變數 pass_code，請將 pass 後加上 _code")),

        ("1-1-6", "練習題", "保護內建 print 命名 print_pages", 8, ("print_pages",),
         lambda g: (True, f"安全變數 print_pages = {g.get('print_pages')}，未污染 print 嘴巴")
         if g.get("print_pages") in [20, 50]
         else (False, "請將變數命名為 print_pages 並設為 20 或 50")),

        ("1-1-6", "挑戰題", "安全統計變數（避開 sum/max 關鍵字）", 3, (),
         lambda g: (True, "成功避開關鍵字危險，建立合法的自訂統計變數！")
         if any(isinstance(v, (int, float)) and any(w in k.lower() for w in ['sum', 'max', 'total']) and k not in ['sum', 'max'] for k, v in g.items() if not k.startswith('_'))
         else (False, "請建立非 sum/max 之安全統計變數（如 total_sum, val_max）")),
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
        badge = '🏆 傳奇大師（金牌徽章 🥇）—— 完全掌握記憶體與變數命名心法！'
    elif total_score >= 80:
        badge = '🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，僅少數細節需微調！'
    elif total_score >= 60:
        badge = '🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作檢查！'
    else:
        badge = '🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 1-1：變數命名規則與記憶體參照 —— 自動評分報告")
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
        "unit": "1-1",
        "unit_title": "變數命名規則與記憶體參照",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_1_1.py",
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
auto_grade_unit_1_1()
