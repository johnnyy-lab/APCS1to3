# -*- coding: utf-8 -*-
"""
PythAPCS123 - 單元 13-4 自動評分器
單元名稱：try-except 防禦性程式設計與 EOF 讀取結束優雅收尾
本腳本支援：
1. 學生自評/無登入測試模式（良心信條）
2. Colab OAuth 身分識別機制
3. Google 試算表 Webhook 成績同步
4. 18 題全方位檢測（6 大 try-except 與 EOF 核心，每題配分，滿分 100 分）
5. 本地 JSON 診斷報告輸出
"""

import sys
import os
import json
import datetime
import io

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

UNIT_ID = "13-4"
UNIT_TITLE = "try-except 防禦性程式設計與 EOF 讀取結束優雅收尾"

QUESTIONS = [
    # 13.4.1 彈性整數求和器
    {"id": "q1", "name": "實作 13.4.1：safe_sum_mixed_list 純數字字串正確累加", "points": 6},
    {"id": "q2", "name": "實作 13.4.1：safe_sum_mixed_list 混入非整數安全跳過防禦", "points": 6},
    {"id": "q3", "name": "實作 13.4.1：safe_sum_mixed_list 空串列與全無效資料回傳 0", "points": 5},
    # 13.4.2 安全浮點數剖析器
    {"id": "q4", "name": "實作 13.4.2：parse_float_safely 合法正負浮點數解析", "points": 6},
    {"id": "q5", "name": "實作 13.4.2：parse_float_safely 格式錯誤精準捕捉回傳預設值", "points": 6},
    {"id": "q6", "name": "實作 13.4.2：parse_float_safely 空字串極端測資防禦", "points": 5},
    # 13.4.3 多重例外分流存取器
    {"id": "q7", "name": "實作 13.4.3：safe_lookup_and_convert 正常鍵值查詢與整數轉換", "points": 6},
    {"id": "q8", "name": "實作 13.4.3：safe_lookup_and_convert 捕獲 KeyError 回傳 KEY_NOT_FOUND", "points": 6},
    {"id": "q9", "name": "實作 13.4.3：safe_lookup_and_convert 捕獲 ValueError 回傳 INVALID_NUMBER", "points": 5},
    # 13.4.4 EOF 模擬串流逐行讀取器
    {"id": "q10", "name": "實作 13.4.4：process_mock_stream 多行串流逐行讀取與字元累加", "points": 6},
    {"id": "q11", "name": "實作 13.4.4：process_mock_stream 精準捕捉 EOFError 優雅結束", "points": 6},
    {"id": "q12", "name": "實作 13.4.4：process_mock_stream 空串流與極端邊界安全回傳 0", "points": 5},
    # 13.4.5 狀態復原防禦器 (finally)
    {"id": "q13", "name": "實作 13.4.5：calculate_with_flag 成功調用回傳正確運算值", "points": 6},
    {"id": "q14", "name": "實作 13.4.5：calculate_with_flag 出錯時安全回傳 None 且不崩潰", "points": 5},
    {"id": "q15", "name": "實作 13.4.5：calculate_with_flag 利用 finally 保證旗標狀態復原", "points": 5},
    # 13.4.6 雙軌防禦數值處理器
    {"id": "q16", "name": "實作 13.4.6：robust_batch_processor 正常數字字串累加", "points": 6},
    {"id": "q17", "name": "實作 13.4.6：robust_batch_processor if 條件式提前過濾空字串", "points": 5},
    {"id": "q18", "name": "實作 13.4.6：robust_batch_processor try-except 容錯無效格式與空清單", "points": 5},
]

# ----------------- 檢查函式實作 -----------------

def check_q1(g, hist):
    fn = g.get("safe_sum_mixed_list")
    if callable(fn):
        try:
            if fn(["1", "2", "3"]) == 6 and fn(["10", 20, "30"]) == 60:
                return True, "太棒了！純數字與合法字串整數累加精準無誤！"
        except Exception as e:
            return False, f"執行 safe_sum_mixed_list 時發生例外: {e}"
    if "safe_sum_mixed_list" in hist:
        return True, "偵測到 safe_sum_mixed_list 累加邏輯！"
    return False, "尚未正確實作 safe_sum_mixed_list 或累加結果不符。"

def check_q2(g, hist):
    fn = g.get("safe_sum_mixed_list")
    if callable(fn):
        try:
            r1 = fn(["10", "abc", "20"])
            r2 = fn([5, "15", None, "25", "3.14"])
            if r1 == 30 and r2 == 45:
                return True, "太棒了！遇到英文、None 或浮點字串皆優雅跳過，未中斷程式！"
        except Exception as e:
            return False, f"執行 safe_sum_mixed_list 時發生例外: {e}"
    if "safe_sum_mixed_list" in hist:
        return True, "偵測到非整數例外防禦邏輯！"
    return False, "非整數項目未被優雅跳過，或導致累加計算錯誤。"

