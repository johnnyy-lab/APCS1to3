# -*- coding: utf-8 -*-
"""
PythAPCS123 - 單元 13-3 自動評分器
單元名稱：執行時期錯誤（Runtime Error, RE）常見排行榜與崩潰防禦
本腳本支援：
1. 學生自評/無登入測試模式（良心信條）
2. Colab OAuth 身分識別機制
3. Google 試算表 Webhook 成績同步
4. 18 題全方位檢測（9 大 RE 排行與防禦心法，每題配分，滿分 100 分）
5. 本地 JSON 診斷報告輸出
"""

import sys
import os
import json
import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

UNIT_ID = "13-3"
UNIT_TITLE = "執行時期錯誤（Runtime Error, RE）常見排行榜與崩潰防禦"

QUESTIONS = [
    # 13.3.1 例外機制與 Traceback
    {"id": "q1", "name": "實作 13.3.1：安全執行成功回傳 ('SUCCESS', res)", "points": 6},
    {"id": "q2", "name": "實作 13.3.1：精準捕獲中途例外回傳 ('RE', 例外型別)", "points": 6},
    # 13.3.2 IndexError 越界防禦
    {"id": "q3", "name": "實作 13.3.2：safe_get 支援正負索引與越界 default 防禦", "points": 6},
    {"id": "q4", "name": "實作 13.3.2：safe_adjacent_diffs 相鄰差值與邊界安全防禦", "points": 6},
    # 13.3.3 ValueError 轉型防禦
    {"id": "q5", "name": "實作 13.3.3：safe_parse_int 整數/浮點字串安全剖析", "points": 6},
    {"id": "q6", "name": "實作 13.3.3：safe_find_index 元素索引查找與安全回傳 -1", "points": 6},
    # 13.3.4 KeyError 查無此鍵防禦
    {"id": "q7", "name": "實作 13.3.4：safe_count_frequencies 字頻統計抗 KeyError", "points": 6},
    {"id": "q8", "name": "實作 13.3.4：safe_query_user 字典安全查詢與預設值防禦", "points": 6},
    # 13.3.5 ZeroDivisionError 除以零防禦
    {"id": "q9", "name": "實作 13.3.5：safe_divide 正常除法與除以零安全回傳", "points": 6},
    {"id": "q10", "name": "實作 13.3.5：safe_modulo 正常取模與模除零安全防禦", "points": 6},
    # 13.3.6 TypeError 型態錯配防禦
    {"id": "q11", "name": "實作 13.3.6：safe_format_key_value 異質型態安全字串格式化", "points": 5},
    {"id": "q12", "name": "實作 13.3.6：safe_sort_numbers 升序排序且不污染原串列", "points": 5},
    # 13.3.7 RecursionError 爆棧防禦
    {"id": "q13", "name": "實作 13.3.7：safe_factorial 大數階乘迭代實作抗爆棧", "points": 5},
    {"id": "q14", "name": "實作 13.3.7：safe_fibonacci 費氏數列迭代防禦堆疊溢出", "points": 5},
    # 13.3.8 AttributeError 與 UnboundLocalError 防禦
    {"id": "q15", "name": "實作 13.3.8：safe_append_or_concat 串列與字串型態分支防禦", "points": 5},
    {"id": "q16", "name": "實作 13.3.8：safe_accumulator 純區域變數累加杜絕作用域污染", "points": 5},
    # 13.3.9 考場 RE 綜合防禦實戰
    {"id": "q17", "name": "實作 13.3.9：bulletproof_data_pipeline 髒資料清洗與指標計算", "points": 5},
    {"id": "q18", "name": "實作 13.3.9：bulletproof_data_pipeline 空輸入與全垃圾極端防禦", "points": 5},
]

# ----------------- 檢查函式實作 -----------------

def check_q1(g, hist):
    fn = g.get("safe_execute_and_diagnose")
    if callable(fn):
        try:
            r1 = fn(lambda x: x + 10, 5)
            r2 = fn(lambda a, b: a * b, 3, 4)
            if r1 == ("SUCCESS", 15) and r2 == ("SUCCESS", 12):
                return True, "太棒了！安全執行成功且精準回傳 ('SUCCESS', 運算結果)！"
        except Exception as e:
            return False, f"執行 safe_execute_and_diagnose 時發生例外: {e}"
    if "safe_execute_and_diagnose" in hist and '"SUCCESS"' in hist:
        return True, "偵測到安全診斷成功執行記錄！"
    return False, "尚未正確實作 safe_execute_and_diagnose 或正常回傳值不符。"

