import streamlit as st
import os
from src.laptop_repair.crew import LaptopRepairCrew

# --- Page Configuration ---
st.set_page_config(page_title="Windows System Diagnostic Agent", layout="wide")

# --- Header ---
st.title("🤖 Windows System Diagnostic Agent")
st.markdown("""
Welcome! I'm an AI agent designed to help you diagnose problems with your Windows computer.
Describe the issue you're facing, provide your Gemini API key, and I'll investigate.
""")

# --- Session State Initialization ---
if 'diagnosis_report' not in st.session_state:
    st.session_state.diagnosis_report = ""
if 'submitted_problem' not in st.session_state:
    st.session_state.submitted_problem = ""

# --- Input Section ---
with st.container(border=True):
    st.header("1. Enter Your Details")
    
    # Gemini API Key Input
    gemini_api_key = st.text_input(
        "Enter your Google Gemini API Key",
        type="password",
        help="Your API key is required to power the diagnostic agents."
    )
    
    # Problem Description Input
    problem_input = st.text_area(
        "Describe your problem",
        height=100,
        placeholder="e.g., 'My computer is running very slow and the fan is constantly loud.'"
    )

# --- Run Button and Logic ---
if st.button("🔍 Diagnose My System", type="primary"):
    if not gemini_api_key:
        st.warning("Please enter your Gemini API Key to proceed.")
    elif not problem_input:
        st.warning("Please describe the problem before starting the diagnosis.")
    else:
        # Set the API key in the environment for the crew to use
        os.environ["GEMINI_API_KEY"] = gemini_api_key
        st.session_state.submitted_problem = problem_input
        st.session_state.diagnosis_report = ""  # Clear previous report
        
        # Initialize and run the crew
        repair_crew = LaptopRepairCrew(problem_input)
        with st.spinner('The diagnostic agents are investigating... This may take a moment.'):
            try:
                report = repair_crew.run()
                st.session_state.diagnosis_report = report
            except Exception as e:
                st.error(f"An error occurred while running the diagnosis: {e}")
                # For debugging, you can uncomment the line below
                # st.exception(e)

# --- Output Section ---
if st.session_state.diagnosis_report:
    st.header("2. Diagnosis and Proposed Fix")
    with st.container(border=True):
        st.markdown(f"**Problem Investigated:** *{st.session_state.submitted_problem}*")
        st.markdown("---")

        report = st.session_state.diagnosis_report

        # Check if the report contains a script
        if "--- SCRIPT START ---" in report:
            try:
                # Split the report into diagnosis and script parts
                diagnosis, script_full = report.split("--- SCRIPT START ---", 1)
                script_content = script_full.split("--- SCRIPT END ---")[0].strip()

                # Display the diagnosis
                st.markdown(diagnosis)

                # Display the proposed fix script with clear warnings
                st.subheader("Proposed Fix Script")
                st.warning(
                    "⚠️ **Execute at your own risk!** This script is intended to make changes to your system."
                    " Please review the contents carefully before running."
                )
                
                # Show the script in a code block
                st.code(script_content, language='powershell')

                # Add a download button
                st.download_button(
                    label="📥 Download Fix Script (.ps1)",
                    data=script_content.encode('utf-8'), # Encode to bytes
                    file_name="fix_script.ps1",
                    mime="text/plain"
                )

            except ValueError:
                # Fallback if splitting fails
                st.markdown(report)
        else:
            # If no script is found, just display the entire report
            st.markdown(report)

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; font-size: 0.9em; color: grey;">
    <p>Powered by <strong>crewAI</strong>, <strong>Google Gemini</strong>, and <strong>Streamlit</strong></p>
    <p><strong>Disclaimer:</strong> This tool executes system commands. While designed for safety, use it at your own risk.
    Always back up important data before making system changes.</p>
</div>
""", unsafe_allow_html=True)