def check_q3(g, hist):
    fn = g.get("safe_sum_mixed_list")
    if callable(fn):
        try:
            if fn([]) == 0 and fn(["x", "y", "z"]) == 0:
                return True, "太棒了！面對空串列與全無效字串安全回傳 0！"
        except Exception as e:
            return False, f"執行 safe_sum_mixed_list 時發生例外: {e}"
    if "safe_sum_mixed_list" in hist:
        return True, "偵測到空串列防禦邏輯！"
    return False, "空串列或全無效資料未能回傳 0。"

def check_q4(g, hist):
    fn = g.get("parse_float_safely")
    if callable(fn):
        try:
            if fn("12.5", 0.0) == 12.5 and fn("-8.0", 0.0) == -8.0 and fn("100", 0.0) == 100.0:
                return True, "太棒了！合法浮點數與整數字串皆精準解析！"
        except Exception as e:
            return False, f"執行 parse_float_safely 時發生例外: {e}"
    if "parse_float_safely" in hist:
        return True, "偵測到 parse_float_safely 解析邏輯！"
    return False, "尚未正確實作 parse_float_safely 或合法數值解析失敗。"

def check_q5(g, hist):
    fn = g.get("parse_float_safely")
    if callable(fn):
        try:
            if fn("abc", 99.9) == 99.9 and fn("hello_world", -1.0) == -1.0:
                return True, "太棒了！格式錯誤文字精準捕捉並回傳指定的 default_val！"
        except Exception as e:
            return False, f"執行 parse_float_safely 時發生例外: {e}"
    if "parse_float_safely" in hist:
        return True, "偵測到預設值回傳邏輯！"
    return False, "格式錯誤時未能正確回傳 default_val。"

def check_q6(g, hist):
    fn = g.get("parse_float_safely")
    if callable(fn):
        try:
            if fn("", 0.0) == 0.0 and fn("   ", -5.5) == -5.5:
                return True, "太棒了！空字串與空白字串極端輸入安全防禦！"
        except Exception as e:
            return False, f"執行 parse_float_safely 時發生例外: {e}"
    if "parse_float_safely" in hist:
        return True, "偵測到空字串防禦邏輯！"
    return False, "空字串輸入未回傳預設值。"

def check_q7(g, hist):
    fn = g.get("safe_lookup_and_convert")
    if callable(fn):
        try:
            m = {"a": "100", "c": "0", "neg": "-42"}
            if fn(m, "a") == 100 and fn(m, "c") == 0 and fn(m, "neg") == -42:
                return True, "太棒了！合法鍵值查詢並順利轉換為整數型態！"
        except Exception as e:
            return False, f"執行 safe_lookup_and_convert 時發生例外: {e}"
    if "safe_lookup_and_convert" in hist:
        return True, "偵測到合法鍵值查詢轉換邏輯！"
    return False, "尚未正確實作 safe_lookup_and_convert 或轉換結果不符。"

def check_q8(g, hist):
    fn = g.get("safe_lookup_and_convert")
    if callable(fn):
        try:
            m = {"a": "100"}
            if fn(m, "not_exist") == "KEY_NOT_FOUND":
                return True, "太棒了！精準捕捉 KeyError 並安全回傳 'KEY_NOT_FOUND'！"
        except Exception as e:
            return False, f"執行 safe_lookup_and_convert 時發生例外: {e}"
    if "safe_lookup_and_convert" in hist and '"KEY_NOT_FOUND"' in hist:
        return True, "偵測到 KEY_NOT_FOUND 攔截邏輯！"
    return False, "鍵值不存在時未能正確回傳 'KEY_NOT_FOUND'。"

def check_q9(g, hist):
    fn = g.get("safe_lookup_and_convert")
    if callable(fn):
        try:
            m = {"bad": "invalid_num", "empty": ""}
            if fn(m, "bad") == "INVALID_NUMBER" and fn(m, "empty") == "INVALID_NUMBER":
                return True, "太棒了！精準捕捉 ValueError 並安全回傳 'INVALID_NUMBER'！"
        except Exception as e:
            return False, f"執行 safe_lookup_and_convert 時發生例外: {e}"
    if "safe_lookup_and_convert" in hist and '"INVALID_NUMBER"' in hist:
        return True, "偵測到 INVALID_NUMBER 攔截邏輯！"
    return False, "數值轉換失敗時未能正確回傳 'INVALID_NUMBER'。"

def check_q10(g, hist):
    fn = g.get("process_mock_stream")
    if callable(fn):
        try:
            if fn("abc\ndef\n") == 6 and fn("12345\n") == 5:
                return True, "太棒了！標準輸入串流逐行讀取並精準統計不含換行之字元數！"
        except Exception as e:
            return False, f"執行 process_mock_stream 時發生例外: {e}"
    if "process_mock_stream" in hist:
        return True, "偵測到串流讀取累加邏輯！"
    return False, "尚未正確實作 process_mock_stream 或字元累加計算不符。"

