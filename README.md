# Enhancing Recruitment with Prompt Engineering 🎯🤖

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask Web App](https://img.shields.io/badge/Flask-Web%20App-red.svg)](app.py)
[![Google Gemini API](https://img.shields.io/badge/Google-Gemini%20AI-orange.svg)](https://aistudio.google.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An end-to-end AI-powered recruitment intelligence platform featuring a **Glassmorphism Web Dashboard** and **Python Flask API** powered by **Google Gemini AI Models**. This project automates key HR workflows including job description generation, candidate resume screening (with PDF text extraction & Tesseract OCR fallback), match scoring against job requirements, and tailored interview question generation.

---

## 📌 Table of Contents

- [Overview](#overview)
- [Web Application Interface](#web-application-interface)
- [Key Features](#key-features)
- [System Architecture & Workflow](#system-architecture--workflow)
- [Project Structure](#project-structure)
- [Quick Start: Running Web App Locally](#quick-start-running-web-app-locally)
- [Deployment Options](#deployment-options)
- [Environment Configuration](#environment-configuration)
- [Prompt Engineering Strategies](#prompt-engineering-strategies)
- [License](#license)

---

## 🚀 Overview

Recruitment processes often involve time-consuming manual tasks such as drafting job specs, parsing resumes, scoring candidate fit, and structuring interview questions. This project provides both an interactive **Web Application Dashboard** and a **Jupyter Notebook pipeline** using OpenAI `gpt-4` to transform traditional hiring into an efficient, automated, and objective workflow.

---

## 🌐 Web Application Interface

The project comes with a modern single-page web dashboard (`app.py` + HTML5/CSS3/JS UI):
- **Job Spec Generator**: Input job titles to receive structured, ready-to-post specifications.
- **Candidate Resume Screener**: Drag & drop candidate PDF resumes for automatic text/OCR parsing and match scoring (1–10 scale) with detailed qualitative rationale.
- **Interview Question Synthesis**: Formulate targeted technical and situational questions.
- **API Settings Modal**: Easily enter or switch OpenAI API keys per session.

---

## ✨ Key Features

1. **Job Description Generator** 📝
   - Dynamically creates detailed, professional job descriptions tailored to target roles (e.g., Data Engineer, ML Engineer).
2. **Automated Resume Parsing (Text & OCR Fallback)** 📄
   - Extracts plain text from candidate PDF resumes using **PyMuPDF (`fitz`)**.
   - Integrates **Tesseract OCR (`pytesseract`)** fallback to read scanned, image-based, or non-selectable PDF resumes seamlessly.
3. **Resume Screening & Match Scoring** 📊
   - Evaluates candidate experience against specific Job Requirements.
   - Provides a numerical match score (1–10 scale) along with a detailed qualitative breakdown highlighting strengths, gaps, and recommendations.
4. **Tailored Interview Question Generator** ❓
   - Generates customized behavioral and technical interview questions based on role and seniority level.

---

## 💻 Quick Start: Running Web App Locally

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/Enhancing_Recruitment_with_Prompt_Engineering.git
   cd Enhancing_Recruitment_with_Prompt_Engineering
   ```

2. **Create & Activate Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and insert your OpenAI API Key:
   ```bash
   cp .env.example .env
   ```

5. **Launch Flask Web Application**:
   ```bash
   python app.py
   ```
   Open your browser and navigate to `http://localhost:5000`.

---

## ☁️ Deployment Options

Deploy this application for free on popular cloud platforms:
- **Render**: Connect your GitHub repository and deploy with Gunicorn using our included `Procfile` and `render.yaml`.
- **Hugging Face Spaces**: Deploy as a Docker or Python space.
- **Railway / Vercel**: Instant deployment via CLI or GitHub integration.

---

## 📁 Project Structure

```text
Enhancing_Recruitment_with_Prompt_Engineering/
├── app.py                                               # Flask Web Server & REST API
├── templates/
│   └── index.html                                       # Single Page Web Application UI
├── static/
│   ├── css/style.css                                    # Glassmorphism dark-theme CSS
│   └── js/app.js                                        # Frontend logic & drag-and-drop parser
├── Enhancing_Recruitment_with_Prompt_Engineering.ipynb  # Interactive Jupyter Notebook
├── README.md                                             # Main project documentation
├── Procfile                                              # WSGI production server start command
├── render.yaml                                           # Render cloud blueprint config
├── requirements.txt                                      # Python package dependencies
├── .env.example                                          # Template for environment variables
├── .gitignore                                            # Ignored files & sensitive data
└── LICENSE                                               # MIT Open Source License
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