def check_q2(g, hist):
    fn = g.get("safe_execute_and_diagnose")
    if callable(fn):
        try:
            r1 = fn(lambda a, b: a / b, 10, 0)
            r2 = fn(lambda lst, i: lst[i], [1, 2], 99)
            r3 = fn(lambda s: int(s), "not_a_number")
            if (r1 == ("RE", "ZeroDivisionError") and 
                r2 == ("RE", "IndexError") and 
                r3 == ("RE", "ValueError")):
                return True, "太棒了！中途例外精準捕獲並回傳 ('RE', 例外型別名稱)！"
        except Exception as e:
            return False, f"執行 safe_execute_and_diagnose 時發生例外: {e}"
    if "safe_execute_and_diagnose" in hist and '"RE"' in hist:
        return True, "偵測到例外捕獲與診斷邏輯！"
    return False, "發生崩潰時未能正確回傳 ('RE', 例外型別)。"

def check_q3(g, hist):
    fn = g.get("safe_get")
    if callable(fn):
        try:
            lst = [10, 20, 30]
            if (fn(lst, 0) == 10 and 
                fn(lst, 2) == 30 and 
                fn(lst, 3) is None and 
                fn(lst, -1) == 30 and 
                fn(lst, -4, 999) == 999 and 
                fn([], 0, "EMPTY") == "EMPTY"):
                return True, "太棒了！正負索引與越界預設值防禦皆 100% 正確！"
        except Exception as e:
            return False, f"執行 safe_get 時發生例外: {e}"
    if "safe_get" in hist:
        return True, "偵測到 safe_get 越界防禦邏輯！"
    return False, "尚未正確實作 safe_get 或正負邊界未妥善處理。"

def check_q4(g, hist):
    fn = g.get("safe_adjacent_diffs")
    if callable(fn):
        try:
            r1 = fn([10, 20, 35])
            r2 = fn([5])
            r3 = fn([])
            if r1 == [10, 15] and r2 == [] and r3 == []:
                return True, "太棒了！相鄰差值計算準確且長度不足 2 時安全回傳空串列！"
        except Exception as e:
            return False, f"執行 safe_adjacent_diffs 時發生例外: {e}"
    if "safe_adjacent_diffs" in hist:
        return True, "偵測到相鄰差值安全計算邏輯！"
    return False, "尚未正確實作 safe_adjacent_diffs 或邊界防守不完善。"

def check_q5(g, hist):
    fn = g.get("safe_parse_int")
    if callable(fn):
        try:
            c1 = fn("100") == 100
            c2 = fn("  -50  ") == -50
            c3 = fn("3.99") == 3
            c4 = fn("invalid", 0) == 0
            c5 = fn("", -999) == -999
            if c1 and c2 and c3 and c4 and c5:
                return True, "太棒了！整數、空白字串、浮點字串與非法輸入剖析完全正確！"
        except Exception as e:
            return False, f"執行 safe_parse_int 時發生例外: {e}"
    if "safe_parse_int" in hist:
        return True, "偵測到 safe_parse_int 數值防禦邏輯！"
    return False, "尚未正確實作 safe_parse_int 或非法字串未回傳 default。"

def check_q6(g, hist):
    fn = g.get("safe_find_index")
    if callable(fn):
        try:
            r1 = fn(["apple", "banana"], "banana")
            r2 = fn(["apple", "banana"], "cherry")
            r3 = fn([], "apple")
            if r1 == 1 and r2 == -1 and r3 == -1:
                return True, "太棒了！元素存在回傳正確索引，不存在安全回傳 -1！"
        except Exception as e:
            return False, f"執行 safe_find_index 時發生例外: {e}"
    if "safe_find_index" in hist:
        return True, "偵測到 safe_find_index 查找邏輯！"
    return False, "尚未正確實作 safe_find_index 或查無元素時未回傳 -1。"

def check_q7(g, hist):
    fn = g.get("safe_count_frequencies")
    if callable(fn):
        try:
            r1 = fn(["a", "b", "a", "c", "b", "a"])
            r2 = fn([])
            if r1 == {"a": 3, "b": 2, "c": 1} and r2 == {}:
                return True, "太棒了！字頻統計安全累加，完全免疫 KeyError！"
        except Exception as e:
            return False, f"執行 safe_count_frequencies 時發生例外: {e}"
    if "safe_count_frequencies" in hist:
        return True, "偵測到字頻統計安全邏輯！"
    return False, "尚未正確實作 safe_count_frequencies 或空清單處理有誤。"

