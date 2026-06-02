import re

with open('app.py', encoding='utf-8') as f:
    src = f.read()

# Check 1: st.rerun() after batch results
batch_persist_idx = src.find('st.session_state.batch_results  = _batch_results')
if batch_persist_idx != -1:
    after_block = src[batch_persist_idx:batch_persist_idx+800]
    if 'st.rerun()' in after_block:
        print('CHECK 1 PASS: st.rerun() found after batch_results persist')
    else:
        print('CHECK 1 FAIL: st.rerun() NOT found after batch_results persist')
else:
    print('CHECK 1 WARN: batch_results assign not found')

# Check 2: No more unreliable dir() check
if '"uploaded_files" in dir()' not in src:
    print('CHECK 2 PASS: Unreliable dir() check removed')
else:
    print('CHECK 2 FAIL: dir() check still present')

# Check 3: No TalentLens references
if 'talentlens' not in src.lower():
    print('CHECK 3 PASS: No TalentLens references remain')
else:
    print('CHECK 3 FAIL: TalentLens still present')

# Check 4: Emoji template names gone from BUILTIN_TEMPLATES
emoji_pattern = re.compile(r'[\U0001F300-\U0001FFFF]')
builtin_idx = src.find('BUILTIN_TEMPLATES')
builtin_block = src[builtin_idx:builtin_idx+800]
if not emoji_pattern.search(builtin_block):
    print('CHECK 4 PASS: No emoji in BUILTIN_TEMPLATES')
else:
    print('CHECK 4 FAIL: Emoji still in BUILTIN_TEMPLATES')

# Check 5: Button is full width
btn_idx = src.find('"analyse_button"')
if btn_idx != -1 and 'use_container_width=True' in src[btn_idx:btn_idx+200]:
    print('CHECK 5 PASS: use_container_width=True on analyse button')
else:
    print('CHECK 5 FAIL: button missing use_container_width')

# Check 6: Advanced Configuration expander
if 'Advanced Configuration' in src:
    print('CHECK 6 PASS: Advanced Configuration expander found')
else:
    print('CHECK 6 FAIL: Advanced Configuration expander missing')

# Check 7: Getting Started removed
if '"Getting Started"' not in src and "'Getting Started'" not in src:
    print('CHECK 7 PASS: Getting Started cards removed')
else:
    print('CHECK 7 FAIL: Getting Started still present')

# Check 8: Page header wordmark removed
if 'page-header-brand' not in src:
    print('CHECK 8 PASS: Duplicate page header removed')
else:
    print('CHECK 8 FAIL: page-header-brand still present')

# Check 9: disabled=not _can_run on button
if 'disabled=not _can_run' in src:
    print('CHECK 9 PASS: Button has disabled= state')
else:
    print('CHECK 9 FAIL: Button missing disabled= state')

print()
print(f'Total lines: {src.count(chr(10)):,}')
print(f'Total size:  {len(src):,} bytes')
