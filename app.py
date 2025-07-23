import streamlit as st
import os
from src.laptop_repair.crew import LaptopRepairCrew

# --- Page Configuration ---
st.set_page_config(page_title="Windows System Diagnostic Agent", layout="wide")

# --- Header ---
st.title("🤖 Windows System Diagnostic Agent")
st.markdown("""
Welcome! I'm an AI agent designed to help you diagnose problems with your Windows computer.
Describe the issue you're facing, provide your Gemini API key, and I'll investigate and create a fix script for you.
""")

# --- Session State Initialization ---
if 'diagnosis_report' not in st.session_state:
    st.session_state.diagnosis_report = ""
if 'submitted_problem' not in st.session_state:
    st.session_state.submitted_problem = ""
if 'show_script_permission' not in st.session_state:
    st.session_state.show_script_permission = False
if 'user_approved_script' not in st.session_state:
    st.session_state.user_approved_script = False
if 'script_content' not in st.session_state:
    st.session_state.script_content = ""
if 'diagnosis_content' not in st.session_state:
    st.session_state.diagnosis_content = ""

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
        # Reset session state for new diagnosis
        st.session_state.show_script_permission = False
        st.session_state.user_approved_script = False
        st.session_state.script_content = ""
        st.session_state.diagnosis_content = ""
        
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
                
                # Check if the report contains a script
                if "--- BATCH SCRIPT START ---" in report:
                    # Split the report into diagnosis and script parts
                    try:
                        diagnosis, script_full = report.split("--- BATCH SCRIPT START ---", 1)
                        script_content = script_full.split("--- BATCH SCRIPT END ---")[0].strip()
                        
                        st.session_state.diagnosis_content = diagnosis
                        st.session_state.script_content = script_content
                        st.session_state.show_script_permission = True
                    except ValueError:
                        st.session_state.diagnosis_content = report
                        st.session_state.show_script_permission = False
                else:
                    st.session_state.diagnosis_content = report
                    st.session_state.show_script_permission = False
                    
            except Exception as e:
                st.error(f"An error occurred while running the diagnosis: {e}")

# --- Diagnosis Results Section ---
if st.session_state.diagnosis_report:
    st.header("2. Diagnosis Results")
    with st.container(border=True):
        st.markdown(f"**Problem Investigated:** *{st.session_state.submitted_problem}*")
        st.markdown("---")
        
        # Display the diagnosis part
        if st.session_state.diagnosis_content:
            st.markdown(st.session_state.diagnosis_content)
        else:
            st.markdown(st.session_state.diagnosis_report)

# --- Script Permission Section ---
if st.session_state.show_script_permission and not st.session_state.user_approved_script:
    st.header("3. 🔧 Proposed Fix Script")
    
    with st.container(border=True):
        st.warning("""
        ⚠️ **IMPORTANT: Script Generation Request**
        
        The diagnostic agent has identified your issue and can create a Windows Batch Script (.bat file) to fix it automatically.
        
        **Before you proceed:**
        - The script will make changes to your system
        - Always backup important data before running system repair scripts
        - Review the script content carefully before execution
        - Run the script as Administrator when prompted
        """)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("✅ Yes, Create Fix Script", type="primary", use_container_width=True):
                st.session_state.user_approved_script = True
                st.rerun()
        
        with col2:
            if st.button("❌ No, Just Show Diagnosis", use_container_width=True):
                st.session_state.show_script_permission = False
                st.rerun()
                
        with col3:
            if st.button("🔄 Run New Diagnosis", use_container_width=True):
                # Clear all session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

# --- Script Display Section ---
if st.session_state.user_approved_script and st.session_state.script_content:
    st.header("4. 📥 Your Fix Script")
    
    with st.container(border=True):
        st.success("✅ Script has been generated based on your approval!")
        
        # Display the script with syntax highlighting
        st.subheader("Batch Script Content:")
        st.code(st.session_state.script_content, language='batch')
        
        # Download button
        col1, col2 = st.columns([1, 1])
        with col1:
            st.download_button(
                label="📥 Download Fix Script (.bat)",
                data=st.session_state.script_content.encode('utf-8'),
                file_name="system_fix_script.bat",
                mime="application/x-bat",
                type="primary",
                use_container_width=True
            )
        
        with col2:
            if st.button("🔄 Generate New Script", use_container_width=True):
                st.session_state.user_approved_script = False
                st.session_state.show_script_permission = True
                st.rerun()
        
        # Instructions
        st.subheader("📋 How to Run the Script:")
        st.info("""
        1. **Download** the script file using the button above
        2. **Right-click** on the downloaded .bat file
        3. **Select "Run as administrator"** (very important!)
        4. **Follow** the prompts in the command window
        5. **Wait** for the script to complete
        6. **Restart** your computer if prompted
        7. **Test** if your original problem is resolved
        """)

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; font-size: 0.9em; color: grey;">
    <p>Powered by <strong>crewAI</strong>, <strong>Google Gemini</strong>, and <strong>Streamlit</strong></p>
    <p><strong>⚠️ Important Disclaimer:</strong> This tool generates system repair scripts. While designed for safety, 
    always backup your data before running any system modifications. Use at your own risk.</p>
</div>
""", unsafe_allow_html=True)