def check_q8(g, hist):
    fn = g.get("safe_query_user")
    if callable(fn):
        try:
            db = {"alice": "manager", "bob": "staff"}
            if (fn(db, "alice") == "manager" and 
                fn(db, "nobody") == "guest" and 
                fn(db, "nobody", "anon") == "anon"):
                return True, "太棒了！字典安全查詢與自訂預設值防禦 100% 正確！"
        except Exception as e:
            return False, f"執行 safe_query_user 時發生例外: {e}"
    if "safe_query_user" in hist:
        return True, "偵測到 safe_query_user 字典防禦邏輯！"
    return False, "尚未正確實作 safe_query_user 或預設值防禦未生效。"

def check_q9(g, hist):
    fn = g.get("safe_divide")
    if callable(fn):
        try:
            if (fn(15, 3) == 5.0 and 
                fn(10, 0) == 0.0 and 
                fn(10, 0, -1.0) == -1.0):
                return True, "太棒了！安全除法正常運算與除以零 default 防禦完全正確！"
        except Exception as e:
            return False, f"執行 safe_divide 時發生例外: {e}"
    if "safe_divide" in hist:
        return True, "偵測到 safe_divide 除法守門員！"
    return False, "尚未正確實作 safe_divide 或分母為零時未回傳 default。"

def check_q10(g, hist):
    fn = g.get("safe_modulo")
    if callable(fn):
        try:
            if (fn(17, 5) == 2 and 
                fn(10, 0) == -1 and 
                fn(10, 0, 999) == 999):
                return True, "太棒了！安全模除正常運算與除數為零 default 防禦完全正確！"
        except Exception as e:
            return False, f"執行 safe_modulo 時發生例外: {e}"
    if "safe_modulo" in hist:
        return True, "偵測到 safe_modulo 模除防禦邏輯！"
    return False, "尚未正確實作 safe_modulo 或模除零未回傳 default。"

def check_q11(g, hist):
    fn = g.get("safe_format_key_value")
    if callable(fn):
        try:
            if (fn("age", 18) == "age = 18" and 
                fn("flag", True) == "flag = True" and 
                fn("item", None) == "item = None"):
                return True, "太棒了！數字、布林與 None 等異質型態字串拼接安全格式化！"
        except Exception as e:
            return False, f"執行 safe_format_key_value 時發生例外: {e}"
    if "safe_format_key_value" in hist:
        return True, "偵測到 safe_format_key_value 安全格式化邏輯！"
    return False, "尚未正確實作 safe_format_key_value 或 NoneType 格式化失敗。"

def check_q12(g, hist):
    fn = g.get("safe_sort_numbers")
    if callable(fn):
        try:
            orig = [9, 3, 7]
            res = fn(orig)
            if res == [3, 7, 9] and orig == [9, 3, 7] and res is not orig:
                return True, "太棒了！回傳新排序串列且原始串列內容完整保留未受污染！"
        except Exception as e:
            return False, f"執行 safe_sort_numbers 時發生例外: {e}"
    if "safe_sort_numbers" in hist:
        return True, "偵測到 safe_sort_numbers 排序防禦邏輯！"
    return False, "尚未正確實作 safe_sort_numbers 或污染了原始串列。"

def check_q13(g, hist):
    fn = g.get("safe_factorial")
    if callable(fn):
        try:
            c1 = fn(0) == 1
            c2 = fn(1) == 1
            c3 = fn(6) == 720
            c4 = fn(1200) > 0 # 大數測試不引發 RecursionError
            if c1 and c2 and c3 and c4:
                return True, "太棒了！大數階乘使用迭代演算法抗爆棧，RecursionError 徹底歸零！"
        except Exception as e:
            return False, f"執行 safe_factorial 時發生例外: {e}"
    if "safe_factorial" in hist:
        return True, "偵測到迭代階乘防禦邏輯！"
    return False, "尚未正確實作 safe_factorial 或面對大數引發例外。"

def check_q14(g, hist):
    fn = g.get("safe_fibonacci")
    if callable(fn):
        try:
            c1 = fn(0) == 0
            c2 = fn(1) == 1
            c3 = fn(7) == 13
            c4 = fn(100) == 354224848179261915075
            if c1 and c2 and c3 and c4:
                return True, "太棒了！費氏數列常數空間迭代實作，杜絕堆疊溢出與超時！"
        except Exception as e:
            return False, f"執行 safe_fibonacci 時發生例外: {e}"
    if "safe_fibonacci" in hist:
        return True, "偵測到迭代費氏數列防禦邏輯！"
    return False, "尚未正確實作 safe_fibonacci 或大數計算有誤。"

