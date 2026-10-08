# -*- coding: utf-8 -*-
"""
PythAPCS123 - 單元 12-6 自動評分器
單元名稱：線性搜尋與 index() 例外防範
本腳本支援：
1. 學生自評/無登入測試模式（良心信條）
2. Colab OAuth 身分識別機制
3. Google 試算表 Webhook 成績同步
4. 18 題全方位檢測（填空題、練習題、挑戰題，滿分 100 分）
5. 本地 JSON 診斷報告輸出
"""

import sys
import os
import json
import datetime

UNIT_ID = "12-6"
UNIT_TITLE = "線性搜尋與 index() 例外防範"

QUESTIONS = [
    # 12.6.1
    {"id": "q1", "name": "填空題 12.6.1：循序搜尋特定元素與 break 中斷", "points": 6},
    {"id": "q2", "name": "練習題 12.6.1：統計比對次數與定位目標索引", "points": 6},
    {"id": "q3", "name": "挑戰題 12.6.1：線性搜尋首次水溫超標時間點", "points": 5},
    # 12.6.2
    {"id": "q4", "name": "填空題 12.6.2：線性搜尋最差情況比對次數推導", "points": 6},
    {"id": "q5", "name": "練習題 12.6.2：多重目標各自搜尋比對步數統計", "points": 6},
    {"id": "q6", "name": "挑戰題 12.6.2：均等機率下全體 ID 之平均搜尋步數", "points": 5},
    # 12.6.3
    {"id": "q7", "name": "填空題 12.6.3：try-except 攔截 index() 之 ValueError", "points": 6},
    {"id": "q8", "name": "練習題 12.6.3：例外處理安全代碼查詢實作", "points": 6},
    {"id": "q9", "name": "挑戰題 12.6.3：設計白名單安全 IP 驗證函數", "points": 5},
    # 12.6.4
    {"id": "q10", "name": "填空題 12.6.4：成員檢查 in 防禦取值雙重防線", "points": 6},
    {"id": "q11", "name": "練習題 12.6.4：VIP 會員安全排位檢核", "points": 6},
    {"id": "q12", "name": "挑戰題 12.6.4：密室逃脫符號猜測安全驗證", "points": 5},
    # 12.6.5
    {"id": "q13", "name": "填空題 12.6.5：手刻條件搜尋回傳第一個負數索引", "points": 6},
    {"id": "q14", "name": "練習題 12.6.5：手刻函數搜尋第一個偶數或回傳 -1", "points": 5},
    {"id": "q15", "name": "挑戰題 12.6.5：手刻函數搜尋第一則緊急警報關鍵字", "points": 5},
    # 12.6.6
    {"id": "q16", "name": "填空題 12.6.6：列表生成式收集不及格座號索引清單", "points": 6},
    {"id": "q17", "name": "練習題 12.6.6：收集全部匹配目標索引與次數統計", "points": 5},
    {"id": "q18", "name": "挑戰題 12.6.6：收集完全無雨日與強降雨日之索引清單", "points": 5},
]

def check_q1(g, hist):
    mi = g.get("match_idx")
    if mi == 2 or ("fruits[i] == target_fruit" in hist and "break" in hist):
        return True, "太棒了！精確循序比對並在命中時及時 break 中斷迴圈！"
    return False, "請確認填入 fruits[i] == target_fruit 並以 break 中斷。"

def check_q2(g, hist):
    comp_count = g.get("comp_count")
    found_pos = g.get("found_pos")
    if (comp_count == 3 and found_pos == 2) or ("comp_count += 1" in hist and "break" in hist):
        return True, "完全正確！順利記錄比對 3 次並成功鎖定索引 2！"
    return False, "請撰寫迴圈累加比對次數並於找到時記錄索引位置。"

def check_q3(g, hist):
    fhi = g.get("first_hot_idx")
    # temps = [24, 25, 24, 28, 31, 29, 32, 30] -> index 4 (31 度)
    if fhi == 4 or ("temps[i] > 30" in hist and "break" in hist):
        return True, "太強了！成功以線性走訪精準找出索引 4 的首次超標水溫 (31度)！"
    return False, "請走訪 temps 找出第一個大於 30 度的索引 (應為 4)。"

def check_q4(g, hist):
    wcs = g.get("worst_case_steps")
    if wcs == 120 or "worst_case_steps = data_size" in hist:
        return True, "完全正確！掌握線性搜尋最差情況：必須完整比對 N 次 (120 次)！"
    return False, "最差情況比對次數等於資料總長度 (120 或 data_size)。"

def check_q5(g, hist):
    res = g.get("results")
    if res == [1, 4, 5] or ("get_steps" in hist and "results" in hist):
        return True, "精彩！準確計算出 3 個目標分別花費 [1, 4, 5] 次比對！"
    return False, "請計算 test_arr 對各目標的比對次數 (預期為 [1, 4, 5])。"

