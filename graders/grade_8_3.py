# ==============================================================================
# 🧪 《PythAPCS123》單元 8-3：常用串列方法 —— 官方智慧評分與日誌記錄器
# 存放位置：web/graders/grade_8_3.py
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
NOTEBOOK_FILE = "PythAPCS123_8-3_common_list_methods.ipynb"

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


def auto_grade_unit_8_3(env=None):
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
        # 8-3-1 .append() 尾端動態追加元素 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-3-1", "填空題", "呼叫 append 方法依序追加 (a 包含 [100, 200])", 6, ("a",),
         lambda g: (
             (True, "使用 .append(100) 與 .append(200) 動態追加成功！")
             if g.get("a") == [100, 200] or
                ("a.append(100)" in history_clean and "a.append(200)" in history_clean)
             else (False, "請在 8-3-1 填空題空格填入方法名稱 append！")
         )),

        ("8-3-1", "練習題", "及格名單過濾收集器 (passed_list.append(score))", 9, (),
         lambda g: (
             (True, "及格分數 append 收集與 print(*passed_list) 輸出正確！")
             if (".append(" in history_str and ">= 60" in history_str and "print(*" in history_str) or
                ("85 90" in history_str or "70 60 100" in history_str)
             else (False, "請讀入 n 筆成績，若 >= 60 則 append 進 passed_list 並以 print(*passed_list) 印出！")
         )),

        ("8-3-1", "挑戰題", "3 的倍數收集生成器 (multiples.append(i))", 5, (),
         lambda g: (
             (True, "迴圈中倍數過濾與 append 收集正確！")
             if ("% 3 == 0" in history_str and ".append(" in history_str) or
                ("3 6 9" in history_str)
             else (False, "請走訪 1 到 n，將 3 的倍數 append 入串列中並印出！")
         )),

        # ----------------------------------------------------------------------
        # 8-3-2 .pop() 元素彈出與提取 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-3-2", "填空題", "呼叫 pop() 彈出末端元素 (last_item == 30)", 6, ("last_item", "nums"),
         lambda g: (
             (True, "使用 .pop() 成功彈出並保存末端元素！")
             if (g.get("last_item") == 30 and g.get("nums") == [10, 20]) or
                ("nums.pop()" in history_clean)
             else (False, "請在 8-3-2 填空題空格填入方法名稱 pop！")
         )),

        ("8-3-2", "練習題", "堆疊出牌模擬器 (cards.pop() 與 Remaining 顯示)", 9, (),
         lambda g: (
             (True, "兩回合 cards.pop() 出牌與剩餘牌組輸出正確！")
             if ("cards.pop()" in history_clean and "Play card:" in history_str and "Remaining:" in history_str) or
                ("Diamond Q" in history_str and "Spade A" in history_str)
             else (False, "請連續呼叫 cards.pop() 出牌兩次，依序印出出的牌與剩餘牌組！")
         )),

        ("8-3-2", "挑戰題", "FIFO 佇列模擬器 (queue.pop(0) 叫號看診)", 5, (),
         lambda g: (
             (True, "佇列首位 queue.pop(0) 移出與狀態通報正確！")
             if ("queue.pop(0)" in history_clean and "Served:" in history_str) or
                ("Patient 1" in history_str and "Patient 2" in history_str)
             else (False, "請以迴圈呼叫 queue.pop(0) 看診 k 次並輸出服務病患！")
         )),

        # ----------------------------------------------------------------------
        # 8-3-3 .insert(idx, val) 指定位置插入 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-3-3", "填空題", "呼叫 insert(1, 20) 完成中間插入", 6, ("nums",),
         lambda g: (
             (True, "使用 .insert(1, 20) 插入指定位置成功！")
             if g.get("nums") == [10, 20, 30] or
                ("nums.insert(1,20)" in history_clean or "nums.insert(1, 20)" in history_str)
             else (False, "請在 8-3-3 填空題空格填入方法名稱 insert！")
         )),

        ("8-3-3", "練習題", "哨兵隊長加頂儀 (a.insert(0, 0))", 9, (),
         lambda g: (
             (True, "最前端哨兵 a.insert(0, 0) 插入輸出正確！")
             if ("insert(0, 0)" in history_str or "insert(0,0)" in history_clean) or
                ("[0, 5, 10, 15]" in history_str or "[0, 99, 88, 77]" in history_str)
             else (False, "請讀入 3 個整數存入 a，並使用 a.insert(0, 0) 在首位插入哨兵 0！")
         )),

        ("8-3-3", "挑戰題", "保持遞增之排序插入模擬 (sorted_list.insert(i, x))", 5, (),
         lambda g: (
             (True, "遞增排序位置尋找與 insert(i, x) 插入正確！")
             if (".insert(" in history_str and ("append(" in history_str or "break" in history_str)) or
                ("10 20 25 30 40" in history_str)
             else (False, "請找出首個大於 x 的位置進行 insert(i, x) 保持數列遞增！")
         )),

        # ----------------------------------------------------------------------
        # 8-3-4 .remove(val) 依數值精準刪除 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-3-4", "填空題", "呼叫 remove('Bob') 移除名冊成員", 6, ("members",),
         lambda g: (
             (True, "使用 .remove('Bob') 精準移除元素成功！")
             if g.get("members") == ["Alice", "Charlie"] or
                ('members.remove("Bob")' in history_clean or "members.remove('Bob')" in history_clean)
             else (False, "請在 8-3-4 填空題空格填入方法名稱 remove！")
         )),

        ("8-3-4", "練習題", "瑕疵品批號剔除器 (if in 檢查搭配 batches.remove)", 9, (),
         lambda g: (
             (True, "瑕疵批號 in 存在檢查與 .remove() 剔除正確！")
             if ("in batches" in history_str and "batches.remove(" in history_str and "NOT FOUND" in history_str) or
                ("101 202 404 505" in history_str or "NOT FOUND" in history_str)
             else (False, "請檢查 defect_batch 是否在 batches 中，存在則 remove 否則印出 NOT FOUND！")
         )),

        ("8-3-4", "挑戰題", "重複值全數連根拔起 (while 2 in a: a.remove(2))", 5, (),
         lambda g: (
             (True, "while in 迴圈全數移除重複元素完全正確！")
             if ("while 2 in a:" in history_str or "while 2 in a" in history_str or "while2ina:" in history_clean) or
                ("[1, 3, 4, 5]" in history_str)
             else (False, "請使用 while 2 in a: 反覆呼叫 a.remove(2) 清理所有 2！")
         )),

        # ----------------------------------------------------------------------
        # 8-3-5 .reverse() 原地就地反轉 (共 20 分)
        # ----------------------------------------------------------------------
        ("8-3-5", "填空題", "呼叫 reverse() 原地反轉 (letters == ['C', 'B', 'A'])", 6, ("letters",),
         lambda g: (
             (True, "呼叫 .reverse() 完成原地就地反轉！")
             if g.get("letters") == ["C", "B", "A"] or
                ("letters.reverse()" in history_clean)
             else (False, "請在 8-3-5 填空題空格填入方法名稱 reverse！")
         )),

        ("8-3-5", "練習題", "逆序倒數就地計時器 (countdown.reverse())", 9, (),
         lambda g: (
             (True, "countdown.reverse() 就地反轉與 print(*countdown) 輸出正確！")
             if ("countdown.reverse()" in history_clean and "print(*countdown)" in history_clean) or
                ("4 3 2 1" in history_str or "40 30 20 10" in history_str)
             else (False, "請使用 countdown.reverse() 進行原地反轉並以 print(*countdown) 印出！")
         )),

        ("8-3-5", "挑戰題", "雙端操作模擬器 (append, insert, pop, reverse)", 5, (),
         lambda g: (
             (True, "四大串列方法四部曲模擬輸出正確！")
             if (".append(" in history_str and ".insert(" in history_str and ".pop(" in history_str and ".reverse(" in history_str) or
                ("30 20 10 0" in history_str)
             else (False, "請依序執行 append, insert, pop, reverse 四步操作並印出結果！")
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
        badge = '🏆 傳奇大師（金牌徽章 🥇）—— 徹底精通 append、pop、insert、remove 與 reverse 五大神兵方法，串列操控行雲流水！'
    elif total_score >= 80:
        badge = '🥈 卓越冒險者（銀牌徽章 🥈）—— 表現優異，常用串列方法呼叫精準純熟！'
    elif total_score >= 60:
        badge = '🥉 扎根學徒（銅牌徽章 🥉）—— 基礎已建立，請針對紅叉題目微調方法參數與佇列/堆疊邏輯！'
    else:
        badge = '🌱 潛力新星 —— 請確認上方各題目是否都已按下播放鍵 ▶ 執行作答喔！'

    print("=" * 72)
    print(" 📊 《PythAPCS123》單元 8-3：常用串列方法 —— 自動評分報告")
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
        "unit": "8-3",
        "unit_title": "常用串列方法",
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
        "grader_source": os.environ.get("GRADER_SOURCE", "").strip() or "web/graders/grade_8_3.py",
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
auto_grade_unit_8_3()
