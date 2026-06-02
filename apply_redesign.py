# apply_redesign.py
# Programmatic redesign of HirangAI to feel like a premium SaaS recruitment platform.
import re
import ast

def main():
    print("Loading app.py...")
    with open("app.py", "r", encoding="utf-8") as f:
        src = f.read()

    print("Stage 3: Replacing CSS block...")
    # The original CSS block starts with st.markdown("""\n    <style>\n    /* ── Google Font` and ends with `unsafe_allow_html=True,\n)`
    # Let's find the boundaries of the CSS block.
    start_css = src.find('st.markdown(\n    """\n    <style>')
    if start_css == -1:
        start_css = src.find('st.markdown(\n    """\n    <style>\n    /* ── Google Font')
    
    end_css = src.find('unsafe_allow_html=True,\n)', start_css)
    if end_css != -1:
        end_css = src.find(')', end_css) + 1
        print(f"Found CSS block from index {start_css} to {end_css}")
    else:
        print("CSS block not found or unmatched boundaries")
        return

    NEW_CSS = """st.markdown(
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

    src = src[:start_css] + NEW_CSS + src[end_css:]

    print("Stage 4: Navigation Bar and page config icon...")
    src = src.replace('page_icon="🔍"', 'page_icon="H"')
    src = src.replace("page_icon='\U0001f50d'", "page_icon='H'")

    # Inject Nav Bar helper just before "with st.sidebar:"
    NAV_BAR = """
# Sticky navigation header
st.markdown(
    \"\"\"
    <div class="hirang-nav">
        <span class="hirang-nav-brand">HirangAI</span>
        <div class="hirang-nav-links">
            <a href="#overview">Overview</a>
            <a href="#leaderboard">Leaderboard</a>
            <a href="#evaluations">Evaluations</a>
            <a href="#comparison">Comparison</a>
            <a href="#export">Export</a>
        </div>
    </div>
    \"\"\",
    unsafe_allow_html=True,
)

"""
    src = src.replace("with st.sidebar:", NAV_BAR + "with st.sidebar:")

    print("Stage 9: Simplifying Sidebar...")
    # Let's extract from "with st.sidebar:" to "# ── HR Configuration Panel" and replace it
    sb_start = src.find("with st.sidebar:")
    sb_config_heading = src.find("# ── HR Configuration Panel")
    if sb_start != -1 and sb_config_heading != -1:
        # Reconstruct the top of the sidebar
        new_sb_top = """with st.sidebar:
    st.markdown('<div class="sidebar-logo">HirangAI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">Choose Better. Hire Smarter.</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div style="font-size:0.75rem;color:#64748b;margin-bottom:18px;padding-left:2px;">'
        f'Session screening: <strong>{st.session_state.analysis_count}</strong> candidates</div>',
        unsafe_allow_html=True
    )
    
    """
        src = src[:sb_start] + new_sb_top + src[sb_config_heading:]
    else:
        print("Could not find sidebar top bounds to simplify!")

    # Clean up "⚙️ HR Configuration" heading emoji in sidebar
    src = src.replace("st.markdown('<div class=\"section-heading\">⚙️ HR Configuration</div>', unsafe_allow_html=True)",
                      "st.markdown('<div class=\"section-heading\">Settings</div>', unsafe_allow_html=True)")

    print("Stage 5: Replacing Hero Banner & adding Getting Started...")
    # Find "# ── Hero banner ──" to the next "# ── Main input layout ──" or matching st.markdown
    hero_comment = src.find("# Hero banner")
    if hero_comment == -1:
        hero_comment = src.find("# \u2500\u2500 Hero banner")
    
    # We find the st.markdown following it
    hero_md = src.find("st.markdown(", hero_comment)
    hero_md_end = src.find("unsafe_allow_html=True,\n)", hero_md)
    if hero_md_end != -1:
        hero_md_end = src.find(")", hero_md_end) + 1
        
        NEW_HERO_AND_GETTING_STARTED = """st.markdown(
    \"\"\"
    <div class="page-header" id="top">
        <span class="page-header-brand">HirangAI</span>
        <span class="page-header-tagline">Choose Better. Hire Smarter.</span>
    </div>
    \"\"\",
    unsafe_allow_html=True,
)

