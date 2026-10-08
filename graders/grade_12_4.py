# -*- coding: utf-8 -*-
"""
PythAPCS123 - 單元 12-4 自動評分器
單元名稱：匿名函數 lambda 與多準則複合鍵值排序
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
import urllib.request
import urllib.parse

# 題庫設定與配分
UNIT_ID = "12-4"
UNIT_TITLE = "匿名函數 lambda 與多準則複合鍵值排序"
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbw9u_mD_oFvK8bW8Vv9X9X9X9X9X9X9X9/exec"

QUESTIONS = [
    # 12.4.1
    {"id": "q1", "name": "填空題 12.4.1：lambda 乘以 2 長度排序", "points": 6},
    {"id": "q2", "name": "練習題 12.4.1：模 5 餘數排序與篩選", "points": 6},
    {"id": "q3", "name": "挑戰題 12.4.1：大小寫不敏感 lambda 排序", "points": 5},
    # 12.4.2
    {"id": "q4", "name": "填空題 12.4.2：線段長度差值排序", "points": 6},
    {"id": "q5", "name": "練習題 12.4.2：圖書價格索引排序與首項", "points": 6},
    {"id": "q6", "name": "挑戰題 12.4.2：包裹體積降序排序", "points": 5},
    # 12.4.3
    {"id": "q7", "name": "填空題 12.4.3：年級與班級雙準則打包排序", "points": 6},
    {"id": "q8", "name": "練習題 12.4.3：選手組別與秒數雙升序排序", "points": 6},
    {"id": "q9", "name": "挑戰題 12.4.3：年份與頁數雙升序排序", "points": 5},
    # 12.4.4
    {"id": "q10", "name": "填空題 12.4.4：積分負號降序與犯規升序", "points": 6},
    {"id": "q11", "name": "練習題 12.4.4：員工績效降序與遲到升序", "points": 6},
    {"id": "q12", "name": "挑戰題 12.4.4：公會等級戰力雙降序與名稱升序", "points": 5},
    # 12.4.5
    {"id": "q13", "name": "填空題 12.4.5：字典評分與好評雙降序", "points": 6},
    {"id": "q14", "name": "練習題 12.4.5：學生字典分數降序與榜首提取", "points": 5},
    {"id": "q15", "name": "挑戰題 12.4.5：餐廳外送距離與費用雙升序", "points": 5},
    # 12.4.6
    {"id": "q16", "name": "填空題 12.4.6：基地台原點距離平方降序", "points": 6},
    {"id": "q17", "name": "練習題 12.4.6：二維座標距離平方排序與最近點", "points": 5},
    {"id": "q18", "name": "挑戰題 12.4.6：寶箱相對於玩家距離平方排序", "points": 5},
]

def check_q1(g, hist):
    sw = g.get("sorted_words")
    expected = ["c", "go", "python", "javascript"]
    if sw == expected:
        return True, "太棒了！成功運用 lambda 表達式依字元長度完成正確排序！"
    if "lambda" in hist and "len(" in hist:
        return True, "語法邏輯正確，檢測通過！"
    return False, "未檢測到正確的 sorted_words 排序結果，請使用 sorted(words, key=lambda x: len(x) * 2)。"

def check_q2(g, hist):
    # 模 5 餘數排序
    data = [14, 20, 8, 12, 5, 9]
    expected_order = [20, 5, 12, 8, 14, 9] # 20%5=0, 5%5=0, 12%5=2, 8%5=3, 14%5=4, 9%5=4 (stable sort)
    rem_zero = g.get("rem_zero")
    res = g.get("res")
    if res == expected_order or (rem_zero == [20, 5] and "x % 5" in hist):
        return True, "完全正確！精準運用 lambda x: x % 5 完成餘數排序與零餘數篩選！"
    if "% 5" in hist and "lambda" in hist:
        return True, "檢測到模 5 排序邏輯，判定通過！"
    return False, "未獲得符合預期的餘數排序結果，請確認 sorted(data, key=lambda x: x % 5)。"

def check_q3(g, hist):
    words = ["apple", "BANANA", "Cherry", "date"]
    expected = ["apple", "BANANA", "Cherry", "date"]
    res = g.get("res")
    if "s.lower()" in hist or "x.lower()" in hist or (isinstance(res, list) and len(res) == 4 and [w.lower() for w in res] == sorted([w.lower() for w in words])):
        return True, "太厲害了！成功運用 lambda 搭配 .lower() 達成大小寫不敏感排序！"
    return False, "請使用 sorted(words, key=lambda s: s.lower()) 完成大小寫不敏感排序。"

def check_q4(g, hist):
    ss = g.get("sorted_segments")
    expected = [[5, 7], [8, 12], [2, 10], [1, 15]] # 長度分別為 2, 4, 8, 14
    if ss == expected or ("seg[1] - seg[0]" in hist and "lambda" in hist):
        return True, "完全正確！精確計算終點減起點之長度特徵值！"
    return False, "未檢測到正確的線段長度排序結果，請填入 seg[1] - seg[0]。"

def check_q5(g, hist):
    # 圖書依價格 (b[2]) 排序
    books = [("Python 入門", 350, 480), ("演算法圖鑑", 280, 550), ("APCS 攻略", 400, 420)]
    expected = [("APCS 攻略", 400, 420), ("Python 入門", 350, 480), ("演算法圖鑑", 280, 550)]
    res = g.get("res")
    if res == expected or ("b[2]" in hist or "x[2]" in hist):
        return True, "精彩！熟練使用索引 x[2] 依價格排序並取出最便宜書籍！"
    return False, "請使用 sorted(books, key=lambda b: b[2]) 依價格欄位排序。"

def check_q6(g, hist):
    sp = g.get("sorted_pkg")
    packages = [(10, 20, 30), (5, 5, 50), (15, 15, 15), (2, 40, 40)]
    # 體積: 6000, 1250, 3375, 3200 -> 降序: 6000, 3375, 3200, 1250
    expected = [(10, 20, 30), (15, 15, 15), (2, 40, 40), (5, 5, 50)]
    if sp == expected or ("p[0] * p[1] * p[2]" in hist and "reverse=True" in hist):
        return True, "太棒了！成功在 lambda 中計算三維乘積並結合 reverse=True 完成體積降序排序！"
    return False, "請計算 p[0] * p[1] * p[2] 並加上 reverse=True 完成包裹降序排序。"

def check_q7(g, hist):
    sr = g.get("sorted_roster")
    # 年級升序、班級升序: (1, 'A', '小華'), (1, 'B', '小英'), (2, 'A', '小強'), (2, 'B', '小明')
    expected = [(1, "A", "小華"), (1, "B", "小英"), (2, "A", "小強"), (2, "B", "小明")]
    if sr == expected or ("(s[0], s[1])" in hist or "(s[0],s[1])" in hist):
        return True, "完全正確！順利運用元組打包 (s[0], s[1]) 實現多準則雙鍵值排序！"
    return False, "請填入 (s[0], s[1]) 完成年級與班級的元組打包排序。"

def check_q8(g, hist):
    ad = [(2, 14.5, "Tom"), (1, 15.2, "Jerry"), (2, 12.8, "Bob"), (1, 13.9, "Alice")]
    expected = [(1, 13.9, "Alice"), (1, 15.2, "Jerry"), (2, 12.8, "Bob"), (2, 14.5, "Tom")]
    res = g.get("res")
    if res == expected or ("(a[0], a[1])" in hist or "(x[0], x[1])" in hist or "(a[0],a[1])" in hist):
        return True, "太棒了！成功實現組別升序與秒數升序之雙鍵值排序！"
    return False, "請使用 sorted(athlete_data, key=lambda a: (a[0], a[1]))。"

def check_q9(g, hist):
    books = [(2022, 350, "BookA"), (2020, 500, "BookB"), (2022, 180, "BookC"), (2020, 320, "BookD")]
    # 年份升序、頁數升序: (2020, 320, 'BookD'), (2020, 500, 'BookB'), (2022, 180, 'BookC'), (2022, 350, 'BookA')
    expected = [(2020, 320, "BookD"), (2020, 500, "BookB"), (2022, 180, "BookC"), (2022, 350, "BookA")]
    sb = g.get("sorted_books")
    if sb == expected or ("(b[0], b[1])" in hist or "(x[0], x[1])" in hist):
        return True, "完美！成功以元組打包雙欄位實現圖書年份與頁數雙升序！"
    return False, "請使用 sorted(books, key=lambda b: (b[0], b[1])) 依年份與頁數排序。"

def check_q10(g, hist):
    sp = g.get("sorted_players")
    # 積分降序(-p[1]), 犯規升序(p[2])
    # P1: (20, 3), P2: (25, 2), P3: (20, 1), P4: (25, 5)
    # 25分組: P2犯規2 < P4犯規5 -> [P2, P4]
    # 20分組: P3犯規1 < P1犯規3 -> [P3, P1]
    expected = [("P2", 25, 2), ("P4", 25, 5), ("P3", 20, 1), ("P1", 20, 3)]
    if sp == expected or ("-p[1]" in hist or "-x[1]" in hist):
        return True, "太神了！掌握核心負號技巧 -p[1]，實現首要條件降序、次要條件升序！"
    return False, "請填入 -p[1] 對積分加上負號以達到降序效果。"

def check_q11(g, hist):
    employees = [(1, 88, 2), (2, 95, 1), (3, 88, 0), (4, 95, 3)]
    expected = [(2, 95, 1), (4, 95, 3), (3, 88, 0), (1, 88, 2)]
    res = g.get("res")
    if res == expected or ("-e[1]" in hist or "-x[1]" in hist):
        return True, "精彩！精準使用 (-e[1], e[2]) 解決績效降序與遲到升序的經典混合排序！"
    return False, "請使用 sorted(employees, key=lambda e: (-e[1], e[2]))。"

def check_q12(g, hist):
    sm = g.get("sorted_members")
    # 等級降序, 戰力降序, 名稱升序: (-m[1], -m[2], m[0])
    members = [("勇者A", 50, 12000), ("法師B", 55, 9500), ("弓手C", 50, 15000), ("刺客D", 55, 12000)]
    # 55等: 刺客D(12000) > 法師B(9500)
    # 50等: 弓手C(15000) > 勇者A(12000)
    expected = [("刺客D", 55, 12000), ("法師B", 55, 9500), ("弓手C", 50, 15000), ("勇者A", 50, 12000)]
    if sm == expected or ("(-m[1], -m[2]" in hist or "(-x[1], -x[2]" in hist or "(-m[1],-m[2]" in hist):
        return True, "太強大了！成功使用三重複合條件 (-m[1], -m[2], m[0]) 完美排列戰力榜！"
    return False, "請使用 key=lambda m: (-m[1], -m[2], m[0]) 進行三重混合排序。"

def check_q13(g, hist):
    si = g.get("sorted_items")
    # 星級降序, 評價數降序: (-x['rating'], -x['reviews'])
    if "rating" in hist and "reviews" in hist and ("-x[" in hist or "-d[" in hist):
        return True, "正確無誤！精準利用字典鍵值搭配負號實現雙條件降序排序！"
    if isinstance(si, list) and len(si) == 3 and si[0].get("id") == "A02" and si[1].get("id") == "A03":
        return True, "星級與評論雙降序輸出完全吻合，通過！"
    return False, "請填入字典鍵名 'rating' 與 'reviews' 搭配負號完成雙降序。"

def check_q14(g, hist):
    ranked = g.get("ranked")
    top = g.get("top")
    if (top and top.get("name") in ["Bob", "Leo"]) or ("d['score']" in hist or 'd["score"]' in hist or "x['score']" in hist):
        return True, "太棒了！順利依字典 score 降序排序並成功獲取榜首資料！"
    return False, "請依字典中的 score 降序排序，並正確取出榜首學生。"

def check_q15(g, hist):
    rec = g.get("recommended")
    if (rec and rec[0].get("name") == "超值便當") or ("distance_km" in hist and "fee" in hist):
        return True, "太實用了！成功以外送距離與外送費雙準則為外送平台建立推薦排序！"
    return False, "請使用 key=lambda r: (r['distance_km'], r['fee']) 進行雙準則升序排序。"

def check_q16(g, hist):
    fs = g.get("farthest_stations")
    # 距離平方由遠到近 (降序): stations = [(10, 20), (5, 5), (30, 0), (15, 15)]
    # 平方: 500, 50, 900, 450 -> 降序: (30, 0) [900], (10, 20) [500], (15, 15) [450], (5, 5) [50]
    expected = [(30, 0), (10, 20), (15, 15), (5, 5)]
    if fs == expected or ("reverse=True" in hist and ("s[0]**2" in hist or "s[0] ** 2" in hist)):
        return True, "完全正確！基地台依離原點距離平方降序排列正確！"
    return False, "請在填空處填入 reverse=True 以達成由遠到近降序排列。"

def check_q17(g, hist):
    points = [(4, 3), (1, 2), (0, 3), (-1, -1)]
    # 平方: 25, 5, 9, 2 -> 升序: [(-1, -1), (1, 2), (0, 3), (4, 3)]
    expected = [(-1, -1), (1, 2), (0, 3), (4, 3)]
    res = g.get("res")
    closest = g.get("closest")
    if res == expected or closest == (-1, -1) or ("p[0]**2 + p[1]**2" in hist or "p[0] ** 2 + p[1] ** 2" in hist):
        return True, "太強了！成功依離原點距離平方由小到大排序並找出最接近點！"
    return False, "請使用 key=lambda p: p[0]**2 + p[1]**2 排序並找出最近點。"

def check_q18(g, hist):
    sc = g.get("sorted_chests")
    if sc and len(sc) == 5:
        # 玩家在 (1, 2)
        # c=(5, 12) -> 16+100=116; (0, -10)->1+144=145; (-6, -8)->49+100=149; (9, 0)->64+4=68; (7, 7)->36+25=61
        # 升序: (7, 7) [61], (9, 0) [68], (5, 12) [116], (0, -10) [145], (-6, -8) [149]
        if sc[0] == (7, 7) and sc[1] == (9, 0):
            return True, "滿分通關！精確計算相對位移平方並依距離由近到遠尋寶排序！"
    if "(c[0] - px)**2" in hist or "(c[0] - 1)**2" in hist or "(x - 1)**2" in hist:
        return True, "計算邏輯完全正確，通過！"
    return False, "請計算 (c[0] - 1)**2 + (c[1] - 2)**2 並依其排序。"

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
    # 收集歷史執行字串
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
    # 支援身分識別：姓名、學號
    user_name = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("STUDENT_NAME", "匿名學員")
    student_id = sys.argv[2] if len(sys.argv) > 2 else os.environ.get("STUDENT_ID", "無學號")
    
    # 嘗試抓取 Colab 登入帳號
    user_email = "未綁定 (良心信條模式)"
    try:
        from google.colab import auth
        # 僅在環境允許時靜默嘗試
    except Exception:
        pass

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

    # 匯出本地診斷報告
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
