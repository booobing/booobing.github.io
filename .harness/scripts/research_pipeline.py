from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

PIPELINE_VERSION = 1
PIPELINE_NAME = "research"
DEFAULT_WORKSPACE_ROOT = Path(".harness/tmp/research")
MANIFEST_NAME = "manifest.json"


@dataclass(frozen=True)
class StageContract:
    name: str
    description: str
    required_artifacts: tuple[str, ...]


STAGES: tuple[StageContract, ...] = (
    StageContract(
        name="ideation",
        description="Literature search, research question, and hypothesis framing.",
        required_artifacts=("ideation/research_brief.md", "ideation/literature_map.json"),
    ),
    StageContract(
        name="planning",
        description="Experiment design, baselines, metrics, and artifact contract.",
        required_artifacts=("planning/experiment_plan.md", "planning/artifact_contract.json"),
    ),
    StageContract(
        name="setup",
        description="Runtime, data, and environment preparation.",
        required_artifacts=("experiment/configs/environment.md",),
    ),
    StageContract(
        name="coding",
        description="Runnable experiment code and usage notes.",
        required_artifacts=("experiment/code/README.md",),
    ),
    StageContract(
        name="execution",
        description="Real experiment execution record and logs.",
        required_artifacts=("experiment/results/run_manifest.json",),
    ),
    StageContract(
        name="analysis",
        description="Analysis report grounded in real execution artifacts.",
        required_artifacts=("analysis/report.md",),
    ),
    StageContract(
        name="figure_gen",
        description="Figure manifest and generated figure references.",
        required_artifacts=("paper/figures/figure_manifest.json",),
    ),
    StageContract(
        name="writing",
        description="Draft paper source that cites only available artifacts.",
        required_artifacts=("paper/paper.tex",),
    ),
    StageContract(
        name="review",
        description="Reviewer pass covering evidence, scope, and reproducibility.",
        required_artifacts=("review/report.md",),
    ),
)
STAGE_BY_NAME = {stage.name: stage for stage in STAGES}
STAGE_ORDER = tuple(stage.name for stage in STAGES)


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug[:48] or "research"


def parse_topic(raw_topic: str) -> dict[str, str | None]:
    value = raw_topic.strip()
    lowered = value.lower()
    if lowered.startswith("original:"):
        return {
            "raw_topic": raw_topic,
            "topic": value.split(":", 1)[1].strip(),
            "paper_mode": "original",
            "survey_depth": None,
        }
    if lowered.startswith("survey:"):
        parts = value.split(":", 2)
        if len(parts) == 3 and parts[1].strip().lower() in {"short", "standard", "long"}:
            return {
                "raw_topic": raw_topic,
                "topic": parts[2].strip(),
                "paper_mode": "survey",
                "survey_depth": parts[1].strip().lower(),
            }
        return {
            "raw_topic": raw_topic,
            "topic": value.split(":", 1)[1].strip(),
            "paper_mode": "survey",
            "survey_depth": "standard",
        }
    return {
        "raw_topic": raw_topic,
        "topic": value,
        "paper_mode": "original",
        "survey_depth": None,
    }


def make_session_id(topic: str) -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    return f"{stamp}-{slugify(topic)}"


def manifest_path(workspace: Path) -> Path:
    return workspace / MANIFEST_NAME


def resolve_workspace(path: str | None, session_id: str | None = None) -> Path:
    if path:
        return Path(path)
    if session_id is None:
        raise ValueError("session_id is required when workspace is not provided")
    return DEFAULT_WORKSPACE_ROOT / session_id


def stage_template(stage: StageContract) -> dict[str, object]:
    return {
        "status": "pending",
        "description": stage.description,
        "required_artifacts": list(stage.required_artifacts),
        "artifacts": [],
        "started_at": None,
        "completed_at": None,
        "error": None,
    }


def new_manifest(raw_topic: str, profile: str) -> dict[str, object]:
    topic_info = parse_topic(raw_topic)
    session_id = make_session_id(str(topic_info["topic"]))
    now = utc_now()
    return {
        "schema_version": PIPELINE_VERSION,
        "pipeline": PIPELINE_NAME,
        "session_id": session_id,
        "raw_topic": topic_info["raw_topic"],
        "topic": topic_info["topic"],
        "paper_mode": topic_info["paper_mode"],
        "survey_depth": topic_info["survey_depth"],
        "profile": profile,
        "status": "initialized",
        "current_stage": STAGE_ORDER[0],
        "created_at": now,
        "updated_at": now,
        "stage_order": list(STAGE_ORDER),
        "stages": {stage.name: stage_template(stage) for stage in STAGES},
    }


def load_manifest(workspace: Path) -> dict[str, object]:
    path = manifest_path(workspace)
    if not path.exists():
        raise SystemExit(f"manifest not found: {path}")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("pipeline") != PIPELINE_NAME:
        raise SystemExit(f"unsupported pipeline manifest: {manifest.get('pipeline')}")
    return manifest


