# redesign.py — HirangAI design system replacement
# Run: python redesign.py
import re, ast

with open("app.py", encoding="utf-8") as f:
    src = f.read()

original = src

# ── 1. Replace the CSS block ──────────────────────────────────────────────────
NEW_CSS = """\
st.markdown(
    \"\"\"
    <style>
    /* Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Global */
    html, body, [class*="css"] { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    .stApp { background: #09090d; min-height: 100vh; }
    #MainMenu, footer { visibility: hidden; }
    header { visibility: hidden; }
    .main .block-container { padding-top: 68px !important; }

    /* Sticky nav */
    .hirang-nav {
        position: fixed; top: 0; left: 0; right: 0; z-index: 9999;
        height: 48px; background: rgba(9,9,13,0.97);
        border-bottom: 1px solid rgba(255,255,255,0.07);
        padding: 0 24px; display: flex; align-items: center;
        justify-content: space-between;
    }
    .hirang-nav-brand { font-size: 0.95rem; font-weight: 700; color: #f1f5f9; letter-spacing: -0.3px; }
    .hirang-nav-links { display: flex; gap: 4px; }
    .hirang-nav-links a {
        color: #64748b; text-decoration: none; font-size: 0.8rem; font-weight: 500;
        padding: 5px 10px; border-radius: 5px; transition: color 0.12s, background 0.12s;
    }
    .hirang-nav-links a:hover { color: #f1f5f9; background: rgba(255,255,255,0.05); }

    /* Section anchor helper */
    .section-anchor { display: block; height: 56px; margin-top: -56px; visibility: hidden; }

    /* Page header wordmark */
    .page-header { display: flex; align-items: baseline; gap: 14px; padding-bottom: 20px; margin-bottom: 28px; border-bottom: 1px solid rgba(255,255,255,0.07); }
    .page-header-brand  { font-size: 1.4rem; font-weight: 700; color: #f1f5f9; letter-spacing: -0.5px; }
    .page-header-tagline { font-size: 0.8rem; color: #475569; }

    /* Section heading */
    .section-heading {
        font-size: 0.68rem; font-weight: 600; letter-spacing: 1.5px;
        text-transform: uppercase; color: #4f46e5;
        margin: 28px 0 12px; padding-bottom: 8px;
        border-bottom: 1px solid rgba(79,70,229,0.15);
    }

    /* Cards */
    .glass-card, .card {
        background: #111118; border: 1px solid rgba(255,255,255,0.07);
        border-radius: 8px; padding: 20px; margin-bottom: 12px;
        transition: border-color 0.15s;
    }
    .glass-card:hover, .card:hover { border-color: rgba(79,70,229,0.2); }
    .card-label { font-size: 0.67rem; font-weight: 600; letter-spacing: 1.2px; text-transform: uppercase; color: #4f46e5; margin-bottom: 4px; }
    .card-title { font-size: 0.95rem; font-weight: 600; color: #f1f5f9; margin-bottom: 4px; }
    .card-desc  { font-size: 0.8rem; color: #64748b; line-height: 1.5; margin-bottom: 14px; }

    /* Info boxes */
    .info-box    { background: rgba(79,70,229,0.05); border: 1px solid rgba(79,70,229,0.15); border-left: 2px solid #4f46e5; border-radius: 6px; padding: 10px 14px; color: #a5b4fc; font-size: 0.82rem; margin-top: 8px; line-height: 1.5; }
    .success-box { background: rgba(5,150,105,0.05); border: 1px solid rgba(5,150,105,0.18); border-left: 2px solid #059669; border-radius: 6px; padding: 10px 14px; color: #6ee7b7; font-size: 0.82rem; margin-top: 8px; }
    .warning-box { background: rgba(217,119,6,0.05); border: 1px solid rgba(217,119,6,0.18); border-left: 2px solid #d97706; border-radius: 6px; padding: 10px 14px; color: #fcd34d; font-size: 0.82rem; margin-top: 8px; }

    /* Divider */
    hr { border: none; border-top: 1px solid rgba(255,255,255,0.06) !important; margin: 20px 0 !important; }

    /* Sidebar */
    [data-testid="stSidebar"] { background: #0d0d14 !important; border-right: 1px solid rgba(255,255,255,0.06) !important; }
    [data-testid="stSidebar"] .block-container { padding-top: 56px !important; }
    .sidebar-logo    { font-size: 1.05rem; font-weight: 700; color: #f1f5f9; margin-bottom: 2px; }
    .sidebar-tagline { font-size: 0.72rem; color: #475569; margin-bottom: 20px; }
    .sidebar-stat { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 6px; padding: 10px 14px; margin-bottom: 8px; }
    .sidebar-stat-label { font-size: 0.67rem; color: #64748b; font-weight: 500; letter-spacing: 0.5px; text-transform: uppercase; }
    .sidebar-stat-value { font-size: 1.25rem; font-weight: 700; color: #f1f5f9; margin-top: 2px; }

    /* Widgets */
    .stTextArea > div > div > textarea {
        background: #111118 !important; border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 6px !important; color: #f1f5f9 !important;
        font-family: 'Inter', sans-serif !important; font-size: 0.875rem !important;
        resize: vertical; transition: border-color 0.15s !important;
    }
    .stTextArea > div > div > textarea:focus {
        border-color: rgba(79,70,229,0.5) !important;
        box-shadow: 0 0 0 2px rgba(79,70,229,0.08) !important;
    }
    .stFileUploader { background: rgba(17,17,24,0.8) !important; border: 1px dashed rgba(255,255,255,0.1) !important; border-radius: 6px !important; }
    .stFileUploader:hover { border-color: rgba(79,70,229,0.35) !important; }
    .stButton > button {
        background: #4f46e5 !important; border: none !important; border-radius: 6px !important;
        color: #fff !important; font-family: 'Inter', sans-serif !important;
        font-size: 0.875rem !important; font-weight: 600 !important; padding: 10px 20px !important;
        transition: background 0.15s !important; box-shadow: none !important;
    }
    .stButton > button:hover { background: #4338ca !important; transform: none !important; box-shadow: none !important; }
    label, .stFileUploader label { color: #64748b !important; font-size: 0.82rem !important; font-weight: 500 !important; }

    /* Score bars */
    @keyframes bar-grow { from { width: 0%; } to { width: var(--bar-w); } }
    .cat-bar-track { background: rgba(255,255,255,0.05); border-radius: 3px; height: 6px; overflow: hidden; flex: 1; }
    .cat-bar-fill  { height: 100%; border-radius: 3px; animation: bar-grow 0.5s ease-out forwards; width: var(--bar-w); }

    /* ATS */
    .ats-chip { display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 500; margin: 2px 2px 2px 0; white-space: nowrap; }
    .ats-chip-match { background: rgba(5,150,105,0.08); border: 1px solid rgba(5,150,105,0.22); color: #34d399; }
    .ats-chip-miss  { background: rgba(217,119,6,0.07);  border: 1px solid rgba(217,119,6,0.2);  color: #fbbf24; }
    .ats-section-row { display: flex; align-items: center; gap: 8px; padding: 5px 0; font-size: 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.04); }
    .ats-section-ok   { color: #34d399; }
    .ats-section-miss { color: #fbbf24; }
    .ats-sub-label { font-size: 0.72rem; font-weight: 600; color: #64748b; margin-bottom: 4px; }
    .ats-bar-track { background: rgba(255,255,255,0.05); border-radius: 3px; height: 5px; overflow: hidden; flex: 1; }
    .ats-bar-fill  { height: 100%; border-radius: 3px; animation: bar-grow 0.5s ease-out forwards; width: var(--bar-w); background: #0891b2; }

    /* Status badges */
    .status-badge { display: inline-flex; align-items: center; gap: 3px; padding: 2px 7px; border-radius: 4px; font-size: 0.65rem; font-weight: 600; white-space: nowrap; vertical-align: middle; }
    .status-shortlisted { background: rgba(5,150,105,0.08); border: 1px solid rgba(5,150,105,0.25); color: #34d399; }
    .status-hold        { background: rgba(217,119,6,0.08); border: 1px solid rgba(217,119,6,0.25); color: #fbbf24; }
    .status-rejected    { background: rgba(220,38,38,0.08); border: 1px solid rgba(220,38,38,0.25); color: #f87171; }
    .status-new         { background: rgba(100,116,139,0.06); border: 1px solid rgba(100,116,139,0.18); color: #64748b; }

    /* Pipeline stat card */
    .pipeline-stat-card { background: #111118; border: 1px solid rgba(255,255,255,0.07); border-radius: 8px; padding: 16px 18px; text-align: center; }
    .pipeline-stat-num  { font-size: 1.75rem; font-weight: 700; line-height: 1; }
    .pipeline-stat-lbl  { font-size: 0.65rem; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: #64748b; margin-top: 4px; }

    /* Interview rec */
    .interview-rec-strip { display: flex; align-items: center; gap: 12px; border-radius: 6px; padding: 10px 14px; margin-bottom: 12px; }

    /* Shortlist card */
    .shortlist-cand-card { background: rgba(5,150,105,0.04); border: 1px solid rgba(5,150,105,0.12); border-left: 2px solid #059669; border-radius: 6px; padding: 10px 14px; margin-bottom: 6px; }

    /* Weight badges */
    .weight-total-ok  { display: flex; justify-content: space-between; align-items: center; background: rgba(5,150,105,0.05); border: 1px solid rgba(5,150,105,0.2); border-radius: 6px; padding: 8px 14px; margin: 10px 0 8px; }
    .weight-total-err { display: flex; justify-content: space-between; align-items: center; background: rgba(220,38,38,0.05); border: 1px solid rgba(220,38,38,0.2); border-radius: 6px; padding: 8px 14px; margin: 10px 0 8px; }
    .weight-total-label     { font-size: 0.7rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }
    .weight-total-value-ok  { font-size: 0.88rem; font-weight: 700; color: #34d399; }
    .weight-total-value-err { font-size: 0.88rem; font-weight: 700; color: #f87171; }

    /* Getting Started workflow */
    .workflow-card { background: #111118; border: 1px solid rgba(255,255,255,0.07); border-radius: 8px; padding: 16px; text-align: center; }
    .workflow-step-num   { font-size: 0.65rem; font-weight: 700; color: #4f46e5; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 6px; }
    .workflow-step-label { font-size: 0.82rem; font-weight: 500; color: #94a3b8; line-height: 1.4; }

    /* Overview cards */
    .top-candidate-card { background: #111118; border: 1px solid rgba(79,70,229,0.18); border-radius: 8px; padding: 22px; }
    .overview-metric     { background: #111118; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 14px 16px; text-align: center; }
    .overview-metric-num { font-size: 1.6rem; font-weight: 700; line-height: 1; }
    .overview-metric-lbl { font-size: 0.65rem; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; color: #64748b; margin-top: 4px; }
    </style>
    \"\"\",
    unsafe_allow_html=True,
)"""

