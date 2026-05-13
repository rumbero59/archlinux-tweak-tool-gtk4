#!/usr/bin/env python3
"""
ATT Log Coverage Audit
Finds on_* callbacks that have no fn.log_* or fn.show_in_app_notification call.
Run from project root: python3 audit_log_coverage.py
"""
import ast
from pathlib import Path

LOG_ATTRS = {
    'log_section', 'log_subsection', 'log_info', 'log_item',
    'log_info_concise', 'log_success', 'log_warn', 'log_tip',
    'log_error', 'show_in_app_notification', 'debug_print',
}

# Functions that always call a log_* internally — callbacks delegating to these are covered
LOG_DELEGATES = {
    'open_url_in_browser',
    'install_package',
    'install_discovery',
    'remove_discovery',
    'install_samba',
    'uninstall_samba',
}

SKIP_PREFIXES = (
    'on_map', 'on_unmap', 'on_draw', 'on_realize', 'on_unrealize',
    'on_size_allocate', 'on_notify', 'on_key_', 'on_motion_',
    'on_enter_', 'on_leave_', 'on_scroll_', 'on_focus_',
)

# Exact names intentionally excluded: pure UI-state callbacks with no user-visible action
SKIP_EXACT = {
    'on_comment_changed',  # enables button based on text length — no action
    'on_response',         # dialog return-value wrapper — no action
}


def _has_log_call(func_node):
    for child in ast.walk(func_node):
        if not isinstance(child, ast.Call):
            continue
        func = child.func
        if isinstance(func, ast.Attribute) and func.attr in LOG_ATTRS | LOG_DELEGATES:
            return True
        if isinstance(func, ast.Name) and func.id in LOG_ATTRS | LOG_DELEGATES:
            return True
    return False


def audit_file(filepath):
    try:
        source = filepath.read_text(encoding='utf-8')
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError as e:
        return None, f"PARSE ERROR: {e}"

    all_cb, missing = [], []

    # Only check class methods and module-level functions; skip nested closures
    # (nested on_response / on_lock_response are GTK dialog handlers, not user callbacks)
    for node in tree.body:
        candidates = []
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            candidates = [node]
        elif isinstance(node, ast.ClassDef):
            candidates = [
                n for n in node.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
        for fn_node in candidates:
            if not fn_node.name.startswith('on_'):
                continue
            all_cb.append(fn_node.name)
            if fn_node.name.startswith(SKIP_PREFIXES) or fn_node.name in SKIP_EXACT:
                continue
            if not _has_log_call(fn_node):
                missing.append((fn_node.lineno, fn_node.name))

    return (all_cb, missing), None


def main():
    base = Path(__file__).parent / 'usr/share/archlinux-tweak-tool'
    py_files = sorted(base.glob('*.py'))

    total_cb = 0
    total_missing = 0
    file_results = {}

    for pyfile in py_files:
        result, err = audit_file(pyfile)
        if err:
            print(f"[!] {pyfile.name}: {err}")
            continue
        all_cb, missing = result
        total_cb += len(all_cb)
        total_missing += len(missing)
        if missing:
            file_results[pyfile.name] = missing

    if not file_results:
        print(f"All {total_cb} audited callbacks have log coverage.")
        return

    for filename in sorted(file_results):
        print(f"\n{filename}")
        for lineno, name in sorted(file_results[filename]):
            print(f"  {lineno:4d}  {name}")

    sep = '=' * 60
    print(f"\n{sep}")
    covered = total_cb - total_missing
    print(f"Covered : {covered} / {total_cb}")
    print(f"Missing : {total_missing} / {total_cb}")
    print(sep)


if __name__ == '__main__':
    main()