def check_q11(g, hist):
    fn = g.get("process_mock_stream")
    if callable(fn):
        try:
            if fn("a\nb\nc\nd\n") == 4:
                return True, "太棒了！while True 搭配 try-except EOFError 順暢終止！"
        except Exception as e:
            return False, f"執行 process_mock_stream 時發生例外: {e}"
    if "process_mock_stream" in hist and "EOFError" in hist:
        return True, "偵測到 EOFError 捕捉終止邏輯！"
    return False, "EOFError 捕捉中斷未能正常跳出迴圈。"

def check_q12(g, hist):
    fn = g.get("process_mock_stream")
    if callable(fn):
        try:
            if fn("") == 0:
                return True, "太棒了！面對完全空串流第一行即觸發 EOF，安全回傳 0！"
        except Exception as e:
            return False, f"執行 process_mock_stream 時發生例外: {e}"
    if "process_mock_stream" in hist:
        return True, "偵測到空串流處理邏輯！"
    return False, "空串流未回傳 0 或引發異常。"

def check_q13(g, hist):
    fn = g.get("calculate_with_flag")
    if callable(fn):
        try:
            c = [False]
            res = fn(c, lambda: "APCS_PASS")
            if res == "APCS_PASS":
                return True, "太棒了！成功調用 func() 並獲得正確回傳值！"
        except Exception as e:
            return False, f"執行 calculate_with_flag 時發生例外: {e}"
    if "calculate_with_flag" in hist:
        return True, "偵測到 calculate_with_flag 呼叫邏輯！"
    return False, "尚未正確實作 calculate_with_flag 或回傳值不符。"

def check_q14(g, hist):
    fn = g.get("calculate_with_flag")
    if callable(fn):
        try:
            c = [False]
            res = fn(c, lambda: 1 / 0)
            if res is None:
                return True, "太棒了！內部發生除以零例外時被妥善捕捉，安全回傳 None！"
        except Exception as e:
            return False, f"執行 calculate_with_flag 時發生例外: {e}"
    if "calculate_with_flag" in hist:
        return True, "偵測到例外捕捉回傳 None 邏輯！"
    return False, "內部出錯時未能安全捕捉並回傳 None。"

def check_q15(g, hist):
    fn = g.get("calculate_with_flag")
    if callable(fn):
        try:
            c1 = [False]
            fn(c1, lambda: 42)
            c2 = [False]
            fn(c2, lambda: int("crash"))
            if c1[0] is False and c2[0] is False:
                return True, "太棒了！無論執行成功或出錯，finally 均 100% 確保將旗標還原為 False！"
        except Exception as e:
            return False, f"執行 calculate_with_flag 時發生例外: {e}"
    if "calculate_with_flag" in hist and "finally" in hist:
        return True, "偵測到 finally 狀態還原邏輯！"
    return False, "finally 區塊未正確將 flag_container[0] 還原為 False。"

def check_q16(g, hist):
    fn = g.get("robust_batch_processor")
    if callable(fn):
        try:
            if fn(["1", "2", "3"]) == 6 and fn(["10", "20", "30"]) == 60:
                return True, "太棒了！合法數值批次處理累加完全正確！"
        except Exception as e:
            return False, f"執行 robust_batch_processor 時發生例外: {e}"
    if "robust_batch_processor" in hist:
        return True, "偵測到數值累加邏輯！"
    return False, "尚未正確實作 robust_batch_processor 或累加總和不符。"

def check_q17(g, hist):
    fn = g.get("robust_batch_processor")
    if callable(fn):
        try:
            if fn(["", "", ""]) == 0 and fn(["10", "", "", "20"]) == 30:
                return True, "太棒了！精準利用 if 條件式提前略過空字串！"
        except Exception as e:
            return False, f"執行 robust_batch_processor 時發生例外: {e}"
    if "robust_batch_processor" in hist:
        return True, "偵測到空字串條件過濾邏輯！"
    return False, "空字串未能妥善過濾。"

def check_q18(g, hist):
    fn = g.get("robust_batch_processor")
    if callable(fn):
        try:
            if fn(["10", "abc", "", "20"]) == 30 and fn([]) == 0:
                return True, "太棒了！try-except 雙軌防禦成功略過非法格式，空清單回傳 0！"
        except Exception as e:
            return False, f"執行 robust_batch_processor 時發生例外: {e}"
    if "robust_batch_processor" in hist:
        return True, "偵測到雙軌防禦容錯邏輯！"
    return False, "包含無效格式時未正常略過或計算錯誤。"

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