def save_manifest(workspace: Path, manifest: dict[str, object]) -> None:
    workspace.mkdir(parents=True, exist_ok=True)
    manifest["updated_at"] = utc_now()
    manifest_path(workspace).write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def ensure_stage_dirs(workspace: Path) -> None:
    for stage in STAGES:
        for artifact in stage.required_artifacts:
            (workspace / artifact).parent.mkdir(parents=True, exist_ok=True)


def stages(manifest: dict[str, object]) -> dict[str, dict[str, object]]:
    value = manifest["stages"]
    if not isinstance(value, dict):
        raise SystemExit("manifest stages must be an object")
    return value  # type: ignore[return-value]


def get_stage(manifest: dict[str, object], stage_name: str) -> dict[str, object]:
    if stage_name not in STAGE_BY_NAME:
        raise SystemExit(f"unknown stage: {stage_name}")
    return stages(manifest)[stage_name]


def first_open_stage(manifest: dict[str, object]) -> str | None:
    stage_map = stages(manifest)
    for status in ("failed", "running", "pending"):
        for stage_name in STAGE_ORDER:
            if stage_map[stage_name]["status"] == status:
                return stage_name
    return None


def refresh_current_stage(manifest: dict[str, object]) -> None:
    current = first_open_stage(manifest)
    manifest["current_stage"] = current
    manifest["status"] = "completed" if current is None else str(get_stage(manifest, current)["status"])


def normalize_artifact(workspace: Path, artifact: str) -> str:
    path = Path(artifact)
    if path.is_absolute():
        try:
            return path.resolve().relative_to(workspace.resolve()).as_posix()
        except ValueError as exc:
            raise SystemExit(f"artifact must be inside workspace: {artifact}") from exc
    if ".." in path.parts:
        raise SystemExit(f"artifact path may not escape workspace: {artifact}")
    return path.as_posix()


def add_artifacts(workspace: Path, stage: dict[str, object], artifact_paths: Sequence[str]) -> None:
    artifacts = stage["artifacts"]
    if not isinstance(artifacts, list):
        raise SystemExit("stage artifacts must be a list")
    for artifact in artifact_paths:
        normalized = normalize_artifact(workspace, artifact)
        if normalized not in artifacts:
            artifacts.append(normalized)


def missing_required_artifacts(workspace: Path, stage: dict[str, object]) -> list[str]:
    required = stage["required_artifacts"]
    if not isinstance(required, list):
        raise SystemExit("required_artifacts must be a list")
    return [str(path) for path in required if not (workspace / str(path)).exists()]


def assert_stage_can_start(manifest: dict[str, object], stage_name: str) -> None:
    stage_map = stages(manifest)
    stage_position = STAGE_ORDER.index(stage_name)
    for earlier in STAGE_ORDER[:stage_position]:
        if stage_map[earlier]["status"] != "completed":
            raise SystemExit(f"stage '{stage_name}' cannot start before '{earlier}' is completed")
    status = stage_map[stage_name]["status"]
    if status == "completed":
        raise SystemExit(f"stage already completed: {stage_name}")


def print_status(workspace: Path, manifest: dict[str, object]) -> None:
    refresh_current_stage(manifest)
    print(f"WORKSPACE={workspace}")
    print(f"SESSION_ID={manifest['session_id']}")
    print(f"TOPIC={manifest['topic']}")
    print(f"PAPER_MODE={manifest['paper_mode']}")
    if manifest.get("survey_depth"):
        print(f"SURVEY_DEPTH={manifest['survey_depth']}")
    print(f"STATUS={manifest['status']}")
    print(f"CURRENT_STAGE={manifest['current_stage']}")
    for stage_name in STAGE_ORDER:
        stage = get_stage(manifest, stage_name)
        missing = missing_required_artifacts(workspace, stage)
        suffix = "" if not missing else f" missing={','.join(missing)}"
        print(f"{stage_name}: {stage['status']}{suffix}")


def command_init(args: argparse.Namespace) -> int:
    manifest = new_manifest(args.topic, args.profile)
    workspace = resolve_workspace(args.workspace, str(manifest["session_id"]))
    path = manifest_path(workspace)
    if path.exists() and not args.force:
        raise SystemExit(f"manifest already exists: {path}")
    ensure_stage_dirs(workspace)
    save_manifest(workspace, manifest)
    print(f"WORKSPACE={workspace}")
    print(f"SESSION_ID={manifest['session_id']}")
    print(f"CURRENT_STAGE={manifest['current_stage']}")
    print("STATUS=initialized")
    return 0


def command_status(args: argparse.Namespace) -> int:
    workspace = resolve_workspace(args.workspace)
    manifest = load_manifest(workspace)
    print_status(workspace, manifest)
    return 0


def command_start(args: argparse.Namespace) -> int:
    workspace = resolve_workspace(args.workspace)
    manifest = load_manifest(workspace)
    stage_name = args.stage or first_open_stage(manifest)
    if stage_name is None:
        print("STATUS=completed")
        return 0
    assert_stage_can_start(manifest, stage_name)
    stage = get_stage(manifest, stage_name)
    stage["status"] = "running"
    stage["started_at"] = stage["started_at"] or utc_now()
    stage["error"] = None
    manifest["current_stage"] = stage_name
    manifest["status"] = "running"
    save_manifest(workspace, manifest)
    print(f"CURRENT_STAGE={stage_name}")
    print("STATUS=running")
    return 0


