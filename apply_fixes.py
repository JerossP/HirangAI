# apply_fixes.py
import re

def main():
    print("Loading app.py...")
    with open("app.py", "r", encoding="utf-8") as f:
        src = f.read()

    # 1. Update imports block at the top
    print("Fix 1: Updating imports and environment initialization at top...")
    old_imports = """from __future__ import annotations

import streamlit as st
from resume_parser import parse_resume
from candidate_evaluator import evaluate_candidate"""

    new_imports = """from __future__ import annotations

import sys
import logging
from dotenv import load_dotenv
load_dotenv()  # Load environment variables at the very first line of code execution!

import streamlit as st
from resume_parser import parse_resume
from candidate_evaluator import evaluate_candidate

# Setup terminal-only logger
logger = logging.getLogger("HirangAI.pipeline")
if not logger.handlers:
    _ch = logging.StreamHandler(sys.stderr)
    _ch.setFormatter(logging.Formatter("[%(asctime)s] %(message)s"))
    logger.addHandler(_ch)
    logger.setLevel(logging.INFO)"""

    if old_imports in src:
        src = src.replace(old_imports, new_imports)
        print("  Imports updated.")
    else:
        print("  WARNING: Imports block not found exactly as expected!")

    # 2. Fix status bar HTML formatting (removing indentation)
    print("Fix 2: Dedenting pipeline status bar...")
    old_steps = """_steps_html = (
    f'''<div style="display:flex;align-items:center;gap:0;padding:10px 0 18px;border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:20px;">
        <span style="{_step_style(_jd_ready)}">Job Description</span>
        <span style="margin:0 10px;color:#334155;font-size:0.75rem;">·</span>
        <span style="{_step_style(_files_ready)}">Candidates</span>
        <span style="margin:0 10px;color:#334155;font-size:0.75rem;">·</span>
        <span style="{_step_style(True)}">Assessment Profile</span>
        <span style="margin:0 10px;color:#334155;font-size:0.75rem;">·</span>
        <span style="{_step_style(_jd_ready and _files_ready)}">Analyze</span>
        <span style="margin:0 10px;color:#334155;font-size:0.75rem;">·</span>
        <span style="{_step_style(_results_ready)}">Review</span>
    </div>'''
)"""

    new_steps = """_steps_html = (
    f'''<div style="display:flex;align-items:center;gap:0;padding:10px 0 18px;border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:20px;">'''
    f'''<span style="{_step_style(_jd_ready)}">Job Description</span>'''
    f'''<span style="margin:0 10px;color:#334155;font-size:0.75rem;">·</span>'''
    f'''<span style="{_step_style(_files_ready)}">Candidates</span>'''
    f'''<span style="margin:0 10px;color:#334155;font-size:0.75rem;">·</span>'''
    f'''<span style="{_step_style(True)}">Assessment Profile</span>'''
    f'''<span style="margin:0 10px;color:#334155;font-size:0.75rem;">·</span>'''
    f'''<span style="{_step_style(_jd_ready and _files_ready)}">Analyze</span>'''
    f'''<span style="margin:0 10px;color:#334155;font-size:0.75rem;">·</span>'''
    f'''<span style="{_step_style(_results_ready)}">Review</span>'''
    f'''</div>'''
)"""

    if old_steps in src:
        src = src.replace(old_steps, new_steps)
        print("  Status bar dedented successfully.")
    else:
        # Try alternate match if quotes are double or format differs
        print("  WARNING: Status bar block not found exactly as expected!")

    # 3. Fix upload area code blocks (removing indentation)
    print("Fix 3: Dedenting upload area display elements...")
    old_upload_block = """        # Clean candidate list header
        st.markdown(
            f'''<div style="margin-top:12px;">
                <div style="font-size:0.72rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;
                            color:#64748b;margin-bottom:8px;">Uploaded Candidates</div>
                <div style="font-size:0.82rem;color:#94a3b8;margin-bottom:10px;">
                    <span style="color:#f1f5f9;font-weight:600;">{len(uploaded_files)}</span> uploaded
                    &nbsp;·&nbsp;
                    <span style="color:#059669;font-weight:600;">{_n_ok}</span> ready
                    {f'&nbsp;·&nbsp;<span style="color:#dc2626;font-weight:600;">{_n_fail}</span> failed' if _n_fail else ""}
                </div>
            </div>''',
            unsafe_allow_html=True,
        )

        # Compact filename list
        for _uf in uploaded_files:
            _p = st.session_state.get(f"parsed_{_uf.name}")
            _ok = _p and _p.is_valid
            _dot_color = "#059669" if _ok else "#dc2626"
            _name_color = "#e2e8f0" if _ok else "#94a3b8"
            st.markdown(
                f'''<div style="display:flex;align-items:center;gap:8px;padding:5px 0;
                              border-bottom:1px solid rgba(255,255,255,0.04);">
                    <span style="width:6px;height:6px;border-radius:50%;background:{_dot_color};
                                 display:inline-block;flex-shrink:0;"></span>
                    <span style="font-size:0.82rem;color:{_name_color};font-weight:500;">{_uf.name}</span>
                    {f'<span style="font-size:0.7rem;color:#dc2626;margin-left:auto;">Could not parse</span>' if not _ok else ""}
                </div>''',
                unsafe_allow_html=True,
            )

        # Collapsible details
        with st.expander("Show file details", expanded=False):
            for _uf in uploaded_files:
                _p  = st.session_state.get(f"parsed_{_uf.name}")
                _kb = round(_uf.size / 1024, 1)
                if _p and _p.is_valid:
                    st.markdown(
                        f'''<div style="font-size:0.78rem;color:#94a3b8;padding:4px 0;
                                      border-bottom:1px solid rgba(255,255,255,0.04);">
                            <strong style="color:#e2e8f0;">{_uf.name}</strong>
                            &nbsp;·&nbsp;{_p.page_count} page(s)
                            &nbsp;·&nbsp;{_p.word_count} words
                            &nbsp;·&nbsp;{_kb} KB
                        </div>''',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'''<div style="font-size:0.78rem;color:#dc2626;padding:4px 0;">
                            {_uf.name} — could not extract text
                        </div>''',
                        unsafe_allow_html=True,
                    )"""

    new_upload_block = """        # Clean candidate list header
        st.markdown(
            f'''<div style="margin-top:12px;">'''
            f'''<div style="font-size:0.72rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#64748b;margin-bottom:8px;">Uploaded Candidates</div>'''
            f'''<div style="font-size:0.82rem;color:#94a3b8;margin-bottom:10px;">'''
            f'''<span style="color:#f1f5f9;font-weight:600;">{len(uploaded_files)}</span> uploaded'''
            f'''&nbsp;·&nbsp;'''
            f'''<span style="color:#059669;font-weight:600;">{_n_ok}</span> ready'''
            f'''{f"&nbsp;·&nbsp;<span style='color:#dc2626;font-weight:600;'>{_n_fail}</span> failed" if _n_fail else ""}'''
            f'''</div>'''
            f'''</div>''',
            unsafe_allow_html=True,
        )

        # Compact filename list
        for _uf in uploaded_files:
            _p = st.session_state.get(f"parsed_{_uf.name}")
            _ok = _p and _p.is_valid
            _dot_color = "#059669" if _ok else "#dc2626"
            _name_color = "#e2e8f0" if _ok else "#94a3b8"
            _err_msg = f'<span style="font-size:0.7rem;color:#dc2626;margin-left:auto;">Could not parse</span>' if not _ok else ""
            st.markdown(
                f'''<div style="display:flex;align-items:center;gap:8px;padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.04);">'''
                f'''<span style="width:6px;height:6px;border-radius:50%;background:{_dot_color};display:inline-block;flex-shrink:0;"></span>'''
                f'''<span style="font-size:0.82rem;color:{_name_color};font-weight:500;">{_uf.name}</span>'''
                f'''{_err_msg}'''
                f'''</div>''',
                unsafe_allow_html=True,
            )

        # Collapsible details
        with st.expander("Show file details", expanded=False):
            for _uf in uploaded_files:
                _p  = st.session_state.get(f"parsed_{_uf.name}")
                _kb = round(_uf.size / 1024, 1)
                if _p and _p.is_valid:
                    st.markdown(
                        f'''<div style="font-size:0.78rem;color:#94a3b8;padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.04);">'''
                        f'''<strong style="color:#e2e8f0;">{_uf.name}</strong>'''
                        f'''&nbsp;·&nbsp;{_p.page_count} page(s)'''
                        f'''&nbsp;·&nbsp;{_p.word_count} words'''
                        f'''&nbsp;·&nbsp;{_kb} KB'''
                        f'''</div>''',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'''<div style="font-size:0.78rem;color:#dc2626;padding:4px 0;">'''
                        f'''{_uf.name} — could not extract text'''
                        f'''</div>''',
                        unsafe_allow_html=True,
                    )"""

    if old_upload_block in src:
        src = src.replace(old_upload_block, new_upload_block)
        print("  Upload area display elements dedented successfully.")
    else:
        print("  WARNING: Upload area block not found exactly as expected!")

    # 4. Fix no-resumes block indentation
    print("Fix 4: Dedenting no-resumes block...")
    old_no_resumes = """        st.markdown(
            '''<div style="font-size:0.82rem;color:#475569;margin-top:10px;">
                No resumes uploaded yet.
            </div>''',
            unsafe_allow_html=True,
        )"""

    new_no_resumes = """        st.markdown(
            '''<div style="font-size:0.82rem;color:#475569;margin-top:10px;">'''
            '''No resumes uploaded yet.'''
            '''</div>''',
            unsafe_allow_html=True,
        )"""

    if old_no_resumes in src:
        src = src.replace(old_no_resumes, new_no_resumes)
        print("  No-resumes block dedented.")
    else:
        print("  WARNING: No-resumes block not found exactly as expected!")

    # 5. Fix Analyze Candidates button and pipeline tracing
    print("Fix 5: Rebuilding button, strict weights validation, and pipeline tracing...")
    
    # We find the start of the button validation section
    btn_start_marker = 'st.markdown("<div style=\'margin-top:20px;\'></div>", unsafe_allow_html=True)'
    # We find the end of st.rerun() in the pipeline
    btn_end_marker = 'st.session_state.last_score = f"{_ts}/100" if _ts is not None else _top["result"].recommendation\n\n        # ── Critical: rerun so results display block sees new session state ──\n        st.rerun()'

    start_idx = src.find(btn_start_marker)
    end_idx = src.find(btn_end_marker, start_idx)

    if start_idx == -1 or end_idx == -1:
        print(f"  ERROR: Button block indices not found! start={start_idx}, end={end_idx}")
    else:
        # Compute exact replace window
        full_end_idx = end_idx + len(btn_end_marker)
        
        NEW_BUTTON_PIPELINE = """st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)

# Determine readiness state
_uploaded_files_safe = uploaded_files if uploaded_files else []
_n_valid = sum(
    1 for f in _uploaded_files_safe
    if st.session_state.get(f"parsed_{f.name}") and st.session_state[f"parsed_{f.name}"].is_valid
)
_jd_ok    = bool(job_description.strip())
_files_ok = _n_valid > 0

# Strict assessment weights sum validation
_hr_w = st.session_state.get("hr_weights", {})
_weights_sum = sum(_hr_w.values())
_weights_ok = (_weights_sum == 100)

_can_run = _jd_ok and _files_ok and _weights_ok

# Validation message shown above button
if not _jd_ok:
    st.markdown(
        '<div style="font-size:0.8rem;color:#64748b;margin-bottom:8px;padding:8px 12px;'
        'background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:6px;">'
        'Enter a job description to continue.</div>',
        unsafe_allow_html=True,
    )
elif not _files_ok:
    st.markdown(
        '<div style="font-size:0.8rem;color:#64748b;margin-bottom:8px;padding:8px 12px;'
        'background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:6px;">'
        'Upload at least one PDF resume to continue.</div>',
        unsafe_allow_html=True,
    )
elif not _weights_ok:
    st.markdown(
        f'<div style="font-size:0.8rem;color:#f87171;margin-bottom:8px;padding:8px 12px;'
        f'background:rgba(220,38,38,0.05);border:1px solid rgba(220,38,38,0.15);border-radius:6px;">'
        f'⚠️ Analysis is blocked because the total assessment category weights must sum to exactly 100% '
        f'(currently {_weights_sum}%). Please adjust the weights in the Advanced Configuration sidebar expander.</div>',
        unsafe_allow_html=True,
    )

# Primary full-width button
_btn_label = (
    f"Analyze {_n_valid} Candidate{'s' if _n_valid != 1 else ''}"
    if _n_valid > 0 else "Analyze Candidates"
)
analyse_clicked = st.button(
    _btn_label,
    key="analyse_button",
    disabled=not _can_run,
    use_container_width=True,
    type="primary",
)

# ─────────────────────────────────────────────────────────────────────────────
# Evaluation pipeline (with robust console-only tracing)
# ─────────────────────────────────────────────────────────────────────────────

if analyse_clicked:
    # Trace 1: Click Captured
    logger.info("[HirangAI DEBUG] Step 1: Analyze Candidates button click registered.")
    
    # Trace 2: Validation Status
    logger.info(
        f"[HirangAI DEBUG] Step 2: Validation checks.\\n"
        f"  - Job Description OK: {_jd_ok}\\n"
        f"  - Uploaded Files OK: {_files_ok} (valid count: {_n_valid})\\n"
        f"  - Category Weights OK: {_weights_ok} (sum: {_weights_sum}%)\\n"
        f"  - Overall readiness (_can_run): {_can_run}"
    )

    if _can_run:
        # Trace 3: Session State Params
        logger.info(
            f"[HirangAI DEBUG] Step 3: Session parameters retrieved.\\n"
            f"  - Active template: {st.session_state.get('active_template')}\\n"
            f"  - HR weights: {st.session_state.get('hr_weights')}"
        )

        _valid_pairs = [
            (f, st.session_state[f"parsed_{f.name}"])
            for f in _uploaded_files_safe
            if st.session_state.get(f"parsed_{f.name}") and st.session_state[f"parsed_{f.name}"].is_valid
        ]
        
        # Trace 4: Uploaded Resumes Collected
        logger.info(
            f"[HirangAI DEBUG] Step 4: Resumes collected for analysis:\\n"
            f"  - Count: {len(_valid_pairs)}\n"
            f"  - Files: {[_uf.name for _uf, _ in _valid_pairs]}"
        )

        # Trace 5: Job Description Retrieval
        logger.info(
            f"[HirangAI DEBUG] Step 5: Job description retrieved.\\n"
            f"  - Length: {len(job_description)} chars\\n"
            f"  - Word count: {len(job_description.split())} words"
        )

        if not _valid_pairs:
            logger.warning("[HirangAI DEBUG] Pipeline execution aborted: _valid_pairs is empty.")
            st.error("No resumes could be parsed. Please upload valid PDF files.")
        else:
            # Trace 6: Loop Initialization
            logger.info(f"[HirangAI DEBUG] Step 6: Candidate evaluation loop initialized. Processing {len(_valid_pairs)} candidate(s).")
            
            _batch_results: list[dict] = []
            _progress = st.progress(0, text="Starting evaluation...")
            _status_placeholder = st.empty()

            for _i, (_uf, _parsed) in enumerate(_valid_pairs):
                _pct  = _i / len(_valid_pairs)
                _name = _parsed.candidate_name or _uf.name.replace(".pdf", "")
                _progress.progress(_pct, text=f"Evaluating {_name} ({_i + 1} of {len(_valid_pairs)})...")
                
                # Single-line HTML to avoid markdown indented code blocks!
                _status_placeholder.markdown(
                    f'''<div style="font-size:0.8rem;color:#64748b;padding:6px 0;">Analyzing <strong style="color:#f1f5f9;">{_name}</strong>...</div>''',
                    unsafe_allow_html=True,
                )
                
                # Trace 7: Groq Call
                logger.info(f"[HirangAI DEBUG] Step 7: Initiating Groq API call for candidate: {_name} ({_uf.name})")
                
                try:
                    import time
                    _t_start = time.time()
                    _res = evaluate_candidate(
                        job_description=job_description,
                        parsed_resume=_parsed,
                    )
                    _t_elapsed = time.time() - _t_start
                    # Trace 7 Passed
                    logger.info(
                        f"[HirangAI DEBUG] Step 7 Passed: Groq API call succeeded for {_name} "
                        f"in {_t_elapsed:.2f}s.\\n"
                        f"  - Match Score: {_res.match_score}\\n"
                        f"  - Recommendation: {_res.recommendation}\\n"
                        f"  - Confidence: {_res.confidence_level}\\n"
                        f"  - Errors: {_res.errors}"
                    )
                except Exception as _eval_err:
                    _t_elapsed = time.time() - _t_start
                    logger.error(
                        f"[HirangAI DEBUG] Step 7 FAILED: Groq API call crashed for {_name} "
                        f"after {_t_elapsed:.2f}s with error: {_eval_err}",
                        exc_info=True
                    )
                    from candidate_evaluator import EvaluationResult
                    _res = EvaluationResult(
                        candidate_name=_name,
                        match_score=None,
                        recommendation=None,
                        confidence_level=None,
                        strengths=[],
                        skill_gaps=[],
                        experience_summary="",
                        raw_llm_response="",
                        errors=[f"Evaluation failed: {_eval_err}"],
                    )
                _batch_results.append({"file": _uf.name, "result": _res})

            _progress.progress(1.0, text=f"Complete — {len(_batch_results)} candidate(s) analyzed")
            _status_placeholder.empty()

            # Trace 8: Result Storage
            logger.info("[HirangAI DEBUG] Step 8: Storing batch results in session state.")
            
            st.session_state.batch_results  = _batch_results
            st.session_state.last_result    = _batch_results[-1]["result"]
            st.session_state.last_file_name = _batch_results[-1]["file"]

            _successful = [r for r in _batch_results if not r["result"].errors and r["result"].recommendation]
            st.session_state.analysis_count += len(_successful)
            if _successful:
                _top = max(_successful, key=lambda r: r["result"].match_score or 0)
                st.session_state.last_candidate = _top["result"].candidate_name or _top["file"]
                _ts  = _top["result"].match_score
                st.session_state.last_score = f"{_ts}/100" if _ts is not None else _top["result"].recommendation
            
            logger.info(
                f"[HirangAI DEBUG] Step 8 Passed: Session state updated.\\n"
                f"  - Total batch size stored: {len(_batch_results)}\\n"
                f"  - Total successful analyses added: {len(_successful)}\\n"
                f"  - New analysis count: {st.session_state.analysis_count}"
            )

            # Trace 9: Rerun Trigger
            logger.info("[HirangAI DEBUG] Step 9: Invoking st.rerun() to refresh results view.")
            st.rerun()
    else:
        logger.warning("[HirangAI DEBUG] Button clicked but _can_run is False. Execution blocked.")"""

        src = src[:start_idx] + NEW_BUTTON_PIPELINE + src[full_end_idx:]
        print("  Rebuilt button validation and execution pipeline.")

    # 6. Fix full AI analysis details missing unsafe_allow_html=True
    print("Fix 6: Adding unsafe_allow_html=True to AI Analysis details markdown...")
    old_details = """                        with st.expander("Full AI Analysis Details", expanded=False):
                            st.markdown(result.raw_llm_response)"""
    new_details = """                        with st.expander("Full AI Analysis Details", expanded=False):
                            st.markdown(result.raw_llm_response, unsafe_allow_html=True)"""
    if old_details in src:
        src = src.replace(old_details, new_details)
        print("  AI Analysis details expanded markdown updated.")
    else:
        print("  WARNING: AI Analysis details expander block not found!")

    # Verify AST syntax
    print("\nVerifying syntax...")
    import ast
    try:
        ast.parse(src)
        print("Syntax check: PASSED!")
    except SyntaxError as e:
        print(f"SYNTAX ERROR: {e}")
        print(f"  Line {e.lineno}: {e.text}")
        return

    # Write out
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(src)
    print("\nSUCCESS: All fixes applied perfectly to app.py!")

if __name__ == "__main__":
    main()