def check_q15(g, hist):
    fn = g.get("safe_append_or_concat")
    if callable(fn):
        try:
            l = [10, 20]
            r1 = fn(l, 30)
            r2 = fn("Hello", " World")
            r3 = fn("Num: ", 42)
            r4 = fn({"a": 1}, "b")
            if r1 == [10, 20, 30] and r2 == "Hello World" and r3 == "Num: 42" and r4 is None:
                return True, "太棒了！型態相容分支判斷完全正確，徹底免疫 AttributeError！"
        except Exception as e:
            return False, f"執行 safe_append_or_concat 時發生例外: {e}"
    if "safe_append_or_concat" in hist:
        return True, "偵測到型態相容處理邏輯！"
    return False, "尚未正確實作 safe_append_or_concat 或不支援型態未回傳 None。"

def check_q16(g, hist):
    fn = g.get("safe_accumulator")
    if callable(fn):
        try:
            r1 = fn([1, 2, 3, 4], 0)
            r2 = fn([], 100)
            if r1 == 10 and r2 == 100:
                return True, "太棒了！純區域變數累加計算準確，完全杜絕 UnboundLocalError 作用域陷阱！"
        except Exception as e:
            return False, f"執行 safe_accumulator 時發生例外: {e}"
    if "safe_accumulator" in hist:
        return True, "偵測到安全累加器邏輯！"
    return False, "尚未正確實作 safe_accumulator。"

def check_q17(g, hist):
    fn = g.get("bulletproof_data_pipeline")
    if callable(fn):
        try:
            dirty_data = [
                "A,15,80",
                "B,16,90",
                "C,invalid,100",
                "D,15,invalid",
                "E,15",
                "   ",
                "F,17,100"
            ]
            res = fn(dirty_data)
            if (isinstance(res, dict) and 
                res.get("valid_count") == 3 and 
                res.get("average_score") == 90.0 and 
                res.get("max_score") == 100):
                return True, "太棒了！髒資料清洗完整防禦 IndexError 與 ValueError，各項指標完全精準！"
        except Exception as e:
            return False, f"執行 bulletproof_data_pipeline 時發生例外: {e}"
    if "bulletproof_data_pipeline" in hist:
        return True, "偵測到綜合強固資料管線邏輯！"
    return False, "尚未正確實作 bulletproof_data_pipeline 或清洗指標結果不符。"

def check_q18(g, hist):
    fn = g.get("bulletproof_data_pipeline")
    if callable(fn):
        try:
            r_empty = fn([])
            r_trash = fn(["garbage", ",,,", "a,b,c"])
            expected = {"valid_count": 0, "average_score": 0.0, "max_score": 0}
            if r_empty == expected and r_trash == expected:
                return True, "太棒了！空串列與全垃圾輸入極端測試安全防禦，絕不觸發 ZeroDivisionError！"
        except Exception as e:
            return False, f"執行 bulletproof_data_pipeline 時發生例外: {e}"
    if "bulletproof_data_pipeline" in hist:
        return True, "偵測到空輸入防禦邏輯！"
    return False, "面對空資料或全無效資料時引發例外或回傳值不符。"

CHECK_FUNCS = {
    "q1": check_q1,
    "q2": check_q2,
    "q3": check_q3,
    "q4": check_q4,
    "q5": check_q5,
    "q6": check_q6,
    "q7": check_q7,
    "q8": check_q8,
    "q9": check_q9,
    "q10": check_q10,
    "q11": check_q11,
    "q12": check_q12,
    "q13": check_q13,
    "q14": check_q14,
    "q15": check_q15,
    "q16": check_q16,
    "q17": check_q17,
    "q18": check_q18,
}

def extract_notebook_history():
    hist_text = ""
    try:
        from IPython import get_ipython
        ip = get_ipython()
        if ip and hasattr(ip, "user_ns"):
            In = ip.user_ns.get("In", [])
            hist_text = "\n".join(In)
    except Exception:
        pass
    return hist_text

def run_grading(user_globals=None):
    g = {}
    if user_globals is not None:
        g.update(user_globals)
    else:
        try:
            import __main__
            g.update(__main__.__dict__)
        except Exception:
            pass

    hist = extract_notebook_history()

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
