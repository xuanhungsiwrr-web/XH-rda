"""Versioned workspace layout shared by CLI, MCP, render, learning and migration."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath

PLUGIN_VERSION = "0.9.2"
LAYOUT_VERSION = 3
LEGACY_LAYOUT_VERSION = 2


V3_PATHS = {
    "user_input": "10_Sources/10_User_Input",
    "source_snapshots": "10_Sources/20_Source_Snapshots",
    "templates": "20_Templates",
    "research": "30_Working/10_Research",
    "evidence": "30_Working/20_Evidence",
    "specs": "30_Working/30_Specs",
    "drafts": "30_Working/40_Drafts",
    "reviews": "30_Working/50_Reviews",
    "edit_analysis": "30_Working/60_Edit_Analysis",
    "learning_candidates": "30_Working/70_Learning_Candidates",
    "ai": "30_Working/.ai",
    "internal": "30_Working/.xh",
    "artifacts": "30_Working/.xh/artifacts",
    "render": "30_Working/.xh/render",
    "state_db": "30_Working/.xh/state.sqlite",
    "migration": "30_Working/.xh/migrations",
    "legacy_sources": "30_Working/.xh/legacy-unclassified/sources",
    "legacy_calculations": "30_Working/.xh/legacy-out-of-scope/calculations",
    "outputs": "40_Outputs",
    "feedback": "50_Feedback",
}

V2_PATHS = {
    "user_input": "sources",
    "source_snapshots": "sources",
    "templates": "templates",
    "research": "research",
    "evidence": "evidence",
    "specs": "specs",
    "drafts": "drafts",
    "reviews": "reviews",
    "edit_analysis": "edits",
    "learning_candidates": ".ai/learning-candidates",
    "ai": ".ai",
    "internal": ".xh",
    "artifacts": ".xh/artifacts",
    "render": ".xh/render",
    "state_db": ".xh/state.sqlite",
    "migration": ".xh/migrations",
    "legacy_sources": "sources",
    "legacy_calculations": "calculations",
    "outputs": "outputs",
    "feedback": "feedback",
}


@dataclass(frozen=True)
class WorkspaceLayout:
    version: int
    paths: dict[str, str]

    def rel(self, key: str, *parts: str) -> str:
        if key not in self.paths:
            raise KeyError("Unknown layout key: " + key)
        path = PurePosixPath(self.paths[key])
        for part in parts:
            path /= str(part).replace("\\", "/")
        return path.as_posix()

    def at(self, root: str | Path, key: str, *parts: str) -> Path:
        return Path(root) / Path(self.rel(key, *parts))


LAYOUTS = {
    LEGACY_LAYOUT_VERSION: WorkspaceLayout(LEGACY_LAYOUT_VERSION, V2_PATHS),
    LAYOUT_VERSION: WorkspaceLayout(LAYOUT_VERSION, V3_PATHS),
}


def layout_for(version: int) -> WorkspaceLayout:
    try:
        return LAYOUTS[int(version)]
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"Unsupported workspace layout version: {version}") from exc


def detect_layout(root: str | Path) -> WorkspaceLayout:
    root = Path(root)
    config_file = root / "project.json"
    if config_file.is_file():
        try:
            config = json.loads(config_file.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError("Invalid project.json; repair it before opening the workspace") from exc
        explicit = config.get("layout_version")
        if explicit is not None:
            return layout_for(explicit)
        if int(config.get("schema_version", LEGACY_LAYOUT_VERSION)) <= LEGACY_LAYOUT_VERSION:
            return LAYOUTS[LEGACY_LAYOUT_VERSION]
    if (root / V3_PATHS["state_db"]).is_file() or (root / "30_Working").is_dir():
        return LAYOUTS[LAYOUT_VERSION]
    return LAYOUTS[LEGACY_LAYOUT_VERSION]


def ensure_new_layout(root: str | Path) -> WorkspaceLayout:
    root = Path(root)
    layout = LAYOUTS[LAYOUT_VERSION]
    for key in (
        "user_input", "source_snapshots", "templates", "research", "evidence",
        "specs", "drafts", "reviews", "edit_analysis", "learning_candidates",
        "ai", "artifacts", "render", "migration", "outputs", "feedback",
    ):
        layout.at(root, key).mkdir(parents=True, exist_ok=True)
    return layout


def _join(prefix: str, suffix: str) -> str:
    return (PurePosixPath(prefix) / suffix).as_posix() if suffix else prefix


def map_legacy_path(path: str, meta: dict | None = None) -> dict:
    """Return a conservative v2 -> v3 mapping; never guess source provenance."""
    normalized = str(path).replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    normalized = normalized.lstrip("/")
    meta = meta or {}
    prefix, _, suffix = normalized.partition("/")
    direct = {
        "templates": "templates",
        "research": "research",
        "evidence": "evidence",
        "specs": "specs",
        "drafts": "drafts",
        "reviews": "reviews",
        "edits": "edit_analysis",
        "outputs": "outputs",
        "feedback": "feedback",
        ".ai": "ai",
        ".xh": "internal",
    }
    if prefix == "sources":
        provenance = str(meta.get("provenance") or meta.get("source_bucket") or "").lower()
        if provenance in {"user", "user_input", "10_user_input"}:
            key, status = "user_input", "classified"
        elif provenance in {"snapshot", "source_snapshot", "20_source_snapshots"}:
            key, status = "source_snapshots", "classified"
        else:
            key, status = "legacy_sources", "legacy-unclassified"
        return {"from": normalized, "to": _join(V3_PATHS[key], suffix), "status": status,
                "reason": "source provenance required; no folder-name inference"}
    if prefix == "calculations":
        return {"from": normalized, "to": _join(V3_PATHS["legacy_calculations"], suffix),
                "status": "legacy-out-of-scope", "reason": "preserved; calculations are outside workspace scope"}
    if prefix in direct:
        return {"from": normalized, "to": _join(V3_PATHS[direct[prefix]], suffix),
                "status": "mapped", "reason": "approved workspace mapping"}
    return {"from": normalized, "to": normalized, "status": "unchanged",
            "reason": "path is outside known legacy workspace roots"}


def rewrite_known_paths(value):
    """Rewrite embedded project-relative v2 paths without touching URLs or arbitrary text."""
    if isinstance(value, dict):
        return {k: rewrite_known_paths(v) for k, v in value.items()}
    if isinstance(value, list):
        return [rewrite_known_paths(v) for v in value]
    if not isinstance(value, str) or "://" in value or ":" in value:
        return value
    normalized = value.replace("\\", "/")
    prefix = normalized.split("/", 1)[0]
    if prefix in {"sources", "calculations"}:
        return map_legacy_path(normalized)["to"]
    if prefix in {"templates", "research", "evidence", "specs", "drafts", "reviews",
                  "edits", "outputs", "feedback", ".ai", ".xh"}:
        return map_legacy_path(normalized)["to"]
    return value
