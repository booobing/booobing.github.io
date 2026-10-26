from __future__ import annotations

from pathlib import Path

SPECIFY_DIR = Path(".specify")
SPECS_DIR = Path("specs")
CONSTITUTION = SPECIFY_DIR / "memory" / "constitution.md"
NEEDS_CLARIFICATION = "NEEDS CLARIFICATION"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _feature_dirs() -> list[Path]:
    if not SPECS_DIR.exists():
        return []
    return sorted(path for path in SPECS_DIR.iterdir() if path.is_dir() and not path.name.startswith("."))


def main() -> int:
    if not SPECIFY_DIR.exists():
        print("Spec Kit: not initialized")
        print("STATUS=SKIPPED")
        return 0

    problems: list[str] = []
    warnings: list[str] = []

    if not CONSTITUTION.exists():
        warnings.append(".specify/memory/constitution.md is missing")
    else:
        constitution_text = _read_text(CONSTITUTION)
        if "AGENTS.md" not in constitution_text:
            warnings.append("constitution does not mention AGENTS.md as the operational source of truth")

    for feature_dir in _feature_dirs():
        spec = feature_dir / "spec.md"
        plan = feature_dir / "plan.md"
        tasks = feature_dir / "tasks.md"

        if not spec.exists():
            problems.append(f"{feature_dir.as_posix()}: missing spec.md")
            continue

        if plan.exists() and not spec.exists():
            problems.append(f"{feature_dir.as_posix()}: plan.md exists without spec.md")
        if tasks.exists() and not plan.exists():
            problems.append(f"{feature_dir.as_posix()}: tasks.md exists without plan.md")

        for artifact in (spec, plan, tasks):
            if artifact.exists() and NEEDS_CLARIFICATION in _read_text(artifact):
                problems.append(f"{artifact.as_posix()}: unresolved NEEDS CLARIFICATION marker")

    for warning in warnings:
        print(f"WARNING: {warning}")

    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        print("STATUS=NEEDS_ATTENTION")
        return 20

    print("Spec Kit: initialized")
    print(f"Features checked: {len(_feature_dirs())}")
    print("STATUS=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
