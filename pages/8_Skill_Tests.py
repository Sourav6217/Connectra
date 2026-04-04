import streamlit as st
import sys, os, pathlib, time

from styles import GLOBAL_CSS
from data.sqlite_db import get_skill_test_results, upsert_skill_test_result
from utils.matching import calculate_talent_score

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

wallet = st.session_state.get("wallet", "0x742d35Cc6634C0532925a3b844Bc454e4438f44e")

# ── Question Bank ────────────────────────────────────────────────────────────
TESTS = {
    "Python": [
        {"q": "What does `len([1,2,3])` return?", "opts": ["2","3","4","Error"], "ans": 1},
        {"q": "Which keyword defines a function in Python?", "opts": ["func","def","fn","define"], "ans": 1},
        {"q": "What is the output of `type(3.14)`?", "opts": ["<class 'int'>","<class 'float'>","<class 'str'>","<class 'num'>"], "ans": 1},
        {"q": "Which of these is a mutable data type?", "opts": ["tuple","string","list","int"], "ans": 2},
        {"q": "What does `range(3)` produce?", "opts": ["[1,2,3]","[0,1,2]","[0,1,2,3]","(0,1,2)"], "ans": 1},
    ],
    "SQL": [
        {"q": "Which clause filters rows AFTER GROUP BY?", "opts": ["WHERE","HAVING","FILTER","ORDER BY"], "ans": 1},
        {"q": "What does `SELECT DISTINCT` do?", "opts": ["Sorts rows","Removes duplicates","Counts rows","Joins tables"], "ans": 1},
        {"q": "Which JOIN returns all rows from both tables?", "opts": ["INNER JOIN","LEFT JOIN","RIGHT JOIN","FULL OUTER JOIN"], "ans": 3},
        {"q": "Which aggregate function returns the average?", "opts": ["SUM()","COUNT()","AVG()","MAX()"], "ans": 2},
        {"q": "What does `NULL` represent in SQL?", "opts": ["Zero","Empty string","Unknown/missing","False"], "ans": 2},
    ],
    "JavaScript": [
        {"q": "What does `===` check?", "opts": ["Value only","Type only","Value and type","Reference"], "ans": 2},
        {"q": "Which method adds an element to end of an array?", "opts": ["push()","pop()","shift()","append()"], "ans": 0},
        {"q": "What is `typeof null` in JS?", "opts": ["null","undefined","object","boolean"], "ans": 2},
        {"q": "Which keyword declares a block-scoped variable?", "opts": ["var","let","const","both let and const"], "ans": 3},
        {"q": "What does `Promise.resolve()` return?", "opts": ["undefined","A rejected promise","A resolved promise","An error"], "ans": 2},
    ],
    "React": [
        {"q": "What hook manages local state in a component?", "opts": ["useEffect","useRef","useState","useContext"], "ans": 2},
        {"q": "What is the virtual DOM?", "opts": ["The real DOM","A JS copy of the DOM","A CSS engine","A server"], "ans": 1},
        {"q": "When does useEffect with `[]` run?", "opts": ["Every render","Only on unmount","Only on mount","Never"], "ans": 2},
        {"q": "What are React props?", "opts": ["Internal state","Passed-in data","CSS variables","Event handlers"], "ans": 1},
        {"q": "Which method re-renders a class component?", "opts": ["this.update()","this.render()","this.setState()","this.rerender()"], "ans": 2},
    ],
    "Machine Learning": [
        {"q": "What does overfitting mean?", "opts": ["Model is too simple","Model memorises training data","Model has low variance","Model underfits data"], "ans": 1},
        {"q": "Which metric is best for imbalanced classification?", "opts": ["Accuracy","Precision","F1-Score","MSE"], "ans": 2},
        {"q": "What does regularisation prevent?", "opts": ["Underfitting","Overfitting","Low accuracy","Slow training"], "ans": 1},
        {"q": "Which algorithm builds multiple decision trees?", "opts": ["KNN","SVM","Random Forest","Logistic Regression"], "ans": 2},
        {"q": "What is the purpose of a validation set?", "opts": ["Final testing","Tune hyperparameters","Train the model","Balance classes"], "ans": 1},
    ],
    "AWS": [
        {"q": "What does S3 stand for?", "opts": ["Secure Server Storage","Simple Storage Service","Scalable System Service","Swift Storage Solution"], "ans": 1},
        {"q": "Which AWS service runs serverless functions?", "opts": ["EC2","ECS","Lambda","Beanstalk"], "ans": 2},
        {"q": "What is an IAM role used for?", "opts": ["Storing files","Granting permissions","Running containers","DNS routing"], "ans": 1},
        {"q": "Which service provides a managed relational DB?", "opts": ["DynamoDB","S3","RDS","ElastiCache"], "ans": 2},
        {"q": "What does a VPC provide?", "opts": ["Object storage","Isolated network","Global CDN","Email service"], "ans": 1},
    ],
}

