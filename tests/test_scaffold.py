from __future__ import annotations

import py_compile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class ScaffoldTestCase(unittest.TestCase):
    def test_agent_module_has_valid_python_syntax(self) -> None:
        py_compile.compile(str(ROOT / "productivity_agent" / "agent.py"), doraise=True)

    def test_demo_api_module_has_valid_python_syntax(self) -> None:
        py_compile.compile(str(ROOT / "productivity_agent" / "demo_api.py"), doraise=True)

    def test_toolbox_config_mentions_required_google_stack(self) -> None:
        content = (ROOT / "toolbox" / "tools.yaml").read_text(encoding="utf-8")
        self.assertIn("type: alloydb-postgres", content)
        self.assertIn("workflow_store_run", content)
        self.assertIn("task_manager_create_task", content)
        self.assertIn("notes_create_note", content)
        self.assertIn("calendar_create_event", content)

    def test_schema_contains_required_tables(self) -> None:
        content = (ROOT / "db" / "schema.sql").read_text(encoding="utf-8")
        self.assertIn("CREATE TABLE IF NOT EXISTS workflow_runs", content)
        self.assertIn("CREATE TABLE IF NOT EXISTS tasks", content)
        self.assertIn("CREATE TABLE IF NOT EXISTS notes", content)
        self.assertIn("CREATE TABLE IF NOT EXISTS calendar_events", content)

    def test_readme_mentions_adk_and_cloud_run(self) -> None:
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Google ADK", content)
        self.assertIn("Cloud Run", content)
        self.assertIn("AlloyDB", content)
        self.assertIn("MCP", content)


if __name__ == "__main__":
    unittest.main()
