import os
import sys

from breadcrumb_validation import validate_breadcrumb_content


SKIPPED_FILES = {"index.html", "404.html", "de/index.html", "de/404.html"}


def audit_breadcrumbs(root_dir):
    print(f"--- Breadcrumb Deep Audit [Cortex-v3] ---\n")
    print(f"Scanning {root_dir}...")

    issues = []
    valid_files = 0
    total_files = 0

    for subdir, dirs, files in os.walk(root_dir):
        dirs[:] = [name for name in dirs if name not in {".git", "node_modules"}]
        for file in files:
            if not file.endswith(".html"):
                continue

            total_files += 1
            filepath = os.path.join(subdir, file)
            rel_path = os.path.relpath(filepath, root_dir).replace("\\", "/")

            if rel_path in SKIPPED_FILES:
                continue

            try:
                with open(filepath, "r", encoding="utf-8") as handle:
                    file_issues = validate_breadcrumb_content(handle.read(), rel_path)
                    if file_issues:
                        issues.append((rel_path, file_issues))
                    else:
                        valid_files += 1
            except Exception as exc:
                issues.append((rel_path, [f"Error processing file: {exc}"]))

    print(f"\nAudit complete.")
    print(f"Total HTML files analyzed: {total_files}")
    print(f"Files with Perfect Breadcrumbs: {valid_files}")
    print(f"Files with Issues: {len(issues)}")

    if issues:
        print("\n--- DETAILED ISSUES ---")
        for file, file_issues in sorted(issues):
            print(f"\n[FILE] {file}")
            for msg in file_issues:
                print(f"  - {msg}")

    return len(issues)


if __name__ == "__main__":
    issue_count = audit_breadcrumbs(os.getcwd())
    sys.exit(1 if issue_count else 0)
