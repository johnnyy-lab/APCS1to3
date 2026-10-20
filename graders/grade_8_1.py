# ==============================================================================
# 🧪 《PythAPCS123》單元 8-1：串列建立、正負索引與解包輸出 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_8_1.py
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
NOTEBOOK_FILE = "PythAPCS123_8-1_list_creation_indexing_and_unpacking.ipynb"

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


def auto_grade_unit_8_1(env=None):
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
        # 8-1-1 串列宣告與中括號語法 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-1-1", "填空題", "方括號串列宣告 numbers = [10, 20, 30]", 6, ("numbers",),
         lambda g: (
             (True, "方括號串列宣告完全正確！")
             if g.get("numbers") == [10, 20, 30] or
                ("numbers=[10,20,30]" in history_clean or "numbers = [10, 20, 30]" in history_str)
             else (False, "請在 8-1-1 填空題空格填入方括號 [ ] 並包裹 10, 20, 30！")
         )),

        ("8-1-1", "練習題", "每日氣溫紀錄儀 (temps 串列打包輸出)", 9, ("temps",),
         lambda g: (
             (True, "每日氣溫串列打包與輸出正確！")
             if ("temps" in g and isinstance(g.get("temps"), list) and len(g.get("temps")) == 3) or
                ("temps" in history_str and "[" in history_str and "]" in history_str) or
                ("[25, 28, 26]" in history_str or "[18, 17, 20]" in history_str)
             else (False, "請將三個輸入的氣溫數值存入 temps 串列中並印出！")
         )),

        ("8-1-1", "挑戰題", "購物車明細打包機 ([item, qty, price, total])", 5, ("receipt",),
         lambda g: (
             (True, "四項購物車明細元素打包串列輸出正確！")
             if ("receipt" in g and isinstance(g.get("receipt"), list) and len(g.get("receipt")) == 4) or
                ("['Apple', 5, 20, 100]" in history_str or "receipt" in history_str and "*" in history_str)
             else (False, "請計算總花費 total 並將 item, qty, price, total 打包成 receipt 串列印出！")
         )),

        # ----------------------------------------------------------------------
        # 8-1-2 正向與負向索引存取 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-1-2", "填空題", "索引存取金牌 champion_medal = medals[2 或 -1]", 6, ("champion_medal",),
         lambda g: (
             (True, "成功透過索引取出 'Gold' 獎牌！")
             if g.get("champion_medal") == "Gold" or
                ("medals[2]" in history_clean or "medals[-1]" in history_clean)
             else (False, "請在 8-1-2 填空題中括號內填入 2 或 -1 取出 Gold！")
         )),

        ("8-1-2", "練習題", "賽車冠亞季軍與殿軍通報 (Champion 與 Last Place)", 9, (),
         lambda g: (
             (True, "冠亞季殿軍 racers 索引 0 與 -1 通報正確！")
             if ("Champion:" in history_str and "Last Place:" in history_str and
                 ("racers[0]" in history_clean or "racers[-1]" in history_clean or "racers" in history_str)) or
                ("Lightning" in history_str and "Mater" in history_str)
             else (False, "請建立 racers 串列，以 racers[0] 輸出 Champion，racers[-1] 輸出 Last Place！")
         )),

        ("8-1-2", "挑戰題", "五邊形周長計算器 (edges[0] 到 edges[4] 加總)", 5, (),
         lambda g: (
             (True, "五邊長索引存取與周長總和計算正確！")
             if ("Perimeter:" in history_str and ("edges[0]" in history_clean or "perimeter" in history_str or "sum(" in history_str)) or
                ("Perimeter: 25" in history_str)
             else (False, "請讀入 5 邊長存入 edges 串列，計算周長並輸出 Perimeter: [周長]！")
         )),

        # ----------------------------------------------------------------------
        # 8-1-3 索引就地修改與值替換 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-1-3", "填空題", "索引賦值修改不及格成績 scores[1] = 60", 6, ("scores",),
         lambda g: (
             (True, "成功透過 scores[1] = 60 完成就地修改！")
             if g.get("scores") == [80, 60, 95] or
                ("scores[1]=60" in history_clean or "scores[1] = 60" in history_str)
             else (False, "請在 8-1-3 填空題填入索引 1 與新數值 60！")
         )),

        ("8-1-3", "練習題", "首尾元素對調器 (a[0], a[2] = a[2], a[0])", 9, (),
         lambda g: (
             (True, "首尾元素單行交換賦值輸出正確！")
             if ("a[0], a[2] = a[2], a[0]" in history_str or "a[0],a[2]=a[2],a[0]" in history_clean or
                 ("a[0]" in history_str and "a[2]" in history_str and "=" in history_str)) or
                ("[30, 20, 10]" in history_str or "[11, 50, 99]" in history_str)
             else (False, "請讀入 3 個整數存入 a，將 a[0] 與 a[2] 對調後印出！")
         )),

        ("8-1-3", "挑戰題", "負數歸零淨化器 (numbers[i] = 0)", 5, (),
         lambda g: (
             (True, "迴圈巡檢與負數歸零淨化正確！")
             if ("numbers[i] < 0" in history_clean and ("numbers[i] = 0" in history_clean or "numbers[i]=0" in history_clean)) or
                ("[5, 0, 8, 0]" in history_str)
             else (False, "請走訪 numbers 串列，若小於 0 則將該位置數值修改為 0！")
         )),

        # ----------------------------------------------------------------------
        # 8-1-4 串列乘法快速初始化 [0] * n (共 20 分)
        # ----------------------------------------------------------------------
        ("8-1-4", "填空題", "串列乘法快速宣告 slots = [0] * 8", 6, ("slots",),
         lambda g: (
             (True, "串列乘法 [0] * 8 建立 8 格串列完全正確！")
             if (isinstance(g.get("slots"), list) and len(g.get("slots")) == 8 and all(x == 0 for x in g.get("slots"))) or
                ("[0]*8" in history_clean or "[0] * 8" in history_str)
             else (False, "請在 8-1-4 填空題空格填入 * 8！")
         )),

        ("8-1-4", "練習題", "點名出缺席登記簿 ([0] * 5 出席修改為 1)", 9, (),
         lambda g: (
             (True, "點名串列初始 [0] * 5 與出席狀態修改正確！")
             if ("roll_call" in history_str and "[0] * 5" in history_str or "[0]*5" in history_clean) or
                ("[0, 1, 0, 0, 1]" in history_str or "[1, 0, 1, 0, 0]" in history_str)
             else (False, "請建立 roll_call = [0] * 5，將輸入的出席隊員位置修改為 1 並印出！")
         )),

        ("8-1-4", "挑戰題", "骰子點數計數器 (counts[pip] += 1 桶子計數法)", 5, (),
         lambda g: (
             (True, "長度 7 之次數陣列初始化與次數統計輸出正確！")
             if ("counts" in history_str and "[0] * 7" in history_str or "[0]*7" in history_clean) and
                ("Number 6 count:" in history_str or "+= 1" in history_str)
             else (False, "請建立 counts = [0] * 7，統計點數 6 出現次數並依格式印出！")
         )),

        # ----------------------------------------------------------------------
        # 8-1-5 星號解包輸出 print(*a) (共 20 分)
        # ----------------------------------------------------------------------
        ("8-1-5", "填空題", "星號解包運算子 print(*ans)", 6, (),
         lambda g: (
             (True, "星號解包 print(*ans) 填寫正確！")
             if ("print(*ans)" in history_clean or "print( *ans )" in history_str)
             else (False, "請在 8-1-5 填空題 ans 前方填入星號 * 進行解包！")
         )),

        ("8-1-5", "練習題", "幸運號碼公布機 (print(*lottery) 與 sep=',' 排版)", 9, (),
         lambda g: (
             (True, "樂透號碼星號解包與逗號分隔輸出正確！")
             if ("print(*lottery)" in history_clean and ("sep=','" in history_clean or 'sep=","' in history_clean)) or
                ("7 14 21 28" in history_str and "7,14,21,28" in history_str)
             else (False, "請讀入 4 個號碼，分別以 print(*lottery) 與 print(*lottery, sep=',') 輸出！")
         )),

        ("8-1-5", "挑戰題", "陣列平移輪替輸出 ([a[2], a[0], a[1]] 解包印出)", 5, (),
         lambda g: (
             (True, "三個元素右移輪替與星號解包輸出正確！")
             if ("print(*" in history_str and ("a[2]" in history_str or "new_" in history_str)) or
                ("3 1 2" in history_str)
             else (False, "請將三個元素向右循環平移一位，並以 print(*新串列) 一行印出！")
         ))
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
        badge = '🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通串列建立、正負索引、就地修改、[0]*n 乘法與 print(*a) 解包，序列神手！'
    elif total_score >= 80:
        badge = '🥈 卓越冒險者（銀牌徽章 🥈）—— 表現優異，串列索引存取與星號解包掌握紮實！'
    elif total_score >= 60:
        badge = '🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目微調索引與初始化乘法！'
    else:
        badge = '🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 8-1：串列建立、正負索引與解包輸出 —— 自動評分報告")
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
        "unit": "8-1",
        "unit_title": "串列建立、正負索引與解包輸出",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_8_1.py",
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
auto_grade_unit_8_1()