# Find and replace the CSS block
css_pat = re.compile(
    r'st\.markdown\(\s*"""[\s\S]*?<style>[\s\S]*?</style>[\s\S]*?""",\s*\n\s*unsafe_allow_html=True,\s*\n\)',
    re.DOTALL
)
src, n = css_pat.subn(NEW_CSS, src, count=1)
print(f"CSS block: {n} replaced")

# ── 2. page config icon ────────────────────────────────────────────────────────
src = src.replace('page_icon="\\U0001f50d"', 'page_icon="H"', 1)
src = src.replace('page_icon="\\U0001F50D"', 'page_icon="H"', 1)
# Try literal glyph too
for icon in ['\U0001f50d', '\U0001F50D']:
    src = src.replace(f'page_icon="{icon}"', 'page_icon="H"', 1)

# ── 3. Inject nav bar right before sidebar block ───────────────────────────────
NAV = (
    '\n# Nav bar\n'
    'st.markdown(\n'
    '    """\n'
    '    <div class="hirang-nav">\n'
    '        <span class="hirang-nav-brand">HirangAI</span>\n'
    '        <div class="hirang-nav-links">\n'
    '            <a href="#overview">Overview</a>\n'
    '            <a href="#leaderboard">Leaderboard</a>\n'
    '            <a href="#evaluations">Evaluations</a>\n'
    '            <a href="#comparison">Comparison</a>\n'
    '            <a href="#export">Export</a>\n'
    '        </div>\n'
    '    </div>\n'
    '    """,\n'
    '    unsafe_allow_html=True,\n'
    ')\n\n'
)
src = src.replace('\nwith st.sidebar:\n', NAV + '\nwith st.sidebar:\n', 1)
print("Nav bar injected")

