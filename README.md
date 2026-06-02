# HirangAI

A resume screening and candidate evaluation tool built with Python and Streamlit, using the Groq API for AI-assisted candidate assessments.

---

## Project Overview

Reviewing resumes manually is time-consuming, especially when a single job posting attracts dozens or even hundreds of applicants. Hiring teams often have to read through each PDF individually, compare candidates inconsistently, and track everything in separate spreadsheets — all before even conducting a single interview.

HirangAI was built to address this problem. The system allows recruiters to upload multiple PDF resumes at once, automatically parse each one for contact information, score them against a job description using keyword-based ATS (Applicant Tracking System) criteria, and then request an AI-generated evaluation from the Groq API. Candidates are ranked based on a combined score and can be marked as shortlisted, on hold, or rejected. The final shortlist can be exported as an Excel file.

The goal was not to automate hiring decisions, but to reduce the manual overhead of initial screening so recruiters can spend more time on the candidates who actually matter.

---

##  Features

- Upload multiple PDF resumes in a single session
- Extract candidate name, email, and phone number from each resume using regex heuristics
- Score each resume against a job description using ATS keyword matching, experience range detection, and education alignment
- Generate per-candidate AI evaluations (strengths, experience summary, skill gaps, and a fit recommendation) using the Groq API with Llama 3.3 70B
- Adjust scoring weights between ATS score and AI fit score using interactive sliders
- Select from predefined job role templates (e.g., Software Engineer, Data Analyst) to pre-fill job description fields
- View candidates in a ranked table and assign review statuses (Shortlisted, On Hold, Rejected)
- Export the ranked shortlist to an Excel file with contact details and scores

---

##  Technologies Used

| Technology | Purpose |
| :--- | :--- |
| Python 3.11+ | Core programming language |
| Streamlit | Web interface and session state management |
| Groq API | AI inference for candidate evaluations |
| Llama 3.3 70B | Language model used via Groq |
| pdfplumber | PDF text extraction |
| openpyxl | Excel file generation |
| python-dotenv | Loading environment variables from `.env` |
| `re` (standard library) | Regex-based contact info extraction and experience parsing |
| Git / GitHub | Version control |

---

## System Architecture

### Module Descriptions

**`app.py`** is the main entry point and handles everything related to the user interface. It manages Streamlit session state, renders the upload panel, job description form, scoring weight sliders, candidate tabs, rankings table, and the export button. Most of the application flow — from uploading files to displaying results — is coordinated here.

**`resume_parser.py`** is responsible for reading uploaded PDF files and extracting usable text. It uses `pdfplumber` to open each file page by page and concatenates the extracted text. After extraction, it runs a set of regex patterns to detect the candidate's email address, phone number, and a best-guess candidate name based on the first short line of text in the document. Detected section headers (e.g., Experience, Education, Skills) are also identified and stored.

**`ats_scorer.py`** scores each parsed resume against the recruiter's job description. It checks for the presence of required and preferred keywords, estimates years of experience by detecting date ranges in the resume text, checks whether the candidate's listed education matches the required degree level, and measures how complete the resume appears to be (i.e., whether common sections are present). These checks are combined into a 0–100 ATS score.

**`candidate_evaluator.py`** handles all communication with the Groq API. It takes the parsed resume text and the job description, calls the appropriate prompt from `prompts.py`, sends the request to Groq, and parses the structured response. It also handles rate limit errors (HTTP 429) with retry logic and extracts the numeric scores and text fields from the model's markdown output.

**`prompts.py`** contains the prompt templates used when calling the Groq API. The prompts instruct the model to evaluate a candidate's fit for a given role, output strengths, flag experience gaps, and return a structured score block that the evaluator can parse.

### Architecture Flow

