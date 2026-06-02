# HirangAI 🔍

> **Agentic AI-powered resume screening, ATS matching, and multi-candidate evaluation for modern HR recruiters.**

HirangAI is an advanced talent-acquisition agent that automates the screening, evaluation, and ranking of job applicants. By combining deterministic **ATS Compatibility Scoring** with semantic **Groq LLM-powered Candidate Evaluations**, HirangAI provides recruiters with a unified, human-in-the-loop decision dashboard to accelerate hiring pipelines from hours to seconds.

---

## 📖 Project Overview

### What is HirangAI?
In modern recruitment, hiring teams are flooded with hundreds of resume files per opening. Sifting through PDFs manually is error-prone, subjective, and extremely slow. 

**HirangAI** solves this by acting as an autonomous hiring co-pilot:
1. **Resume Ingestion & Parsing:** Extracting text and contact heuristics from uploaded PDFs.
2. **ATS Compatibility Matching:** Scoring resumes heuristically based on keyword presence, structural completeness, education matches, and experience ranges.
3. **Semantic LLM Evaluation:** Running deep candidate suitability checks using the Groq Llama-3.3 agent to output strengths, detected gaps, and professional recommendations.
4. **Human-AI Collaborative Ranking:** Ordering candidates dynamically inside a recruiter-led Streamlit dashboard where HR teams can adjust weight priorities in real-time.
5. **Shortlist and Export:** Instantly compiling and exporting ranked candidates alongside their validated contact information to professional Excel workbooks.

### Target Users
* **HR Recruiters & Headhunters:** To instantly screen and rank bulk candidate pools.
* **Hiring Managers:** To review detailed semantic reports and key skill-gap breakdowns before conducting interviews.
* **Talent Acquisition Teams:** To manage standardized assessment profiles across engineering, product, sales, and design openings.

---

## ✨ Features & Status

| Category | Feature | Status |
| :--- | :--- | :--- |
| **Ingestion** | Multiple PDF Resume Upload & Caching | ✅ Live & Stable |
| **Parsing** | Candidate Name, Email, & Phone Heuristic Extraction | ✅ Live & Stable |
| **Screening** | Deterministic ATS Scoring (0–100) | ✅ Live & Stable |
| **AI Assessment** | Groq Llama-3.3 Agent Candidate Evaluations | ✅ Live & Stable |
| **AI Insights** | Strengths, Experience Summary, and Skill Gap Analysis | ✅ Live & Stable |
| **UI Dashboard** | Glassmorphic Streamlit Tab-Based Presentation | ✅ Live & Stable |
| **Decision Flow** | recruiter Review Statuses (Shortlisted, Hold, Reject) | ✅ Live & Stable |
| **Collaboration** | Interactive Assessment Weights & Template Customization | ✅ Live & Stable |
| **Exporting** | Automated Excel Rankings Export with Contact Details | ✅ Live & Stable |

---

## 🚀 Quick Start

### 1. Clone / Navigate to the Project Folder
```bash
cd TalentLensAI
```

### 2. Create a Virtual Environment
```bash
# Initialize venv
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS / Linux)
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit your `.env` file and insert your active **Groq API Key**:
```env
# ── Groq (Required) ──────────────────────────────────────────────────────────
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
```

### 5. Launch the Application
```bash
streamlit run app.py
```
Open **http://localhost:8501** in your web browser to access the HirangAI Recruiter Dashboard.

---

## 🔑 Environment Variables

| Variable | Required | Description |
| :--- | :--- | :--- |
| `GROQ_API_KEY` | **Yes** | Your Groq API key (starts with `gsk_`) |


---

## 🛠 System Architecture & Flow

HirangAI is built as a modular, high-performance web app with clear separations of concern:

```
                  ┌──────────────────────────────┐
                  │      Streamlit Frontend      │
                  │          (app.py)            │
                  └──────────────┬───────────────┘
                                 │
         ┌───────────────────────┼────────────────────────┐
         ▼                       ▼                        ▼
┌──────────────────┐   ┌──────────────────┐    ┌────────────────────┐
│  Resume Parser   │   │   ATS Scoring    │    │  Groq LLM Engine   │
│(resume_parser.py)│   │ (ats_scorer.py)  │    │(candidate_evaluator│
└────────┬─────────┘   └────────┬─────────┘    │       .py)         │
         │                      │              └──────────┬─────────┘
         ▼                      ▼                         ▼
┌─────────────────────────────────────────────────────────┐
│              Candidate Ranking & Review                 │
│              (Interactive Recruiter Tabs)               │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│               Excel Export Module                       │
│      (openpyxl-generated rankings spreadsheet)          │
└─────────────────────────────────────────────────────────┘
```

### Module Responsibilities
* **`app.py`:** Handles the presentation layer, interactive state management (`st.session_state`), HR assessment template selector, slider logic, and table building.
* **`resume_parser.py`:** Handles lazy-loading of PDF bytes using `pdfplumber`, parsing text strings, and running heuristic regex checks to extract candidate names, phone numbers, and emails.
* **`ats_scorer.py`:** Deterministically scores candidates against the JD. Evaluates required and preferred keywords, estimates years of experience via date range extraction, checks degree alignment, and measures profile completeness.
* **`candidate_evaluator.py` & `prompts.py`:** Manages semantic evaluations. Crafts comprehensive assessment prompts, fires them to Groq's API, handles rate limit exceptions (HTTP 429), and extracts structured scoring blocks from LLM markdown.

---

## 📸 Interface Screenshots Placeholders

### 1. Main Dashboard & Candidate Upload
*Recruiters can drag-and-drop multiple resume PDFs and customize assessment template weights.*
`![Branded Ingestion Dashboard](docs/screenshots/dashboard_upload.png)` *(Placeholder)*

### 2. Candidate Rankings Leaderboard
*Interactive table showing combined recruiter scores (70% Fit + 30% ATS) and individual candidate statuses.*
`![Recruiter Leaderboard Screen](docs/screenshots/leaderboard.png)` *(Placeholder)*

### 3. AI Candidate Evaluation Tabs
*Dynamic tab-based container rendering detailed strengths, experience summaries, and missing skill-gaps.*
`![Candidate Evaluation View](docs/screenshots/candidate_evaluation.png)` *(Placeholder)*

### 4. Excel Rankings Export
*Exported Excel spreadsheet displaying color-coded scores and extracted contact emails and phone numbers.*
`![Excel Export Results](docs/screenshots/excel_export.png)` *(Placeholder)*

---

## 📄 License
MIT License — see `LICENSE` for details.