SKILL_ICONS = {
    "Python": "🐍", "SQL": "🗄️", "JavaScript": "⚡", "React": "⚛️",
    "Machine Learning": "🤖", "AWS": "☁️",
}

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class='anim-up' style='margin-bottom:20px;'>
  <div class='s-title' style='font-size:26px;'>Skill Tests</div>
  <div class='s-sub'>Time-bound assessments · Optional but boosts your Talent Score by up to 10 pts</div>
</div>
""", unsafe_allow_html=True)

# ── Load existing results ────────────────────────────────────────────────────
results_df = get_skill_test_results(wallet)
completed = set(results_df["skill_name"].tolist()) if not results_df.empty else set()

# ── State ────────────────────────────────────────────────────────────────────
if "test_active" not in st.session_state:
    st.session_state.test_active = False
if "test_skill" not in st.session_state:
    st.session_state.test_skill = None
if "test_answers" not in st.session_state:
    st.session_state.test_answers = {}
if "test_start_time" not in st.session_state:
    st.session_state.test_start_time = None
if "test_submitted" not in st.session_state:
    st.session_state.test_submitted = False
if "test_result" not in st.session_state:
    st.session_state.test_result = None

TEST_DURATION = 3 * 60  # 3 minutes

# ── Test Selection Grid ───────────────────────────────────────────────────────
if not st.session_state.test_active:

    # Show existing scores summary if any
    if not results_df.empty:
        avg_pct = round(results_df["percentage"].mean(), 1)
        bonus   = round(results_df["percentage"].mean() / 100 * 10, 1)
        c1, c2, c3 = st.columns(3)
        for col, (val, lbl) in zip([c1, c2, c3], [
            (f"{len(results_df)}/{len(TESTS)}", "Tests Completed"),
            (f"{avg_pct}%", "Average Score"),
            (f"+{bonus:.1f} pts", "Talent Score Boost"),
        ]):
            with col:
                st.markdown(f"""
                <div class='m-card' style='text-align:center;'>
                  <div class='m-lbl'>{lbl}</div>
                  <div class='m-val' style='font-size:22px;'>{val}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    # How it works banner
    st.markdown("""
    <div class='g-card' style='border-color:rgba(56,138,221,.2);margin-bottom:20px;'>
      <div style='display:flex;align-items:center;gap:20px;flex-wrap:wrap;'>
        <div style='display:flex;align-items:center;gap:8px;font-size:13px;color:#4a6a84;'>
          <svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='#378ADD' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='12' r='10'/><polyline points='12 6 12 12 16 14'/></svg>
          <span>3 min timer</span>
        </div>
        <div style='display:flex;align-items:center;gap:8px;font-size:13px;color:#4a6a84;'>
          <svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='#1D9E75' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><polyline points='9 11 12 14 22 4'/><path d='M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11'/></svg>
          <span>5 questions per skill</span>
        </div>
        <div style='display:flex;align-items:center;gap:8px;font-size:13px;color:#4a6a84;'>
          <svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='#EF9F27' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><polygon points='12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2'/></svg>
          <span>Improves talent score</span>
        </div>
        <div style='display:flex;align-items:center;gap:8px;font-size:13px;color:#4a6a84;'>
          <svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='#7F77DD' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z'/></svg>
          <span>Visible to employers</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Skill cards grid
    st.markdown("<div style='display:grid;grid-template-columns:repeat(3,1fr);gap:12px;'>", unsafe_allow_html=True)
    cols_row = [st.columns(3), st.columns(3)]
    skills_list = list(TESTS.keys())

    for i, skill in enumerate(skills_list):
        row_idx = i // 3
        col_idx = i % 3
        col = cols_row[row_idx][col_idx]
        with col:
            prev = results_df[results_df["skill_name"] == skill].iloc[0] if skill in completed else None
            if prev is not None:
                pct = float(prev["percentage"])
                bar_col = "#1D9E75" if pct >= 70 else "#EF9F27" if pct >= 50 else "#E24B4A"
                score_html = f"""
                <div style='margin-top:10px;'>
                  <div style='display:flex;justify-content:space-between;font-size:11px;color:#2a4a34;margin-bottom:4px;'>
                    <span>Your score</span>
                    <span style='color:{bar_col};font-weight:600;'>{pct:.0f}%</span>
                  </div>
                  <div class='bar-bg'><div class='bar' style='width:{pct}%;background:{bar_col};'></div></div>
                </div>"""
                btn_label = "Retake Test"
                btn_style = "secondary"
            else:
                score_html = "<div style='font-size:12px;color:#2a4a34;margin-top:10px;'>Not attempted yet</div>"
                btn_label = "Start Test"
                btn_style = "primary"

            st.markdown(f"""
            <div class='g-card' style='text-align:center;padding:18px 14px;min-height:150px;
                 {"border-color:rgba(29,158,117,.4);" if skill in completed else ""}'>
              <div style='font-size:24px;margin-bottom:8px;'>{SKILL_ICONS.get(skill,"📋")}</div>
              <div style='font-family:Syne,sans-serif;font-size:14px;font-weight:700;color:#fff;'>{skill}</div>
              <div style='font-size:11px;color:#4a6a84;margin-top:2px;'>5 questions · 3 min</div>
              {score_html}
            </div>
            """, unsafe_allow_html=True)

            if st.button(btn_label, key=f"start_{skill}", use_container_width=True):
                st.session_state.test_active = True
                st.session_state.test_skill = skill
                st.session_state.test_answers = {}
                st.session_state.test_start_time = time.time()
                st.session_state.test_submitted = False
                st.session_state.test_result = None
                st.rerun()

# ── Active Test ───────────────────────────────────────────────────────────────
else:
    skill = st.session_state.test_skill
    questions = TESTS[skill]
    elapsed = time.time() - st.session_state.test_start_time
    remaining = max(0, TEST_DURATION - int(elapsed))
    mins, secs = divmod(remaining, 60)

    if not st.session_state.test_submitted:
        # Timer display
        timer_col = "#E24B4A" if remaining < 30 else "#EF9F27" if remaining < 60 else "#4de8b4"
        st.markdown(f"""
        <div style='display:flex;align-items:center;justify-content:space-between;
                    padding:12px 20px;background:rgba(10,25,48,.8);border:1px solid rgba(29,158,117,.2);
                    border-radius:12px;margin-bottom:20px;'>
          <div style='font-family:Syne,sans-serif;font-size:18px;font-weight:700;color:#fff;'>
            {SKILL_ICONS.get(skill,"")} {skill} Test
          </div>
          <div style='display:flex;align-items:center;gap:8px;'>
            <svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='{timer_col}' stroke-width='2'><circle cx='12' cy='12' r='10'/><polyline points='12 6 12 12 16 14'/></svg>
            <span style='font-family:DM Mono,monospace;font-size:16px;color:{timer_col};font-weight:600;'>
              {mins:02d}:{secs:02d}
            </span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Auto-submit on timeout
        if remaining == 0:
            st.session_state.test_submitted = True
            st.rerun()

        # Questions
        for i, q in enumerate(questions):
            st.markdown(f"""
            <div class='g-card' style='margin-bottom:10px;'>
              <div style='font-size:13px;font-weight:600;color:#c8d8e8;margin-bottom:12px;'>
                Q{i+1} / {len(questions)} — {q['q']}
              </div>
            """, unsafe_allow_html=True)
            chosen = st.radio(
                f"q_{i}",
                options=q["opts"],
                index=st.session_state.test_answers.get(i, 0),
                label_visibility="collapsed",
                key=f"radio_{skill}_{i}"
            )
            st.session_state.test_answers[i] = q["opts"].index(chosen)
            st.markdown("</div>", unsafe_allow_html=True)

        col_cancel, col_submit = st.columns([1, 3])
        with col_cancel:
            if st.button("← Cancel", key="cancel_test"):
                st.session_state.test_active = False
                st.session_state.test_skill = None
                st.rerun()
        with col_submit:
            if st.button("Submit Test", use_container_width=True, key="submit_test"):
                st.session_state.test_submitted = True
                st.rerun()

    else:
        # Calculate result
        questions = TESTS[skill]
        correct = sum(
            1 for i, q in enumerate(questions)
            if st.session_state.test_answers.get(i, -1) == q["ans"]
        )
        total = len(questions)
        pct = round(correct / total * 100)
        result_col = "#4de8b4" if pct >= 70 else "#f5c263" if pct >= 50 else "#f08080"

        # Save to DB
        if st.session_state.test_result is None:
            upsert_skill_test_result(wallet, skill, correct, total)
            st.session_state.test_result = {"correct": correct, "total": total, "pct": pct}

        res = st.session_state.test_result

        st.markdown(f"""
        <div class='g-card anim-up' style='text-align:center;padding:36px 24px;
             border-color:{"rgba(29,158,117,.4)" if pct >= 70 else "rgba(239,159,39,.3)"};'>
          <div style='font-size:36px;margin-bottom:16px;'>{SKILL_ICONS.get(skill,"📋")}</div>
          <div style='font-family:Syne,sans-serif;font-size:44px;font-weight:800;
                      color:{result_col};margin-bottom:8px;'>{res["pct"]}%</div>
          <div style='font-size:16px;color:#fff;font-weight:600;margin-bottom:6px;'>
            {res["correct"]} / {res["total"]} correct
          </div>
          <div style='font-size:13px;color:#4a6a84;margin-bottom:20px;'>
            {"Excellent! Well above the benchmark." if pct >= 80 else
             "Good score — a bit more practice and you'll ace it." if pct >= 60 else
             "Keep practising — your score will improve your profile visibility."}
          </div>
          <div style='display:inline-flex;align-items:center;gap:8px;
                      padding:8px 18px;background:rgba(29,158,117,.12);
                      border:1px solid rgba(29,158,117,.3);border-radius:50px;
                      font-size:13px;color:#4de8b4;'>
            <svg width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'><polyline points='23 6 13.5 15.5 8.5 10.5 1 18'/><polyline points='17 6 23 6 23 12'/></svg>
            Talent score updated
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Answer review
        st.markdown("<div style='margin-top:20px;'>", unsafe_allow_html=True)
        st.markdown("<div class='s-title' style='font-size:16px;margin-bottom:10px;'>Answer Review</div>",
                    unsafe_allow_html=True)
        for i, q in enumerate(questions):
            user_ans = st.session_state.test_answers.get(i, -1)
            correct_ans = q["ans"]
            is_correct = user_ans == correct_ans
            icon_html = (
                '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#4de8b4" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>'
                if is_correct else
                '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f08080" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>'
            )
            border = "rgba(29,158,117,.25)" if is_correct else "rgba(226,75,74,.2)"
            st.markdown(f"""
            <div style='padding:10px 14px;border:1px solid {border};border-radius:10px;
                        margin-bottom:8px;'>
              <div style='display:flex;align-items:flex-start;gap:8px;'>
                {icon_html}
                <div>
                  <div style='font-size:13px;color:#c8d8e8;margin-bottom:4px;'>{q["q"]}</div>
                  {"" if is_correct else f'<div style="font-size:12px;color:#f08080;">Your answer: {q["opts"][user_ans] if user_ans >= 0 else "None"}</div>'}
                  <div style='font-size:12px;color:#4de8b4;'>Correct: {q["opts"][correct_ans]}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Back to Tests", use_container_width=False):
            st.session_state.test_active = False
            st.session_state.test_skill = None
            st.session_state.test_submitted = False
            st.session_state.test_result = None
            st.rerun()
