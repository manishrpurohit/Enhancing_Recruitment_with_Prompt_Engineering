import os
from dotenv import load_dotenv

# Load environment variables unconditionally
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path, override=True)

from flask import Flask, render_template, request, jsonify

# Try importing CORS gracefully
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False

# Try importing Google GenAI SDK gracefully
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

# Try importing PDF parsing & OCR libraries gracefully
try:
    import pymupdf as fitz
    FITZ_AVAILABLE = True
except ImportError:
    try:
        import fitz
        FITZ_AVAILABLE = True
    except ImportError:
        FITZ_AVAILABLE = False

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

app = Flask(__name__)
if CORS_AVAILABLE:
    CORS(app)


# Helper function to initialize Google Gemini client
def get_gemini_client(custom_key=None):
    if not GENAI_AVAILABLE:
        return None, "Google GenAI library is missing. Please run: pip install google-genai"
    
    api_key = custom_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None, "Google Gemini API key is missing. Please set GOOGLE_API_KEY in environment or UI settings."
    
    try:
        client = genai.Client(api_key=api_key)
        return client, None
    except Exception as e:
        return None, str(e)


# Helper function to generate content from Gemini
def generate_gemini_response(prompt, custom_key=None, system_instruction=None, model_name=None):
    client, error = get_gemini_client(custom_key)
    if error:
        return None, error

    selected_model = model_name or os.getenv("DEFAULT_MODEL", "gemini-3.6-flash")

    try:
        config = {}
        if system_instruction:
            config["system_instruction"] = system_instruction
        
        response = client.models.generate_content(
            model=selected_model,
            contents=prompt,
            config=config if config else None
        )
        return response.text, None
    except Exception as e:
        return None, f"Google Gemini API Error: {str(e)}"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health_check():
    api_key_set = bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))
    return jsonify({
        "status": "healthy",
        "api_key_configured": api_key_set,
        "provider": "Google Gemini AI",
        "ocr_available": OCR_AVAILABLE,
        "genai_available": GENAI_AVAILABLE
    })


@app.route("/api/generate-jd", methods=["POST"])
def generate_jd():
    data = request.get_json() or {}
    role = data.get("role", "").strip()
    company_type = data.get("company_type", "tech company").strip()
    custom_key = data.get("api_key", "").strip()

    if not role:
        return jsonify({"error": "Role title is required."}), 400

    prompt = f"Write a detailed, structured job description for the role of {role} in a {company_type}. Include Sections: Role Overview, Key Responsibilities, Required Qualifications, Nice-to-Haves, and Key Deliverables."
    system_instruction = "You are an expert HR Talent Acquisition Specialist and Technical Writer."

    result, error = generate_gemini_response(prompt, custom_key=custom_key, system_instruction=system_instruction)
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"result": result, "role": role})


@app.route("/api/screen-resume", methods=["POST"])
def screen_resume():
    data = request.get_json() or {}
    resume_text = data.get("resume_text", "").strip()
    job_requirements = data.get("job_requirements", "").strip()
    custom_key = data.get("api_key", "").strip()

    if not resume_text:
        return jsonify({"error": "Resume text is required."}), 400
    if not job_requirements:
        return jsonify({"error": "Job requirements are required."}), 400

    prompt = (
        f"JOB REQUIREMENTS:\n{job_requirements}\n\n"
        f"CANDIDATE RESUME:\n{resume_text}\n\n"
        "Please evaluate the candidate match against the requirements in the following structured format:\n"
        "MATCH SCORE: [X/10]\n"
        "SUMMARY: [Brief candidate snapshot]\n"
        "STRENGTHS:\n- [Point 1]\n- [Point 2]\n"
        "GAPS / AREAS FOR IMPROVEMENT:\n- [Point 1]\n- [Point 2]\n"
        "RECOMMENDATION: [Proceed to Interview / Request Clarification / Reject]"
    )
    system_instruction = "You are a Senior Technical Recruiter evaluating candidate fit objectively against job criteria."

    result, error = generate_gemini_response(prompt, custom_key=custom_key, system_instruction=system_instruction)
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"result": result})


@app.route("/api/generate-questions", methods=["POST"])
def generate_questions():
    data = request.get_json() or {}
    role = data.get("role", "").strip()
    experience_level = data.get("experience_level", "Mid-Senior").strip()
    custom_key = data.get("api_key", "").strip()

    if not role:
        return jsonify({"error": "Role is required."}), 400

    prompt = (
        f"Generate 5 interview questions for a {experience_level} {role}.\n"
        "Include 3 Technical Deep-Dive questions and 2 Behavioral / Situational questions.\n"
        "For each question, provide a short guidance tip on what a strong answer looks like."
    )
    system_instruction = "You are a lead technical interviewer."

    result, error = generate_gemini_response(prompt, custom_key=custom_key, system_instruction=system_instruction)
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"result": result, "role": role})


@app.route("/api/parse-pdf", methods=["POST"])
def parse_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "File must be a PDF."}), 400

    if not FITZ_AVAILABLE:
        return jsonify({"error": "PyMuPDF (fitz) is not installed on the server. Please run: pip install PyMuPDF"}), 500

    try:
        file_bytes = file.read()
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        extracted_text = ""
        used_ocr = False

        for page in doc:
            page_text = page.get_text()
            if not page_text.strip() and OCR_AVAILABLE:
                try:
                    pix = page.get_pixmap(dpi=200)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    page_text = pytesseract.image_to_string(img)
                    used_ocr = True
                except Exception:
                    pass
            extracted_text += page_text + "\n"

        extracted_text = extracted_text.strip()
        if not extracted_text:
            return jsonify({"error": "Could not extract readable text from PDF."}), 400

        return jsonify({
            "filename": file.filename,
            "text": extracted_text,
            "char_count": len(extracted_text),
            "used_ocr": used_ocr
        })
    except Exception as e:
        return jsonify({"error": f"Failed to parse PDF: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