# ── 4. Simplify sidebar: remove session stats + how-it-works blurb ─────────────
# Replace from sidebar-logo to HR Configuration Panel heading (exclusive)
old_sb_top = (
    '    st.markdown(\'<div class="sidebar-logo">'
)
# We know the sidebar starts with the logo and then session stats,
# then "How It Works", then HR Configuration
# Strategy: find the exact block to remove

# Remove "Session Stats" section and "How It Works" section
sb_remove = re.compile(
    r'    st\.markdown\(\'<div class="section-heading">Session Stats</div>\', unsafe_allow_html=True,\s*\).*?'
    r'    # \u2500\u2500 HR Configuration Panel',
    re.DOTALL
)
sb_match = sb_remove.search(src)
if sb_match:
    src = sb_remove.sub(
        '    st.markdown(\'<div class="section-heading">Session</div>\', unsafe_allow_html=True)\n'
        '    st.markdown(\n'
        '        f"""\n'
        '        <div class="sidebar-stat">\n'
        '            <div class="sidebar-stat-label">Resumes Analysed</div>\n'
        '            <div class="sidebar-stat-value">{st.session_state.analysis_count}</div>\n'
        '        </div>\n'
        '        """,\n'
        '        unsafe_allow_html=True,\n'
        '    )\n\n'
        '    # \u2500\u2500 HR Configuration Panel',
        src, count=1
    )
    print("Sidebar stats simplified")
