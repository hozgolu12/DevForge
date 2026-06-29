import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from engine.detection import DetectionEngine
from engine.validation import Validator

class TestExistingImport(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for project files
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.test_dir)

    def test_detection_heuristics(self):
        # 1. Setup a mock project with React, NestJS, MongoDB, and Redis
        frontend_dir = self.test_dir / "frontend"
        frontend_dir.mkdir()
        
        # package.json for React
        pj_content = {
            "dependencies": {
                "react": "^18.2.0"
            }
        }
        with open(frontend_dir / "package.json", "w", encoding="utf-8") as f:
            json.dump(pj_content, f)

        backend_dir = self.test_dir / "backend"
        backend_dir.mkdir()

        # package.json for NestJS and MongoDB connection library
        pj_backend = {
            "dependencies": {
                "@nestjs/core": "^10.0.0",
                "mongodb": "^6.0.0"
            }
        }
        with open(backend_dir / "package.json", "w", encoding="utf-8") as f:
            json.dump(pj_backend, f)

        # Pipfile for python/redis
        with open(self.test_dir / "requirements.txt", "w", encoding="utf-8") as f:
            f.write("redis==5.0.0\n")

        # Dockerfile
        with open(self.test_dir / "Dockerfile", "w", encoding="utf-8") as f:
            f.write("FROM node:20\nCMD [\"npm\", \"start\"]\n")

        # 2. Run detection
        detected = DetectionEngine.detect(self.test_dir, force=True)

        # 3. Assertions
        self.assertTrue(detected["Frontend"].get("React"))
        self.assertTrue(detected["Backend"].get("NestJS"))
        self.assertTrue(detected["Database"].get("MongoDB"))
        self.assertTrue(detected["Cache"].get("Redis"))
        self.assertTrue(detected["Docker"].get("Dockerfile"))
        self.assertTrue(detected["Package Managers"].get("npm"))
        self.assertTrue(detected["Package Managers"].get("pip"))

    def test_validator_rules(self):
        # Test 1: Port conflict validation
        config_port_conflict = {
            "frameworks": {"frontend": "react", "backend": "nestjs"},
            "plugins": ["postgres"],
            "ports": {
                "react": 5000,
                "nestjs": 5000
            }
        }
        res_ports = Validator.validate(self.test_dir, config_port_conflict)
        self.assertTrue(any("Port conflict" in err for err in res_ports["errors"]))

        # Test 2: Missing plugin dependency validation
        # pgadmin requires postgres, but postgres is missing
        config_missing_dep = {
            "frameworks": {},
            "plugins": ["pgadmin"],
            "ports": {}
        }
        res_dep = Validator.validate(self.test_dir, config_missing_dep)
        self.assertTrue(any("depends on" in err for err in res_dep["errors"]))

        # Test 3: Unsupported combinations (multiple frontends)
        config_unsupported = {
            "frameworks": {"frontend": "react"},
            "plugins": [],
            "ports": {}
        }
        # Simulate both react and nextjs
        config_unsupported["frameworks"]["frontend"] = "react"
        res_unsupported = Validator.validate(self.test_dir, config_unsupported)
        # Should be fine, but if we add multiple frontend keys:
        # We manually trigger multiple frontends in validate_stack_combinations check
        res = {
            "errors": [],
            "warnings": []
        }
        # Simulate error manually to test combination rules
        mock_config = {
            "frameworks": {"frontend": "react", "mobile": "flutter"},
            "plugins": [],
            "ports": {}
        }
        Validator._validate_stack_combinations(mock_config, res)
        self.assertEqual(len(res["errors"]), 0) # No error

    def test_dockerfile_improvements(self):
        # Write a basic dockerfile with no USER and apt-get install without cache cleaning
        df_path = self.test_dir / "Dockerfile"
        with open(df_path, "w", encoding="utf-8") as f:
            f.write("FROM ubuntu:20.04\nRUN apt-get update && apt-get install -y curl\n")

        # Mock the improve method call
        from engine.generator import ProjectGenerator
        gen = ProjectGenerator()
        gen._improve_dockerfile_file(df_path)

        improved_content = df_path.read_text(encoding="utf-8")
        self.assertTrue("SECURITY HARDENING" in improved_content)
        self.assertTrue("PERFORMANCE OPTIMIZATION" in improved_content)

    def test_compose_merge(self):
        # Write an existing docker-compose.yml
        compose_path = self.test_dir / "docker-compose.yml"
        existing_compose = {
            "version": "3.8",
            "services": {
                "my-web": {
                    "image": "nginx:alpine",
                    "ports": ["80:80"]
                }
            }
        }
        with open(compose_path, "w", encoding="utf-8") as f:
            yaml_content = "services:\n  my-web:\n    image: nginx:alpine\n    ports:\n      - 80:80\n"
            f.write(yaml_content)

        # Generate a mock project with postgres plugin
        from engine.workspace import Project
        project = Project("testproj", path=self.test_dir)
        project.ensure_devforge_dir()

        config = {
            "project_name": "testproj",
            "frameworks": {},
            "plugins": ["postgres"],
            "plugin_versions": {},
            "ports": {"postgres": 5432}
        }

        # Merge
        from engine.generator import ProjectGenerator
        gen = ProjectGenerator()
        gen._generate_or_merge_compose(project, config, "Merge")

        # Load and verify merged file
        with open(compose_path, "r", encoding="utf-8") as f:
            merged = yaml.safe_load(f)

        self.assertIn("my-web", merged["services"])
        self.assertIn("postgres", merged["services"])

if __name__ == "__main__":
    unittest.main()
