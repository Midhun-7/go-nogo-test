import streamlit as st
import numpy as np
import random
import time
import json
import matplotlib.pyplot as plt

# Configuration
TOTAL_TRIALS = 30
TARGET_PROBABILITY = 0.7
COMMISSION_THRESHOLD = 0.25  # 25% Commission Errors

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

# Final Result Analysis
if st.session_state.done:
    results = st.session_state.results
    commission_errors = sum(1 for r in results if r["stimulus"] == "NO-GO" and r["responded"])
    omission_errors = sum(1 for r in results if r["stimulus"] == "GO" and not r["responded"])
    correct_go = sum(1 for r in results if r["stimulus"] == "GO" and r["responded"])
    correct_nogo = sum(1 for r in results if r["stimulus"] == "NO-GO" and not r["responded"])
    total_correct = correct_go + correct_nogo
    reaction_times = [r["reaction_time"] for r in results if r["reaction_time"] is not None]
    avg_rt = round(sum(reaction_times) / len(reaction_times), 2) if reaction_times else 0

    commission_rate = commission_errors / (sum(1 for r in results if r["stimulus"] == "NO-GO")) if results else 0

    # Show basic summary
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
    - 📉 **Commission Error Rate:** {commission_rate*100:.1f}%
    """)

    # Alert for high commission error rate
    if commission_rate > COMMISSION_THRESHOLD:
        st.error("⚠️ Your commission error rate is above 25%. This may indicate potential signs of ADHD.\n\nWe recommend consulting a medical professional for proper evaluation.")
    else:
        st.success("🎉 Your commission error rate is within a typical range. No immediate concern indicated.")

    # Cite the research
    st.markdown("""
    > 📚 Based on: Barkley, R.A., et al. (1992). "The Go/No-Go Task and ADHD: Response Inhibition Deficits."  
    > A commission error rate above **25%** is often observed in individuals with **impulse control challenges**.
    """)

    # Matplotlib visualization
    st.markdown("### 📊 Error Distribution Chart")
    labels = ['Correct GO', 'Correct NO-GO', 'Commission Errors', 'Omission Errors']
    values = [correct_go, correct_nogo, commission_errors, omission_errors]

    fig, ax = plt.subplots()
    ax.bar(labels, values, color=["green", "blue", "red", "orange"])
    ax.set_ylabel("Count")
    ax.set_title("Go/No-Go Task Performance Summary")
    plt.xticks(rotation=15)
    st.pyplot(fig)

    # Download button
    st.download_button(
        label="📄 Download Raw Data",
        data=json.dumps(results, indent=2),
        file_name="go_nogo_results.json",
        key="download_raw_data_button"
    )
