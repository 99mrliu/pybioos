import os
import re
import tempfile
import unittest
import urllib.request
from pathlib import Path, PurePosixPath

from bioos import bioos
from bioos.ops.auth import login_to_bioos, resolve_workspace


@unittest.skipUnless(
    os.getenv("BIOOS_RUN_INTEGRATION") == "1",
    "set BIOOS_RUN_INTEGRATION=1 to run Bio-OS workflow file download integration test",
)
class TestWorkflowFilesDownloadIntegration(unittest.TestCase):
    def test_download_main_wdl_from_workspace(self):
        workspace_name = os.getenv(
            "BIOOS_INTEGRATION_WORKSPACE",
            "Phlower_P2W_20260626_154105",
        )

        login_to_bioos()
        workspace_id, _ = resolve_workspace(workspace_name)
        ws = bioos.workspace(workspace_id)
        workflows = ws.workflows.list()

        self.assertFalse(workflows.empty, f"No workflows found in workspace {workspace_name}")
        workflow = next(
            (row for row in workflows.to_dict("records") if row.get("MainWorkflowPath")),
            None,
        )
        self.assertIsNotNone(workflow, "No workflow with MainWorkflowPath found")

        file_path = workflow["MainWorkflowPath"]
        with tempfile.TemporaryDirectory() as tmpdir:
            downloaded = self._download_wdl_tree(
                ws=ws,
                workflow_id=workflow["ID"],
                root_file_path=file_path,
                output_dir=Path(tmpdir),
            )

        self.assertGreater(len(downloaded), 0)
        for downloaded_content in downloaded.values():
            self.assertGreater(len(downloaded_content), 0)
            self.assertTrue(
                any(token in downloaded_content for token in ("version", "workflow", "task")),
                "Downloaded file does not look like a WDL file",
            )

    def _download_wdl_tree(self, ws, workflow_id, root_file_path, output_dir):
        downloaded = {}

        def download_one(file_path):
            normalized = PurePosixPath(file_path).as_posix()
            if normalized in downloaded:
                return

            info = ws.workflows.get_workflow_files_download_info(
                workflow_id=workflow_id,
                file_path=normalized,
            )
            url = info.get("PreSignedURL")
            self.assertTrue(url, f"No PreSignedURL returned for {normalized}: {info}")

            local_path = output_dir.joinpath(
                *[part for part in PurePosixPath(normalized).parts if part not in ("", ".", "..")]
            )
            local_path.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(url, local_path)
            content = local_path.read_text(encoding="utf-8", errors="replace")
            downloaded[normalized] = content

            base_dir = PurePosixPath(normalized).parent
            for match in re.finditer(r'^\s*import\s+"([^"]+)"', content, flags=re.MULTILINE):
                download_one((base_dir / match.group(1)).as_posix())

        download_one(root_file_path)
        return downloaded
