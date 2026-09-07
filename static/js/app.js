/**
 * RECRUITAI ASSIST - FRONTEND INTERACTIVE APPLICATION LOGIC
 */

document.addEventListener('DOMContentLoaded', () => {
    checkHealthStatus();
    initTabs();
    initPresets();
    initDropzone();
    initFormHandlers();
    initSettingsModal();
});

/* ==========================================================================
   Toast Notifications
   ========================================================================== */
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let iconClass = 'fa-circle-info';
    if (type === 'success') iconClass = 'fa-circle-check';
    if (type === 'error') iconClass = 'fa-circle-exclamation';

    toast.innerHTML = `
        <i class="fa-solid ${iconClass}"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(50px)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

/* ==========================================================================
   Health Check & Status Badge
   ========================================================================== */
async function checkHealthStatus() {
    const badge = document.getElementById('api-status-badge');
    const text = badge.querySelector('.status-text');

    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        if (data.api_key_configured || getStoredApiKey()) {
            badge.classList.add('healthy');
            text.textContent = 'API Ready';
        } else {
            badge.classList.remove('healthy');
            text.textContent = 'API Key Needed';
        }
    } catch (err) {
        badge.classList.remove('healthy');
        text.textContent = 'Server Offline';
    }
}

function getStoredApiKey() {
    return sessionStorage.getItem('CUSTOM_GEMINI_KEY') || '';
}

/* ==========================================================================
   Tab Navigation
   ========================================================================== */
function initTabs() {
    const buttons = document.querySelectorAll('.tab-btn');
    const contents = document.querySelectorAll('.tab-content');

    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.getAttribute('data-tab');

            buttons.forEach(b => b.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(target).classList.add('active');
        });
    });
}

/* ==========================================================================
   Quick Preset Handlers
   ========================================================================== */
function initPresets() {
    // 1. JD Generator Presets
    document.getElementById('preset-jd-data-eng')?.addEventListener('click', () => {
        document.getElementById('jd-role').value = 'Lead Data Engineer';
        document.getElementById('jd-company').value = 'FinTech Cloud Enterprise';
    });

    document.getElementById('preset-jd-ml-eng')?.addEventListener('click', () => {
        document.getElementById('jd-role').value = 'Senior Machine Learning Engineer';
        document.getElementById('jd-company').value = 'AI Research Lab & SaaS';
    });

    document.getElementById('preset-jd-devops')?.addEventListener('click', () => {
        document.getElementById('jd-role').value = 'Principal DevOps Architect';
        document.getElementById('jd-company').value = 'E-Commerce Global Tech';
    });

    // 2. Candidate Screener Sample Preset
    document.getElementById('preset-screener-sample')?.addEventListener('click', () => {
        document.getElementById('screener-requirements').value = 
            "5+ years Python development experience, strong expertise in AWS/GCP cloud services, PyTorch or TensorFlow, Docker, Kubernetes, REST API design, and CI/CD pipelines.";
        
        document.getElementById('screener-resume-text').value = 
            "Alex Mercer - Senior Software Engineer\n" +
            "Summary: 6 years of experience building scalable backend services and AI data pipelines.\n" +
            "Skills: Python, FastAPI, Docker, Kubernetes, AWS (S3, EC2, Lambda), PyTorch, PostgreSQL, Git.\n" +
            "Experience:\n" +
            "- Senior Software Engineer at DataStream Inc (2021-Present): Built ETL pipelines processing 10TB+ daily using Python & PyTorch.\n" +
            "- Backend Engineer at CloudTech Solutions (2018-2021): Designed REST APIs and deployed microservices on AWS Kubernetes.";
        
        showToast('Loaded sample requirements & candidate resume!', 'info');
    });

    // 3. Interview Questions Presets
    document.getElementById('preset-q-ml')?.addEventListener('click', () => {
        document.getElementById('q-role').value = 'Machine Learning Specialist';
        document.getElementById('q-level').value = 'Mid-Senior Level';
    });

    document.getElementById('preset-q-cloud')?.addEventListener('click', () => {
        document.getElementById('q-role').value = 'Cloud Infrastructure Architect';
        document.getElementById('q-level').value = 'Lead / Principal Architect';
    });
}

/* ==========================================================================
   File Dropzone & PDF Parser
   ========================================================================== */
function initDropzone() {
    const dropzone = document.getElementById('pdf-dropzone');
    const fileInput = document.getElementById('pdf-file-input');
    const promptState = document.getElementById('dropzone-prompt');
    const fileInfoState = document.getElementById('dropzone-file-info');
    const fileNameDisplay = document.getElementById('file-name-display');
    const fileMetaDisplay = document.getElementById('file-meta-display');
    const btnRemove = document.getElementById('btn-remove-pdf');
    const resumeTextarea = document.getElementById('screener-resume-text');

    promptState.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleFileUpload(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(e.target.files[0]);
        }
    });

    btnRemove.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.value = '';
        promptState.style.display = 'block';
        fileInfoState.style.display = 'none';
        resumeTextarea.value = '';
    });

    async function handleFileUpload(file) {
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            showToast('Please upload a valid PDF file.', 'error');
            return;
        }

        fileNameDisplay.textContent = file.name;
        fileMetaDisplay.textContent = `${(file.size / 1024).toFixed(1)} KB - Extracting text...`;
        promptState.style.display = 'none';
        fileInfoState.style.display = 'flex';

        const formData = new FormData();
        formData.append('file', file);

        try {
            showToast('Parsing PDF resume...', 'info');
            const res = await fetch('/api/parse-pdf', {
                method: 'POST',
                body: formData
            });

            const data = await res.json();
            if (res.ok) {
                resumeTextarea.value = data.text;
                fileMetaDisplay.textContent = `${(file.size / 1024).toFixed(1)} KB - ${data.char_count} chars ${data.used_ocr ? '(OCR parsed)' : '(Text parsed)'}`;
                showToast('PDF resume extracted successfully!', 'success');
            } else {
                showToast(data.error || 'Failed to parse PDF.', 'error');
            }
        } catch (err) {
            showToast('Error uploading PDF file.', 'error');
        }
    }
}

/* ==========================================================================
   Form Handlers & API Calls
   ========================================================================== */
function initFormHandlers() {
    // 1. Job Description Form
    document.getElementById('form-jd').addEventListener('submit', async (e) => {
        e.preventDefault();
        const role = document.getElementById('jd-role').value.trim();
        const company_type = document.getElementById('jd-company').value.trim();

        const placeholder = document.getElementById('jd-placeholder');
        const loading = document.getElementById('jd-loading');
        const output = document.getElementById('jd-output');
        const actions = document.getElementById('jd-actions');

        placeholder.style.display = 'none';
        output.style.display = 'none';
        actions.style.display = 'none';
        loading.style.display = 'block';

        try {
            const res = await fetch('/api/generate-jd', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ role, company_type, api_key: getStoredApiKey() })
            });
            const data = await res.json();
            loading.style.display = 'none';

            if (res.ok) {
                output.innerHTML = typeof marked !== 'undefined' ? marked.parse(data.result) : data.result;
                output.setAttribute('data-raw-text', data.result);
                output.style.display = 'block';
                actions.style.display = 'flex';
                showToast('Job Description generated!', 'success');
            } else {
                showToast(data.error || 'Generation failed', 'error');
                placeholder.style.display = 'block';
            }
        } catch (err) {
            loading.style.display = 'none';
            showToast('Server request failed', 'error');
            placeholder.style.display = 'block';
        }
    });

    document.getElementById('btn-copy-jd').addEventListener('click', () => {
        const text = document.getElementById('jd-output').getAttribute('data-raw-text') || document.getElementById('jd-output').textContent;
        navigator.clipboard.writeText(text);
        showToast('Copied Job Description!', 'success');
    });

    document.getElementById('btn-download-jd').addEventListener('click', () => {
        const text = document.getElementById('jd-output').getAttribute('data-raw-text') || document.getElementById('jd-output').textContent;
        const role = document.getElementById('jd-role').value || 'Job_Description';
        downloadTextFile(`${role.replace(/\s+/g, '_')}_JD.txt`, text);
    });

    // 2. Candidate Screener Form
    document.getElementById('form-screener').addEventListener('submit', async (e) => {
        e.preventDefault();
        const job_requirements = document.getElementById('screener-requirements').value.trim();
        const resume_text = document.getElementById('screener-resume-text').value.trim();

        const placeholder = document.getElementById('screener-placeholder');
        const loading = document.getElementById('screener-loading');
        const output = document.getElementById('screener-output');
        const actions = document.getElementById('screener-actions');
        const scoreWidget = document.getElementById('score-gauge-widget');

        placeholder.style.display = 'none';
        output.style.display = 'none';
        actions.style.display = 'none';
        scoreWidget.style.display = 'none';
        loading.style.display = 'block';

        try {
            const res = await fetch('/api/screen-resume', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ job_requirements, resume_text, api_key: getStoredApiKey() })
            });
            const data = await res.json();
            loading.style.display = 'none';

            if (res.ok) {
                output.innerHTML = typeof marked !== 'undefined' ? marked.parse(data.result) : data.result;
                output.setAttribute('data-raw-text', data.result);
                output.style.display = 'block';
                actions.style.display = 'flex';

                // Extract & render Visual Match Score Gauge
                renderScoreGauge(data.result);
                showToast('Candidate evaluation completed!', 'success');
            } else {
                showToast(data.error || 'Evaluation failed', 'error');
                placeholder.style.display = 'block';
            }
        } catch (err) {
            loading.style.display = 'none';
            showToast('Server request failed', 'error');
            placeholder.style.display = 'block';
        }
    });

    document.getElementById('btn-copy-screener').addEventListener('click', () => {
        const text = document.getElementById('screener-output').getAttribute('data-raw-text') || document.getElementById('screener-output').textContent;
        navigator.clipboard.writeText(text);
        showToast('Copied evaluation report!', 'success');
    });

    // 3. Interview Questions Form
    document.getElementById('form-questions').addEventListener('submit', async (e) => {
        e.preventDefault();
        const role = document.getElementById('q-role').value.trim();
        const experience_level = document.getElementById('q-level').value;

        const placeholder = document.getElementById('questions-placeholder');
        const loading = document.getElementById('questions-loading');
        const output = document.getElementById('questions-output');
        const actions = document.getElementById('questions-actions');

        placeholder.style.display = 'none';
        output.style.display = 'none';
        actions.style.display = 'none';
        loading.style.display = 'block';

        try {
            const res = await fetch('/api/generate-questions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ role, experience_level, api_key: getStoredApiKey() })
            });
            const data = await res.json();
            loading.style.display = 'none';

            if (res.ok) {
                output.innerHTML = typeof marked !== 'undefined' ? marked.parse(data.result) : data.result;
                output.setAttribute('data-raw-text', data.result);
                output.style.display = 'block';
                actions.style.display = 'flex';
                showToast('Interview questions generated!', 'success');
            } else {
                showToast(data.error || 'Generation failed', 'error');
                placeholder.style.display = 'block';
            }
        } catch (err) {
            loading.style.display = 'none';
            showToast('Server request failed', 'error');
            placeholder.style.display = 'block';
        }
    });

    document.getElementById('btn-copy-questions').addEventListener('click', () => {
        const text = document.getElementById('questions-output').getAttribute('data-raw-text') || document.getElementById('questions-output').textContent;
        navigator.clipboard.writeText(text);
        showToast('Copied interview questions!', 'success');
    });
}

/* ==========================================================================
   Visual Score Gauge Extraction
   ========================================================================== */
function renderScoreGauge(text) {
    const widget = document.getElementById('score-gauge-widget');
    const numDisplay = document.getElementById('score-number-display');
    const badgeText = document.getElementById('score-badge-text');

    // Extract score pattern e.g. "MATCH SCORE: 8/10" or "8/10" or "Score: 7"
    const match = text.match(/(?:SCORE|MATCH SCORE|EVALUATION):\s*(\d+(?:\.\d+)?)\s*\/\s*10/i) || text.match(/(\d+)\s*\/\s*10/);

    if (match && match[1]) {
        const score = parseFloat(match[1]);
        numDisplay.textContent = score;

        widget.classList.remove('score-green', 'score-yellow', 'score-red');

        if (score >= 8) {
            widget.classList.add('score-green');
            badgeText.textContent = `Strong Candidate Match (${score}/10)`;
        } else if (score >= 5) {
            widget.classList.add('score-yellow');
            badgeText.textContent = `Moderate Candidate Match (${score}/10)`;
        } else {
            widget.classList.add('score-red');
            badgeText.textContent = `Low Candidate Match (${score}/10)`;
        }

        widget.style.display = 'flex';
    } else {
        widget.style.display = 'none';
    }
}

function downloadTextFile(filename, text) {
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

/* ==========================================================================
   Settings Modal (API Key)
   ========================================================================== */
function initSettingsModal() {
    const modal = document.getElementById('modal-settings');
    const btnOpen = document.getElementById('btn-settings');
    const btnClose = document.getElementById('btn-close-settings');
    const btnSave = document.getElementById('btn-save-key');
    const btnClear = document.getElementById('btn-clear-key');
    const inputKey = document.getElementById('custom-api-key');

    btnOpen.addEventListener('click', () => {
        inputKey.value = getStoredApiKey();
        modal.style.display = 'flex';
    });

    btnClose.addEventListener('click', () => modal.style.display = 'none');

    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.style.display = 'none';
    });

    btnSave.addEventListener('click', () => {
        const key = inputKey.value.trim();
        if (key) {
            sessionStorage.setItem('CUSTOM_GEMINI_KEY', key);
            showToast('Custom Gemini API Key saved for this session.', 'success');
        } else {
            sessionStorage.removeItem('CUSTOM_GEMINI_KEY');
        }
        modal.style.display = 'none';
        checkHealthStatus();
    });

    btnClear.addEventListener('click', () => {
        sessionStorage.removeItem('CUSTOM_GEMINI_KEY');
        inputKey.value = '';
        showToast('Custom Gemini API Key cleared.', 'info');
        modal.style.display = 'none';
        checkHealthStatus();
    });
}