else:
    print("WARN: sidebar stats pattern not found")

# Fix sidebar logo (remove emoji if present)
src = src.replace(
    'st.markdown(\'<div class="sidebar-logo">\U0001f50d HirangAI</div>\'',
    'st.markdown(\'<div class="sidebar-logo">HirangAI</div>\''
)
src = src.replace(
    'st.markdown(\'<div class="sidebar-tagline">AI-Powered Resume Screening</div>\'',
    'st.markdown(\'<div class="sidebar-tagline">Choose Better. Hire Smarter.</div>\''
)

# ── 5. Replace hero banner with clean page header + Getting Started ────────────
hero_pat = re.compile(
    r'# \u2500+ Hero banner[\s\S]*?# \u2500+\n\nst\.markdown\(\s*"""[\s\S]*?</div>\s*""",\s*unsafe_allow_html=True,\s*\)\n',
    re.DOTALL
)
NEW_HERO = (
    '# Page header\n'
    '# ' + '\u2500'*77 + '\n\n'
    'st.markdown(\n'
    '    """\n'
    '    <div class="page-header" id="top">\n'
    '        <span class="page-header-brand">HirangAI</span>\n'
    '        <span class="page-header-tagline">Choose Better. Hire Smarter.</span>\n'
    '    </div>\n'
    '    """,\n'
    '    unsafe_allow_html=True,\n'
    ')\n\n'
    'if not st.session_state.get("batch_results"):\n'
    '    st.markdown(\'<div class="section-heading">Getting Started</div>\', unsafe_allow_html=True)\n'
    '    _gs_cols = st.columns(5, gap="small")\n'
    '    _gs_steps = [\n'
    '        ("Step 1", "Paste Job Description"),\n'
    '        ("Step 2", "Upload Candidate Resumes"),\n'
    '        ("Step 3", "Select Evaluation Profile"),\n'
    '        ("Step 4", "Analyze Candidates"),\n'
    '        ("Step 5", "Review Rankings and Recommendations"),\n'
    '    ]\n'
    '    for _gsc, (_gsn, _gsl) in zip(_gs_cols, _gs_steps):\n'
    '        _gsc.markdown(\n'
    '            f\'<div class="workflow-card">\'\n'
    '            f\'<div class="workflow-step-num">{_gsn}</div>\'\n'
    '            f\'<div class="workflow-step-label">{_gsl}</div></div>\',\n'
    '            unsafe_allow_html=True,\n'
    '        )\n'
    '    st.markdown("<br>", unsafe_allow_html=True)\n\n'
)
src, n = hero_pat.subn(NEW_HERO, src, count=1)
print(f"Hero banner: {n} replaced")

