import posixpath
import re
import sys
import urllib.request
from pathlib import Path, PurePosixPath
from typing import Dict, List, Set, Tuple

from bioos.cli.common import add_argument, add_bool_argument, build_parser, run_cli
from bioos.errors import ParameterError
from bioos.ops.auth import DEFAULT_ENDPOINT, resolve_auth_settings, resolve_credentials
from bioos.service.BioOsService import BioOsService
from volcengine.const.Const import REGION_CN_NORTH1


IMPORT_PATTERN = re.compile(r'^\s*import\s+"([^"]+)"', flags=re.MULTILINE)


def build_args():
    parser = build_parser("Download workflow WDL files from Bio-OS.")
    add_argument(parser, "workspace_name", required=True, help="Workspace name.")
    add_argument(parser, "workflow", required=True, help="Workflow name or workflow ID.")
    add_argument(parser, "target", required=True, help="Local directory to save downloaded WDL files.")
    add_bool_argument(
        parser,
        "include_imports",
        default=True,
        help_text="Download imported WDL files recursively.",
        negative_help_text="Only download the main workflow WDL.",
    )
    add_bool_argument(
        parser,
        "allow_non_succeeded",
        default=False,
        help_text="Try to download even when workflow validation status is not Succeeded.",
    )
    return parser


def handle(args):
    service = _build_service(args)
    workspace_id, workspace = _resolve_workspace(service, args.workspace_name)
    workflow = _resolve_workflow(service, workspace_id, args.workflow)
    phase = _workflow_phase(workflow)
    if phase and phase != "Succeeded" and not args.allow_non_succeeded:
        raise RuntimeError(
            f"Workflow {workflow.get('Name') or workflow.get('ID')} status is {phase}; "
            "use --allow-non-succeeded to try downloading anyway."
        )

    main_file_path = workflow.get("MainWorkflowPath")
    if not main_file_path:
        raise RuntimeError(f"Workflow {workflow.get('Name') or workflow.get('ID')} has no MainWorkflowPath.")

    target = Path(args.target).expanduser()
    target.mkdir(parents=True, exist_ok=True)

    downloaded: Dict[str, dict] = {}
    _download_wdl_tree(
        service=service,
        workspace_id=workspace_id,
        workflow_id=str(workflow["ID"]),
        file_path=_normalize_workflow_path(main_file_path),
        target=target,
        include_imports=args.include_imports,
        downloaded=downloaded,
        visiting=set(),
    )

    files = sorted(downloaded.values(), key=lambda item: item["file_path"])
    return {
        "success": True,
        "workspace_name": args.workspace_name,
        "workspace_id": workspace_id,
        "resolved_workspace_name": workspace.get("Name"),
        "workflow": args.workflow,
        "workflow_id": str(workflow["ID"]),
        "workflow_name": workflow.get("Name"),
        "main_workflow_path": _normalize_workflow_path(main_file_path),
        "target": str(target.resolve()),
        "downloaded_count": len(files),
        "files": files,
    }


def _build_service(args):
    settings = resolve_auth_settings(
        access_key=getattr(args, "ak", None),
        secret_key=getattr(args, "sk", None),
        endpoint=getattr(args, "endpoint", None),
    )
    access_key, secret_key = resolve_credentials(
        getattr(args, "ak", None),
        getattr(args, "sk", None),
    )
    endpoint = settings["endpoint"] or DEFAULT_ENDPOINT
    region = settings["region"] or REGION_CN_NORTH1

    service = object.__new__(BioOsService)
    BioOsService.__init__(service, endpoint=endpoint, region=region)
    service.set_ak(access_key)
    service.set_sk(secret_key)
    return service


def _resolve_workspace(service, workspace_ref: str) -> Tuple[str, dict]:
    content = service.list_workspaces({"PageSize": 0})
    records = content.get("Items") or []
    id_matches = [row for row in records if str(row.get("ID", "")) == workspace_ref]
    if len(id_matches) == 1:
        return str(id_matches[0]["ID"]), id_matches[0]

    name_matches = [row for row in records if str(row.get("Name", "")) == workspace_ref]
    if len(name_matches) == 1:
        return str(name_matches[0]["ID"]), name_matches[0]
    if len(name_matches) > 1:
        raise RuntimeError(f"Multiple workspaces found with name {workspace_ref}. Use workspace ID instead.")

    raise RuntimeError(f"Workspace not found by name or ID: {workspace_ref}")


