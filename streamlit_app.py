import os
import sys
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'), override=True)

# Try importing Google GenAI SDK gracefully
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# Try importing PyMuPDF for PDF resume extraction gracefully
try:
    import pymupdf as fitz
    FITZ_AVAILABLE = True
except ImportError:
    try:
        import fitz
        FITZ_AVAILABLE = True
    except ImportError:
        FITZ_AVAILABLE = False

# Page Configuration
st.set_page_config(
    page_title="AI Recruitment Assist | Gemini GenAI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Theme
st.markdown("""
<style>
    /* Dark Theme Accent Styling */
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
    }
    
    /* Header Gradient Banner */
    .main-header {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(16, 185, 129, 0.15));
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(10px);
    }
    
    .main-header h1 {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(90deg, #818cf8, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .main-header p {
        color: #9ca3af;
        margin-top: 8px;
        font-size: 1rem;
    }

    /* Metric Card Styling */
    .metric-card {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    
    /* Result Box Styling */
    .result-container {
        background: #111827;
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 20px;
        margin-top: 16px;
    }
</style>
""", unsafe_allow_html=True)


# Safe secret retriever
def get_secret(key_name, default=""):
    try:
        return st.secrets.get(key_name, default)
    except Exception:
        return default


# Helper function to get Gemini Client
def get_client(custom_api_key=""):
    if not GENAI_AVAILABLE:
        return None, "google-genai library is missing. Please check requirements.txt."
    
    # Priority: 1. UI Input 2. Streamlit Secrets 3. Environment Variable
    api_key = custom_api_key.strip() or get_secret("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

    if not api_key:
        return None, "Google API Key is missing. Please provide it in the sidebar or setup GOOGLE_API_KEY in secrets / .env file."

    try:
        client = genai.Client(api_key=api_key)
        return client, None
    except Exception as e:
        return None, f"Failed to initialize Gemini Client: {str(e)}"


# Helper function to call Gemini AI
def generate_response(prompt, custom_key="", system_instruction=None, model_name="gemini-3.6-flash"):
    client, error = get_client(custom_key)
    if error:
        return None, error
    
    try:
        config = {}
        if system_instruction:
            config["system_instruction"] = system_instruction
            
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config if config else None
        )
        return response.text, None
    except Exception as e:
        return None, f"Gemini API Error: {str(e)}"


# Helper to extract PDF text
def extract_pdf_text(file_bytes):
    if not FITZ_AVAILABLE:
        return None, "PyMuPDF library is not available for PDF parsing."
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        return text.strip(), None
    except Exception as e:
        return None, f"PDF Extraction Failed: {str(e)}"


# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/google-logo.png", width=48)
    st.title("Settings & Status")
    
    custom_api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        help="Leave blank if set in Streamlit Secrets or .env file",
        key="sidebar_api_key"
    )
    
    model_choice = st.selectbox(
        "Select Model",
        options=["gemini-3.6-flash"],
        index=0
    )
    
    st.divider()
    
    # Status Checks
    active_key = custom_api_key or os.getenv("GOOGLE_API_KEY") or get_secret("GOOGLE_API_KEY")
    key_configured = bool(active_key)
    
    st.write("**System Status:**")
    st.markdown(f"• **GenAI Library**: {'✅ Installed' if GENAI_AVAILABLE else '❌ Missing'}")
    st.markdown(f"• **API Key**: {'✅ Configured' if key_configured else '⚠️ Not Found'}")
    st.markdown(f"• **PDF Engine**: {'✅ Available' if FITZ_AVAILABLE else '⚠️ Missing (PyMuPDF)'}")
    
    st.divider()
    st.caption("Powered by Google Gemini 3.6 Flash & Prompt Engineering")


# --- MAIN HEADER ---
st.markdown("""
<div class="main-header">
    <h1>⚡ Enhancing Recruitment with Prompt Engineering</h1>
    <p>Automate Job Description creation, Candidate Resume evaluation, and Interview Question generation using Google Gemini AI.</p>
</div>
""", unsafe_allow_html=True)


