import streamlit as st
import json
import os
import random
import time
from datetime import datetime
from PIL import Image

DATA_FILE = "data.json"

st.set_page_config(page_title="小学作业批改 & 错题本", page_icon="📚", layout="wide")


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"mistakes": [], "practice_history": []}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_math_question(grade, difficulty, q_type):
    if difficulty == "简单":
        max_num = 20 if grade <= 2 else 100
    elif difficulty == "中等":
        max_num = 50 if grade <= 2 else 500
    else:
        max_num = 100 if grade <= 2 else 1000

    if q_type == "加法":
        a = random.randint(1, max_num)
        b = random.randint(1, max_num)
        question = f"{a} + {b} = ?"
        answer = a + b
    elif q_type == "减法":
        a = random.randint(1, max_num)
        b = random.randint(1, a)
        question = f"{a} - {b} = ?"
        answer = a - b
    elif q_type == "乘法":
        if grade <= 2:
            a = random.randint(1, 9)
            b = random.randint(1, 9)
        else:
            a = random.randint(1, 20)
            b = random.randint(1, 20)
        question = f"{a} × {b} = ?"
        answer = a * b
    elif q_type == "除法":
        if grade <= 2:
            b = random.randint(1, 9)
            answer = random.randint(1, 9)
        else:
            b = random.randint(1, 15)
            answer = random.randint(1, 15)
        a = b * answer
        question = f"{a} ÷ {b} = ?"
    elif q_type == "混合运算":
        a = random.randint(1, max(10, max_num // 5))
        b = random.randint(1, 9)
        c = random.randint(1, 9)
        op1 = random.choice(["+", "-", "×"])
        if op1 == "×":
            answer = a * b
            if random.random() > 0.5:
                question = f"{a} × {b} + {c} = ?"
                answer = a * b + c
            else:
                question = f"{a} × {b} - {c} = ?"
                answer = a * b - c
        else:
            if op1 == "+":
                question = f"{a} + {b} × {c} = ?"
                answer = a + b * c
            else:
                temp = a - b * c
                if temp < 0:
                    a = b * c + random.randint(1, 20)
                    temp = a - b * c
                question = f"{a} - {b} × {c} = ?"
                answer = a - b * c
    elif q_type == "应用题":
        scenarios = [
            ("小明有{a}个苹果，又买了{b}个，一共有多少个？", "+"),
            ("树上有{a}只鸟，飞走了{b}只，还剩几只？", "-"),
            ("每排有{b}个座位，共{a}排，一共有多少个座位？", "×"),
            ("{a}个糖果平均分给{b}个小朋友，每人分几个？", "÷"),
        ]
        scenario, op = random.choice(scenarios)
        if op == "÷":
            b = random.randint(2, 9)
            answer = random.randint(2, 10)
            a = b * answer
        elif op == "×":
            a = random.randint(2, 9)
            b = random.randint(2, 9)
            answer = a * b
        elif op == "+":
            a = random.randint(1, max_num)
            b = random.randint(1, max_num)
            answer = a + b
        else:
            a = random.randint(10, max_num)
            b = random.randint(1, a)
            answer = a - b
        question = scenario.format(a=a, b=b)
    else:
        a = random.randint(1, max_num)
        b = random.randint(1, max_num)
        question = f"{a} + {b} = ?"
        answer = a + b

    return question, answer


def grade_answer(student_answer, correct_answer, tolerance=0):
    try:
        sa = float(student_answer)
        ca = float(correct_answer)
        return abs(sa - ca) <= tolerance
    except (ValueError, TypeError):
        student_str = str(student_answer).strip().replace(" ", "")
        correct_str = str(correct_answer).strip().replace(" ", "")
        return student_str == correct_str


def render_practice_mode():
    st.header("📝 练习模式")
    st.markdown("自动生成题目，即时批改")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        grade = st.selectbox("年级", ["一年级", "二年级", "三年级", "四年级", "五年级", "六年级"], index=2)
        grade_num = int(grade.replace("年级", "").replace("一", "1").replace("二", "2").replace("三", "3").replace("四", "4").replace("五", "5").replace("六", "6"))
    with col2:
        difficulty = st.selectbox("难度", ["简单", "中等", "困难"])
    with col3:
        q_type = st.selectbox("题型", ["加法", "减法", "乘法", "除法", "混合运算", "应用题"])
    with col4:
        num_questions = st.slider("题目数量", 5, 30, 10)

    tolerance = 0
    if q_type == "应用题":
        tolerance = st.number_input("允许误差（应用题，0为精确）", min_value=0, value=0)

    if st.button("🎲 生成题目", type="primary", use_container_width=True):
        questions = []
        for _ in range(num_questions):
            q, a = generate_math_question(grade_num, difficulty, q_type)
            questions.append({"question": q, "answer": a})
        st.session_state.practice_questions = questions
        st.session_state.practice_answers = [""] * len(questions)
        st.session_state.practice_graded = False
        st.session_state.practice_tolerance = tolerance

    if "practice_questions" in st.session_state and st.session_state.practice_questions:
        questions = st.session_state.practice_questions
        st.markdown("---")
        st.subheader(f"✏️ 答题区（共 {len(questions)} 题）")

        for i, q in enumerate(questions):
            col_q, col_a = st.columns([3, 1])
            with col_q:
                st.markdown(f"**第 {i+1} 题：** {q['question']}")
            with col_a:
                st.session_state.practice_answers[i] = st.text_input(
                    "答案", key=f"ans_{i}", label_visibility="collapsed",
                    value=st.session_state.practice_answers[i]
                )

        st.markdown("---")
        if st.button("✅ 提交批改", type="primary", use_container_width=True):
            st.session_state.practice_graded = True

        if st.session_state.get("practice_graded", False):
            correct_count = 0
            wrong_list = []
            tolerance = st.session_state.get("practice_tolerance", 0)

            for i, q in enumerate(questions):
                student_ans = st.session_state.practice_answers[i].strip()
                is_correct = grade_answer(student_ans, q["answer"], tolerance)
                if is_correct:
                    correct_count += 1
                else:
                    wrong_list.append({
                        "question": q["question"],
                        "student_answer": student_ans if student_ans else "（未作答）",
                        "correct_answer": str(q["answer"]),
                        "subject": "数学",
                        "type": q_type,
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

            score = correct_count / len(questions) * 100
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                st.metric("得分", f"{score:.0f} 分")
            with col_s2:
                st.metric("正确", f"{correct_count} / {len(questions)}")
            with col_s3:
                st.metric("错误", f"{len(wrong_list)} 题")

            if score >= 90:
                st.success("🌟 太棒了！非常优秀！")
            elif score >= 70:
                st.info("👍 不错哦！继续加油！")
            elif score >= 60:
                st.warning("💪 及格了，还需要多练习！")
            else:
                st.error("📖 需要加强练习，不要灰心！")

            st.markdown("### 📋 批改详情")
            for i, q in enumerate(questions):
                student_ans = st.session_state.practice_answers[i].strip()
                is_correct = grade_answer(student_ans, q["answer"], tolerance)
                if is_correct:
                    st.markdown(f"~~第 {i+1} 题：{q['question']}~~ ✅ **{student_ans}** — 正确")
                else:
                    display_ans = student_ans if student_ans else "（未作答）"
                    st.markdown(f"~~第 {i+1} 题：{q['question']}~~ ❌ 你的答案：**{display_ans}** → 正确答案：**{q['answer']}**")

            if wrong_list:
                st.markdown("---")
                if st.button("📕 将错题收录到错题本", use_container_width=True):
                    data = load_data()
                    data["mistakes"].extend(wrong_list)
                    data["practice_history"].append({
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "grade": grade,
                        "type": q_type,
                        "difficulty": difficulty,
                        "score": score,
                        "total": len(questions)
                    })
                    save_data(data)
                    st.success(f"已收录 {len(wrong_list)} 道错题到错题本！")

            st.session_state.practice_graded = False


def render_homework_grade():
    st.header("📸 作业批改模式")
    st.markdown("上传作业照片，输入题目和答案进行批改")

    uploaded_file = st.file_uploader("上传作业/试卷照片", type=["jpg", "jpeg", "png", "bmp"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="上传的作业照片", use_container_width=True)

    st.markdown("---")
    st.subheader("📝 输入题目信息")

    if "homework_questions" not in st.session_state:
        st.session_state.homework_questions = []

    num_q = st.number_input("题目数量", min_value=1, max_value=100, value=5)

    if st.button("📋 生成输入框"):
        st.session_state.homework_questions = [
            {"question": "", "correct_answer": "", "student_answer": ""}
            for _ in range(int(num_q))
        ]

    if st.session_state.homework_questions:
        subject = st.selectbox("科目", ["数学", "语文", "英语", "其他"])

        for i in range(len(st.session_state.homework_questions)):
            st.markdown(f"**第 {i+1} 题**")
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.session_state.homework_questions[i]["question"] = st.text_input(
                    "题目内容", key=f"hw_q_{i}",
                    value=st.session_state.homework_questions[i]["question"]
                )
            with col2:
                st.session_state.homework_questions[i]["correct_answer"] = st.text_input(
                    "正确答案", key=f"hw_ca_{i}",
                    value=st.session_state.homework_questions[i]["correct_answer"]
                )
            with col3:
                st.session_state.homework_questions[i]["student_answer"] = st.text_input(
                    "学生答案", key=f"hw_sa_{i}",
                    value=st.session_state.homework_questions[i]["student_answer"]
                )

        st.markdown("---")
        if st.button("✅ 开始批改", type="primary", use_container_width=True):
            correct_count = 0
            wrong_list = []

            for i, q in enumerate(st.session_state.homework_questions):
                if not q["question"] or not q["correct_answer"]:
                    continue
                is_correct = grade_answer(q["student_answer"], q["correct_answer"])
                if is_correct:
                    correct_count += 1
                else:
                    wrong_list.append({
                        "question": q["question"],
                        "student_answer": q["student_answer"] if q["student_answer"] else "（未作答）",
                        "correct_answer": q["correct_answer"],
                        "subject": subject,
                        "type": "手动录入",
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

            total = sum(1 for q in st.session_state.homework_questions if q["question"] and q["correct_answer"])
            if total > 0:
                score = correct_count / total * 100
                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    st.metric("得分", f"{score:.0f} 分")
                with col_s2:
                    st.metric("正确", f"{correct_count} / {total}")
                with col_s3:
                    st.metric("错误", f"{len(wrong_list)} 题")

                st.markdown("### 📋 批改结果")
                for i, q in enumerate(st.session_state.homework_questions):
                    if not q["question"] or not q["correct_answer"]:
                        continue
                    is_correct = grade_answer(q["student_answer"], q["correct_answer"])
                    if is_correct:
                        st.markdown(f"✅ **第 {i+1} 题：** {q['question']} — 答案：**{q['student_answer']}** ✓")
                    else:
                        sa = q["student_answer"] if q["student_answer"] else "（未作答）"
                        st.markdown(f"❌ **第 {i+1} 题：** {q['question']} — 学生答案：**{sa}** → 正确答案：**{q['correct_answer']}**")

                if wrong_list:
                    st.markdown("---")
                    if st.button("📕 将错题收录到错题本", use_container_width=True):
                        data = load_data()
                        data["mistakes"].extend(wrong_list)
                        save_data(data)
                        st.success(f"已收录 {len(wrong_list)} 道错题到错题本！")


def render_mistake_book():
    st.header("📕 错题本")

    data = load_data()
    mistakes = data.get("mistakes", [])

    if not mistakes:
        st.info("📭 错题本为空，快去练习或批改作业吧！")
        return

    st.markdown(f"共收录 **{len(mistakes)}** 道错题")

    col1, col2, col3 = st.columns(3)
    with col1:
        subjects = list(set(m["subject"] for m in mistakes))
        filter_subject = st.multiselect("按科目筛选", subjects, default=subjects)
    with col2:
        types = list(set(m["type"] for m in mistakes))
        filter_type = st.multiselect("按题型筛选", types, default=types)
    with col3:
        sort_by = st.selectbox("排序方式", ["时间最新", "科目分组"])

    filtered = [m for m in mistakes if m["subject"] in filter_subject and m["type"] in filter_type]

    if sort_by == "科目分组":
        grouped = {}
        for m in filtered:
            grouped.setdefault(m["subject"], []).append(m)
        for subj, items in grouped.items():
            st.subheader(f"📘 {subj}（{len(items)} 题）")
            for idx, m in enumerate(items):
                render_mistake_card(m, idx, subj)
    else:
        for idx, m in enumerate(reversed(filtered)):
            render_mistake_card(m, len(filtered) - 1 - idx, m["subject"])

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ 清空错题本", use_container_width=True):
            data["mistakes"] = []
            save_data(data)
            st.success("错题本已清空！")
            st.rerun()
    with col2:
        if st.button("📊 导出错题记录", use_container_width=True):
            export_text = "=== 错题本 ===\n\n"
            for m in mistakes:
                export_text += f"[{m['time']}] [{m['subject']}] {m['question']}\n"
                export_text += f"  学生答案: {m['student_answer']}  →  正确答案: {m['correct_answer']}\n\n"
            st.download_button(
                "⬇️ 下载错题本",
                data=export_text,
                file_name=f"错题本_{datetime.now().strftime('%Y%m%d')}.txt",
                use_container_width=True
            )


def render_mistake_card(m, idx, subj):
    with st.expander(f"[{m['time']}] {m['question'][:40]}{'...' if len(m['question']) > 40 else ''}"):
        st.markdown(f"**题目：** {m['question']}")
        st.markdown(f"**学生答案：** :red[{m['student_answer']}]")
        st.markdown(f"**正确答案：** :green[{m['correct_answer']}]")
        st.markdown(f"**科目：** {m['subject']} | **题型：** {m['type']}")
        st.markdown(f"**时间：** {m['time']}")

        if st.button("✅ 标记为已掌握", key=f"master_{idx}_{subj}"):
            data = load_data()
            for i, item in enumerate(data["mistakes"]):
                if (item["question"] == m["question"] and
                    item["student_answer"] == m["student_answer"] and
                    item["time"] == m["time"]):
                    data["mistakes"].pop(i)
                    break
            save_data(data)
            st.success("已移除！")
            st.rerun()


def render_statistics():
    st.header("📊 学习统计")

    data = load_data()
    mistakes = data.get("mistakes", [])
    history = data.get("practice_history", [])

    if not mistakes and not history:
        st.info("📭 暂无数据，先去练习或批改作业吧！")
        return

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("错题总数", f"{len(mistakes)} 题")
    with col2:
        st.metric("练习次数", f"{len(history)} 次")
    with col3:
        if history:
            avg_score = sum(h["score"] for h in history) / len(history)
            st.metric("平均得分", f"{avg_score:.1f} 分")
        else:
            st.metric("平均得分", "—")
    with col4:
        if mistakes:
            subj_counts = {}
            for m in mistakes:
                subj_counts[m["subject"]] = subj_counts.get(m["subject"], 0) + 1
            worst = max(subj_counts, key=subj_counts.get)
            st.metric("薄弱科目", f"{worst}（{subj_counts[worst]}题）")
        else:
            st.metric("薄弱科目", "—")

    if history:
        st.markdown("---")
        st.subheader("📈 练习历史")
        recent = history[-20:]
        chart_data = {
            "得分": [h["score"] for h in recent],
        }
        st.line_chart(chart_data)

        st.markdown("### 📋 最近练习记录")
        for h in reversed(recent):
            st.markdown(
                f"- **{h['time']}** | {h['grade']} | {h['type']} | {h['difficulty']} | "
                f"得分: {h['score']:.0f}分 ({h['total']}题)"
            )

    if mistakes:
        st.markdown("---")
        st.subheader("📉 错题分布")
        col1, col2 = st.columns(2)
        with col1:
            subj_counts = {}
            for m in mistakes:
                subj_counts[m["subject"]] = subj_counts.get(m["subject"], 0) + 1
            st.bar_chart(subj_counts)
        with col2:
            type_counts = {}
            for m in mistakes:
                type_counts[m["type"]] = type_counts.get(m["type"], 0) + 1
            st.bar_chart(type_counts)


def main():
    st.title("📚 小学作业批改 & 错题本")

    menu = st.sidebar.radio(
        "功能菜单",
        ["📝 练习模式", "📸 作业批改", "📕 错题本", "📊 学习统计"],
        index=0
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📌 使用说明")
    st.sidebar.markdown("""
    1. **练习模式**：自动生成数学题，即时批改
    2. **作业批改**：上传作业照片，手动录入批改
    3. **错题本**：查看所有错题，支持筛选和导出
    4. **学习统计**：查看学习数据和趋势
    """)

    if menu == "📝 练习模式":
        render_practice_mode()
    elif menu == "📸 作业批改":
        render_homework_grade()
    elif menu == "📕 错题本":
        render_mistake_book()
    elif menu == "📊 学习统计":
        render_statistics()


if __name__ == "__main__":
    main()