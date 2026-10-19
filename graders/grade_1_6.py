# ==============================================================================
# 🧪 《PythAPCS123》單元 1-6：縮排規範與代碼區塊 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_1_6.py
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
NOTEBOOK_FILE = "PythAPCS123_1-6_indentation_and_code_blocks.ipynb"

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


def auto_grade_unit_1_6():
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

    test_cases = [
        # 1-6-1 行首嚴禁任意留白——抓出出列站錯的 IndentationError (共 25 分)
        ("1-6-1", "填空題", "刪除行首多餘空格 my_score = 95", 7, ("my_score",),
         lambda g: (True, "成功刪除行首多餘空格，my_score = 95！") if (g.get("my_score") == 95 or g.get("score") == 95)
         else (False, "找不到 my_score 或數值不為 95，請刪除第二行最前方的多餘空格")),

        ("1-6-1", "練習題", "排版混亂修復 price 與 num", 10, ("price", "num"),
         lambda g: (True, f"多行縮排修復正確：price={g.get('price')}, num={g.get('num')}")
         if ((g.get("price") == 50 and g.get("num") == 3) or (g.get("price") == 80 and g.get("num") == 2))
         else (False, "找不到變數 price 與 num，請將所有行靠齊最左側並計算總額")),

        ("1-6-1", "挑戰題", "四行循序計算獎金 bonus", 8, ("bonus",),
         lambda g: (True, f"四行循序計算完成：bonus = {g.get('bonus')}")
         if "bonus" in g
         else (False, "找不到變數 bonus，請宣告 base, rate 計算 bonus = base * rate // 100")),

        # 1-6-2 縮排界定程式區塊——「母雞帶小鴨」的層級從屬概念 (共 25 分)
        ("1-6-2", "填空題", "if 區塊內補齊 4 個空格縮排", 7, ("score",),
         lambda g: (True, "條件判斷與縮排語法完全正確！") if g.get("score") == 100
         else (False, "請在 if 條件下的 print 指令前補上 4 個空格完成縮排")),

        ("1-6-2", "練習題", "補給藥水 if 縮排雙行 print (potion)", 10, ("potion",),
         lambda g: (True, "縮排區塊撰寫完全正確！") if "potion" in g
         else (False, "請宣告 potion = True 並在 if 縮排區塊內撰寫兩行 print")),

        ("1-6-2", "挑戰題", "模擬戰鬥獲勝金幣增加 is_win, gold", 8, ("gold", "is_win"),
         lambda g: (True, f"戰鬥獲勝金幣增加成功：gold = {g.get('gold')}")
         if (g.get("is_win") is True and "gold" in g)
         else (False, "請設定 is_win = True 並在 if 區塊內增加 gold 數值")),

        # 1-6-3 空格與 Tab 絕不混用——守護建築結構的 TabError 警告 (共 25 分)
        ("1-6-3", "填空題", "手動補齊為 4 個空格一致深度", 7, ("msg1", "msg2", "flag"),
         lambda g: (True, "縮排深度一致性校正成功！")
         if (g.get("flag") is True and "msg1" in g and "msg2" in g)
         else (False, "請將 msg2 前方的縮排手動補滿為 4 個空格齊頭")),

        ("1-6-3", "練習題", "三計算指令校正為標準 4 空格 sum_val", 10, ("sum_val",),
         lambda g: (True, f"縮排校正與總和計算完成：sum_val = {g.get('sum_val')}")
         if g.get("sum_val") in [60, 15]
         else (False, "請校正 val1, val2, val3 縮排為 4 格並算出 sum_val (60 或 15)")),

        ("1-6-3", "挑戰題", "兩層巢狀縮排 (has_ticket, is_vip)", 8, ("has_ticket", "is_vip"),
         lambda g: (True, "兩層巢狀縮排設計成功！")
         if ("has_ticket" in g and "is_vip" in g)
         else (False, "請宣告 has_ticket 與 is_vip 並以 4 格與 8 格進行巢狀縮排")),

        # 1-6-4 優雅的呼吸留白——中間與後方的美化空白規範 (共 25 分)
        ("1-6-4", "填空題", "運算子兩側優雅呼吸留白 ans", 7, ("ans",),
         lambda g: (True, "運算子呼吸留白正確：ans = 120") if g.get("ans") == 120
         else (False, "找不到變數 ans 或數值不為 120，請填入帶空格的 = 與 +")),

        ("1-6-4", "練習題", "擁擠算式美化重排 result", 10, ("result",),
         lambda g: (True, f"算式美化重排計算成功：result = {g.get('result')}")
         if g.get("result") in [17, 46]
         else (False, "變數 result 數值不符合測資（預期 17 或 46）")),

        ("1-6-4", "挑戰題", "文具店結帳清單頂尖工程師排版", 8, ("pen", "notebook", "ruler"),
         lambda g: (True, "文具店結帳變數設定與總價計算正確！")
         if ("pen" in g and "notebook" in g and "ruler" in g)
         else (False, "請宣告 pen=15, notebook=45, ruler=20 並計算 3筆+2本+1尺之總花費")),
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
        badge = '🏆 傳奇大師（金牌徽章 🥇）—— 縮排規範與代碼品味臻於化境！'
    elif total_score >= 80:
        badge = '🥈 卓越冒險者（銀牌徽章 🥈）—— 表現極佳，僅少數細節需微調！'
    elif total_score >= 60:
        badge = '🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目稍作檢查！'
    else:
        badge = '🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 1-6：縮排規範與代碼區塊 —— 自動評分報告")
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
        "unit": "1-6",
        "unit_title": "縮排規範與代碼區塊",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_1_6.py",
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
auto_grade_unit_1_6()
