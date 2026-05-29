#!/usr/bin/env python3
"""Cross-platform validator for trellis-mcu-templates.

Replaces scripts/validate.ps1. Run with `python scripts/validate.py`.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FAILURES: list[str] = []


def fail(message: str) -> None:
    FAILURES.append(message)


def read_text(rel_path: str) -> str:
    return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def assert_contains(text: str, pattern: str, message: str, *, flags: int = 0) -> None:
    if not re.search(pattern, text, flags):
        fail(message)


def assert_not_contains(text: str, pattern: str, message: str, *, flags: int = 0) -> None:
    if re.search(pattern, text, flags):
        fail(message)


def assert_substring(text: str, needle: str, message: str) -> None:
    if needle not in text:
        fail(message)


# ---------------------------------------------------------------------------
# 1. index.json structural checks
# ---------------------------------------------------------------------------

index_path = REPO_ROOT / "index.json"
if not index_path.exists():
    fail("index.json is missing")
else:
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
        for template in index.get("templates", []):
            tid = template.get("id")
            if not tid:
                fail("Template entry is missing id")
                continue
            if not template.get("type"):
                fail(f"Template '{tid}' is missing type")
            tpath = template.get("path")
            if not tpath:
                fail(f"Template '{tid}' is missing path")
                continue
            template_dir = REPO_ROOT / tpath
            if not template_dir.exists():
                fail(f"Template '{tid}' path does not exist: {tpath}")
            if template.get("type") == "skill":
                skill_path = template_dir / "SKILL.md"
                if not skill_path.exists():
                    fail(f"Skill template '{tid}' is missing SKILL.md")
                else:
                    skill_text = skill_path.read_text(encoding="utf-8")
                    pattern = rf"^---\s*\r?\nname:\s*{re.escape(tid)}\s*\r?\ndescription:"
                    if not re.search(pattern, skill_text):
                        fail(f"Skill '{tid}' frontmatter name/description is missing or mismatched")
    except json.JSONDecodeError as exc:
        fail(f"index.json is not valid JSON: {exc}")


# ---------------------------------------------------------------------------
# 2. Load all text bodies once
# ---------------------------------------------------------------------------

readme = read_text("README.md")
index_text = read_text("index.json")
skill = read_text("skills/mcu-bootstrap/SKILL.md")
checklist = read_text("docs/bootstrap-checklist.md")
version_control = read_text("specs/mcu-stm32-base/firmware/version-control.md")
coding_standard = read_text("specs/mcu-stm32-base/firmware/coding-standard.md")
pitfalls = read_text("specs/mcu-stm32-base/firmware/pitfalls.md")
pitfalls_index = read_text("specs/mcu-stm32-base/firmware/pitfalls-index.md")
firmware_index = read_text("specs/mcu-stm32-base/firmware/index.md")
project_context = read_text("specs/mcu-stm32-base/firmware/project-context.md")
directory_structure = read_text("specs/mcu-stm32-base/firmware/directory-structure.md")
verification = read_text("specs/mcu-stm32-base/firmware/verification.md")
memory_placement = read_text("specs/mcu-stm32-base/firmware/memory-placement.md")
uart_dma_protocol = read_text("specs/mcu-stm32-base/firmware/uart-dma-protocol.md")
freertos_ownership = read_text("specs/mcu-stm32-base/firmware/freertos-task-ownership.md")
ui_display = read_text("specs/mcu-stm32-base/firmware/ui-display.md")
storage_persistence = read_text("specs/mcu-stm32-base/firmware/storage-persistence.md")
command_contracts = read_text("specs/mcu-stm32-base/firmware/command-contracts.md")
guides_index = read_text("specs/mcu-stm32-base/guides/index.md")
data_flow_guide = read_text("specs/mcu-stm32-base/guides/firmware-data-flow-guide.md")
reuse_guide = read_text("specs/mcu-stm32-base/guides/firmware-reuse-guide.md")
task_process = read_text("specs/mcu-stm32-base/guides/task-process.md")
feedback_loop = read_text("docs/pitfall-feedback-loop.md")
external_kb = read_text("docs/external-knowledge-base.md")
push_all = read_text("scripts/push-all.sh")

generic_template_text = "\n".join([
    readme, index_text, skill, checklist,
    version_control, coding_standard,
    pitfalls, pitfalls_index, firmware_index,
    project_context, directory_structure, verification,
    memory_placement, uart_dma_protocol, freertos_ownership,
    ui_display, storage_persistence, command_contracts,
    guides_index, data_flow_guide, reuse_guide, task_process,
    feedback_loop, external_kb,
])


# ---------------------------------------------------------------------------
# 3. Generic content hygiene (project-specific wording, default toolchain)
# ---------------------------------------------------------------------------

# Chinese words assembled at runtime so this file itself doesn't trip the check.
def chars(*code_points: int) -> str:
    return "".join(chr(cp) for cp in code_points)


_company = chars(0x516C, 0x53F8)         # 公司
_mainstream = chars(0x4E3B, 0x6D41)       # 主流
_default = chars(0x9ED8, 0x8BA4)          # 默认
_project = chars(0x9879, 0x76EE)          # 项目

org_specific_patterns = [
    re.escape(chars(0x5408, 0x9CB8)),
    re.escape(chars(0x5317, 0x4EAC, 0x5408, 0x9CB8)),
    "90%",
    "company C coding",
    re.escape(f"{_company} MCU"),
    re.escape(_company + chars(0x7EA7)),
    re.escape(_company + chars(0x4E3B, 0x7EBF)),
    re.escape(_company + chars(0x6807, 0x51C6)),
    re.escape(_company + chars(0x5185, 0x7F51)),
    re.escape(f"{_company} SVN"),
    re.escape(_company + chars(0x5F00, 0x53D1, 0x8005)),
]
toolchain_default_patterns = [
    r"STM32CubeIDE\+GCC legacy",
    "CubeIDE legacy",
    "legacy CubeIDE",
    re.escape(f"IAR {_mainstream}"),
    re.escape(_mainstream + _project),
    rf"{_default}.*IAR",
    rf"IAR.*{_default}",
]

assert_not_contains(generic_template_text, "|".join(org_specific_patterns),
                    "template text should avoid organization-specific wording")
assert_not_contains(generic_template_text, r"FatFs|FATFS|LVGL|lvgl|fatfs",
                    "template text should not imply FatFs/LVGL-specific defaults")
assert_not_contains(generic_template_text, "|".join(toolchain_default_patterns),
                    "template text should not make IAR the default or CubeIDE a legacy exception")


# ---------------------------------------------------------------------------
# 4. README.md checks
# ---------------------------------------------------------------------------

for tid in ("mcu-stm32-base", "mcu-bootstrap"):
    assert_contains(readme, re.escape(tid), f"README.md does not mention template id '{tid}'")

assert_not_contains(readme, r"192\.168\.", "README.md should not hard-code an internal registry IP")
assert_contains(readme, r"<registry-url>", "README.md should use the <registry-url> placeholder")
assert_contains(readme, r"pitfalls\.md", "README.md should document the pitfall knowledge base")
assert_contains(readme, r"pitfalls-<category>\.md", "README.md should document the per-category pitfall split convention")
assert_contains(readme, r"pitfall-feedback-loop\.md", "README.md should document the pitfall feedback loop")
assert_contains(readme, r"external-knowledge-base\.md", "README.md should document external knowledge base guidance")
assert_contains(readme, r"firmware-data-flow-guide\.md", "README.md should document the firmware data-flow guide")
assert_contains(readme, r"firmware-reuse-guide\.md", "README.md should document the firmware reuse guide")
assert_contains(readme, r"session_auto_commit", "README.md should mention Trellis config/session guidance")
assert_not_contains(readme, r"storage-fatfs\.md|display-data\.md", "README.md should use generic optional-domain spec names")
assert_contains(readme, r"scripts/validate\.py", "README.md should reference the cross-platform validate.py")
assert_not_contains(readme, r"scripts/validate\.ps1",
                    "README.md should no longer reference the removed validate.ps1")


# ---------------------------------------------------------------------------
# 5. Skill / checklist content rules
# ---------------------------------------------------------------------------

assert_contains(skill, "MCU-BOOTSTRAP:STARTED", "mcu-bootstrap should use an in-progress marker for recoverable bootstrap runs")
assert_contains(skill, "MCU-BOOTSTRAP:DONE", "mcu-bootstrap should still write a final DONE marker")
assert_contains(skill, "MCU-BOOTSTRAP:MODE", "mcu-bootstrap should persist the collaboration mode as a marker")
assert_contains(skill, "COLLABORATION_MODE", "mcu-bootstrap should prompt for COLLABORATION_MODE")
assert_contains(skill, "PowerShell", "mcu-bootstrap should include Windows PowerShell command variants")
assert_contains(skill, "Bash", "mcu-bootstrap should include Bash command variants")
assert_contains(skill, "git remote set-url origin", "mcu-bootstrap should handle existing origin remotes")
assert_contains(skill, "session_auto_commit", "mcu-bootstrap should mention Trellis config/session auto-commit guidance")
assert_contains(skill, "TASK_JSON_PATH", "mcu-bootstrap should mention generic task hook contract")
assert_not_contains(skill, "AskUserQuestion", "mcu-bootstrap should not require an agent-specific AskUserQuestion tool")

assert_contains(checklist, "Windows PowerShell", "bootstrap checklist should include Windows PowerShell command variants")
assert_contains(checklist, r"\{\{TODAY_YYYYMMDD\}\}", "bootstrap checklist should use a date placeholder instead of a fixed date")
assert_not_contains(checklist, "20260527", "bootstrap checklist should not contain a fixed generated date")
assert_not_contains(checklist, r"git push -u origin main", "bootstrap checklist should not push during bootstrap")
assert_contains(checklist, r"svn:ignore.*basename", "bootstrap checklist should clarify SVN ignore basename behavior")
assert_contains(checklist, "session_auto_commit", "bootstrap checklist should cover Trellis config session_auto_commit")
assert_contains(checklist, "TASK_JSON_PATH", "bootstrap checklist should document generic task hook environment")
assert_contains(checklist, r"journal-\*\.md", "bootstrap checklist should document local journal ignore rules")


# ---------------------------------------------------------------------------
# 6. Automation script checks
# ---------------------------------------------------------------------------

assert_not_contains(push_all, r"pr create[\s\S]{0,300}--fill",
                    "push-all.sh should not use gh pr create --fill with a remote-only PR branch")
assert_contains(push_all, r"GIT_TERMINAL_PROMPT=0",
                "push-all.sh should disable interactive git prompts during automation")
assert_contains(push_all, r"GCM_INTERACTIVE=never",
                "push-all.sh should keep Git Credential Manager non-interactive during automation")
assert_contains(push_all, r"PUSH_TIMEOUT_SECONDS",
                "push-all.sh should bound git push duration so one remote cannot block the workflow")
assert_contains(push_all, r"timeout \"\$PUSH_TIMEOUT_SECONDS\" git push",
                "push-all.sh should run git push through timeout when available")
assert_contains(push_all, r"wait_for_pr_checks_to_appear",
                "push-all.sh should wait for GitHub checks to be registered before watching them")
assert_contains(push_all, r"CHECK_DISCOVERY_TIMEOUT_SECONDS",
                "push-all.sh should bound how long it waits for GitHub checks to appear")
assert_contains(push_all, r"mark_failed\(\)",
                "push-all.sh should de-duplicate failed remotes before printing remediation commands")
assert_not_contains(push_all, r'FAILED\+=\("\$r\(待 sync\)"\)',
                    "push-all.sh should keep retryable remote names executable in failure summaries")

# .gitignore order check inside the checklist
m = re.search(r"```gitignore\s*(.*?)```", checklist, flags=re.DOTALL)
if m:
    block = m.group(1)
    hex_idx = block.find("*.hex")
    unignore_idx = block.find("!Bin/*.hex")
    if hex_idx < 0 or unignore_idx < 0 or unignore_idx < hex_idx:
        fail("IAR .gitignore example should ignore '*.hex' before unignoring '!Bin/*.hex'")
else:
    fail("Could not find IAR gitignore block in bootstrap checklist")


# ---------------------------------------------------------------------------
# 6. Spec-file presence and content checks
# ---------------------------------------------------------------------------

assert_contains(version_control, "PowerShell", "version-control.md should include PowerShell examples for Windows users")
assert_contains(version_control, r"\.trellis/workspace/\*/journal-\*\.md",
                "version-control.md should clarify shared Trellis content vs local Trellis runtime ignore rules")
assert_not_contains(version_control, "20260527", "version-control.md should use date placeholders instead of fixed dates")
assert_contains(version_control, "basename", "version-control.md should clarify SVN ignore basename behavior")

assert_contains(coding_standard, r"\{\{PROJECT_YEAR\}\}", "coding-standard.md should use a project year placeholder")
assert_contains(coding_standard, r"pitfalls\.md", "coding-standard.md should link to pitfalls.md")
assert_contains(coding_standard, "USER CODE BEGIN/END", "coding-standard.md should mention generated-code USER CODE boundaries")
assert_contains(coding_standard, "Markdown", "coding-standard.md should require source comment and Markdown sync")
assert_contains(coding_standard, "ref_docs", "coding-standard.md should explain local reference distillation")

assert_contains(firmware_index, r"pitfalls-index\.md", "firmware index should link to pitfalls-index.md")
assert_contains(firmware_index, r"pitfalls\.md", "firmware index should link to pitfalls.md")
assert_not_contains(firmware_index, r"storage-fatfs\.md|display-data\.md",
                    "firmware index should use generic optional-domain spec names")
assert_not_contains(firmware_index, re.escape("pitfalls/README.md"),
                    "firmware index should no longer link to the removed pitfalls/README.md")
assert_contains(firmware_index, r"Tier 1",
                "firmware index should expose a tiered reading list (Tier 1 = minimum required)")
assert_contains(firmware_index, r"Tier 2",
                "firmware index should keep all other specs in Tier 2 trigger table")
for fname in (
    "project-context.md", "directory-structure.md", "verification.md",
    "memory-placement.md", "uart-dma-protocol.md", "freertos-task-ownership.md",
    "ui-display.md", "storage-persistence.md", "command-contracts.md",
):
    assert_contains(firmware_index, re.escape(fname), f"firmware index should link to {fname}")

assert_contains(project_context, "MCU", "project-context.md should capture MCU/toolchain context")
assert_contains(project_context, "ref_docs", "project-context.md should mention ignored local reference inputs")
assert_contains(directory_structure, "USER CODE BEGIN/END", "directory-structure.md should document generated code boundaries")
assert_contains(directory_structure, "IAR", "directory-structure.md should document IDE project synchronization")
assert_contains(verification, "Required Checks By Change Type", "verification.md should include a change-type check matrix")
assert_contains(verification, "Markdown Sync Check", "verification.md should include Markdown sync checks")
assert_contains(memory_placement, "DMA And Cache Rules", "memory-placement.md should include DMA/cache rules")
assert_contains(memory_placement, "Map-File Check", "memory-placement.md should include map-file checks")
assert_contains(uart_dma_protocol, "Receive Path Rules", "uart-dma-protocol.md should include receive path rules")
assert_contains(uart_dma_protocol, "Vendor Library Portability Boundary",
                "uart-dma-protocol.md should include HAL/vendor portability boundaries")
assert_contains(freertos_ownership, "Queue And Buffer Ownership", "freertos-task-ownership.md should include queue and buffer ownership")
assert_contains(freertos_ownership, "Watchdog Rules", "freertos-task-ownership.md should include watchdog rules")
assert_contains(ui_display, "Optional UI", "ui-display.md should be framed as optional UI/display guidance")
assert_contains(ui_display, "Generated UI Code", "ui-display.md should include generated UI code boundaries")
assert_contains(ui_display, "Display-Backed Command Rules", "ui-display.md should include display-backed command rules")
assert_contains(storage_persistence, "Optional Storage", "storage-persistence.md should be framed as optional storage/persistence guidance")
assert_contains(storage_persistence, "Mount Ownership", "storage-persistence.md should include mount ownership rules")
assert_contains(storage_persistence, "append-only", "storage-persistence.md should mention append-only record recovery patterns")
assert_contains(command_contracts, r"Validation & Error Matrix", "command-contracts.md should provide a command-contract matrix shape")
assert_contains(command_contracts, r"Good/Base/Bad Cases", "command-contracts.md should include good/base/bad cases")

assert_contains(guides_index, r"firmware-data-flow-guide\.md", "guides index should link firmware data-flow guide")
assert_contains(guides_index, r"firmware-reuse-guide\.md", "guides index should link firmware reuse guide")
assert_contains(guides_index, r"task-process\.md", "guides index should link task process guide")
assert_contains(data_flow_guide, "ISR", "firmware-data-flow-guide.md should require ISR/task boundary mapping")
assert_contains(data_flow_guide, "Review Checklist", "firmware-data-flow-guide.md should include a review checklist")
assert_contains(reuse_guide, "Search First", "firmware-reuse-guide.md should include search-first rules")
assert_contains(reuse_guide, "Batch Change Checklist", "firmware-reuse-guide.md should include batch-change checklist")
assert_contains(task_process, "research/", "task-process.md should require per-task research artifacts")
assert_contains(task_process, "implement.jsonl", "task-process.md should explain implement.jsonl")
assert_contains(task_process, "check.jsonl", "task-process.md should explain check.jsonl")
assert_contains(task_process, "session_auto_commit", "task-process.md should mention Trellis session config")

assert_contains(pitfalls_index, "PIT-DMA-001", "pitfalls index should include stable pitfall IDs")
assert_contains(pitfalls, "PIT-REPO-001", "pitfalls.md should include repository/tooling pitfalls")
assert_contains(pitfalls, "PIT-DOC-002", "pitfalls.md should include feedback-loop guidance")
assert_contains(pitfalls, r"pitfalls-<category>\.md",
                "pitfalls.md should document the per-category split convention inline")
assert_contains(feedback_loop, r"trellis init --append", "pitfall feedback loop should explain updating existing Trellis projects")
assert_contains(feedback_loop, r"external-knowledge-base\.md", "pitfall feedback loop should mention external knowledge bases for long content")
assert_contains(external_kb, "mcu-knowledge-base", "external knowledge base guide should recommend a repository name")
assert_contains(external_kb, "AGENTS.md", "external knowledge base guide should explain project integration")


# ---------------------------------------------------------------------------
# 7. NEW: canonical snippets vs inline copies must stay in sync
# ---------------------------------------------------------------------------

TEMPLATES_DIR = REPO_ROOT / "templates"

required_template_files = [
    "README.md",
    "agents-bootstrap-block.md",
    "gitignore-block.txt",
    "svn-ignore.list",
    "doc-readme.md",
]
for name in required_template_files:
    if not (TEMPLATES_DIR / name).exists():
        fail(f"templates/{name} is missing")

# Maintenance manual is the single source of truth for maintainer SOPs.
if not (REPO_ROOT / "docs" / "MAINTENANCE.md").exists():
    fail("docs/MAINTENANCE.md is missing (maintainer SOP)")

# Branch protection setup guide for the three remotes.
if not (REPO_ROOT / "docs" / "branch-protection-setup.md").exists():
    fail("docs/branch-protection-setup.md is missing (remote branch protection guide)")

# Open-source license file (required since repo is intended for public release).
if not (REPO_ROOT / "LICENSE").exists():
    fail("LICENSE file is missing (required for open-source distribution)")


def load_template(name: str) -> str:
    return (TEMPLATES_DIR / name).read_text(encoding="utf-8")


# The agents block, gitignore block, and doc-readme content are byte-exact
# substrings of SKILL.md and bootstrap-checklist.md. Strip a single trailing
# newline so we compare logical content, not file-end style.
def normalize(text: str) -> str:
    return text.rstrip("\n").replace("\r\n", "\n")


def check_inline_copy(snippet_name: str, host_name: str, host_text: str) -> None:
    snippet = normalize(load_template(snippet_name))
    if snippet not in normalize(host_text):
        fail(
            f"{host_name} no longer contains the verbatim block from "
            f"templates/{snippet_name}. Re-sync the inline copy with the canonical source."
        )


check_inline_copy("agents-bootstrap-block.md", "SKILL.md", skill)
check_inline_copy("agents-bootstrap-block.md", "bootstrap-checklist.md", checklist)
check_inline_copy("gitignore-block.txt", "SKILL.md", skill)
check_inline_copy("gitignore-block.txt", "bootstrap-checklist.md", checklist)
check_inline_copy("doc-readme.md", "SKILL.md", skill)
check_inline_copy("doc-readme.md", "bootstrap-checklist.md", checklist)


# svn-ignore.list: each entry must appear in both SKILL.md and bootstrap-checklist.md.
# (SKILL/checklist embed entries inside PowerShell arrays and Bash printf args,
# so a substring check on the whole list does not work — check each entry instead.)
svn_entries = [line.strip() for line in load_template("svn-ignore.list").splitlines() if line.strip()]
for host_name, host_text in (("SKILL.md", skill), ("bootstrap-checklist.md", checklist)):
    for entry in svn_entries:
        # Match the entry as a quoted-or-bare token to avoid false positives like
        # `.git` matching inside `.gitignore`.
        pattern = rf'(?<![A-Za-z0-9_.\-/])"?{re.escape(entry)}"?(?![A-Za-z0-9_.\-/])'
        if not re.search(pattern, host_text):
            fail(f"{host_name} is missing svn-ignore entry '{entry}' from templates/svn-ignore.list")


# ---------------------------------------------------------------------------
# 8. Report
# ---------------------------------------------------------------------------

if FAILURES:
    print("Template validation failed:", file=sys.stderr)
    for f in FAILURES:
        print(f" - {f}", file=sys.stderr)
    sys.exit(1)

print("Template validation passed.")