def command_complete(args: argparse.Namespace) -> int:
    workspace = resolve_workspace(args.workspace)
    manifest = load_manifest(workspace)
    stage_name = args.stage or str(manifest["current_stage"])
    stage = get_stage(manifest, stage_name)
    add_artifacts(workspace, stage, args.artifact)
    missing = missing_required_artifacts(workspace, stage)
    if missing and not args.allow_missing:
        for artifact in missing:
            print(f"MISSING={artifact}")
        print("STATUS=BLOCKED")
        return 3
    stage["status"] = "completed"
    stage["completed_at"] = utc_now()
    stage["error"] = None
    refresh_current_stage(manifest)
    save_manifest(workspace, manifest)
    print(f"COMPLETED_STAGE={stage_name}")
    print(f"CURRENT_STAGE={manifest['current_stage']}")
    print(f"STATUS={manifest['status']}")
    return 0


def command_fail(args: argparse.Namespace) -> int:
    workspace = resolve_workspace(args.workspace)
    manifest = load_manifest(workspace)
    stage_name = args.stage or str(manifest["current_stage"])
    stage = get_stage(manifest, stage_name)
    stage["status"] = "failed"
    stage["error"] = args.reason
    manifest["current_stage"] = stage_name
    manifest["status"] = "failed"
    save_manifest(workspace, manifest)
    print(f"FAILED_STAGE={stage_name}")
    print("STATUS=failed")
    return 0


def command_resume(args: argparse.Namespace) -> int:
    workspace = resolve_workspace(args.workspace)
    manifest = load_manifest(workspace)
    refresh_current_stage(manifest)
    current = manifest["current_stage"]
    print(f"WORKSPACE={workspace}")
    print(f"STATUS={manifest['status']}")
    print(f"RESUME_STAGE={current}")
    if current is not None:
        print(f"NEXT_ACTION=python .harness/scripts/research_pipeline.py start --workspace {workspace}")
    return 0


def command_inspect(args: argparse.Namespace) -> int:
    workspace = resolve_workspace(args.workspace)
    manifest = load_manifest(workspace)
    problems: list[str] = []
    stage_order = manifest.get("stage_order")
    if stage_order != list(STAGE_ORDER):
        problems.append("stage_order does not match the built-in research pipeline contract")
    for stage_name in STAGE_ORDER:
        stage = get_stage(manifest, stage_name)
        for artifact in missing_required_artifacts(workspace, stage):
            if stage["status"] == "completed":
                problems.append(f"{stage_name} is completed but missing {artifact}")
    if problems:
        for problem in problems:
            print(f"ERROR={problem}")
        print("STATUS=NEEDS_ATTENTION")
        return 20
    print("STATUS=OK")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manifest-backed research pipeline automation.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", aliases=["run"], help="Create a research workspace.")
    init_parser.add_argument("--topic", required=True)
    init_parser.add_argument("--workspace")
    init_parser.add_argument(
        "--profile",
        default="fast_draft",
        choices=("fast_draft", "local_quick", "cluster_full"),
    )
    init_parser.add_argument("--force", action="store_true")
    init_parser.set_defaults(func=command_init)

    status_parser = subparsers.add_parser("status", help="Show pipeline status.")
    status_parser.add_argument("--workspace", required=True)
    status_parser.set_defaults(func=command_status)

    start_parser = subparsers.add_parser("start", help="Mark the next stage as running.")
    start_parser.add_argument("--workspace", required=True)
    start_parser.add_argument("--stage", choices=STAGE_ORDER)
    start_parser.set_defaults(func=command_start)

    complete_parser = subparsers.add_parser("complete", help="Mark a stage complete.")
    complete_parser.add_argument("--workspace", required=True)
    complete_parser.add_argument("--stage", choices=STAGE_ORDER)
    complete_parser.add_argument("--artifact", action="append", default=[])
    complete_parser.add_argument("--allow-missing", action="store_true")
    complete_parser.set_defaults(func=command_complete)

    fail_parser = subparsers.add_parser("fail", help="Mark a stage failed.")
    fail_parser.add_argument("--workspace", required=True)
    fail_parser.add_argument("--stage", choices=STAGE_ORDER)
    fail_parser.add_argument("--reason", required=True)
    fail_parser.set_defaults(func=command_fail)

    resume_parser = subparsers.add_parser("resume", help="Print the stage to resume from.")
    resume_parser.add_argument("--workspace", required=True)
    resume_parser.set_defaults(func=command_resume)

    inspect_parser = subparsers.add_parser("inspect", help="Validate manifest consistency.")
    inspect_parser.add_argument("--workspace", required=True)
    inspect_parser.set_defaults(func=command_inspect)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