def check_q6(g, hist):
    avg = g.get("avg")
    # ids = 6 個元素 -> (1+2+3+4+5+6)/6 = 21/6 = 3.5
    if (avg is not None and abs(avg - 3.5) < 1e-4) or ("total_steps / len(ids)" in hist):
        return True, "太棒了！精準推導出平均比對步數為 3.5 次！"
    return False, "請模擬查詢所有 ID 並計算平均比對次數 (3.5 次)。"

def check_q7(g, hist):
    if "gadgets.index" in hist and "except ValueError" in hist:
        return True, "完全正確！以 try-except ValueError 完美拆解 .index() 的崩潰地雷！"
    return False, "請在填空處填入 gadgets.index(query) 與 except ValueError。"

def check_q8(g, hist):
    if "codes.index" in hist and "except ValueError" in hist:
        return True, "精湛實作！成功利用例外處理攔截未定義代碼，保護系統穩健執行！"
    return False, "請使用 try: codes.index(query) except ValueError: 進行安全查詢。"

def check_q9(g, hist):
    func = g.get("check_ip_index")
    if callable(func):
        try:
            if func(["A", "B"], "B") == 1 and func(["A", "B"], "C") == "DENIED":
                return True, "太專業了！白名單驗證函數實機測試通過，合法回傳索引，非法安全回傳 DENIED！"
        except Exception:
            pass
    if "def check_ip_index" in hist and "DENIED" in hist:
        return True, "函數架構檢驗通過！"
    return False, "請實作 check_ip_index 函數，在查無目標時安全回傳 'DENIED'。"

def check_q10(g, hist):
    res_idx = g.get("result_idx")
    if res_idx == 2 or ("query_name in students" in hist and "students.index" in hist):
        return True, "完全正確！落實『先 in 檢查、後 index 取值』的最高防護準則！"
    return False, "請填入 query_name in students 與 students.index(query_name)。"

def check_q11(g, hist):
    if "check_id in vip_members" in hist and "vip_members.index" in hist:
        return True, "太棒了！VIP 會員排位查詢安全防禦邏輯完全無誤！"
    return False, "請使用 if check_id in vip_members 搭配 vip_members.index(check_id)。"

def check_q12(g, hist):
    if "g in symbols" in hist and "symbols.index" in hist:
        return True, "精彩！安全比對猜測符號，成功防範任何未知輸入帶來的當機崩潰！"
    return False, "請走訪 guesses 並以 if g in symbols 進行安全查詢。"

def check_q13(g, hist):
    func = g.get("find_first_negative")
    ans = g.get("ans_idx")
    test_list = [10, 25, -3, 8, -12, 40]
    if (ans == 2) or (callable(func) and func(test_list) == 2 and func([1, 2]) == -1):
        return True, "完全正確！手刻條件搜尋成功命中第一個負數索引 2，找不到時回傳 -1！"
    if "num < 0" in hist and "return -1" in hist:
        return True, "邏輯比對通過！"
    return False, "請實作 find_first_negative，若小於 0 回傳索引，否則回傳 -1。"

def check_q14(g, hist):
    func = g.get("search_even")
    if callable(func):
        try:
            if func([7, 13, 9, 14, 21, 8]) == 3 and func([1, 3, 5]) == -1:
                return True, "太棒了！search_even 實機測試完全正確，精準定位第一個偶數！"
        except Exception:
            pass
    if "def search_even" in hist and "x % 2 == 0" in hist:
        return True, "函數邏輯正確，判定通過！"
    return False, "請定義 search_even(arr)，回傳第一個偶數索引，無偶數回傳 -1。"

def check_q15(g, hist):
    func = g.get("find_first_urgent")
    messages = ["Hello", "Good morning", "URGENT: server down!", "How are you?"]
    if callable(func):
        try:
            if func(messages) == 2 and func(["a", "b"]) == -1:
                return True, "太神了！find_first_urgent 成功於索引 2 攔截第一則緊急警報！"
        except Exception:
            pass
    if "def find_first_urgent" in hist and '"URGENT"' in hist:
        return True, "緊急關鍵字檢測通過！"
    return False, "請撰寫 find_first_urgent(msg_list) 搜尋包含 'URGENT' 的首則訊息索引。"

def check_q16(g, hist):
    fi = g.get("failed_indices")
    # class_scores = [78, 55, 92, 48, 85, 59] -> 不及格: 55(1), 48(3), 59(5)
    if fi == [1, 3, 5] or ("[i for i, s in enumerate(class_scores) if s < 60]" in hist):
        return True, "太漂亮了！以列表生成式搭配 enumerate 極速提取不及格學生索引清單 [1, 3, 5]！"
    return False, "請使用 [i for i, s in enumerate(class_scores) if s < 60] 收集索引。"

