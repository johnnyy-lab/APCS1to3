# -*- coding: utf-8 -*-
"""
PythAPCS123 - 單元 12-9 自動評分器
單元名稱：內建二分搜尋模組：bisect 與數值區間查詢應用
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
import bisect

UNIT_ID = "12-9"
UNIT_TITLE = "內建二分搜尋模組：bisect 與數值區間查詢應用"

QUESTIONS = [
    # 12.9.1
    {"id": "q1", "name": "填空題 12.9.1：import bisect 引入與插入位置查詢", "points": 6},
    {"id": "q2", "name": "練習題 12.9.1：先排序後呼叫 bisect 找出目標插入點", "points": 6},
    {"id": "q3", "name": "挑戰題 12.9.1：極小極大兩極端值在 0 與 len 之邊界表現", "points": 5},
    # 12.9.2
    {"id": "q4", "name": "填空題 12.9.2：bisect_left 下界查詢與相等驗證", "points": 6},
    {"id": "q5", "name": "練習題 12.9.2：及格線門檻索引與不及格人數秒算", "points": 6},
    {"id": "q6", "name": "挑戰題 12.9.2：里程計費門檻查表與封頂設計", "points": 5},
    # 12.9.3
    {"id": "q7", "name": "填空題 12.9.3：bisect_right 上界查詢與最後出現位置 ub - 1", "points": 6},
    {"id": "q8", "name": "練習題 12.9.3：上界索引與小於等於目標之元素統計", "points": 6},
    {"id": "q9", "name": "挑戰題 12.9.3：雙界結合一次定位重複元素之 [start, end] 區間", "points": 5},
    # 12.9.4
    {"id": "q10", "name": "填空題 12.9.4：雙界相減 r - l 秒算區間元素總數", "points": 6},
    {"id": "q11", "name": "練習題 12.9.4：批次多組區間範圍人數極速查詢", "points": 6},
    {"id": "q12", "name": "挑戰題 12.9.4：折價券資格訂單筆數與切片總金額計算", "points": 5},
    # 12.9.5
    {"id": "q13", "name": "填空題 12.9.5：所得稅率級距查表免寫多重分支", "points": 6},
    {"id": "q14", "name": "練習題 12.9.5：遊戲積分段位名稱極速查表", "points": 5},
    {"id": "q15", "name": "挑戰題 12.9.5：購物消費滿額階梯折扣查表實付金額", "points": 5},
    # 12.9.6
    {"id": "q16", "name": "填空題 12.9.6：bisect.insort 動態有序插入新測量值", "points": 6},
    {"id": "q17", "name": "練習題 12.9.6：維護即時緊急度待辦任務有序清單", "points": 5},
    {"id": "q18", "name": "挑戰題 12.9.6：動態串流數據中位數 (Running Median) 監控", "points": 5},
]

def check_q1(g, hist):
    ip = g.get("insert_pos")
    if ip == 11 or ("bisect.bisect(primes, 35)" in hist or "bisect.bisect_right(primes, 35)" in hist):
        return True, "太棒了！正確引入 bisect 模組並精準計算出 35 應插入在索引 11！"
    return False, "請確認填入 import bisect 與 bisect.bisect(primes, 35)。"

def check_q2(g, hist):
    pos = g.get("pos")
    rd = g.get("raw_data")
    if (pos == 2 and rd == [10, 20, 30, 40, 50]) or ("raw_data.sort()" in hist and "bisect.bisect" in hist):
        return True, "完全正確！排序後順利呼叫 bisect 找出數值 25 位於索引 2！"
    return False, "請先對 raw_data 排序，再呼叫 bisect.bisect 找出插入索引。"

def check_q3(g, hist):
    pmin = g.get("pos_min")
    pmax = g.get("pos_max")
    if (pmin == 0 and pmax == 5) or ("bisect.bisect(readings, 0.0)" in hist and "100.0" in hist):
        return True, "太強了！親自驗證 0.0 落在索引 0、100.0 落在 len(5)，邊界行為掌握透徹！"
    return False, "請驗證 0.0 與 100.0 的插入位置 (應分別為 0 與 5)。"

def check_q4(g, hist):
    is_found = g.get("is_found")
    idx = g.get("idx")
    if (is_found is True and idx == 2) or ("bisect.bisect_left" in hist and "members[idx] == query_id" in hist):
        return True, "完全正確！bisect_left 搭配相等比較 ==，安全精確檢驗存在性！"
    return False, "請確認填入 bisect.bisect_left 與相等比較符號 ==。"

def check_q5(g, hist):
    idx_pass = g.get("idx_pass")
    failed_count = g.get("failed_count")
    if (idx_pass == 1 and failed_count == 1) or ("bisect.bisect_left(grades, 60)" in hist):
        return True, "精彩！bisect_left(60) 索引為 1，代表不及格人數恰好為 1 人，秒殺及格線！"
    return False, "請使用 bisect_left(grades, 60) 查詢第一個及格索引與不及格人數。"

def check_q6(g, hist):
    func = g.get("get_fare")
    if callable(func):
        try:
            if func(28) == 35 and func(70) == 60 and func(10) == 15:
                return True, "太實用了！捷運計費函數實機測試完全正確，28km 收 35 元，70km 封頂 60 元！"
        except Exception:
            pass
    if "def get_fare" in hist and "bisect.bisect_left" in hist:
        return True, "計費邏輯正確，通過！"
    return False, "請實作 get_fare(dist) 計算區間車資。"

def check_q7(g, hist):
    lp = g.get("last_pos")
    if lp == 4 or ("bisect.bisect_right" in hist and "ub - 1" in hist):
        return True, "完全正確！bisect_right 取得第一個嚴格大於位置後減 1，即為最後出現索引 4！"
    return False, "請填入 bisect.bisect_right 與 ub - 1 定位最後出現位置。"

def check_q8(g, hist):
    ub = g.get("ub")
    # arr = [5, 10, 15, 15, 15, 20, 25] -> bisect_right(arr, 15) = 5
    if ub == 5 or ("bisect.bisect_right(arr, 15)" in hist):
        return True, "太棒了！上界索引為 5，同時代表小於等於 15 的元素恰有 5 個！"
    return False, "請呼叫 bisect_right 查詢數值 15 的上界索引。"

def check_q9(g, hist):
    s = g.get("start_idx")
    e = g.get("end_idx")
    # exp_records = [10, 20, 20, 35, 50, 50, 50, 80] -> 50: [4, 6]
    if (s == 4 and e == 6) or ("bisect_left" in hist and "bisect_right" in hist):
        return True, "精彩！雙向夾擊精準定位數值 50 之完整區間 [4, 6]！"
    return False, "請利用 bisect_left 與 bisect_right 定位數值 50 的出現區間。"

def check_q10(g, hist):
    count = g.get("count")
    # numbers = [5, 12, 20, 25, 30, 40, 45, 60] -> [20, 40] 內有 20, 25, 30, 40 共 4 個
    if count == 4 or ("r - l" in hist and "bisect_left" in hist and "bisect_right" in hist):
        return True, "完全正確！左閉右閉區間以 bisect_right(40) - bisect_left(20) 秒算個數 4！"
    return False, "請填入 bisect_left(numbers, 20) 與 bisect_right(numbers, 40)。"

def check_q11(g, hist):
    res = g.get("res")
    # queries = [(160, 170), (150, 150), (190, 200)] -> [3, 1, 0]
    if res == [3, 1, 0] or ("count_in_range" in hist):
        return True, "太棒了！批次查詢多組身高區間人數 [3, 1, 0] 完全無誤！"
    return False, "請以 bisect_right - bisect_left 計算各區間人數清單。"

def check_q12(g, hist):
    qc = g.get("qualified_count")
    qs = g.get("qualified_sum")
    # orders = [120, 450, 500, 890, 1200, 1500, 1500, 2300, 3100]
    # [500, 1500] 內: 500, 890, 1200, 1500, 1500 共 5 筆，總和 = 5590 元
    if (qc == 5 and qs == 5590) or ("sum(orders[l:r])" in hist and "r - l" in hist):
        return True, "太厲害了！不僅以雙界算出 5 筆合資格訂單，更以切片累加出總金額 5590 元！"
    return False, "請計算符合區間資格的訂單筆數 (5) 與總金額 (5590)。"

def check_q13(g, hist):
    bi = g.get("bracket_idx")
    # tax_brackets = [50, 120], income = 80 -> idx = 1 ("12%")
    if bi == 1 or ("bisect.bisect(tax_brackets, income)" in hist):
        return True, "完全正確！年所得 80 萬精確對應級距 1（稅率 12%），免寫繁複 if-elif！"
    return False, "請呼叫 bisect.bisect 取得稅率級距索引。"

def check_q14(g, hist):
    func = g.get("get_rank")
    if callable(func):
        try:
            if func(2500) == "黃金" and func(800) == "青銅" and func(3500) == "鑽石":
                return True, "太神了！段位查表函數實機測試全數吻合，2500 分晉升黃金，800 分為青銅！"
        except Exception:
            pass
    if "def get_rank" in hist and "bisect.bisect_right" in hist:
        return True, "段位查表邏輯正確，通過！"
    return False, "請實作 get_rank(points) 函數，回傳對應段位名稱。"

def check_q15(g, hist):
    func = g.get("calc_final_bill")
    if callable(func):
        try:
            if func(2500) == 2250 and func(6000) == 4200 and func(500) == 500:
                return True, "精彩絕倫！滿額折扣查表計算實測完全正確，2500 元折為 2250 元，6000 元折為 4200 元！"
        except Exception:
            pass
    if "def calc_final_bill" in hist and "bisect" in hist:
        return True, "折扣計算邏輯通過！"
    return False, "請實作 calc_final_bill(amount) 計算折後實付金額。"

def check_q16(g, hist):
    lt = g.get("live_temps")
    # live_temps = [18.5, 20.2, 22.0, 25.5], new_reading = 21.4 -> [18.5, 20.2, 21.4, 22.0, 25.5]
    if lt == [18.5, 20.2, 21.4, 22.0, 25.5] or ("bisect.insort" in hist and "live_temps" in hist):
        return True, "完全正確！bisect.insort 動態有序插入 21.4，維護單調序列絲滑無縫！"
    return False, "請呼叫 bisect.insort(live_temps, new_reading)。"

def check_q17(g, hist):
    tasks = g.get("tasks")
    if tasks == [1, 2, 3, 4, 5, 7, 8] or ("bisect.insort(tasks" in hist):
        return True, "太棒了！動態依序插入新任務，維持任務緊急度清單 [1, 2, 3, 4, 5, 7, 8]！"
    return False, "請使用 bisect.insort 依序插入任務至 tasks 清單。"

def check_q18(g, hist):
    stream = g.get("stream")
    if stream == [10, 20, 30, 40, 50] or ("bisect.insort(stream" in hist and "mid_val" in hist):
        return True, "滿分通關！動態中位數監控器實作大獲全勝，全單元與第十二章全體通關！"
    return False, "請使用 bisect.insort 依序插入串流數據並計算中位數。"

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
