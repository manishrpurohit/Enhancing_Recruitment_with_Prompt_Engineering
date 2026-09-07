# Deploying to Streamlit Community Cloud

Deploying your **Enhancing Recruitment with Prompt Engineering** project to **Streamlit Community Cloud** is free, quick, and takes only a few minutes with automatic GitHub integration.

---

## 🚀 Step-by-Step Deployment Instructions

### Step 1: Push Code to GitHub
Ensure all your project files (including `streamlit_app.py`, `requirements.txt`, and `.streamlit/config.toml`) are pushed to your GitHub repository.

```bash
git add .
git commit -m "Add Streamlit application for deployment"
git push origin main
```

---

### Step 2: Connect to Streamlit Community Cloud
1. Go to **[share.streamlit.io](https://share.streamlit.io/)** and sign in with your GitHub account.
2. Click on the **"New app"** button.

---

### Step 3: Configure App Deployment
Fill in the deployment details:

- **Repository**: `YourGitHubUsername/Enhancing_Recruitment_with_Prompt_Engineering`
- **Branch**: `main` (or your default branch)
- **Main file path**: `streamlit_app.py`
- **App URL**: *(Optional)* Choose a custom sub-domain name (e.g. `recruitment-prompt-eng.streamlit.app`).

---

### Step 4: Add Google API Key Secrets (Important!)
Before clicking **Deploy**, configure your `GOOGLE_API_KEY` so the live app can access Gemini AI securely:

1. In the **New app** deployment window, click **"Advanced settings..."** (or open **App Settings -> Secrets** after creating the app).
2. Add your Google API key in TOML format:

```toml
GOOGLE_API_KEY = "AIzaSyB4acxqDrCIF2QV5x8AcuE_QKk5iwOP6bo"
DEFAULT_MODEL = "gemini-3.6-flash"
```

3. Click **Save**.

---

### Step 5: Click Deploy!
1. Click **Deploy!**
2. Streamlit Cloud will build the environment by installing packages from `requirements.txt` and launch your live app.
3. Your web app will be live at `https://<your-app-name>.streamlit.app`! 🎉

---

## 💻 Running Locally

To test your Streamlit app locally before deploying:

```bash
# Ensure virtual environment is active
.\.venv\Scripts\activate

# Launch Streamlit app
streamlit run streamlit_app.py
```

The app will open automatically in your browser at `http://localhost:8501`.
