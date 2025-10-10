import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from io import BytesIO
from resume_skill_matcher_wrapper import match_resumes

# --- Page Config ---
st.set_page_config(
    page_title="Job Skill Matcher",
    layout="wide",
    page_icon="💼",
    initial_sidebar_state="expanded"
)

# --- Dark/Light Mode Toggle ---
st.sidebar.title("Settings")
theme_choice = st.sidebar.radio("Select Theme:", ("Light", "Dark"))
if theme_choice == "Dark":
    st.markdown(
        """
        <style>
        .reportview-container {background-color: #0e1117;}
        .stButton>button {background-color:#1f77b4;color:white;}
        .stDataFrame div {color:white;}
        </style>
        """,
        unsafe_allow_html=True
    )

st.title("📌 Job Skill Matcher Dashboard")
st.write("Upload job description and resumes to get skill match analysis.")

# --- Upload Section ---
job_file = st.file_uploader("Upload Job Description (.txt)", type=["txt"])
resume_files = st.file_uploader("Upload Resumes (.pdf, .docx)", type=["pdf","docx"], accept_multiple_files=True)

# --- Analyze Button ---
if st.button("Analyze Resumes"):
    if not job_file or not resume_files:
        st.error("Please upload both job description and at least one resume.")
    else:
        job_text = job_file.read().decode("utf-8")
        results = match_resumes(job_text, resume_files)
        df_results = pd.DataFrame(results)

        # --- Summary Section ---
        st.subheader("📊 Summary Statistics")
        st.metric("Resumes Analyzed", len(df_results))
        st.metric("Average Match %", f"{round(df_results['match_percent'].mean(), 2)}%")
        
        # --- Results Table with hoverable progress bars ---
        st.subheader("✅ Resume Match Results")
        for idx, row in df_results.iterrows():
            match_percent = row['match_percent']
            color = "green" if match_percent >= 70 else "orange" if match_percent >= 40 else "red"
            st.markdown(f"**{row['resume_name']}** - Match: <span style='color:{color}'>{match_percent}%</span>", unsafe_allow_html=True)
            st.progress(match_percent/100)
            st.markdown(f"Matched Skills: {row['matched_skills']}")
            st.markdown(f"Missing Skills: {row['missing_skills']}")
            st.markdown("---")

        # --- Recommendations ---
        st.subheader("💡 Recommendations for Missing Skills")
        for res in results:
            if res['missing_skills']:
                st.info(f"**{res['resume_name']}**: Learn `{res['missing_skills']}`")
            else:
                st.success(f"**{res['resume_name']}**: All required skills matched 🎉")

        # --- Radar Chart: Combined Skill Comparison ---
        st.subheader("📊 Skill Comparison Radar Chart")
        all_skills = list({skill for res in results for skill in (res['matched_skills'] + ", " + res['missing_skills']).split(", ") if skill})
        fig = go.Figure()
        for res in results:
            matched = res['matched_skills'].split(", ") if res['matched_skills'] else []
            values = [1 if skill in matched else 0 for skill in all_skills]
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=all_skills,
                fill='toself',
                name=res['resume_name'],
                hoverinfo='text',
                text=[f"{skill}: {'Matched' if skill in matched else 'Missing'}" for skill in all_skills]
            ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0,1])),
            showlegend=True,
            title="Skill Coverage Comparison"
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- CSV Download ---
        st.subheader("⬇️ Download Results as CSV")
        csv = df_results.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name='resume_skill_match_results.csv',
            mime='text/csv'
        )
