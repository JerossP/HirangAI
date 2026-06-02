# apply_refinements.py
# Applies the bug fix + UI/UX refinement pass to app.py
import ast, re, sys

def main():
    print("Loading app.py...")
    with open("app.py", "r", encoding="utf-8") as f:
        src = f.read()

    original_len = len(src)

    # =========================================================================
    # UI 6 — Clean BUILTIN_TEMPLATES names (remove emoji prefixes)
    # =========================================================================
    print("UI 6: Cleaning template names...")
    src = src.replace('"⚖️ Balanced Assessment"', '"Balanced Assessment"')
    src = src.replace("'⚖️ Balanced Assessment'", "'Balanced Assessment'")
    src = src.replace('"💻 Technical-Heavy Evaluation"', '"Technical-Heavy Evaluation"')
    src = src.replace("'💻 Technical-Heavy Evaluation'", "'Technical-Heavy Evaluation'")
    src = src.replace('"💼 Experience-Focused Evaluation"', '"Experience-Focused Evaluation"')
    src = src.replace("'💼 Experience-Focused Evaluation'", "'Experience-Focused Evaluation'")
    src = src.replace('"⚡ Skills-First Screening"', '"Skills-First Screening"')
    src = src.replace("'⚡ Skills-First Screening'", "'Skills-First Screening'")
    src = src.replace('"🎤 Leadership & Communication Focus"', '"Leadership & Communication Focus"')
    src = src.replace("'🎤 Leadership & Communication Focus'", "'Leadership & Communication Focus'")
    src = src.replace('"📜 Certification-Weighted Evaluation"', '"Certification-Weighted Evaluation"')
    src = src.replace("'📜 Certification-Weighted Evaluation'", "'Certification-Weighted Evaluation'")
    # Fix default template name reference
    src = src.replace(
        '_DEFAULT_TEMPLATE = "⚖️ Balanced Assessment"',
        '_DEFAULT_TEMPLATE = "Balanced Assessment"'
    )

    # =========================================================================
    # SIDEBAR — Replace the entire sidebar section
    # (from "with st.sidebar:" to just before the "# ──────────────" separator
    #  that precedes the nav bar injection / page header)
    # =========================================================================
    print("UI 2: Rebuilding sidebar...")

    OLD_SIDEBAR_START = "with st.sidebar:"
    # Sidebar ends at the separator before page header:
    OLD_SIDEBAR_END = "# ─────────────────────────────────────────────────────────────────────────────\nst.markdown(\n    \"\"\"\n    <div class=\"page-header\""

    sb_start = src.find(OLD_SIDEBAR_START)
    sb_end   = src.find(OLD_SIDEBAR_END, sb_start)

    if sb_start == -1 or sb_end == -1:
        print(f"  ERROR: sidebar boundaries not found (start={sb_start}, end={sb_end})")
        return

    NEW_SIDEBAR = '''with st.sidebar:
    st.markdown('<div class="sidebar-logo">HirangAI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">Choose Better. Hire Smarter.</div>', unsafe_allow_html=True)

    st.markdown(
        f\'\'\'<div style="font-size:0.75rem;color:#64748b;margin-bottom:20px;padding-left:2px;">
        Session — <strong>{st.session_state.analysis_count}</strong> candidates screened</div>\'\'\',
        unsafe_allow_html=True
    )

    # ── Assessment Profile ─────────────────────────────────────────
    st.markdown(\'<div class="section-heading">Assessment Profile</div>\', unsafe_allow_html=True)

    _all_templates: dict[str, dict] = {**BUILTIN_TEMPLATES, **st.session_state.custom_templates}
    _template_names = list(_all_templates.keys())

    _current_idx = (
        _template_names.index(st.session_state.active_template)
        if st.session_state.active_template in _template_names
        else 0
    )

    _selected = st.selectbox(
        label="Assessment Profile",
        options=_template_names,
        index=_current_idx,
        key="template_selectbox",
        help="Weights recalculate scores automatically.",
        label_visibility="collapsed",
    )

    # Apply template when selection changes
    if _selected != st.session_state.active_template:
        new_weights = dict(_all_templates[_selected]["weights"])
        st.session_state.active_template = _selected
        st.session_state.hr_weights      = new_weights
        for _k, _v in new_weights.items():
            st.session_state[f"slider_{_k}"] = _v
        st.rerun()

    _tmpl_desc = _all_templates[_selected].get("description", "")
    if _tmpl_desc:
        st.markdown(
            f\'\'\'<div style="color:#64748b;font-size:0.75rem;margin:4px 0 12px;line-height:1.5;">{_tmpl_desc}</div>\'\'\',
            unsafe_allow_html=True,
        )

    # ── Advanced Configuration (collapsed by default) ──────────────
    # Show expanded if a custom template is active or it was manually opened
    _is_custom = _selected in st.session_state.custom_templates
    _adv_expanded = _is_custom or st.session_state.get("_adv_config_open", False)

    with st.expander("Advanced Configuration", expanded=_adv_expanded):
        st.markdown(
            \'<div style="color:#64748b;font-size:0.72rem;margin-bottom:10px;">\'
            \'Adjust category weights. Total must equal 100%.</div>\',
            unsafe_allow_html=True,
        )

        _cat_config = [
            ("technical_skills",         "Technical Skills"),
            ("relevant_experience",       "Relevant Experience"),
            ("education",                 "Education"),
            ("certifications",            "Certifications"),
            ("communication_soft_skills", "Soft Skills"),
        ]

        _w = st.session_state.hr_weights
        for _key, _label in _cat_config:
            _w[_key] = st.slider(
                label=_label,
                min_value=0,
                max_value=100,
                step=5,
                key=f"slider_{_key}",
            )

        _total = sum(_w.values())
        if _total == 100:
            st.markdown(
                \'<div class="weight-total-ok">\'
                \'<span class="weight-total-label">Total Weight</span>\'
                \'<span class="weight-total-value-ok">100%</span>\'
                \'</div>\',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f\'\'\'<div class="weight-total-err">
                <span class="weight-total-label">Total Weight</span>
                <span class="weight-total-value-err">{_total}%</span>
                </div>\'\'\',
                unsafe_allow_html=True,
            )
            st.markdown(
                \'<div style="color:#f87171;font-size:0.72rem;margin-top:4px;">\'
                \'Weights must sum to 100%.</div>\',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        _btn_reset, _btn_save = st.columns(2, gap="small")
        with _btn_reset:
            if st.button("Reset", key="reset_weights", use_container_width=True):
                _reset_weights = dict(
                    _all_templates.get(st.session_state.active_template,
                                       BUILTIN_TEMPLATES[_DEFAULT_TEMPLATE])["weights"]
                )
                st.session_state.hr_weights = _reset_weights
                for _k, _v in _reset_weights.items():
                    st.session_state[f"slider_{_k}"] = _v
                st.rerun()
        with _btn_save:
            _save_clicked = st.button("Save Template", key="open_save_template", use_container_width=True)

        if _save_clicked or st.session_state.get("_save_template_open"):
            st.session_state["_save_template_open"] = True
            _new_name = st.text_input(
                "Template name",
                placeholder="e.g. Senior Dev Profile",
                key="new_template_name",
            )
            _new_desc = st.text_input(
                "Description (optional)",
                placeholder="What does this template prioritise?",
                key="new_template_desc",
            )
            _do_save, _do_cancel = st.columns(2, gap="small")
            with _do_save:
                if st.button("Save", key="confirm_save_template", use_container_width=True):
                    if _new_name.strip():
                        st.session_state.custom_templates[_new_name.strip()] = {
                            "description": _new_desc.strip() or "Custom template",
                            "weights":     dict(_w),
                        }
                        st.session_state.active_template = _new_name.strip()
                        st.session_state["_save_template_open"] = False
                        st.rerun()
                    else:
                        st.markdown(
                            \'<div style="color:#f87171;font-size:0.74rem;">\'
                            \'Enter a name for the template.</div>\',
                            unsafe_allow_html=True,
                        )
            with _do_cancel:
                if st.button("Cancel", key="cancel_save_template", use_container_width=True):
                    st.session_state["_save_template_open"] = False
                    st.rerun()

        if st.session_state.custom_templates:
            st.markdown("<br>", unsafe_allow_html=True)
            _to_delete = st.selectbox(
                "Delete template",
                options=["— select to delete —"] + list(st.session_state.custom_templates.keys()),
                key="delete_template_select",
            )
            if _to_delete != "— select to delete —":
                if st.button(f"Delete \\u2018{_to_delete}\\u2019", key="confirm_delete_template"):
                    del st.session_state.custom_templates[_to_delete]
                    if st.session_state.active_template == _to_delete:
                        st.session_state.active_template = _DEFAULT_TEMPLATE
                        st.session_state.hr_weights = dict(
                            BUILTIN_TEMPLATES[_DEFAULT_TEMPLATE]["weights"]
                        )
                    st.rerun()

    # ── AI Status ─────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        \'<div style="font-size:0.72rem;color:#64748b;padding:8px 0;border-top:1px solid rgba(255,255,255,0.05);">\'
        \'<span style="color:#059669;font-weight:600;">Active</span> — Groq llama-3.3-70b</div>\',
        unsafe_allow_html=True,
    )

'''

    src = src[:sb_start] + NEW_SIDEBAR + src[sb_end:]
    print(f"  Sidebar replaced. File size change: {len(src) - original_len:+d} bytes")
    original_len = len(src)

    # =========================================================================
    # UI 5 — Remove page header / HirangAI wordmark from content area
    # =========================================================================
    print("UI 5: Removing page header wordmark...")
    # The page header block:
    PAGE_HEADER_BLOCK = '''# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="page-header" id="top">
        <span class="page-header-brand">HirangAI</span>
        <span class="page-header-tagline">Choose Better. Hire Smarter.</span>
    </div>
    """,
    unsafe_allow_html=True,
)

'''
    if PAGE_HEADER_BLOCK in src:
        src = src.replace(PAGE_HEADER_BLOCK, "# ─────────────────────────────────────────────────────────────────────────────\n")
        print("  Page header removed.")
    else:
        print("  WARNING: Page header block not found — skipping.")

    # =========================================================================
    # UI 1 — Remove Getting Started cards, add compact pipeline status bar
    # =========================================================================
    print("UI 1: Replacing Getting Started with status bar...")
    OLD_GETTING_STARTED = '''if not st.session_state.get("batch_results"):
    st.markdown(\'<div class="section-heading">Getting Started</div>\', unsafe_allow_html=True)
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
            f\'<div class="workflow-card">\'
            f\'<div class="workflow-step-num">{_gsn}</div>\'
            f\'<div class="workflow-step-label">{_gsl}</div></div>\',
            unsafe_allow_html=True,
        )
    st.markdown("<br>", unsafe_allow_html=True)'''

    NEW_STATUS_BAR = '''# ── Pipeline status bar ──────────────────────────────────────────────────────
_jd_ready     = bool(st.session_state.get("job_description_input", "").strip())
_files_ready  = bool(st.session_state.get("resume_uploader"))
_profile_name = st.session_state.get("active_template", "Balanced Assessment")
_results_ready = bool(st.session_state.get("batch_results"))

def _step_style(active: bool) -> str:
    return (
        "font-size:0.78rem;font-weight:600;color:#f1f5f9;"
        if active else
        "font-size:0.78rem;font-weight:400;color:#475569;"
    )

_steps_html = (
    f\'\'\'<div style="display:flex;align-items:center;gap:0;padding:10px 0 18px;border-bottom:1px solid rgba(255,255,255,0.06);margin-bottom:20px;">
        <span style="{_step_style(_jd_ready)}">Job Description</span>
        <span style="margin:0 10px;color:#334155;font-size:0.75rem;">·</span>
        <span style="{_step_style(_files_ready)}">Candidates</span>
        <span style="margin:0 10px;color:#334155;font-size:0.75rem;">·</span>
        <span style="{_step_style(True)}">Assessment Profile</span>
        <span style="margin:0 10px;color:#334155;font-size:0.75rem;">·</span>
        <span style="{_step_style(_jd_ready and _files_ready)}">Analyze</span>
        <span style="margin:0 10px;color:#334155;font-size:0.75rem;">·</span>
        <span style="{_step_style(_results_ready)}">Review</span>
    </div>\'\'\'
)
st.markdown(_steps_html, unsafe_allow_html=True)'''

    if OLD_GETTING_STARTED in src:
        src = src.replace(OLD_GETTING_STARTED, NEW_STATUS_BAR)
        print("  Getting Started replaced with status bar.")
    else:
        print("  WARNING: Getting Started block not found — skipping.")

    # =========================================================================
    # UI 3 — Clean upload area (filename-only list, collapsible details)
    # =========================================================================
    print("UI 3: Redesigning upload area...")
    OLD_UPLOAD_DISPLAY = '''    if uploaded_files:
        # Parse any file not yet cached
        for _uf in uploaded_files:
            if st.session_state.get(f"parsed_{_uf.name}") is None:
                with st.spinner(f"Extracting text from {_uf.name}…"):
                    st.session_state[f"parsed_{_uf.name}"] = parse_resume(_uf.read())

        # Per-file status badges
        for _uf in uploaded_files:
            _p  = st.session_state.get(f"parsed_{_uf.name}")
            _kb = round(_uf.size / 1024, 1)
            if _p and _p.is_valid:
                st.markdown(
                    f\'<div class="success-box">\'
                    f\'✅ <strong>{_uf.name}</strong> — {_p.page_count} page(s), {_p.word_count} words\'
                    f\'<span style="opacity:0.6;font-size:0.78rem;"> &nbsp;·&nbsp; {_kb} KB</span>\'
                    f\'</div>\',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f\'<div class="warning-box">\'
                    f\'⚠️ <strong>{_uf.name}</strong> — text could not be extracted.\'
                    f\'</div>\',
                    unsafe_allow_html=True,
                )

        _n_ok = sum(
            1 for f in uploaded_files
            if st.session_state.get(f"parsed_{f.name}") and st.session_state[f"parsed_{f.name}"].is_valid
        )
        st.markdown(
            f\'<div class="info-box">📁 \'
            f\'<strong>{len(uploaded_files)}</strong> file(s) uploaded &nbsp;·&nbsp; \'
            f\'<strong>{_n_ok}</strong> parsed successfully</div>\',
            unsafe_allow_html=True,
        )
    else:
        # Clear cached parses when all files removed
        for _k in [k for k in st.session_state if k.startswith("parsed_") and k not in ("parsed_resume", "parsed_file_name")]:
            del st.session_state[_k]
        st.markdown(
            \'<div class="info-box">\'
            \'📁 No files selected yet. Upload PDF resumes to continue.\'
            \'</div>\',
            unsafe_allow_html=True,
        )'''

    NEW_UPLOAD_DISPLAY = '''    if uploaded_files:
        # Parse any file not yet cached
        for _uf in uploaded_files:
            if st.session_state.get(f"parsed_{_uf.name}") is None:
                with st.spinner(f"Parsing {_uf.name}..."):
                    st.session_state[f"parsed_{_uf.name}"] = parse_resume(_uf.read())

        _n_ok = sum(
            1 for f in uploaded_files
            if st.session_state.get(f"parsed_{f.name}") and st.session_state[f"parsed_{f.name}"].is_valid
        )
        _n_fail = len(uploaded_files) - _n_ok

        # Clean candidate list header
        st.markdown(
            f\'\'\'<div style="margin-top:12px;">
                <div style="font-size:0.72rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;
                            color:#64748b;margin-bottom:8px;">Uploaded Candidates</div>
                <div style="font-size:0.82rem;color:#94a3b8;margin-bottom:10px;">
                    <span style="color:#f1f5f9;font-weight:600;">{len(uploaded_files)}</span> uploaded
                    &nbsp;·&nbsp;
                    <span style="color:#059669;font-weight:600;">{_n_ok}</span> ready
                    {f\'&nbsp;·&nbsp;<span style="color:#dc2626;font-weight:600;">{_n_fail}</span> failed\' if _n_fail else ""}
                </div>
            </div>\'\'\',
            unsafe_allow_html=True,
        )

        # Compact filename list
        for _uf in uploaded_files:
            _p = st.session_state.get(f"parsed_{_uf.name}")
            _ok = _p and _p.is_valid
            _dot_color = "#059669" if _ok else "#dc2626"
            _name_color = "#e2e8f0" if _ok else "#94a3b8"
            st.markdown(
                f\'\'\'<div style="display:flex;align-items:center;gap:8px;padding:5px 0;
                              border-bottom:1px solid rgba(255,255,255,0.04);">
                    <span style="width:6px;height:6px;border-radius:50%;background:{_dot_color};
                                 display:inline-block;flex-shrink:0;"></span>
                    <span style="font-size:0.82rem;color:{_name_color};font-weight:500;">{_uf.name}</span>
                    {f\'<span style="font-size:0.7rem;color:#dc2626;margin-left:auto;">Could not parse</span>\' if not _ok else ""}
                </div>\'\'\',
                unsafe_allow_html=True,
            )

        # Collapsible details
        with st.expander("Show file details", expanded=False):
            for _uf in uploaded_files:
                _p  = st.session_state.get(f"parsed_{_uf.name}")
                _kb = round(_uf.size / 1024, 1)
                if _p and _p.is_valid:
                    st.markdown(
                        f\'\'\'<div style="font-size:0.78rem;color:#94a3b8;padding:4px 0;
                                      border-bottom:1px solid rgba(255,255,255,0.04);">
                            <strong style="color:#e2e8f0;">{_uf.name}</strong>
                            &nbsp;·&nbsp;{_p.page_count} page(s)
                            &nbsp;·&nbsp;{_p.word_count} words
                            &nbsp;·&nbsp;{_kb} KB
                        </div>\'\'\',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f\'\'\'<div style="font-size:0.78rem;color:#dc2626;padding:4px 0;">
                            {_uf.name} — could not extract text
                        </div>\'\'\',
                        unsafe_allow_html=True,
                    )
    else:
        # Clear cached parses when all files removed
        for _k in [k for k in st.session_state if k.startswith("parsed_") and k not in ("parsed_resume", "parsed_file_name")]:
            del st.session_state[_k]
        st.markdown(
            \'\'\'<div style="font-size:0.82rem;color:#475569;margin-top:10px;">
                No resumes uploaded yet.
            </div>\'\'\',
            unsafe_allow_html=True,
        )'''

    if OLD_UPLOAD_DISPLAY in src:
        src = src.replace(OLD_UPLOAD_DISPLAY, NEW_UPLOAD_DISPLAY)
        print("  Upload area redesigned.")
    else:
        print("  WARNING: Upload display block not found — trying partial match...")
        # Fallback: find via key marker
        idx = src.find("# Per-file status badges")
        if idx != -1:
            print(f"  Found 'Per-file status badges' at char {idx} — manual inspection needed.")
        else:
            print("  SKIP: upload display block not replaced.")

    # =========================================================================
    # UI 4 — Full-width Analyze button with disabled state + validation messages
    # Bug 1 — Add st.rerun() after persisting batch results
    # Bug 2 — Fix uploaded_files reference
    # =========================================================================
    print("UI 4 + Bug 1 + Bug 2: Replacing button + validation + evaluation block...")

    OLD_BUTTON_SECTION = '''# ─────────────────────────────────────────────────────────────────────────────
# Analyse button
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("<br>", unsafe_allow_html=True)

btn_col, _ = st.columns([1, 2])
with btn_col:
    _n_valid = sum(
        1 for f in (uploaded_files if "uploaded_files" in dir() else [])
        if st.session_state.get(f"parsed_{f.name}") and st.session_state[f"parsed_{f.name}"].is_valid
    )
    _btn_label = (
        f"🚀 Analyse {_n_valid} Candidate{\'s\' if _n_valid != 1 else \'\'}"
        if _n_valid > 0 else "🚀 Analyse Candidate"
    )
    analyse_clicked = st.button(
        _btn_label,
        key="analyse_button",
        help="Run AI-powered evaluation on all uploaded resumes against the job description.",
    )

# ─────────────────────────────────────────────────────────────────────────────
# Validation + evaluation
# ─────────────────────────────────────────────────────────────────────────────

if analyse_clicked:
    if not job_description.strip():
        st.markdown(
            \'<div class="warning-box">⚠️ Please enter a <strong>job description</strong> before analysing.</div>\',
            unsafe_allow_html=True,
        )
    elif not uploaded_files:
        st.markdown(
            \'<div class="warning-box">⚠️ Please <strong>upload at least one PDF resume</strong> before analysing.</div>\',
            unsafe_allow_html=True,
        )
    else:
        _valid_pairs = [
            (f, st.session_state[f"parsed_{f.name}"])
            for f in uploaded_files
            if st.session_state.get(f"parsed_{f.name}") and st.session_state[f"parsed_{f.name}"].is_valid
        ]
        if not _valid_pairs:
            st.markdown(
                \'<div class="warning-box">⚠️ No resumes could be parsed. Please upload valid PDF files.</div>\',
                unsafe_allow_html=True,
            )
        else:
            _batch_results: list[dict] = []
            _progress = st.progress(0, text="Preparing analysis…")
            for _i, (_uf, _parsed) in enumerate(_valid_pairs):
                _pct = _i / len(_valid_pairs)
                _name = _parsed.candidate_name or _uf.name.replace(".pdf", "")
                _progress.progress(_pct, text=f"🧠 Evaluating {_name} ({_i + 1}/{len(_valid_pairs)})…")
                with st.spinner(f"Analysing {_name}…"):
                    _res = evaluate_candidate(
                        job_description=job_description,
                        parsed_resume=_parsed,
                    )
                _batch_results.append({"file": _uf.name, "result": _res})

            _progress.progress(1.0, text=f"✅ Analysed {len(_batch_results)} candidate(s)")

            # Persist batch
            st.session_state.batch_results   = _batch_results
            st.session_state.last_result      = _batch_results[-1]["result"]  # compat
            st.session_state.last_file_name   = _batch_results[-1]["file"]

            # Update sidebar stats
            _successful = [r for r in _batch_results if not r["result"].errors and r["result"].recommendation]
            st.session_state.analysis_count += len(_successful)
            if _successful:
                _top = max(_successful, key=lambda r: r["result"].match_score or 0)
                st.session_state.last_candidate = _top["result"].candidate_name or _top["file"]
                _ts = _top["result"].match_score
                st.session_state.last_score = f"{_ts}/100" if _ts is not None else _top["result"].recommendation'''

    NEW_BUTTON_SECTION = '''# ─────────────────────────────────────────────────────────────────────────────
# Analyse button + evaluation pipeline
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("<div style=\'margin-top:20px;\'></div>", unsafe_allow_html=True)

# Determine readiness state
_uploaded_files_safe = uploaded_files if uploaded_files else []
_n_valid = sum(
    1 for f in _uploaded_files_safe
    if st.session_state.get(f"parsed_{f.name}") and st.session_state[f"parsed_{f.name}"].is_valid
)
_jd_ok    = bool(job_description.strip())
_files_ok = _n_valid > 0
_can_run  = _jd_ok and _files_ok

# Validation message shown above button
if not _jd_ok:
    st.markdown(
        \'<div style="font-size:0.8rem;color:#64748b;margin-bottom:8px;padding:8px 12px;\'
        \'background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:6px;">\'
        \'Enter a job description to continue.</div>\',
        unsafe_allow_html=True,
    )
elif not _files_ok:
    st.markdown(
        \'<div style="font-size:0.8rem;color:#64748b;margin-bottom:8px;padding:8px 12px;\'
        \'background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:6px;">\'
        \'Upload at least one PDF resume to continue.</div>\',
        unsafe_allow_html=True,
    )

# Primary full-width button
_btn_label = (
    f"Analyze {_n_valid} Candidate{\'s\' if _n_valid != 1 else \'\'}"
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
# Evaluation pipeline
# ─────────────────────────────────────────────────────────────────────────────

if analyse_clicked and _can_run:
    _valid_pairs = [
        (f, st.session_state[f"parsed_{f.name}"])
        for f in _uploaded_files_safe
        if st.session_state.get(f"parsed_{f.name}") and st.session_state[f"parsed_{f.name}"].is_valid
    ]
    if not _valid_pairs:
        st.error("No resumes could be parsed. Please upload valid PDF files.")
    else:
        _batch_results: list[dict] = []
        _progress = st.progress(0, text="Starting evaluation...")
        _status_placeholder = st.empty()

        for _i, (_uf, _parsed) in enumerate(_valid_pairs):
            _pct  = _i / len(_valid_pairs)
            _name = _parsed.candidate_name or _uf.name.replace(".pdf", "")
            _progress.progress(_pct, text=f"Evaluating {_name} ({_i + 1} of {len(_valid_pairs)})...")
            _status_placeholder.markdown(
                f\'\'\'<div style="font-size:0.8rem;color:#64748b;padding:6px 0;">
                    Analyzing <strong style="color:#f1f5f9;">{_name}</strong>...</div>\'\'\',
                unsafe_allow_html=True,
            )
            try:
                _res = evaluate_candidate(
                    job_description=job_description,
                    parsed_resume=_parsed,
                )
            except Exception as _eval_err:
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

        # Persist results to session state
        st.session_state.batch_results  = _batch_results
        st.session_state.last_result    = _batch_results[-1]["result"]
        st.session_state.last_file_name = _batch_results[-1]["file"]

        # Update session counters
        _successful = [r for r in _batch_results if not r["result"].errors and r["result"].recommendation]
        st.session_state.analysis_count += len(_successful)
        if _successful:
            _top = max(_successful, key=lambda r: r["result"].match_score or 0)
            st.session_state.last_candidate = _top["result"].candidate_name or _top["file"]
            _ts  = _top["result"].match_score
            st.session_state.last_score = f"{_ts}/100" if _ts is not None else _top["result"].recommendation

        # ── Critical: rerun so results display block sees new session state ──
        st.rerun()'''

    if OLD_BUTTON_SECTION in src:
        src = src.replace(OLD_BUTTON_SECTION, NEW_BUTTON_SECTION)
        print("  Button + evaluation pipeline replaced (bugs fixed, rerun added).")
    else:
        print("  WARNING: Button section not found — trying to locate manually...")
        idx = src.find("btn_col, _ = st.columns([1, 2])")
        print(f"  btn_col index: {idx}")

    # =========================================================================
    # CSS additions — disabled button opacity, status bar, reduced br bloat
    # =========================================================================
    print("UI 7: CSS polish...")

    OLD_CSS_END = """    </style>
    \"\"\",
    unsafe_allow_html=True,
)"""

    NEW_CSS_ADDITIONS = """
    /* Disabled button state */
    .stButton > button:disabled { opacity: 0.35 !important; cursor: not-allowed !important; }
    .stButton > button:disabled:hover { background: #4f46e5 !important; transform: none !important; }

    /* Pipeline status bar */
    .pipeline-status { display: flex; align-items: center; gap: 0; padding: 10px 0 18px;
                       border-bottom: 1px solid rgba(255,255,255,0.06); margin-bottom: 20px; }

    /* Compact upload list dot */
    .upload-dot-ok   { width: 6px; height: 6px; border-radius: 50%; background: #059669; display: inline-block; }
    .upload-dot-fail { width: 6px; height: 6px; border-radius: 50%; background: #dc2626; display: inline-block; }

    /* Sidebar expander clean look */
    [data-testid="stSidebar"] .stExpander { border: 1px solid rgba(255,255,255,0.07) !important;
                                             border-radius: 6px !important; margin-top: 6px; }
    [data-testid="stSidebar"] .stExpander summary { font-size: 0.8rem !important; color: #94a3b8 !important;
                                                      font-weight: 500 !important; }

    /* Weight total badges */
    .weight-total-ok, .weight-total-err { border-radius: 5px; padding: 7px 12px; margin: 8px 0; }

    /* Tighter glass card */
    .glass-card, .card { padding: 16px 18px !important; }

    /* Job description card label + title spacing */
    .card-label { margin-bottom: 2px !important; }
    .card-title { margin-bottom: 6px !important; }
    </style>
    \"\"\",
    unsafe_allow_html=True,
)"""

    if OLD_CSS_END in src:
        src = src.replace(OLD_CSS_END, NEW_CSS_ADDITIONS)
        print("  CSS additions injected.")
    else:
        print("  WARNING: CSS end marker not found — skipping CSS additions.")

    # =========================================================================
    # Remove JD "info-box" with folder emoji (minor cleanup)
    # =========================================================================
    src = src.replace(
        "f'<div class=\"info-box\">Job description loaded &nbsp;·&nbsp; '\n"
        "            f'<strong>{jd_word_count}</strong> words</div>'",
        "f'<div style=\"font-size:0.78rem;color:#64748b;margin-top:6px;\">'\n"
        "            f'<strong style=\"color:#f1f5f9;\">{jd_word_count}</strong> words · Job description ready</div>'"
    )

    # =========================================================================
    # Verify syntax
    # =========================================================================
    print("\nVerifying syntax...")
    try:
        ast.parse(src)
        print("Syntax: OK")
    except SyntaxError as e:
        print(f"SYNTAX ERROR: {e}")
        print(f"  Line {e.lineno}: {e.text}")
        sys.exit(1)

    with open("app.py", "w", encoding="utf-8") as f:
        f.write(src)
    print(f"\napp.py written successfully. Final size: {len(src):,} bytes")


if __name__ == "__main__":
    main()
