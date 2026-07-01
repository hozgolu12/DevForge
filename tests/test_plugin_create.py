import unittest
from pathlib import Path
import tempfile
import shutil
import yaml
from unittest.mock import MagicMock, patch

from engine.workspace import Project, get_devforge_root
from engine.service_manager import ServiceManager
from engine.ai.models import PluginSpecification, PortSpecification
from engine.plugins.registry import PluginRegistry


class TestPluginCreateAndServiceManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.patcher_root = patch('engine.workspace.get_devforge_root', return_value=self.test_dir)
        self.mock_get_root = self.patcher_root.start()

    def tearDown(self):
        self.patcher_root.stop()
        shutil.rmtree(self.test_dir)

    def test_service_manager_no_exit(self):
        # Create a mock project
        project = Project("test-proj", path=self.test_dir)
        project.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        project.save_manifest({"name": "test-proj", "ports": {}, "plugins": []})
        
        # Write a dummy compose file
        with open(project.compose_file, "w") as f:
            f.write("services:\n  web:\n    image: nginx\n")

        sm = ServiceManager()
        # Mock subprocess.run
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            # Should not raise SystemExit when exit_on_complete=False
            rc = sm.up_all(project, exit_on_complete=False)
            self.assertEqual(rc, 0)
            
            rc_down = sm.down_all(project, exit_on_complete=False)
            self.assertEqual(rc_down, 0)

    def test_plugin_registration(self):
        # Set up a fake registry/plugins.yaml in our temp root
        reg_dir = self.test_dir / "registry"
        reg_dir.mkdir(parents=True, exist_ok=True)
        reg_file = reg_dir / "plugins.yaml"
        with open(reg_file, "w") as f:
            yaml.dump({"plugins": []}, f)

        # Create plugin spec
        spec = PluginSpecification(
            plugin_name="my-custom-test-plugin",
            display_name="My Custom Test Plugin",
            description="Testing custom plugin registration",
            category="database",
            docker_image="library/test-img",
            docker_tag="latest",
            service_name="custom-test",
            ports=[
                PortSpecification(host=9000, container=9000, env_key="TEST_PORT")
            ],
            environment_variables={"TEST_PORT": "9000"},
            version="1.0.0"
        )

        # Register plugin
        rel_path = "plugins/my-custom-test-plugin"
        success = PluginRegistry.register_plugin(spec, rel_path)
        self.assertTrue(success)

        # Check that it exists in registry
        self.assertTrue(PluginRegistry.plugin_exists("my-custom-test-plugin"))
        
        # Find the plugin
        entry = PluginRegistry.find_plugin("my-custom-test-plugin")
        self.assertIsNotNone(entry)
        self.assertEqual(entry["display_name"], "My Custom Test Plugin")
        self.assertEqual(entry["path"], rel_path)