def _resolve_workflow(service, workspace_id: str, workflow_ref: str) -> dict:
    records = _list_workflows(service, workspace_id)
    if not records:
        raise RuntimeError("No workflows found in workspace.")

    id_matches = [row for row in records if str(row.get("ID", "")) == workflow_ref]
    if len(id_matches) == 1:
        return id_matches[0]
    if len(id_matches) > 1:
        raise RuntimeError(f"Multiple workflows found with ID {workflow_ref}.")

    name_matches = [row for row in records if str(row.get("Name", "")) == workflow_ref]
    if len(name_matches) == 1:
        return name_matches[0]
    if len(name_matches) > 1:
        raise RuntimeError(f"Multiple workflows found with name {workflow_ref}. Use workflow ID instead.")

    raise RuntimeError(f"Workflow not found by name or ID: {workflow_ref}")


def _list_workflows(service, workspace_id: str) -> List[dict]:
    content = service.list_workflows(
        {
            "WorkspaceID": workspace_id,
            "SortBy": "CreateTime",
            "PageSize": 0,
        }
    )
    return content.get("Items") or []


def _workflow_phase(workflow: dict) -> str:
    status = workflow.get("Status")
    if isinstance(status, dict):
        return status.get("Phase") or ""
    return str(status) if status else ""


def _download_wdl_tree(
    service,
    workspace_id: str,
    workflow_id: str,
    file_path: str,
    target: Path,
    include_imports: bool,
    downloaded: Dict[str, dict],
    visiting: Set[str],
) -> None:
    normalized = _normalize_workflow_path(file_path)
    if normalized in downloaded:
        return
    if normalized in visiting:
        raise RuntimeError(f"Circular WDL import detected at {normalized}")
    visiting.add(normalized)

    info = service.get_workflow_files_download_info(
        {
            "WorkspaceID": workspace_id,
            "ID": workflow_id,
            "FilePath": normalized,
        }
    )
    url = info.get("PreSignedURL")
    if not url:
        raise RuntimeError(f"No PreSignedURL returned for workflow file {normalized}")

    local_path = _local_path_for(target, normalized)
    local_path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, local_path)
    content = local_path.read_text(encoding="utf-8", errors="replace")
    downloaded[normalized] = {
        "file_path": normalized,
        "local_path": str(local_path.resolve()),
        "bytes": local_path.stat().st_size,
    }

    if include_imports:
        base_dir = PurePosixPath(normalized).parent.as_posix()
        for imported in IMPORT_PATTERN.findall(content):
            imported_path = _normalize_workflow_path(imported, base_dir=base_dir)
            _download_wdl_tree(
                service=service,
                workspace_id=workspace_id,
                workflow_id=workflow_id,
                file_path=imported_path,
                target=target,
                include_imports=include_imports,
                downloaded=downloaded,
                visiting=visiting,
            )

    visiting.remove(normalized)


def _normalize_workflow_path(file_path: str, base_dir: str = "") -> str:
    raw = str(file_path).strip()
    if not raw:
        raise ParameterError("file_path")
    if raw.startswith("/"):
        raise ParameterError("file_path", "workflow file path must be relative")
    joined = posixpath.join(base_dir, raw) if base_dir and base_dir != "." else raw
    normalized = posixpath.normpath(joined)
    if normalized in {"", "."} or normalized.startswith("../") or normalized == "..":
        raise ParameterError("file_path", f"unsafe workflow file path: {file_path}")
    return normalized


def _local_path_for(target: Path, file_path: str) -> Path:
    parts: List[str] = [part for part in PurePosixPath(file_path).parts if part not in {"", "."}]
    return target.joinpath(*parts)


def main():
    parser = build_args()
    args = parser.parse_args()
    sys.exit(run_cli(handle, args))


if __name__ == "__main__":
    main()