```
User uploads PDFs + enters Job Description
              │
              ▼
      resume_parser.py
  (text extraction + contact heuristics)
              │
     ┌────────┴─────────┐
     ▼                  ▼
ats_scorer.py     candidate_evaluator.py
(keyword/ATS        (Groq API call via
 scoring)            prompts.py)
     │                  │
     └────────┬─────────┘
              ▼
         app.py collects scores,
         renders rankings table
              │
              ▼
     Recruiter reviews & marks statuses
              │
              ▼
     Excel export via openpyxl
```

---

##  Project Structure

```
HirangAI/
├── app.py                  # Main Streamlit application
├── resume_parser.py        # PDF parsing and contact extraction
├── ats_scorer.py           # ATS keyword and scoring logic
├── candidate_evaluator.py  # Groq API integration and response parsing
├── prompts.py              # Prompt templates for the Groq LLM
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .gitignore
└── README.md
```

---

## Installation Guide

### Prerequisites

- Python 3.11 or higher
- A valid [Groq API key](https://console.groq.com/)

### Steps

**1. Clone the repository**

```bash
git clone https://github.com/your-username/HirangAI.git
cd HirangAI
```

**2. Create a virtual environment**

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Copy the example file and fill in your Groq API key:

```bash
cp .env.example .env
```

Open `.env` and set:

```env
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
```

**5. Run the application**

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`.

---

## Testing and Evaluation

The system was tested manually throughout development using a set of sample PDF resumes with varying formats and content.

- **Resume parsing** was verified by uploading PDFs with different layouts and checking whether the extracted name, email, and phone matched what was visible in the document. Edge cases like resumes without phone numbers or with unusual formatting were also tested.

- **ATS scoring** was tested by uploading resumes against a job description containing known keywords and verifying that resumes with more matching terms received higher scores. The experience and education checks were validated by using resumes with clearly stated date ranges and degree levels.

- **Candidate evaluation** was tested by submitting sample resumes through the Groq API and reviewing the structured output for consistency. The response parsing logic was tested against different model output formats to ensure the score extraction and text fields were correctly identified.

- **Ranking and review** were tested by uploading multiple resumes at once, adjusting the ATS/AI weight sliders, and confirming that the rankings table updated correctly. Review statuses (Shortlisted, On Hold, Rejected) were assigned and confirmed to persist within the session.

- **Export functionality** was tested by generating Excel files from shortlisted candidates and verifying that contact details, scores, and statuses appeared correctly in the exported spreadsheet.

Test scripts (`test_scoring.py`, `test_categories.py`) are also included in the repository for basic unit-level checks on the scoring logic.

---

## Responsible AI Considerations

HirangAI is designed as a screening support tool, not a replacement for human judgment in hiring.

The AI evaluations generated by the Groq API are based solely on the text content of each resume and the job description provided. They should be treated as a starting point for review, not as a definitive assessment of any candidate's qualifications or potential. Factors like communication skills, cultural fit, and practical experience cannot be fully captured from a resume alone.

All final hiring decisions remain the responsibility of the recruiter. The system's rankings and AI-generated scores are advisory outputs meant to help prioritize which candidates to review first, not to determine who gets hired.

Recruiters using this tool should be aware of the limitations of keyword-based scoring (which may disadvantage candidates who use different but equivalent terminology) and the general limitations of large language models in evaluating people.

---

## Future Improvements

Several features were not implemented within the scope of this project but would be reasonable next steps:

- **Database integration** — Currently, all session data is lost when the app is closed. Storing candidate records and evaluations in a database (e.g., PostgreSQL or SQLite) would make the system more practical for ongoing use.
- **User authentication** — Adding login functionality so multiple recruiters can use the system independently with separate session histories.
- **Candidate history tracking** — The ability to track a candidate across multiple job openings or evaluation sessions.
- **Interview scheduling** — Integration with a calendar API so recruiters can schedule interviews directly from the shortlist view.
- **Analytics dashboard** — Aggregate views showing hiring funnel statistics, average scores by role, and other reporting metrics.
- **Support for additional file formats** — Accepting Word documents (`.docx`) in addition to PDFs.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