# --- MAIN TABS ---
tab_jd, tab_screener, tab_questions, tab_presets = st.tabs([
    "📝 Job Spec Generator", 
    "📄 Resume Screener", 
    "🎯 Interview Questions", 
    "⚡ Quick Presets"
])

# -------------------------------------------------------------
# TAB 1: JOB SPEC GENERATOR
# -------------------------------------------------------------
with tab_jd:
    st.subheader("Generate Structured Job Descriptions")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        role_input = st.text_input("Job Role Title", placeholder="e.g. Senior Machine Learning Engineer", key="jd_role")
        company_type = st.selectbox(
            "Company Industry / Type",
            ["Fast-growing AI Startup", "Enterprise Tech Giant", "Fintech Startup", "Healthcare Tech", "E-commerce Leader"],
            key="jd_company"
        )
        generate_jd_btn = st.button("✨ Generate Job Description", type="primary", key="btn_jd")
        
    with col2:
        st.info("💡 **Prompt Tip**: Generates structured sections including Role Overview, Key Responsibilities, Required Qualifications, and Key Deliverables.")
    
    if generate_jd_btn:
        if not role_input.strip():
            st.error("Please enter a job role title.")
        else:
            with st.spinner("Generating Job Description..."):
                prompt = f"Write a detailed, structured job description for the role of {role_input} in a {company_type}. Include Sections: Role Overview, Key Responsibilities, Required Qualifications, Nice-to-Haves, and Key Deliverables."
                sys_inst = "You are an expert HR Talent Acquisition Specialist and Technical Writer."
                
                result, error = generate_response(prompt, custom_key=custom_api_key, system_instruction=sys_inst, model_name=model_choice)
                
                if error:
                    st.error(error)
                else:
                    st.success("Job Description Generated Successfully!")
                    st.markdown(result)
                    st.download_button(
                        label="📥 Download JD (.txt)",
                        data=result,
                        file_name=f"Job_Description_{role_input.replace(' ', '_')}.txt",
                        mime="text/plain"
                    )

# -------------------------------------------------------------
# TAB 2: RESUME SCREENER
# -------------------------------------------------------------
with tab_screener:
    st.subheader("Screen Candidate Resume against Requirements")
    
    job_reqs = st.text_area(
        "Job Requirements / Role Description",
        placeholder="Paste job requirements here...",
        height=150,
        key="screen_reqs"
    )
    
    st.write("**Candidate Resume Source:**")
    upload_option = st.radio("Choose input method:", ["Paste Resume Text", "Upload PDF Resume"], horizontal=True, key="screen_source")
    
    resume_text = ""
    if upload_option == "Paste Resume Text":
        resume_text = st.text_area("Paste Candidate Resume", placeholder="Paste resume text here...", height=200, key="screen_text")
    else:
        uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"], key="screen_pdf")
        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            extracted, pdf_err = extract_pdf_text(file_bytes)
            if pdf_err:
                st.error(pdf_err)
            else:
                resume_text = extracted
                st.success(f"Extracted {len(resume_text)} characters from '{uploaded_file.name}'!")
                with st.expander("Preview Extracted Text"):
                    st.write(resume_text[:1000] + ("..." if len(resume_text) > 1000 else ""))

    screen_btn = st.button("📊 Evaluate Candidate Match", type="primary", key="btn_screen")
    
    if screen_btn:
        if not job_reqs.strip():
            st.error("Please provide Job Requirements.")
        elif not resume_text.strip():
            st.error("Please provide Candidate Resume text or upload a valid PDF.")
        else:
            with st.spinner("Screening Resume & Calculating Match Score..."):
                prompt = (
                    f"JOB REQUIREMENTS:\n{job_reqs}\n\n"
                    f"CANDIDATE RESUME:\n{resume_text}\n\n"
                    "Please evaluate the candidate match against the requirements in the following structured format:\n"
                    "MATCH SCORE: [X/10]\n"
                    "SUMMARY: [Brief candidate snapshot]\n"
                    "STRENGTHS:\n- [Point 1]\n- [Point 2]\n"
                    "GAPS / AREAS FOR IMPROVEMENT:\n- [Point 1]\n- [Point 2]\n"
                    "RECOMMENDATION: [Proceed to Interview / Request Clarification / Reject]"
                )
                sys_inst = "You are a Senior Technical Recruiter evaluating candidate fit objectively against job criteria."
                
                result, error = generate_response(prompt, custom_key=custom_api_key, system_instruction=sys_inst, model_name=model_choice)
                
                if error:
                    st.error(error)
                else:
                    st.success("Candidate Evaluation Complete!")
                    st.markdown(result)

