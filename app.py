import streamlit as st
from Parser.nastran_parser import parse_f06
from Observer.trend_analysis import analyse_trends
from agent.diagnose import diagnose

st.info("💡 This tool analyses solver logs and suggests root causes and fixes automatically.")
st.success("✅ Analysis Complete")
st.subheader(f"✅ {len(diagnosis)} Issue(s) Found")
# ✅ Page config
st.set_page_config(page_title="Solver Log Agent", layout="centered")

# ✅ Title
st.title("🔍 Solver Log Agent")
st.write("Upload a solver log (.f06) to get quick diagnosis")

# ✅ File upload
uploaded_file = st.file_uploader("Upload .f06 file", type=["f06", "out"])

if uploaded_file:

    # Save temp file
    with open("temp.f06", "wb") as f:
        f.write(uploaded_file.read())

    # Run pipeline
    parsed = parse_f06("temp.f06")
    observations = analyse_trends(parsed)
    diagnosis = diagnose(parsed, observations)

    st.divider()

    # ✅ Show only clean diagnosis
    st.subheader("✅ Diagnosis Result")

    for d in diagnosis:

        with st.container():
            st.markdown("### 🚨 Issue")
            st.error(d["issue"])   # red highlight

            st.markdown("### 🔍 Cause")
            st.info(d["cause"])    # blue box

            st.markdown("### 🛠 Fix Recommendation")
            
            for fix in d["fix"]:
                st.write(f"✅ {fix}")