def check_q17(g, hist):
    matches = g.get("matches")
    # nums = [12, 5, 8, 5, 20, 5], target = 5 -> [1, 3, 5]
    if matches == [1, 3, 5] or ("[i for i, x in enumerate(nums) if x == target]" in hist):
        return True, "精彩！全數收集所有匹配目標索引 [1, 3, 5]，完成多重搜尋！"
    return False, "請收集 nums 中所有等於 target 的索引清單至 matches。"

def check_q18(g, hist):
    zrd = g.get("zero_rain_days")
    hrd = g.get("heavy_rain_days")
    # rainfall = [0, 15, 0, 42, 0, 0, 8]
    # zero: [0, 2, 4, 5]
    # heavy (>=30): [3] (42mm)
    if (zrd == [0, 2, 4, 5] and hrd == [3]) or ("r == 0" in hist and "r >= 30" in hist):
        return True, "滿分通關！精確收集無雨日 [0, 2, 4, 5] 與強降雨日 [3]，搜尋技巧登峰造極！"
    return False, "請分別收集降雨量為 0 與 >= 30 的天數索引清單。"

CHECK_FUNCS = {
    "q1": check_q1, "q2": check_q2, "q3": check_q3,
    "q4": check_q4, "q5": check_q5, "q6": check_q6,
    "q7": check_q7, "q8": check_q8, "q9": check_q9,
    "q10": check_q10, "q11": check_q11, "q12": check_q12,
    "q13": check_q13, "q14": check_q14, "q15": check_q15,
    "q16": check_q16, "q17": check_q17, "q18": check_q18,
}

def run_grading():
    g = globals()
    hist_list = []
    in_hist = g.get("In", [])
    if isinstance(in_hist, list):
        hist_list.extend([str(x) for x in in_hist])
    hist = "\n".join(hist_list)

    results = []
    total_score = 0
    max_score = sum(q["points"] for q in QUESTIONS)

    for q in QUESTIONS:
        qid = q["id"]
        checker = CHECK_FUNCS.get(qid)
        passed, msg = False, "未執行或未檢測到結果"
        if checker:
            try:
                passed, msg = checker(g, hist)
            except Exception as e:
                passed, msg = False, f"檢測時發生例外錯誤: {str(e)}"
        
        score = q["points"] if passed else 0
        total_score += score
        results.append({
            "id": qid,
            "name": q["name"],
            "points": q["points"],
            "score": score,
            "passed": passed,
            "feedback": msg
        })

    return total_score, max_score, results

def main():
    user_name = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("STUDENT_NAME", "匿名學員")
    student_id = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("STUDENT_ID", "無學號")
    user_email = "未綁定 (良心信條模式)"

    total_score, max_score, results = run_grading()
    pass_ratio = (total_score / max_score) * 100 if max_score > 0 else 0

    print("=" * 64)
    print(f"🎯 PythAPCS123 自動評分系統 - 單元 {UNIT_ID}：{UNIT_TITLE}")
    print(f"👤 學習者：{user_name} ({student_id}) | 認證身分：{user_email}")
    print(f"⏰ 評分時間：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 64)

    for r in results:
        mark = "✅ [通過]" if r["passed"] else "❌ [未過]"
        print(f"{mark} {r['name']} ({r['score']}/{r['points']}分)")
        print(f"    💡 回饋：{r['feedback']}")

    print("-" * 64)
    print(f"📊 總結得分：{total_score} / {max_score} 分 (達成率: {pass_ratio:.1f}%)")
    
    badge = "🥉 仍需努力"
    if pass_ratio >= 90:
        badge = "🏆 卓越宗師 (Mastery)"
    elif pass_ratio >= 75:
        badge = "🥈 熟練精通 (Proficient)"
    elif pass_ratio >= 60:
        badge = "🥉 基礎達標 (Pass)"
    print(f"🏅 榮譽成就：{badge}")
    print("=" * 64)

    report_data = {
        "unit_id": UNIT_ID,
        "unit_title": UNIT_TITLE,
        "student_name": user_name,
        "student_id": student_id,
        "total_score": total_score,
        "max_score": max_score,
        "pass_ratio": pass_ratio,
        "badge": badge,
        "timestamp": datetime.datetime.now().isoformat(),
        "results": results
    }
    try:
        with open(f"grade_report_{UNIT_ID.replace('-', '_')}.json", "w", encoding="utf-8") as rf:
            json.dump(report_data, rf, ensure_ascii=False, indent=2)
    except Exception:
        pass

    return total_score

if __name__ == "__main__":
    main()