# ── 6. Remove emoji from card titles ─────────────────────────────────────────
src = src.replace(
    '<div class="card-title">\U0001f4cb Job Description</div>',
    '<div class="card-title">Job Description</div>'
)
src = src.replace(
    '<div class="card-title">\U0001f4c4 Upload Resumes</div>',
    '<div class="card-title">Upload Resumes</div>'
)

# ── 7. HR Config heading (remove emoji) ──────────────────────────────────────
src = src.replace(
    "'\u003cdiv class=\"section-heading\"\u003e\u2699\ufe0f HR Configuration\u003c/div\u003e'",
    "'\u003cdiv class=\"section-heading\"\u003eSettings\u003c/div\u003e'"
)
# Try different quote styles
src = src.replace(
    'section-heading">\u2699\ufe0f HR Configuration',
    'section-heading">Settings'
)
src = src.replace(
    'section-heading">⚙️ HR Configuration',
    'section-heading">Settings'
)

# ── 8. Section anchors ────────────────────────────────────────────────────────
anchor = lambda name: f'    st.markdown(\'<span class="section-anchor" id="{name}"></span>\', unsafe_allow_html=True)\n\n'

REPLACEMENTS = [
    ('    # \u2500\u2500 Pipeline Overview', anchor("overview") + '    # \u2500\u2500 Pipeline Overview'),
    ('    # \u2500\u2500 Candidate Leaderboard', anchor("leaderboard") + '    # \u2500\u2500 Candidate Leaderboard'),
    ('    # \u2500\u2500 Individual evaluation reports', anchor("evaluations") + '    # \u2500\u2500 Individual evaluation reports'),
]
for old, new in REPLACEMENTS:
    if old in src:
        src = src.replace(old, new, 1)
        print(f"Anchor added: {old[:40]}")
    else:
        print(f"WARN: not found: {old[:40]}")

# Comparison and export anchors (outside the if-block, at module level)
for marker, anchor_id in [
    ('# CANDIDATE COMPARISON DASHBOARD', 'comparison'),
    ('# RANKINGS EXPORT', 'export'),
]:
    anchor_html = f'st.markdown(\'<span class="section-anchor" id="{anchor_id}"></span>\', unsafe_allow_html=True)\n\n'
    if marker in src:
        src = src.replace(marker, anchor_html + marker, 1)
        print(f"Anchor added: #{anchor_id}")

# ── 9. Verify syntax ──────────────────────────────────────────────────────────
try:
    ast.parse(src)
    print("Syntax: OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(src)

print(f"Done. Lines: {src.count(chr(10)):,}")
