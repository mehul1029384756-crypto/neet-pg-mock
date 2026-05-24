import streamlit as st
import pandas as pd
import time
import streamlit.components.v1 as components

# --- PAGE SETUP ---
st.set_page_config(page_title="NEET PG Pro Simulator", layout="wide", initial_sidebar_state="expanded")

# --- CSS INJECTION (THE UI FIX) ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] button p {
        white-space: nowrap !important;
        font-size: 13px !important;
    }
    [data-testid="stSidebar"] button {
        padding: 0.25rem 0rem !important;
        width: 100% !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- LOAD DATABASE ---
@st.cache_data
def load_questions():
    try:
        df = pd.read_csv("questions.csv")
        return df.to_dict('records')
    except FileNotFoundError:
        st.error("⚠️ questions.csv not found! Please create it in the same folder.")
        return []

questions = load_questions()

# --- APP STATE INITIALIZATION ---
if 'started' not in st.session_state:
    st.session_state.started = False
if 'start_time' not in st.session_state:
    st.session_state.start_time = 0
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'current_q' not in st.session_state:
    st.session_state.current_q = 0
if 'answers' not in st.session_state:
    st.session_state.answers = {} 
if 'review' not in st.session_state:
    st.session_state.review = set() 
if 'score' not in st.session_state:
    st.session_state.score = 0

total_q = len(questions)

# --- START SCREEN ---
if not st.session_state.started:
    st.title("NEET PG / INICET Grand Mock")
    st.markdown("### Instructions")
    st.write("1. The clock starts the moment you begin.")
    st.write("2. Select an option to auto-save your answer. Use Next/Back to navigate.")
    st.write("3. 🔵 = Unattempted | 🟡 = Attempted")
    st.write("4. You must click **Submit Exam** at the end to see your results and explanations.")
    
    if st.button("🚀 BEGIN TEST", type="primary", use_container_width=True):
        st.session_state.started = True
        st.session_state.start_time = time.time()
        st.rerun()

# --- MAIN APP LOGIC ---
else:
    # --- SIDEBAR DASHBOARD ---
    with st.sidebar:
        if not st.session_state.submitted:
            st.header("⏳ Time Elapsed")
            components.html(f"""
            <div id="clock" style="font-family: monospace; font-size: 32px; font-weight: bold; color: #ff4b4b; text-align: center; padding: 10px; border: 2px solid #ff4b4b; border-radius: 8px; background: #fff0f0;">00:00:00</div>
            <script>
                var startTime = {st.session_state.start_time} * 1000;
                setInterval(function() {{
                    var now = new Date().getTime();
                    var distance = now - startTime;
                    var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                    var seconds = Math.floor((distance % (1000 * 60)) / 1000);
                    document.getElementById("clock").innerHTML = 
                        (hours < 10 ? "0" + hours : hours) + ":" + 
                        (minutes < 10 ? "0" + minutes : minutes) + ":" + 
                        (seconds < 10 ? "0" + seconds : seconds);
                }}, 1000);
            </script>
            """, height=80)
            
            st.markdown("---")
            st.header("📊 Exam Navigator")
        else:
            st.header("🏁 Exam Results")
            st.write(f"### Score: {st.session_state.score} / {total_q}")
            
            # --- THE AESTHETIC HTML REPORT GENERATOR (NOW WITH OPTIONS) ---
            html_report = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; padding: 40px; max-width: 900px; margin: auto; }}
                .header {{ text-align: center; margin-bottom: 40px; border-bottom: 2px solid #ddd; padding-bottom: 20px; }}
                .score-box {{ font-size: 28px; font-weight: bold; color: #2c3e50; background: #e0f7fa; padding: 15px 30px; border-radius: 8px; display: inline-block; margin-top: 10px; }}
                .card {{ background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 25px; border-left: 6px solid #ccc; }}
                .correct {{ border-left-color: #2ecc71; }}
                .incorrect {{ border-left-color: #e74c3c; }}
                .skipped {{ border-left-color: #f39c12; }}
                .q-text {{ font-weight: bold; font-size: 16px; margin-bottom: 15px; line-height: 1.5; }}
                .options-box {{ background-color: #f9f9f9; border: 1px solid #eaeaea; border-radius: 6px; padding: 12px 20px; margin-bottom: 15px; }}
                .options-box ul {{ margin: 0; padding-left: 20px; color: #444; font-size: 15px; line-height: 1.6; }}
                .ans-row {{ margin: 8px 0; font-size: 15px; }}
                .label {{ font-weight: bold; display: inline-block; width: 120px; }}
                .pearl {{ background: #fffde7; padding: 15px; border-left: 4px solid #f1c40f; margin-top: 20px; font-style: italic; border-radius: 0 4px 4px 0; }}
            </style>
            </head>
            <body>
                <div class="header">
                    <h1>INICET / NEET PG Performance Report</h1>
                    <div class="score-box">Final Score: {st.session_state.score} / {total_q}</div>
                </div>
            """
            
            for i in range(total_q):
                q_data = questions[i]
                user_ans_key = st.session_state.answers.get(i)
                correct_ans_key = q_data["Correct"]
                
                options_map = {
                    "Option_A": q_data["Option_A"],
                    "Option_B": q_data["Option_B"],
                    "Option_C": q_data["Option_C"],
                    "Option_D": q_data["Option_D"]
                }
                
                user_ans_text = options_map.get(user_ans_key, "Skipped completely")
                correct_ans_text = options_map.get(correct_ans_key, "Error")
                
                if user_ans_key == correct_ans_key:
                    status_class = "correct"
                    icon = "✅ Correct"
                elif user_ans_key is None:
                    status_class = "skipped"
                    icon = "⚠️ Skipped"
                else:
                    status_class = "incorrect"
                    icon = "❌ Incorrect"
                    
                html_report += f"""
                <div class="card {status_class}">
                    <div class="q-text">Q{i+1}. {q_data['Question']}</div>
                    
                    <div class="options-box">
                        <ul>
                            <li><b>A:</b> {q_data['Option_A']}</li>
                            <li><b>B:</b> {q_data['Option_B']}</li>
                            <li><b>C:</b> {q_data['Option_C']}</li>
                            <li><b>D:</b> {q_data['Option_D']}</li>
                        </ul>
                    </div>

                    <div class="ans-row"><span class="label">Status:</span> <b>{icon}</b></div>
                    <div class="ans-row"><span class="label">Your Answer:</span> {user_ans_text}</div>
                    <div class="ans-row"><span class="label">Correct Answer:</span> {correct_ans_text}</div>
                    <div class="pearl"><b>Clinical Pearl:</b><br><br>{q_data['Explanation']}</div>
                </div>
                """
                
            html_report += "</body></html>"
            
            st.download_button(
                label="📄 Download Report",
                data=html_report.encode('utf-8'),
                file_name="NEET_PG_Scorecard.html",
                mime="text/html",
                use_container_width=True,
                type="primary"
            )
            # --- END EXPORT LOGIC ---
            
            st.markdown("---")
            st.write("**Review Your Answers:**")

        # Question Grid Navigation
        cols = st.columns(4)
        for i in range(total_q):
            flag = "🚩" if i in st.session_state.review and not st.session_state.submitted else ""
            
            if st.session_state.submitted:
                user_ans = st.session_state.answers.get(i)
                correct_ans = questions[i]["Correct"]
                if user_ans == correct_ans:
                    color = "🟢" 
                elif user_ans is None:
                    color = "⚪" 
                else:
                    color = "🔴" 
            else:
                if i in st.session_state.answers:
                    color = "🟡" 
                else:
                    color = "🔵" 

            if cols[i % 4].button(f"{color} {i+1} {flag}", key=f"nav_{i}"):
                st.session_state.current_q = i
                st.rerun()

        if not st.session_state.submitted:
            st.markdown("---")
            if st.button("🛑 SUBMIT EXAM", type="primary", use_container_width=True):
                st.session_state.submitted = True
                st.session_state.score = sum(
                    1 for i in range(total_q) 
                    if st.session_state.answers.get(i) == questions[i]["Correct"]
                )
                st.balloons()
                st.rerun()

    # --- MAIN EXAM AREA ---
    if total_q > 0:
        q = questions[st.session_state.current_q]
        options_dict = {
            "Option_A": q["Option_A"],
            "Option_B": q["Option_B"],
            "Option_C": q["Option_C"],
            "Option_D": q["Option_D"]
        }
        display_options = list(options_dict.values())
        
        mode_text = "Review Mode" if st.session_state.submitted else "Active Exam"
        st.subheader(f"Question {st.session_state.current_q + 1} of {total_q} | {mode_text}")
        st.markdown(f"### {q['Question']}")
        
        prev_ans_key = st.session_state.answers.get(st.session_state.current_q)
        prev_index = display_options.index(options_dict[prev_ans_key]) if prev_ans_key else None

        def record_answer():
            selected_text = st.session_state[f"radio_{st.session_state.current_q}"]
            if selected_text:
                for k, v in options_dict.items():
                    if v == selected_text:
                        st.session_state.answers[st.session_state.current_q] = k
                        break

        if not st.session_state.submitted:
            st.radio("Choose an option:", display_options, index=prev_index, 
                     key=f"radio_{st.session_state.current_q}", on_change=record_answer)
        else:
            st.radio("Your selection:", display_options, index=prev_index, disabled=True, key=f"radio_review_{st.session_state.current_q}")

        st.markdown("---")

        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("⬅️ Back"):
                if st.session_state.current_q > 0:
                    st.session_state.current_q -= 1
                    st.rerun()

        with col2:
            if not st.session_state.submitted:
                button_label = "Unmark Review" if st.session_state.current_q in st.session_state.review else "🚩 Mark for Review"
                if st.button(button_label):
                    if st.session_state.current_q in st.session_state.review:
                        st.session_state.review.remove(st.session_state.current_q)
                    else:
                        st.session_state.review.add(st.session_state.current_q)
                    st.rerun()

        with col3:
            if st.button("Next ➡️"):
                if st.session_state.current_q < total_q - 1:
                    st.session_state.current_q += 1
                    st.rerun()

        if st.session_state.submitted:
            st.divider()
            correct_key = q["Correct"]
            
            if prev_ans_key == correct_key:
                st.success(f"✅ You answered correctly: **{options_dict[correct_key]}**")
            elif prev_ans_key is None:
                st.warning(f"⚠️ You skipped this question. The correct answer is: **{options_dict[correct_key]}**")
            else:
                st.error(f"❌ You chose: {options_dict.get(prev_ans_key, 'None')}")
                st.success(f"✅ The correct answer is: **{options_dict[correct_key]}**")
                
            st.info(f"**Clinical Pearl / Explanation:**\n\n{q['Explanation']}")
            
            st.markdown("---")
            if st.button("🔄 Retake Exam / Clear Memory"):
                st.session_state.clear()
                st.rerun()
