import streamlit as st
from Parser.nastran_parser import parse_f06
from Observer.trend_analysis import analyse_trends
from agent.diagnose import diagnose

st.title("SDA Solver Log Agent")

uploaded_file = st.file_uploader("Upload .f06 file")

if uploaded_file:
    with open("temp.f06", "wb") as f:
        f.write(uploaded_file.read())

    parsed = parse_f06("temp.f06")
    observations = analyse_trends(parsed)
    diagnosis = diagnose(parsed, observations)

    st.subheader("Observations")
    st.write(observations)

    st.subheader("Diagnosis")
    st.write(diagnosis)