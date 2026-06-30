# ==============================================================================
# DEVFORGE AI PLUGIN GENERATION SYSTEM TESTS
# ==============================================================================
# Comprehensive unit tests for AI Providers, Factory, Collectors, Cache,
# Validator, Renderer, Registry, and Installer.
# Uses unittest.mock to prevent actual API calls and network overhead.
# ==============================================================================

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml

# Imports from engine
from engine.ai.factory import AIFactory
from engine.ai.models import (
    HealthCheckSpecification,
    PluginSpecification,
    PortSpecification,
)
from engine.ai.plugin_generator import AIPluginGenerator
from engine.ai.provider import AIProvider, extract_json
from engine.config.ai_config import AIConfig
from engine.detector.knowledge_collector import KnowledgeCollector
from engine.detector.metadata_collector import MetadataCollector
from engine.plugins.cache import PluginCache
from engine.plugins.installer import PluginInstaller
from engine.plugins.registry import PluginRegistry
from engine.plugins.renderer import PluginRenderer
from engine.plugins.validator import PluginValidator
from engine.workspace import Project


class TestAISystem(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory structure for tests
        self.test_dir = Path(tempfile.mkdtemp())
        self.project_path = self.test_dir / "myproject"
        self.project_path.mkdir()

        # Set up a mock devforge root structure
        self.df_root = self.test_dir / "devforge"
        self.df_root.mkdir()
        (self.df_root / "registry").mkdir()
        (self.df_root / "plugins").mkdir()
        (self.df_root / "plugins" / "generated").mkdir()

        # Patch get_devforge_root globally to return our mock root
        self.patcher_root = patch("engine.workspace.get_devforge_root", return_value=self.df_root)
        self.patcher_root_registry = patch("engine.plugins.registry.get_devforge_root", return_value=self.df_root)
        self.patcher_root_cache = patch("engine.plugins.cache.get_devforge_root", return_value=self.df_root)
        self.patcher_root_manager = patch("engine.plugin_manager.get_devforge_root", return_value=self.df_root)

        self.mock_root = self.patcher_root.start()
        self.mock_root_reg = self.patcher_root_registry.start()
        self.mock_root_cache = self.patcher_root_cache.start()
        self.mock_root_mgr = self.patcher_root_manager.start()

        # Write default plugins.yaml registry
        self.reg_file = self.df_root / "registry" / "plugins.yaml"
        self.default_registry = {
            "plugins": [
                {
                    "name": "postgres",
                    "display_name": "PostgreSQL",
                    "category": "database",
                    "versions": ["16"],
                    "path": "plugins/postgres",
                }
            ]
        }
        with open(self.reg_file, "w", encoding="utf-8") as f:
            yaml.dump(self.default_registry, f)

        # Build a valid mock PluginSpecification
        self.mock_spec = PluginSpecification(
            plugin_name="supabase",
            display_name="Supabase",
            description="Open Source Firebase Alternative",
            category="database",
            docker_image="supabase/postgres",
            docker_tag="15.1.0",
            service_name="supabase",
            ports=[
                PortSpecification(host=54321, container=54321, env_key="SUPABASE_PORT")
            ],
            environment_variables={"SUPABASE_PASSWORD": "mysecretpassword"},
            volumes=["supadata:/var/lib/supabase"],
            healthcheck=HealthCheckSpecification(
                test=["CMD-SHELL", "pg_isready"],
                interval="10s",
                timeout="5s",
                retries=3,
                start_period="5s",
            ),
            dependencies=["postgres"],
        )

    def tearDown(self):
        self.patcher_root.stop()
        self.patcher_root_registry.stop()
        self.patcher_root_cache.stop()
        self.patcher_root_manager.stop()
        shutil.rmtree(self.test_dir)

    # ──────────────────────────────────────────────────────────────────────────
    # 1. TEST CONFIGURATION & ENVIRONMENT EXPANSION
    # ──────────────────────────────────────────────────────────────────────────

    def test_config_loading_and_expansion(self):
        # Create a mock devforge-ai.yaml
        config_yaml = self.project_path / "devforge-ai.yaml"
        config_content = """
provider: groq
model: llama-3.1-8b-instant
temperature: 0.5
providers:
  groq:
    api_key: ${MOCK_GROQ_KEY}
    base_url: https://api.groq.com
    models:
      - llama-3.1-8b-instant
"""
        config_yaml.write_text(config_content)

        # Set environment variable mock
        os.environ["MOCK_GROQ_KEY"] = "super-secret-key-123"

        config = AIConfig.load(config_path=config_yaml)
        self.assertEqual(config.provider, "groq")
        self.assertEqual(config.temperature, 0.5)
        self.assertEqual(config.providers["groq"].api_key, "super-secret-key-123")

    # ──────────────────────────────────────────────────────────────────────────
    # 2. TEST STRATEGY & FACTORY PATTERN RESOLUTION
    # ──────────────────────────────────────────────────────────────────────────

    def test_ai_factory_resolves_providers(self):
        config = AIConfig()
        config.providers["groq"] = MagicMock()
        config.providers["gemini"] = MagicMock()
        config.providers["openai"] = MagicMock()
        config.providers["ollama"] = MagicMock()

        # Test Groq Strategy resolution
        groq_prov = AIFactory.get_provider(config, "groq")
        self.assertEqual(groq_prov.__class__.__name__, "GroqProvider")

        # Test Gemini Strategy resolution
        gemini_prov = AIFactory.get_provider(config, "gemini")
        self.assertEqual(gemini_prov.__class__.__name__, "GeminiProvider")

        # Test OpenAI Strategy resolution
        openai_prov = AIFactory.get_provider(config, "openai")
        self.assertEqual(openai_prov.__class__.__name__, "OpenAIProvider")

        # Test Ollama Strategy resolution
        ollama_prov = AIFactory.get_provider(config, "ollama")
        self.assertEqual(ollama_prov.__class__.__name__, "OllamaProvider")

        # Test invalid provider raising ValueError
        with self.assertRaises(ValueError):
            AIFactory.get_provider(config, "invalid-provider")

    # ──────────────────────────────────────────────────────────────────────────
    # 3. TEST ROBUST JSON PARSING UTILITIES
    # ──────────────────────────────────────────────────────────────────────────

    def test_extract_json_edge_cases(self):
        # Case A: Plain JSON
        plain = '{"key": "value"}'
        self.assertEqual(extract_json(plain), {"key": "value"})

        # Case B: Markdown code block wrapped JSON
        markdown = "```json\n{\n  \"key\": \"value\"\n}\n```"
        self.assertEqual(extract_json(markdown), {"key": "value"})

        # Case C: JSON surrounded by text explanations
        noise = "Certainly! Here is your specification: {\"key\": \"value\"} Hope this helps!"
        self.assertEqual(extract_json(noise), {"key": "value"})

        # Case D: Invalid JSON text
        invalid = "no json here"
        with self.assertRaises(ValueError):
            extract_json(invalid)

    # ──────────────────────────────────────────────────────────────────────────
    # 4. TEST PROVIDER strategy MOCKS (Groq, Gemini, OpenAI, Ollama)
    # ──────────────────────────────────────────────────────────────────────────

    @patch("engine.ai.groq_provider.httpx.Client")
    def test_groq_provider_generates_spec(self, mock_http_client):
        # Mock httpx client POST call returning Groq/OpenAI completions structure
        mock_client_instance = mock_http_client.return_value.__enter__.return_value
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(self.mock_spec.model_dump())
                    }
                }
            ]
        }
        mock_client_instance.post.return_value = mock_response

        config = AIConfig()
        config.providers["groq"] = MagicMock(api_key="test-key")

        provider = AIFactory.get_provider(config, "groq")
        result = provider.generate_plugin("mock prompt")

        self.assertEqual(result.plugin_name, "supabase")
        self.assertEqual(result.ports[0].host, 54321)

    @patch("engine.ai.gemini_provider.httpx.Client")
    def test_gemini_provider_generates_spec(self, mock_http_client):
        # Mock httpx client POST call returning Gemini candidates structure
        mock_client_instance = mock_http_client.return_value.__enter__.return_value
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": json.dumps(self.mock_spec.model_dump())
                            }
                        ]
                    }
                }
            ]
        }
        mock_client_instance.post.return_value = mock_response

        config = AIConfig()
        config.providers["gemini"] = MagicMock(api_key="test-key")

        provider = AIFactory.get_provider(config, "gemini")
        result = provider.generate_plugin("mock prompt")

        self.assertEqual(result.plugin_name, "supabase")
        self.assertEqual(result.ports[0].env_key, "SUPABASE_PORT")

    @patch("engine.ai.openai_provider.httpx.Client")
    def test_openai_provider_generates_spec(self, mock_http_client):
        # Mock httpx client POST call returning OpenAI completions structure
        mock_client_instance = mock_http_client.return_value.__enter__.return_value
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(self.mock_spec.model_dump())
                    }
                }
            ]
        }
        mock_client_instance.post.return_value = mock_response

        config = AIConfig()
        config.providers["openai"] = MagicMock(api_key="test-key")

        provider = AIFactory.get_provider(config, "openai")
        result = provider.generate_plugin("mock prompt")

        self.assertEqual(result.plugin_name, "supabase")

    @patch("engine.ai.ollama_provider.httpx.Client")
    def test_ollama_provider_generates_spec(self, mock_http_client):
        # Mock httpx POST request response
        mock_client_instance = mock_http_client.return_value.__enter__.return_value
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "response": json.dumps(self.mock_spec.model_dump())
        }
        mock_client_instance.post.return_value = mock_response

        config = AIConfig()
        config.providers["ollama"] = MagicMock(base_url="http://localhost:11434")

        provider = AIFactory.get_provider(config, "ollama")
        result = provider.generate_plugin("mock prompt")

        self.assertEqual(result.plugin_name, "supabase")

    # ──────────────────────────────────────────────────────────────────────────
    # 5. TEST METADATA & KNOWLEDGE COLLECTORS
    # ──────────────────────────────────────────────────────────────────────────

    def test_metadata_collector_extracts_correctly(self):
        # Write package.json with dependencies
        pj = self.project_path / "package.json"
        pj_data = {
            "dependencies": {"supabase": "1.0.0"},
            "devDependencies": {"jest": "29.0.0"},
        }
        with open(pj, "w") as f:
            json.dump(pj_data, f)

        # Write requirements.txt
        reqs = self.project_path / "requirements.txt"
        reqs.write_text("pymilvus>=2.4.0\n")

        # Write Dockerfile
        df = self.project_path / "Dockerfile"
        df.write_text("FROM python:3.11-slim\nENV MY_VAR=hello\nEXPOSE 8080\n")

        # Collect metadata
        metadata = MetadataCollector.collect(self.project_path)

        self.assertIn("supabase", metadata["packages"])
        self.assertIn("pymilvus", metadata["packages"])
        self.assertIn("JavaScript/TypeScript", metadata["languages"])
        self.assertIn("Python", metadata["languages"])
        self.assertIn("python:3.11-slim", metadata["docker_images"])
        self.assertIn(8080, metadata["ports"])
        self.assertIn("MY_VAR", metadata["environment_variables"])

    def test_knowledge_collector_enrichment(self):
        # Test recognized technology properties
        k_supabase = KnowledgeCollector.collect("supabase")
        self.assertEqual(k_supabase["docker_image"], "supabase/postgres")
        self.assertIn("postgres", k_supabase["dependencies"])
        self.assertEqual(k_supabase["category"], "database")

        # Test completely unrecognized technology fallback heuristics
        k_unknown = KnowledgeCollector.collect("customstore")
        self.assertEqual(k_unknown["docker_image"], "customstore/customstore")
        self.assertEqual(k_unknown["category"], "database")  # contains "store"

        k_another = KnowledgeCollector.collect("my-fancy-worker")
        self.assertEqual(k_another["category"], "service")

    # ──────────────────────────────────────────────────────────────────────────
    # 6. TEST GENERATED PLUGIN CACHE
    # ──────────────────────────────────────────────────────────────────────────

    def test_plugin_cache_operations(self):
        # Cached checking before files created
        self.assertFalse(PluginCache.exists("supabase"))

        # Create cached folder
        cache_dir = self.df_root / "plugins" / "generated" / "supabase"
        cache_dir.mkdir(parents=True)
        (cache_dir / "plugin.yaml").write_text("name: supabase")

        # Verify cache detection
        self.assertTrue(PluginCache.exists("supabase"))
        self.assertEqual(PluginCache.get_path("supabase"), cache_dir)

        # Clear cache
        PluginCache.clear("supabase")
        self.assertFalse(PluginCache.exists("supabase"))

    # ──────────────────────────────────────────────────────────────────────────
    # 7. TEST SPECIFICATION VALIDATOR
    # ──────────────────────────────────────────────────────────────────────────

    def test_plugin_validator_success_and_failures(self):
        # 1. Standard valid spec passes
        res_pass = PluginValidator.validate(self.mock_spec)
        self.assertTrue(res_pass.passed)
        self.assertEqual(len(res_pass.errors), 0)

        # 2. Port Conflict Validation
        active_ports = {"postgres": 54321}  # matches our spec host port
        res_port_fail = PluginValidator.validate(self.mock_spec, active_ports)
        self.assertFalse(res_port_fail.passed)
        self.assertTrue(any("Port conflict" in err for err in res_port_fail.errors))

        # 3. Invalid Category Validation
        bad_spec = self.mock_spec.model_copy()
        bad_spec.category = "invalid-category"
        res_cat_fail = PluginValidator.validate(bad_spec)
        self.assertFalse(res_cat_fail.passed)
        self.assertTrue(any("Category" in err for err in res_cat_fail.errors))

        # 4. Invalid Plugin name Validation (capital letters)
        bad_spec_name = self.mock_spec.model_copy()
        bad_spec_name.plugin_name = "Supabase-Plugin"
        res_name_fail = PluginValidator.validate(bad_spec_name)
        self.assertFalse(res_name_fail.passed)

    # ──────────────────────────────────────────────────────────────────────────
    # 8. TEST PLUGIN FILES RENDERER
    # ──────────────────────────────────────────────────────────────────────────

    def test_plugin_renderer_outputs_expected_files(self):
        renderer = PluginRenderer()
        output_dir = self.test_dir / "rendered_supabase"

        renderer.render(self.mock_spec, output_dir)

        # Confirm all 5 expected files exist
        self.assertTrue((output_dir / "plugin.yaml").exists())
        self.assertTrue((output_dir / "compose.fragment.yaml").exists())
        self.assertTrue((output_dir / "README.md").exists())
        self.assertTrue((output_dir / "env.example").exists())
        self.assertTrue((output_dir / "healthcheck.sh").exists())

        # Verify rendered YAML contents
        yaml_content = (output_dir / "plugin.yaml").read_text()
        parsed_yaml = yaml.safe_load(yaml_content)
        self.assertEqual(parsed_yaml["name"], "supabase")
        self.assertEqual(parsed_yaml["category"], "database")
        self.assertEqual(parsed_yaml["env"]["SUPABASE_PASSWORD"], "mysecretpassword")

        # Verify compose fragment content uses correct anchors
        compose_content = (output_dir / "compose.fragment.yaml").read_text()
        self.assertTrue("container_name: \"{{ project_name }}-supabase\"" in compose_content)
        self.assertTrue("logging: *default-logging" in compose_content)

    # ──────────────────────────────────────────────────────────────────────────
    # 9. TEST REGISTRY PERSISTENCE
    # ──────────────────────────────────────────────────────────────────────────

    def test_plugin_registry_find_and_register(self):
        # 1. Verify priority resolution lookup
        p_postgres = PluginRegistry.find_plugin("PostgreSQL")
        self.assertIsNotNone(p_postgres)
        self.assertEqual(p_postgres["name"], "postgres")

        # 2. Register new generated plugin
        relative_path = "plugins/generated/supabase"
        self.assertTrue(PluginRegistry.register_plugin(self.mock_spec, relative_path))

        # Check that it exists now in registry
        p_supabase = PluginRegistry.find_plugin("supabase")
        self.assertIsNotNone(p_supabase)
        self.assertEqual(p_supabase["path"], relative_path)
        self.assertEqual(p_supabase["display_name"], "Supabase")
        self.assertIn("postgres", p_supabase["depends_on"])

    # ──────────────────────────────────────────────────────────────────────────
    # 10. TEST INSTALLER WORKFLOW
    # ──────────────────────────────────────────────────────────────────────────

    @patch("engine.plugins.installer.PluginManager")
    def test_installer_delegates_to_plugin_manager(self, mock_plugin_mgr):
        mock_mgr_instance = mock_plugin_mgr.return_value
        
        project = Project("myproj", path=self.project_path)
        success = PluginInstaller.install("supabase", project)
        
        self.assertTrue(success)
        mock_mgr_instance.install.assert_called_once_with("supabase", project)


if __name__ == "__main__":
    unittest.main()