# -------------------------------------------------------------
# TAB 3: INTERVIEW QUESTION GENERATOR
# -------------------------------------------------------------
with tab_questions:
    st.subheader("Generate Tailored Technical & Behavioral Questions")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        q_role = st.text_input("Target Role", placeholder="e.g. Senior Data Scientist", key="q_role")
        q_level = st.selectbox("Seniority Level", ["Junior", "Mid-Level", "Senior", "Lead / Principal", "Engineering Manager"], key="q_level")
        q_btn = st.button("🎯 Generate Questions", type="primary", key="btn_q")
    with col2:
        st.info("💡 **Prompt Tip**: Generates 3 technical deep-dive questions and 2 behavioral/situational questions with answer evaluation tips.")
        
    if q_btn:
        if not q_role.strip():
            st.error("Please enter a target role.")
        else:
            with st.spinner("Generating Interview Questions..."):
                prompt = (
                    f"Generate 5 interview questions for a {q_level} {q_role}.\n"
                    "Include 3 Technical Deep-Dive questions and 2 Behavioral / Situational questions.\n"
                    "For each question, provide a short guidance tip on what a strong answer looks like."
                )
                sys_inst = "You are a lead technical interviewer."
                
                result, error = generate_response(prompt, custom_key=custom_api_key, system_instruction=sys_inst, model_name=model_choice)
                
                if error:
                    st.error(error)
                else:
                    st.success("Interview Questions Generated!")
                    st.markdown(result)

# -------------------------------------------------------------
# TAB 4: PRESET QUICK TESTS
# -------------------------------------------------------------
with tab_presets:
    st.subheader("⚡ 1-Click Test Presets")
    st.write("Click any preset below to quickly test Gemini AI responses.")
    
    preset_cols = st.columns(3)
    
    with preset_cols[0]:
        if st.button("📦 Preset 1: Full-Stack Engineer JD"):
            with st.spinner("Generating Full-Stack Engineer JD..."):
                prompt = "Write a detailed job description for a Senior Full-Stack Engineer (React, Node.js, Python, PostgreSQL)."
                res, err = generate_response(prompt, custom_key=custom_api_key, model_name=model_choice)
                if err:
                    st.error(err)
                else:
                    st.markdown(res)
                    
    with preset_cols[1]:
        if st.button("📊 Preset 2: Sample Resume Screening"):
            with st.spinner("Evaluating Sample Resume..."):
                sample_req = "5+ years experience in Python, PyTorch, LLMs, Vector Databases (Pinecone/Qdrant), Docker, microservices."
                sample_res = "Software Engineer with 6 years experience. Expert in Python, PyTorch, LangChain, Pinecone vector store, FastAPI, and Docker deployments."
                prompt = f"JOB REQ:\n{sample_req}\n\nRESUME:\n{sample_res}\n\nProvide MATCH SCORE (X/10), Strengths, Gaps, and Recommendation."
                res, err = generate_response(prompt, custom_key=custom_api_key, model_name=model_choice)
                if err:
                    st.error(err)
                else:
                    st.markdown(res)

    with preset_cols[2]:
        if st.button("❓ Preset 3: DevOps Interview Questions"):
            with st.spinner("Generating DevOps Questions..."):
                prompt = "Generate 5 technical and behavioral interview questions for a Senior DevOps Engineer specializing in Kubernetes and Terraform."
                res, err = generate_response(prompt, custom_key=custom_api_key, model_name=model_choice)
                if err:
                    st.error(err)
                else:
                    st.markdown(res)
