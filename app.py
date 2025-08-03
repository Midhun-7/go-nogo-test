import streamlit as st
import random
import time
import json

# Configuration
TOTAL_TRIALS = 30
TARGET_PROBABILITY = 0.7

# Initialize session state
if "trial_index" not in st.session_state:
    st.session_state.trial_index = 0
    st.session_state.results = []
    st.session_state.current_stimulus = None
    st.session_state.stimulus_time = None
    st.session_state.show_result = False
    st.session_state.done = False

# Title and Instructions
st.title("🧠 Go/No-Go ADHD Test")
st.markdown("Press the **GO button** only if you see 🚦 GO. If you see 🛑 NO-GO, **do nothing** and press 'Next Trial'.")

# Run test
if not st.session_state.done:
    if st.session_state.current_stimulus is None:
        st.session_state.current_stimulus = "GO" if random.random() < TARGET_PROBABILITY else "NO-GO"
        st.session_state.stimulus_time = time.time()

    st.markdown(f"### Trial {st.session_state.trial_index + 1} / {TOTAL_TRIALS}")
    st.markdown(
        f"<h1 style='text-align:center;font-size:80px'>{'🚦 GO' if st.session_state.current_stimulus == 'GO' else '🛑 NO-GO'}</h1>",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("GO Button (Press if GO)", key=f"go_button_{st.session_state.trial_index}"):
            reaction_time = round((time.time() - st.session_state.stimulus_time) * 1000)
            st.session_state.results.append({
                "trial": st.session_state.trial_index + 1,
                "stimulus": st.session_state.current_stimulus,
                "responded": True,
                "reaction_time": reaction_time,
                "correct": st.session_state.current_stimulus == "GO"
            })
            st.session_state.trial_index += 1
            st.session_state.current_stimulus = None
            st.session_state.stimulus_time = None
            if st.session_state.trial_index >= TOTAL_TRIALS:
                st.session_state.done = True
            st.rerun()


    with col2:
        if st.button("Next Trial (No Response)", key=f"next_button_{st.session_state.trial_index}"):
            st.session_state.results.append({
                "trial": st.session_state.trial_index + 1,
                "stimulus": st.session_state.current_stimulus,
                "responded": False,
                "reaction_time": None,
                "correct": st.session_state.current_stimulus == "NO-GO"
            })
            st.session_state.trial_index += 1
            st.session_state.current_stimulus = None
            st.session_state.stimulus_time = None
            if st.session_state.trial_index >= TOTAL_TRIALS:
                st.session_state.done = True
            st.rerun()



    if st.session_state.trial_index >= TOTAL_TRIALS:
        st.session_state.done = True


    # Results
if st.session_state.done:
    results = st.session_state.results
    commission_errors = sum(1 for r in results if r["stimulus"] == "NO-GO" and r["responded"])
    omission_errors = sum(1 for r in results if r["stimulus"] == "GO" and not r["responded"])
    correct_go = sum(1 for r in results if r["stimulus"] == "GO" and r["responded"])
    correct_nogo = sum(1 for r in results if r["stimulus"] == "NO-GO" and not r["responded"])
    total_correct = correct_go + correct_nogo
    reaction_times = [r["reaction_time"] for r in results if r["reaction_time"] is not None]
    avg_rt = round(sum(reaction_times) / len(reaction_times), 2) if reaction_times else 0

    st.success("✅ Test Complete")
    st.markdown(f"""
    ### 🧾 Your Performance Summary  
    - **Total Trials:** {TOTAL_TRIALS}  
    - ✅ **Correct Responses:** {total_correct} / {TOTAL_TRIALS}  
    - 🟢 **Correct GO:** {correct_go}  
    - 🔴 **Correct NO-GO:** {correct_nogo}  
    - ❌ **Commission Errors (Pressed on NO-GO):** {commission_errors}  
    - ❌ **Omission Errors (Missed GO):** {omission_errors}  
    - ⏱️ **Average Reaction Time:** {avg_rt} ms
    """)

    st.download_button(
    label="📄 Download Raw Data",
    data=json.dumps(results, indent=2),
    file_name="go_nogo_results.json",
    key="download_raw_data_button"
)
