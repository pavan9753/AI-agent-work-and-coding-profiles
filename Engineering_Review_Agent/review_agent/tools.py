"""Small deterministic pre-review signals for pasted unified diffs."""

from __future__ import annotations

import json
import re

_FILE_HEADER = re.compile(r"^diff --git a/(.+?) b/(.+)$")
_NEW_LINE_HEADER = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")
_SECRET_PATTERNS = (
    re.compile(r"(?i)(?:api[_-]?key|client[_-]?secret|password|token)\s*[:=]\s*['\"]?[^\s'\"]{8,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
)
_DESTRUCTIVE_PATTERNS = (
    re.compile(r"(?i)\bDROP\s+(?:TABLE|DATABASE|SCHEMA)\b"),
    re.compile(r"(?i)\bTRUNCATE\s+TABLE\b"),
    re.compile(r"(?i)\bdeleteMany\s*\("),
    re.compile(r"(?i)\brm\s+-rf\b"),
)
_RISKY_PATH_PARTS = ("auth", "security", "payment", "migration", "migrations", "permission", "credential")


def inspect_diff(diff_text: str) -> str:
    """Summarize changed paths and surface secret-like and destructive added lines.

    Pass a unified diff as ``diff_text``. The function is deterministic; it does not execute code,
    read the filesystem, or send the diff to a service. Secret values are never returned.
    """
    if not isinstance(diff_text, str) or not diff_text.strip():
        return json.dumps({"error": "Provide a non-empty unified diff."})

    text = diff_text[:200_000]
    files: list[str] = []
    signals: list[dict[str, object]] = []
    added_lines = 0
    current_file = "(unknown file)"
    new_line = 0

    for line in text.splitlines():
        file_match = _FILE_HEADER.match(line)
        if file_match:
            current_file = file_match.group(2)
            if current_file not in files:
                files.append(current_file)
            continue
        line_match = _NEW_LINE_HEADER.match(line)
        if line_match:
            new_line = int(line_match.group(1))
            continue
        if line.startswith("+") and not line.startswith("+++"):
            added_lines += 1
            content = line[1:]
            for pattern in _SECRET_PATTERNS:
                if pattern.search(content):
                    signals.append({"type": "secret_like_value", "file": current_file, "line": new_line,
                                    "message": "Added line matches a credential or private-key pattern; value omitted."})
                    break
            for pattern in _DESTRUCTIVE_PATTERNS:
                if pattern.search(content):
                    signals.append({"type": "destructive_operation", "file": current_file, "line": new_line,
                                    "message": "Added line contains a destructive command or data operation."})
                    break
            new_line += 1
        elif line.startswith("-") and not line.startswith("---"):
            continue
        elif not line.startswith("\\"):
            new_line += 1

    risky_paths = [path for path in files if any(part in path.lower() for part in _RISKY_PATH_PARTS)]
    result = {
        "files_changed": files,
        "file_count": len(files),
        "added_line_count": added_lines,
        "diff_truncated_for_scan": len(diff_text) > len(text),
        "sensitive_area_paths": risky_paths,
        "signals": signals,
        "note": "Signals are heuristics. Review the diff and project context before drawing conclusions.",
    }
    return json.dumps(result)