if not st.session_state.get("batch_results"):
    st.markdown('<div class="section-heading">Getting Started</div>', unsafe_allow_html=True)
    _gs_cols = st.columns(5, gap="small")
    _gs_steps = [
        ("Step 1", "Paste Job Description"),
        ("Step 2", "Upload Resumes"),
        ("Step 3", "Select Template"),
        ("Step 4", "Analyze Candidates"),
        ("Step 5", "Review Recommendations"),
    ]
    for _gsc, (_gsn, _gsl) in zip(_gs_cols, _gs_steps):
        _gsc.markdown(
            f'<div class="workflow-card">'
            f'<div class="workflow-step-num">{_gsn}</div>'
            f'<div class="workflow-step-label">{_gsl}</div></div>',
            unsafe_allow_html=True,
        )
    st.markdown("<br>", unsafe_allow_html=True)"""
        src = src[:hero_comment] + NEW_HERO_AND_GETTING_STARTED + src[hero_md_end:]
    else:
        print("Hero banner boundaries not found!")

    # Remove emoji from main input card titles
    src = src.replace('<div class="card-title">📋 Job Description</div>', '<div class="card-title">Job Description</div>')
    src = src.replace('<div class="card-title">📄 Upload Resumes</div>', '<div class="card-title">Upload Resumes</div>')
    src = src.replace('📝 Job description loaded', 'Job description loaded')

    print("Stage 6: Overview section anchor + Top Candidate Executive Summary...")
    # Inject st.markdown('<span class="section-anchor" id="overview"></span>', unsafe_allow_html=True) before `# ── Pipeline Overview`
    src = src.replace("# ── Pipeline Overview",
                      "st.markdown('<span class=\"section-anchor\" id=\"overview\"></span>', unsafe_allow_html=True)\n\n    # ── Pipeline Overview")

    # Inside Pipeline Overview, we'll inject the Top Candidate Card and Summary Row
    # Let's locate:
    #     st.markdown('<div class="section-heading">📊 Pipeline Overview</div>', unsafe_allow_html=True)
    # We will replace it with the new premium Executive Summary row and Top Candidate Card!
    pipeline_heading_str = "st.markdown('<div class=\"section-heading\">📊 Pipeline Overview</div>', unsafe_allow_html=True)"
    pipeline_heading_idx = src.find(pipeline_heading_str)
    
    if pipeline_heading_idx != -1:
        # Let's see: we want to render the Top Candidate Card first if there's candidates!
        # Top Candidate has name, final score, recommendation, confidence, and 3-5 key strengths.
        top_cand_code = """st.markdown('<div class="section-heading">Executive Summary</div>', unsafe_allow_html=True)
    
    # Identify top candidate
    if _ranked:
        _top_entry = _ranked[0]
        _top_res = _top_entry["result"]
        _top_name = _top_res.candidate_name or _top_entry["file"].replace(".pdf", "")
        _top_score = _ranking_score(_top_entry)
        _top_rec = _interview_rec(_top_score)[0] if _top_score is not None else (_top_res.recommendation or "Recommended")
        _top_conf = _top_res.confidence_level or "High"
        
        # Get 3-5 strengths
        _top_strengths = _top_res.strengths[:4] if _top_res.strengths else ["Demonstrates solid matching qualifications for the role."]
        _strengths_li = "".join(f'<li style="margin-bottom:4px;">{s}</li>' for s in _top_strengths)
        
        _avg_score = round(sum((_ranking_score(e) or 0) for e in _ranked if not e["result"].errors) / max(1, sum(1 for e in _ranked if not e["result"].errors)))
        _highest_score = _top_score if _top_score is not None else 0
        
        _exec_col1, _exec_col2 = st.columns([0.62, 0.38], gap="medium")
        with _exec_col1:
            st.markdown(
                f'''
                <div class="top-candidate-card" style="height: 100%;">
                    <div class="card-label">Top Ranked Candidate</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: #f1f5f9; margin-bottom: 8px;">{_top_name}</div>
                    <div style="display: flex; gap: 16px; margin-bottom: 14px;">
                        <div>
                            <span style="font-size: 0.68rem; color: #64748b; text-transform: uppercase; font-weight: 600;">Match Score</span>
                            <div style="font-size: 1.5rem; font-weight: 800; color: #4f46e5;">{_top_score if _top_score is not None else 'N/A'}<span style="font-size: 0.85rem; font-weight: 500; color: #64748b;">/100</span></div>
                        </div>
                        <div>
                            <span style="font-size: 0.68rem; color: #64748b; text-transform: uppercase; font-weight: 600;">Recommendation</span>
                            <div style="font-size: 0.95rem; font-weight: 700; color: #059669; margin-top: 4px;">{_top_rec}</div>
                        </div>
                        <div>
                            <span style="font-size: 0.68rem; color: #64748b; text-transform: uppercase; font-weight: 600;">AI Confidence</span>
                            <div style="font-size: 0.95rem; font-weight: 700; color: #f1f5f9; margin-top: 4px;">{_top_conf}</div>
                        </div>
                    </div>
                    <div style="font-size: 0.72rem; color: #64748b; font-weight: 600; text-transform: uppercase; margin-bottom: 6px; letter-spacing: 0.5px;">Why This Candidate Ranked First:</div>
                    <ul style="color: #94a3b8; font-size: 0.8rem; line-height: 1.5; padding-left: 16px; margin: 0;">{_strengths_li}</ul>
                </div>
                ''',
                unsafe_allow_html=True
            )
        with _exec_col2:
            # Summary Metrics Row
            st.markdown(
                f'''
                <div style="display: flex; flex-direction: column; gap: 12px; height: 100%; justify-content: space-between;">
                    <div class="overview-metric">
                        <div class="overview-metric-num" style="color: #f1f5f9;">{_n_total}</div>
                        <div class="overview-metric-lbl">Evaluated</div>
                    </div>
                    <div class="overview-metric">
                        <div class="overview-metric-num" style="color: #059669;">{_n_shortlisted}</div>
                        <div class="overview-metric-lbl">Shortlisted</div>
                    </div>
                    <div class="overview-metric">
                        <div class="overview-metric-num" style="color: #4f46e5;">{_avg_score}</div>
                        <div class="overview-metric-lbl">Average Score</div>
                    </div>
                    <div class="overview-metric">
                        <div class="overview-metric-num" style="color: #0891b2;">{_highest_score}</div>
                        <div class="overview-metric-lbl">Highest Score</div>
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown('<div class="section-heading">Pipeline Overview</div>', unsafe_allow_html=True)"""
        src = src.replace(pipeline_heading_str, top_cand_code, 1)
    else:
        print("Pipeline heading for summary metrics not found!")

    print("Stage 7: Leaderboard Redesign...")
    # Inject st.markdown('<span class="section-anchor" id="leaderboard"></span>', unsafe_allow_html=True) before `# ── Candidate Leaderboard`
    src = src.replace("# ── Candidate Leaderboard",
                      "st.markdown('<span class=\"section-anchor\" id=\"leaderboard\"></span>', unsafe_allow_html=True)\n\n    # ── Candidate Leaderboard")

    # Find the leaderboard code. We know it starts around `st.markdown('<div class="section-heading">🏆 Candidate Leaderboard</div>'` (or styled)
    # and renders each column cell. Let's do a complete replace of the leaderboard rendering logic!
    # Let's target: `_lh = st.columns([0.05, 0.20, 0.09, 0.09, 0.10, 0.20, 0.13, 0.14])` down to `_legend_txt`
    leaderboard_start_marker = "_lh = st.columns([0.05, 0.20, 0.09, 0.09, 0.10, 0.20, 0.13, 0.14])"
    leaderboard_start_idx = src.find(leaderboard_start_marker)
    
    # Find where the leaderboard rendering loop ends.
    # The loop ends and followed by `# ── Ranking mode legend`
    legend_comment_marker = "# ── Ranking mode legend"
    legend_comment_idx = src.find(legend_comment_marker)
    
    if leaderboard_start_idx != -1 and legend_comment_idx != -1:
        # Reconstruct the leaderboard columns and rows as a clean SaaS table: Rank | Candidate | Final Score | Fit Score | ATS Score | Recommendation | Status
        NEW_LEADERBOARD_CODE = """# SaaS Clean Table columns
        _lh = st.columns([0.06, 0.24, 0.12, 0.12, 0.12, 0.20, 0.14])
        _lh_labels = ["Rank", "Candidate", "Final Score", "Fit Score", "ATS Score", "Recommendation", "Status"]
        _lh_tips   = ["", "Name & Resume file", f"Combined: Fit×{int(_TL_WEIGHT*100)}% + ATS×{int(_ATS_WEIGHT*100)}%", "Candidate Fit Score", "ATS Compatibility", "", "Review status"]
        for _col, _txt, _tip in zip(_lh, _lh_labels, _lh_tips):
            _col.markdown(
                f'<div style="font-size:0.68rem;font-weight:700;letter-spacing:1px;'
                f'text-transform:uppercase;color:#64748b;padding:6px 0 4px;"'
                f'{f" title=\\\"{_tip}\\\"" if _tip else ""}>{_txt}</div>',
                unsafe_allow_html=True,
            )

        for _rank, _entry in enumerate(_filtered_ranked, 1):
            _r       = _entry["result"]
            _sc      = _active_score(_entry)
            _rec     = _s2r(_sc) if _sc is not None else (_r.recommendation or "—")
            _conf    = _r.confidence_level or "Medium"
            _name    = _r.candidate_name or _entry["file"].replace(".pdf", "")
            
            # ATS score from this entry
            _ats_r   = getattr(_r, "ats_result", None)
            _ats_s   = _ats_r.ats_score if _ats_r else None
            _ats_lbl_col = (
                "#059669" if (_ats_s or 0) >= 80 else
                "#d97706" if (_ats_s or 0) >= 60 else "#dc2626"
            )

            # Final / combined score
            _fin_s   = _combined_score(_entry)
            _fin_col = (
                "#059669" if (_fin_s or 0) >= 85 else
                "#4f46e5" if (_fin_s or 0) >= 65 else
                "#d97706" if (_fin_s or 0) >= 40 else "#dc2626"
            )
            _sc_col  = (
                "#059669" if (_sc or 0) >= 85 else
                "#4f46e5" if (_sc or 0) >= 65 else
                "#d97706" if (_sc or 0) >= 40 else "#dc2626"
            )

            _lb_stat     = _get_status(_entry)
            _lb_stat_cls = {"shortlisted": "status-shortlisted", "hold": "status-hold", "rejected": "status-rejected"}.get(_lb_stat, "status-new")
            _lb_stat_lbl = {"shortlisted": "Shortlisted", "hold": "On Hold", "rejected": "Rejected"}.get(_lb_stat, "New")

            _row = st.columns([0.06, 0.24, 0.12, 0.12, 0.12, 0.20, 0.14])
            
            # Clean uniform row rendering (no big borders/medal cells)
            _cell_style = "font-size:0.85rem; padding:8px 0; color:#e2e8f0; display:flex; align-items:center;"
            
            # Rank
            _row[0].markdown(f'<div style="{_cell_style}font-weight:700;">#{_rank}</div>', unsafe_allow_html=True)
            # Candidate
            _row[1].markdown(
                f'<div style="{_cell_style}flex-direction:column;align-items:flex-start;line-height:1.4;">'
                f'<span style="font-weight:600;color:#f1f5f9;">{_name}</span>'
                f'<span style="font-size:0.7rem;color:#475569;">{_entry["file"]}</span></div>',
                unsafe_allow_html=True,
            )
            # Final Score
            _row[2].markdown(f'<div style="{_cell_style}font-weight:800;color:{_fin_col};font-size:1rem;">{_fin_s if _fin_s is not None else "—"}</div>', unsafe_allow_html=True)
            # Fit Score
            _row[3].markdown(f'<div style="{_cell_style}font-weight:600;color:{_sc_col};">{_sc if _sc is not None else "N/A"}</div>', unsafe_allow_html=True)
            # ATS Score
            _row[4].markdown(f'<div style="{_cell_style}color:{_ats_lbl_col};">{_ats_s if _ats_s is not None else "—"}</div>', unsafe_allow_html=True)
            # Recommendation
            _row[5].markdown(f'<div style="{_cell_style}font-weight:500;">{_rec}</div>', unsafe_allow_html=True)
            # Status
            _row[6].markdown(f'<div style="{_cell_style}"><span class="status-badge {_lb_stat_cls}">{_lb_stat_lbl}</span></div>', unsafe_allow_html=True)
            
        st.markdown("<hr style='margin:12px 0;'>", unsafe_allow_html=True)
        """
        src = src[:leaderboard_start_idx] + NEW_LEADERBOARD_CODE + src[legend_comment_idx:]
    else:
        print("Leaderboard region or boundary not found!")

    # Clean leaderboard heading emoji
    src = src.replace("st.markdown('<div class=\"section-heading\">🏆 Candidate Leaderboard</div>', unsafe_allow_html=True)",
                      "st.markdown('<div class=\"section-heading\">Candidate Leaderboard</div>', unsafe_allow_html=True)")

    print("Stage 8: Tabbed Candidate Reports...")
    # Inject st.markdown('<span class="section-anchor" id="evaluations"></span>', unsafe_allow_html=True) before `# ── Individual evaluation reports`
    src = src.replace("# ── Individual evaluation reports",
                      "st.markdown('<span class=\"section-anchor\" id=\"evaluations\"></span>', unsafe_allow_html=True)\n\n    # ── Individual evaluation reports")

    # Clean individual evaluation reports heading emoji
    src = src.replace("st.markdown('<div class=\"section-heading\">📄 Individual Evaluation Reports</div>', unsafe_allow_html=True)",
                      "st.markdown('<div class=\"section-heading\">Individual Evaluation Reports</div>', unsafe_allow_html=True)")

    # The report loop starts with:
    #     for _rank_idx, _entry in enumerate(_filtered_ranked, 1):
    #         ...
    #         with st.expander(_exp_label, expanded=(_rank_idx == 1)):
    # Let's find: `with st.expander(_exp_label, expanded=(_rank_idx == 1)):`
    # and replace everything inside down to the end of the loop with a clean st.tabs structure!
    # Let's find where the loop body starts and ends.
    # The loop body starts after `with st.expander(_exp_label, expanded=(_rank_idx == 1)):`
    expander_marker = "with st.expander(_exp_label, expanded=(_rank_idx == 1)):"
    expander_idx = src.find(expander_marker)
    
    # The loop body ends where the next section starts, which is:
    # `# CANDIDATE COMPARISON DASHBOARD` (or close to it)
    comparison_comment_idx = src.find("# CANDIDATE COMPARISON DASHBOARD")
    
    if expander_idx != -1 and comparison_comment_idx != -1:
        # We will replace the entire internal expander block with a beautiful st.tabs implementation!
        # The replacement starts at expander_idx + len(expander_marker) and goes down to comparison_comment_idx
        # But we need to make sure the indent is correct. The expander_marker is indented by 8 spaces.
        # So our tab code will be indented by 12 spaces.
        
        NEW_TABS_CODE = """
            # Render errors
            if result.errors:
                for err in result.errors:
                    st.markdown(
                        f'<div class="warning-box">⚠️ <strong>Error:</strong> {err}</div>',
                        unsafe_allow_html=True,
                    )

            if not result.errors and result.recommendation is not None:
                # Terminology & score prep
                _curr_stat     = _get_status(_entry)
                _stat_lbl_map  = {"shortlisted": "Shortlisted", "hold": "On Hold", "rejected": "Rejected"}
                _stat_cls_map  = {"shortlisted": "status-shortlisted", "hold": "status-hold", "rejected": "status-rejected"}
                _curr_stat_txt = _stat_lbl_map.get(_curr_stat, "Not Reviewed")
                _curr_stat_cls = _stat_cls_map.get(_curr_stat, "status-new")

                candidate_label = result.candidate_name or result_file.replace(".pdf", "")
                ai_baseline     = result.match_score

                from prompts import CATEGORY_KEYS, CATEGORY_LABELS
                _hr_w     = st.session_state.hr_weights
                _hr_total = sum(_hr_w.values())
                _has_cats = hasattr(result, "category_scores") and bool(result.category_scores)

                if _has_cats and _hr_total == 100:
                    _weighted_sum = sum(
                        result.category_scores.get(k, 0) * (_hr_w.get(k, 0) / 100)
                        for k in CATEGORY_KEYS
                    )
                    score = max(0, min(100, round(_weighted_sum)))
                else:
                    score = ai_baseline

                from candidate_evaluator import _score_to_recommendation as _s2r
                active_recommendation = _s2r(score) if score is not None else result.recommendation

                if score is not None:
                    if score >= 85:
                        score_colour, score_bg = "#059669", "rgba(5,150,105,0.05)"
                    elif score >= 65:
                        score_colour, score_bg = "#4f46e5", "rgba(79,70,229,0.05)"
                    elif score >= 40:
                        score_colour, score_bg = "#d97706", "rgba(217,119,6,0.05)"
                    else:
                        score_colour, score_bg = "#dc2626", "rgba(220,38,38,0.05)"
                else:
                    score_colour, score_bg = "#4f46e5", "rgba(79,70,229,0.03)"

                rec_colours = {
                    "Exceptional Candidate":      ("#059669", "rgba(5,150,105,0.06)"),
                    "Outstanding Match":          ("#059669", "rgba(5,150,105,0.05)"),
                    "Strong Hire":                ("#4f46e5", "rgba(79,70,229,0.06)"),
                    "Recommended":                ("#4f46e5", "rgba(79,70,229,0.05)"),
                    "Potential Fit":              ("#d97706", "rgba(217,119,6,0.06)"),
                    "Consider with Reservations": ("#d97706", "rgba(217,119,6,0.05)"),
                    "Weak Match":                 ("#dc2626", "rgba(220,38,38,0.05)"),
                    "Not Recommended":            ("#dc2626", "rgba(220,38,38,0.06)"),
                    "Hire":    ("#4f46e5", "rgba(79,70,229,0.06)"),
                    "Maybe":   ("#d97706", "rgba(217,119,6,0.06)"),
                    "No Hire": ("#dc2626", "rgba(220,38,38,0.06)"),
                }
                rec_fg, rec_bg = rec_colours.get(active_recommendation, ("#64748b", "rgba(100,116,139,0.05)"))

                conf_colours = {
                    "High":   ("#059669", "rgba(5,150,105,0.04)"),
                    "Medium": ("#d97706", "rgba(217,119,6,0.04)"),
                    "Low":    ("#dc2626", "rgba(220,38,38,0.04)"),
                }
                conf_fg, conf_bg = conf_colours.get(result.confidence_level or "Medium", ("#64748b", "rgba(100,116,139,0.04)"))

                _ats_res = result.ats_result
                _ats_val = _ats_res.ats_score if _ats_res else None
                if _ats_val is not None:
                    if _ats_val >= 90:
                        _ats_c, _ats_bg = "#0891b2", "rgba(8,145,178,0.05)"
                    elif _ats_val >= 80:
                        _ats_c, _ats_bg = "#0891b2", "rgba(8,145,178,0.04)"
                    elif _ats_val >= 70:
                        _ats_c, _ats_bg = "#06b6d4", "rgba(6,182,212,0.04)"
                    elif _ats_val >= 60:
                        _ats_c, _ats_bg = "#d97706", "rgba(217,119,6,0.04)"
                    else:
                        _ats_c, _ats_bg = "#dc2626", "rgba(220,38,38,0.04)"
                else:
                    _ats_c, _ats_bg = "#64748b", "rgba(100,116,139,0.03)"

                _fin_irec = _combined_score(_entry)
                _irec_lbl_r, _irec_col_r = _interview_rec(_fin_irec)

                # Initialize Tabs
                tab_overview, tab_ats, tab_fit, tab_strengths, tab_gaps = st.tabs([
                    "Overview", "ATS Analysis", "Candidate Fit", "Strengths", "Skill Gaps"
                ])

                # ── OVERVIEW TAB ─────────────────────────────────────────────
                with tab_overview:
                    st.markdown("<br>", unsafe_allow_html=True)
                    # Pipeline Status Actions
                    _sa1, _sa2, _sa3, _sa_info = st.columns([0.15, 0.13, 0.12, 0.60])
                    with _sa1:
                        if st.button("Shortlist", key=f"btn_sl_{_rank_idx}", type="primary" if _curr_stat == "shortlisted" else "secondary", use_container_width=True):
                            st.session_state.candidate_statuses[result_file] = "shortlisted"
                            st.rerun()
                    with _sa2:
                        if st.button("Hold", key=f"btn_ho_{_rank_idx}", type="primary" if _curr_stat == "hold" else "secondary", use_container_width=True):
                            st.session_state.candidate_statuses[result_file] = "hold"
                            st.rerun()
                    with _sa3:
                        if st.button("Reject", key=f"btn_re_{_rank_idx}", type="primary" if _curr_stat == "rejected" else "secondary", use_container_width=True):
                            st.session_state.candidate_statuses[result_file] = "rejected"
                            st.rerun()
                    with _sa_info:
                        st.markdown(f'<div style="padding: 6px 0;">Status: <span class="status-badge {_curr_stat_cls}">{_curr_stat_txt}</span></div>', unsafe_allow_html=True)

                    st.markdown("<hr style='margin:14px 0;'>", unsafe_allow_html=True)

                    # Metrics Row
                    h1, h2, h3, h4 = st.columns(4, gap="medium")
                    with h1:
                        if _ats_val is not None:
                            _ats_lbl = _ats_res.ats_label if _ats_res else ""
                            st.markdown(
                                f'''
                                <div style="background:{_ats_bg}; border:1px solid {_ats_c}25; border-radius:6px; padding:16px 14px; text-align:center;">
                                    <div style="font-size:0.65rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:{_ats_c};margin-bottom:4px;">ATS Score</div>
                                    <div style="font-size:2rem;font-weight:800;color:{_ats_c};line-height:1;">{_ats_val}<span style="font-size:0.9rem;opacity:0.7;">/100</span></div>
                                    <div style="font-size:0.68rem;color:{_ats_c}d0;margin-top:4px;font-weight:600;">{_ats_lbl}</div>
                                </div>
                                ''', unsafe_allow_html=True
                            )
                        else:
                            st.markdown('<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:6px;padding:16px 14px;text-align:center;"><div style="font-size:0.65rem;color:#64748b;text-transform:uppercase;">ATS Score</div><div style="font-size:1.4rem;font-weight:700;color:#475569;margin-top:4px;">N/A</div></div>', unsafe_allow_html=True)
                    with h2:
                        if score is not None:
                            st.markdown(
                                f'''
                                <div style="background:{score_bg}; border:1px solid {score_colour}25; border-radius:6px; padding:16px 14px; text-align:center;">
                                    <div style="font-size:0.65rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:{score_colour};margin-bottom:4px;">Fit Score</div>
                                    <div style="font-size:2rem;font-weight:800;color:{score_colour};line-height:1;">{score}<span style="font-size:0.9rem;opacity:0.7;">/100</span></div>
                                </div>
                                ''', unsafe_allow_html=True
                            )
                        else:
                            st.markdown('<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:6px;padding:16px 14px;text-align:center;"><div style="font-size:0.65rem;color:#64748b;text-transform:uppercase;">Fit Score</div><div style="font-size:1.4rem;font-weight:700;color:#475569;margin-top:4px;">N/A</div></div>', unsafe_allow_html=True)
                    with h3:
                        st.markdown(
                            f'''
                            <div style="background:{rec_bg}; border:1px solid {rec_fg}25; border-radius:6px; padding:16px 14px; text-align:center; height:100%; display:flex; flex-direction:column; justify-content:center;">
                                <div style="font-size:0.65rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:{rec_fg};margin-bottom:4px;">Recommendation</div>
                                <div style="font-size:0.95rem;font-weight:700;color:{rec_fg};">{active_recommendation}</div>
                            </div>
                            ''', unsafe_allow_html=True
                        )
                    with h4:
                        st.markdown(
                            f'''
                            <div style="background:{conf_bg}; border:1px solid {conf_fg}25; border-radius:6px; padding:16px 14px; text-align:center;">
                                <div style="font-size:0.65rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:{conf_fg};margin-bottom:4px;">Confidence</div>
                                <div style="font-size:1.3rem;font-weight:700;color:{conf_fg};margin-top:2px;">{result.confidence_level or 'Medium'}</div>
                            </div>
                            ''', unsafe_allow_html=True
                        )

                    # Interview Recommendation
                    if _fin_irec is not None:
                        st.markdown(
                            f'<div class="interview-rec-strip" style="background:{_irec_col_r}08;border:1px solid {_irec_col_r}20;border-left:3px solid {_irec_col_r};margin-top:14px;">'
                            f'<span style="font-size:0.65rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:{_irec_col_r};">Interview Recommendation</span>'
                            f'<span style="font-size:0.95rem;font-weight:700;color:{_irec_col_r};margin-left:10px;">{_irec_lbl_r}</span>'
                            f'<span style="font-size:0.75rem;color:#64748b;margin-left:auto;">Final Score: {_fin_irec}/100</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

                    # Score explanation cards
                    st.markdown("<div class='section-heading'>Evaluation Summary</div>", unsafe_allow_html=True)
                    _evs_left, _evs_right = st.columns(2, gap="large")
                    
                    def _ats_explanation(ats_v, ats_lbl, missing_kws):
                        if ats_v is None: return "ATS score could not be computed."
                        missing_count = len(missing_kws)
                        if ats_v >= 90: return f"This candidate's resume is an excellent keyword and structural match for the role. Almost all required skills and sections are present."
                        elif ats_v >= 80: return f"Strong ATS alignment — the resume covers the vast majority of required skills. " + (f"{missing_count} preferred keyword(s) were not detected." if missing_count else "")
                        elif ats_v >= 70: return f"Good overall keyword match with a few gaps. " + (f"Missing: {', '.join(missing_kws[:4])}." if missing_kws else "")
                        elif ats_v >= 60: return f"Moderate ATS alignment. Several required or preferred keywords are absent. " + (f"Missing: {', '.join(missing_kws[:4])}." if missing_kws else "")
                        else: return f"Low ATS compatibility — the resume lacks many keywords expected by standard screening systems. " + (f"Missing: {', '.join(missing_kws[:5])}." if missing_kws else "")

                    def _tl_explanation(tl_v, rec_label, ats_v):
                        if tl_v is None: return "HirangAI score could not be computed."
                        gap = (tl_v - (ats_v or tl_v))
                        if abs(gap) <= 10: txt = f"The HirangAI score of {tl_v}/100 is closely aligned with the ATS score."
                        elif gap > 10: txt = f"Despite lower ATS keyword match, the candidate scores {tl_v}/100 on HirangAI, reflecting strong demonstrated skills, relevant experience, and role suitability."
                        else: txt = f"The candidate's resume keyword coverage outpaces the overall AI-assessed fit ({tl_v}/100)."
                        return f"{txt} Recommendation: **{rec_label}**."

                    _eval_ats_val    = _ats_val
                    _eval_ats_lbl    = (_ats_res.ats_label if _ats_res else "N/A")
                    _eval_missing    = list((_ats_res.required_keywords_missing if _ats_res else []) + (_ats_res.preferred_keywords_missing if _ats_res else []))
                    _eval_tl         = score
                    _eval_fin        = _combined_score(_entry)

                    with _evs_left:
                        st.markdown(
                            f'''
                            <div style="background:rgba(6,182,212,0.03);border:1px solid rgba(6,182,212,0.12);border-left:3px solid #06b6d4;border-radius:6px;padding:14px;height:100%;">
                                <div style="font-size:0.65rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#06b6d4;margin-bottom:6px;">ATS Compatibility Summary</div>
                                <div style="font-size:1.3rem;font-weight:800;color:#06b6d4;margin-bottom:4px;">{_eval_ats_val if _eval_ats_val is not None else 'N/A'}<span style="font-size:0.75rem;opacity:0.7;">/100</span></div>
                                <div style="font-size:0.8rem;color:#cbd5e1;line-height:1.5;">{_ats_explanation(_eval_ats_val, _eval_ats_lbl, _eval_missing)}</div>
                            </div>
                            ''', unsafe_allow_html=True
                        )
                    with _evs_right:
                        st.markdown(
                            f'''
                            <div style="background:rgba(79,70,229,0.03);border:1px solid rgba(79,70,229,0.12);border-left:3px solid #4f46e5;border-radius:6px;padding:14px;height:100%;">
                                <div style="font-size:0.65rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#818cf8;margin-bottom:6px;">HirangAI Fit Summary</div>
                                <div style="font-size:1.3rem;font-weight:800;color:{score_colour};margin-bottom:4px;">{_eval_tl if _eval_tl is not None else 'N/A'}<span style="font-size:0.75rem;opacity:0.7;">/100</span></div>
                                <div style="font-size:0.8rem;color:#cbd5e1;line-height:1.5;">{_tl_explanation(_eval_tl, active_recommendation, _eval_ats_val)}</div>
                            </div>
                            ''', unsafe_allow_html=True
                        )

                    if _eval_fin is not None:
                        _fin_c2 = "#059669" if _eval_fin >= 85 else "#4f46e5" if _eval_fin >= 65 else "#d97706" if _eval_fin >= 40 else "#dc2626"
                        st.markdown(
                            f'<div style="background:rgba(79,70,229,0.04);border:1px solid rgba(79,70,229,0.15);border-radius:6px;padding:10px 14px;margin-top:12px;display:flex;align-items:center;gap:12px;">'
                            f'<span style="font-size:0.65rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#818cf8;">Final Ranking Score</span>'
                            f'<span style="font-size:1.3rem;font-weight:800;color:{_fin_c2};">{_eval_fin}</span>'
                            f'<span style="font-size:0.75rem;opacity:0.6;color:#94a3b8;">/100</span>'
                            f'<span style="font-size:0.75rem;color:#64748b;margin-left:auto;">Fit {_eval_tl} × {int(_TL_WEIGHT*100)}% + ATS {_eval_ats_val} × {int(_ATS_WEIGHT*100)}%</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

                # ── ATS ANALYSIS TAB ─────────────────────────────────────────
                with tab_ats:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if _ats_res is not None:
                        # Sub-score bars
                        st.markdown('<div style="font-size:0.68rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#06b6d4;margin-bottom:10px;">ATS Sub-Scores</div>', unsafe_allow_html=True)
                        _sub_col1, _sub_col2 = st.columns(2, gap="large")
                        _sub_items = list((_ats_res.sub_scores or {}).items())
                        for _si, (_slabel, _sval) in enumerate(_sub_items):
                            _scol = _sub_col1 if _si % 2 == 0 else _sub_col2
                            _sval_c = "#059669" if _sval >= 80 else "#06b6d4" if _sval >= 60 else "#d97706" if _sval >= 40 else "#dc2626"
                            _scol.markdown(
                                f'''
                                <div style="margin-bottom:10px;">
                                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                                        <span style="font-size:0.78rem;font-weight:600;color:#cbd5e1;">{_slabel}</span>
                                        <span style="font-size:0.8rem;font-weight:700;color:{_sval_c};">{_sval}</span>
                                    </div>
                                    <div class="ats-bar-track">
                                        <div class="ats-bar-fill" style="--bar-w:{_sval}%;background:{_sval_c};"></div>
                                    </div>
                                </div>
                                ''', unsafe_allow_html=True
                            )

                        st.markdown("<hr style='margin:14px 0;'>", unsafe_allow_html=True)
                        _kw_left, _kw_right = st.columns(2, gap="large")

                        with _kw_left:
                            st.markdown('<div style="font-size:0.68rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#059669;margin-bottom:6px;">Matched Keywords</div>', unsafe_allow_html=True)
                            _matched_all = _ats_res.required_keywords_matched + _ats_res.preferred_keywords_matched
                            if _matched_all:
                                _chip_html = "".join(f'<span class="ats-chip ats-chip-match">{kw}</span>' for kw in _matched_all[:30])
                                st.markdown(f'<div style="display:flex;flex-wrap:wrap;gap:2px;">{_chip_html}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div style="color:#64748b;font-size:0.8rem;">No keywords matched.</div>', unsafe_allow_html=True)

                        with _kw_right:
                            st.markdown('<div style="font-size:0.68rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#d97706;margin-bottom:6px;">Missing Keywords</div>', unsafe_allow_html=True)
                            _missing_all = _ats_res.required_keywords_missing + _ats_res.preferred_keywords_missing
                            if _missing_all:
                                _miss_html = "".join(f'<span class="ats-chip ats-chip-miss">{kw}</span>' for kw in _missing_all[:30])
                                st.markdown(f'<div style="display:flex;flex-wrap:wrap;gap:2px;">{_miss_html}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div style="color:#059669;font-size:0.8rem;">All keywords matched!</div>', unsafe_allow_html=True)

                        st.markdown("<hr style='margin:14px 0;'>", unsafe_allow_html=True)
                        st.markdown('<div style="font-size:0.68rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#06b6d4;margin-bottom:8px;">Resume Structure</div>', unsafe_allow_html=True)
                        _sect_left, _sect_right = st.columns(2, gap="large")
                        _all_sects = [(s, True) for s in _ats_res.sections_present] + [(s, False) for s in _ats_res.sections_missing]
                        for _si2, (_sname, _spresent) in enumerate(_all_sects):
                            _sc2 = _sect_left if _si2 % 2 == 0 else _sect_right
                            _icon2, _cls2 = ("✓", "ats-section-ok") if _spresent else ("⚠", "ats-section-miss")
                            _sc2.markdown(f'<div class="ats-section-row"><span class="{_cls2}" style="font-weight:700;margin-right:6px;">{_icon2}</span><span style="color:#cbd5e1;">{_sname}</span></div>', unsafe_allow_html=True)

                        # Guide box
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown(
                            '<div style="background:rgba(6,182,212,0.03);border:1px solid rgba(6,182,212,0.15);border-left:3px solid #06b6d4;border-radius:6px;padding:10px 14px;font-size:0.78rem;color:#94a3b8;line-height:1.6;">'
                            '<strong style="color:#06b6d4;">ATS Scoring Rubric</strong><br>'
                            '90–100: Excellent ATS Match | 80–89: Strong | 70–79: Good | 60–69: Moderate | Under 60: Low'
                            '</div>', unsafe_allow_html=True
                        )
                    else:
                        st.markdown('<div style="color:#64748b;font-size:0.85rem;">ATS breakdown not available.</div>', unsafe_allow_html=True)

                # ── CANDIDATE FIT TAB ────────────────────────────────────────
                with tab_fit:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if _has_cats:
                        st.markdown('<div style="font-size:0.68rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#4f46e5;margin-bottom:12px;">Weighted Categories</div>', unsafe_allow_html=True)
                        cat_left, cat_right = st.columns(2, gap="large")
                        cats = [(key, CATEGORY_LABELS[key], result.category_scores.get(key)) for key in CATEGORY_KEYS]
                        for idx, (key, label, cat_score) in enumerate(cats):
                            col        = cat_left if idx % 2 == 0 else cat_right
                            s          = cat_score if cat_score is not None else 0
                            weight_pct = _hr_w.get(key, 0)
                            
                            if s >= 85: bar_colour, bar_sc = "#059669", "#059669"
                            elif s >= 65: bar_colour, bar_sc = "#4f46e5", "#4f46e5"
                            elif s >= 40: bar_colour, bar_sc = "#d97706", "#d97706"
                            else: bar_colour, bar_sc = "#dc2626", "#dc2626"
                            
                            col.markdown(
                                f'''
                                <div style="margin-bottom:12px;">
                                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                                        <span style="font-size:0.78rem;font-weight:600;color:#cbd5e1;">{label}</span>
                                        <span style="font-size:0.72rem;color:#64748b;">weight {weight_pct}%</span>
                                    </div>
                                    <div style="display:flex;align-items:center;gap:10px;">
                                        <div class="cat-bar-track">
                                            <div class="cat-bar-fill" style="--bar-w:{s}%;background:{bar_colour};"></div>
                                        </div>
                                        <span style="font-size:0.82rem;font-weight:700;color:{bar_sc};min-width:32px;text-align:right;">{s if cat_score is not None else '—'}</span>
                                    </div>
                                </div>
                                ''', unsafe_allow_html=True
                            )
                        if _hr_total != 100:
                            st.markdown('<div class="warning-box" style="margin-top:10px;">⚠️ Total weights configured must equal 100%.</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="color:#64748b;font-size:0.85rem;">Category details not available.</div>', unsafe_allow_html=True)

                # ── STRENGTHS TAB ────────────────────────────────────────────
                with tab_strengths:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown('<div style="font-size:0.68rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#059669;margin-bottom:8px;">Key Strengths</div>', unsafe_allow_html=True)
                    if result.strengths:
                        bullets = "".join(f'<li style="margin-bottom:5px;">{s}</li>' for s in result.strengths)
                        st.markdown(f'<ul style="color:#94a3b8;font-size:0.82rem;line-height:1.6;padding-left:16px;">{bullets}</ul>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="color:#64748b;font-size:0.8rem;">No strengths found.</div>', unsafe_allow_html=True)

                    if result.experience_summary:
                        st.markdown("<hr style='margin:14px 0;'>", unsafe_allow_html=True)
                        st.markdown('<div style="font-size:0.68rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#4f46e5;margin-bottom:8px;">Experience Summary</div>', unsafe_allow_html=True)
                        st.markdown(f'<div style="color:#cbd5e1;font-size:0.82rem;line-height:1.6;background:rgba(255,255,255,0.01);padding:10px 14px;border:1px solid rgba(255,255,255,0.05);border-radius:6px;">{result.experience_summary}</div>', unsafe_allow_html=True)

                # ── SKILL GAPS TAB ───────────────────────────────────────────
                with tab_gaps:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown('<div style="font-size:0.68rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#d97706;margin-bottom:8px;">Detected Skill Gaps</div>', unsafe_allow_html=True)
                    if result.skill_gaps:
                        gaps = "".join(f'<li style="margin-bottom:5px;">{g}</li>' for g in result.skill_gaps)
                        st.markdown(f'<ul style="color:#94a3b8;font-size:0.82rem;line-height:1.6;padding-left:16px;">{gaps}</ul>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div style="color:#059669;font-size:0.8rem;">No skill gaps detected.</div>', unsafe_allow_html=True)

                    if result.raw_llm_response:
                        st.markdown("<hr style='margin:14px 0;'>", unsafe_allow_html=True)
                        with st.expander("Full AI Analysis Details", expanded=False):
                            st.markdown(result.raw_llm_response)

                    st.markdown("<hr style='margin:14px 0;'>", unsafe_allow_html=True)
                    # Report download
                    _ind_pdf = _build_individual_pdf(
                        entry=_entry,
                        active_score=_active_score(_entry),
                        active_recommendation=active_recommendation,
                        hr_weights=_hr_w,
                    )
                    _cand_fname = (result.candidate_name or result_file.replace(".pdf", "")).replace(" ", "_")
                    st.download_button(
                        label="Download PDF Report",
                        data=_ind_pdf,
                        file_name=f"HirangAI_Report_{_cand_fname}.pdf",
                        mime="application/pdf",
                        key=f"dl_ind_pdf_{_rank_idx}",
                        use_container_width=False,
                    )
        """
        
        src = src[:expander_idx + len(expander_marker)] + NEW_TABS_CODE + src[comparison_comment_idx:]
    else:
        print("Expander loop boundaries not found!")

    print("Stage 10: Injecting Comparison & Export anchors...")
    # Inject st.markdown('<span class="section-anchor" id="comparison"></span>', unsafe_allow_html=True) before `# CANDIDATE COMPARISON DASHBOARD`
    src = src.replace("# CANDIDATE COMPARISON DASHBOARD",
                      "st.markdown('<span class=\"section-anchor\" id=\"comparison\"></span>', unsafe_allow_html=True)\n\n# CANDIDATE COMPARISON DASHBOARD")

    # Inject st.markdown('<span class="section-anchor" id="export"></span>', unsafe_allow_html=True) before `# RANKINGS EXPORT`
    src = src.replace("# RANKINGS EXPORT",
                      "st.markdown('<span class=\"section-anchor\" id=\"export\"></span>', unsafe_allow_html=True)\n\n# RANKINGS EXPORT")

    # Let's clean up emojis from section titles: "⚖️ Candidate Comparison Dashboard" -> "Candidate Comparison Dashboard", "📥 Rankings Export" etc.
    src = src.replace("⚖️ Candidate Comparison Dashboard", "Candidate Comparison Dashboard")
    src = src.replace("st.markdown('<div class=\"section-heading\">📥 Rankings Export</div>', unsafe_allow_html=True)",
                      "st.markdown('<div class=\"section-heading\">Rankings Export</div>', unsafe_allow_html=True)")

    # ── Verify syntax ──────────────────────────────────────────────────────────
    print("Verifying syntax...")
    try:
        ast.parse(src)
        print("Syntax check: OK!")
    except SyntaxError as e:
        print(f"SYNTAX ERROR IN MODIFIED APP.PY: {e}")
        return

    # Write the modified app.py
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(src)
    print("app.py successfully written!")

if __name__ == "__main__":
    main()
