
import os
import tempfile
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.agent.prompt_manager import PromptManager, PromptTemplateData


class TestPromptTemplateData:
    def test_create_template_data(self):
        data = PromptTemplateData(
            name="test_template",
            template="Hello {name}",
            input_variables=["name"],
            description="Test template",
            category="test"
        )
        assert data.name == "test_template"
        assert data.template == "Hello {name}"
        assert data.input_variables == ["name"]

    def test_default_values(self):
        data = PromptTemplateData(
            name="test",
            template="test"
        )
        assert data.input_variables == []
        assert data.description == ""
        assert data.category == "default"


class TestPromptManager:
    @pytest.fixture
    def temp_config_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_init(self, temp_config_dir):
        manager = PromptManager(config_dir=temp_config_dir)
        assert manager.config_dir == temp_config_dir
        assert "streamer_recommendation" in manager.templates

    def test_get_template(self, temp_config_dir):
        manager = PromptManager(config_dir=temp_config_dir)
        template = manager.get_template("streamer_recommendation")
        assert template is not None

    def test_get_template_nonexistent(self, temp_config_dir):
        manager = PromptManager(config_dir=temp_config_dir)
        template = manager.get_template("nonexistent")
        assert template is None

    def test_get_template_data(self, temp_config_dir):
        manager = PromptManager(config_dir=temp_config_dir)
        data = manager.get_template_data("streamer_recommendation")
        assert data is not None
        assert data.name == "streamer_recommendation"

    def test_list_templates(self, temp_config_dir):
        manager = PromptManager(config_dir=temp_config_dir)
        templates = manager.list_templates()
        assert len(templates) &gt; 0

    def test_list_templates_with_category(self, temp_config_dir):
        manager = PromptManager(config_dir=temp_config_dir)
        templates = manager.list_templates(category="recommendation")
        assert len(templates) &gt;= 1

    def test_add_template(self, temp_config_dir):
        manager = PromptManager(config_dir=temp_config_dir)
        success = manager.add_template(
            name="new_template",
            template="Hello {user}",
            input_variables=["user"],
            description="A new template",
            category="custom"
        )
        assert success is True
        assert "new_template" in manager.templates

    def test_add_duplicate_template(self, temp_config_dir):
        manager = PromptManager(config_dir=temp_config_dir)
        manager.add_template("test", "template")
        success = manager.add_template("test", "another template")
        assert success is False

    def test_edit_template(self, temp_config_dir):
        manager = PromptManager(config_dir=temp_config_dir)
        manager.add_template("edit_test", "Old template {var}")

        success = manager.edit_template(
            name="edit_test",
            template="New template {var} {var2}",
            description="Updated description"
        )
        assert success is True

        data = manager.get_template_data("edit_test")
        assert data.template == "New template {var} {var2}"
        assert data.description == "Updated description"

    def test_edit_nonexistent_template(self, temp_config_dir):
        manager = PromptManager(config_dir=temp_config_dir)
        success = manager.edit_template("nonexistent", "test")
        assert success is False

    def test_delete_template(self, temp_config_dir):
        manager = PromptManager(config_dir=temp_config_dir)
        manager.add_template("delete_test", "template")

        success = manager.delete_template("delete_test")
        assert success is True
        assert "delete_test" not in manager.templates

    def test_delete_default_template(self, temp_config_dir):
        manager = PromptManager(config_dir=temp_config_dir)
        success = manager.delete_template("streamer_recommendation")
        assert success is False

    def test_delete_nonexistent_template(self, temp_config_dir):
        manager = PromptManager(config_dir=temp_config_dir)
        success = manager.delete_template("nonexistent")
        assert success is False

    def test_format_prompt(self, temp_config_dir):
        manager = PromptManager(config_dir=temp_config_dir)
        manager.add_template(
            name="format_test",
            template="Hello {name}, welcome to {place}!",
            input_variables=["name", "place"]
        )

        result = manager.format_prompt(
            "format_test",
            name="Alice",
            place="Wonderland"
        )
        assert result == "Hello Alice, welcome to Wonderland!"

    def test_format_prompt_nonexistent(self, temp_config_dir):
        manager = PromptManager(config_dir=temp_config_dir)
        result = manager.format_prompt("nonexistent", test="test")
        assert result is None

    def test_debug_prompt(self, temp_config_dir):
        manager = PromptManager(config_dir=temp_config_dir)
        manager.add_template(
            name="debug_test",
            template="Hi {name}",
            input_variables=["name"],
            description="Debug template"
        )

        debug_info = manager.debug_prompt("debug_test", name="Bob")
        assert debug_info is not None
        assert debug_info["template_name"] == "debug_test"
        assert debug_info["formatted_prompt"] == "Hi Bob"

    def test_debug_prompt_nonexistent(self, temp_config_dir):
        manager = PromptManager(config_dir=temp_config_dir)
        debug_info = manager.debug_prompt("nonexistent")
        assert debug_info is None

    def test_export_templates_json(self, temp_config_dir):
        manager = PromptManager(config_dir=temp_config_dir)
        export_file = temp_config_dir / "export.json"

        success = manager.export_templates(export_file, format="json")
        assert success is True
        assert export_file.exists()

        with open(export_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_export_templates_yaml(self, temp_config_dir):
        manager = PromptManager(config_dir=temp_config_dir)
        export_file = temp_config_dir / "export.yaml"

        success = manager.export_templates(export_file, format="yaml")
        assert success is True
        assert export_file.exists()

    def test_export_invalid_format(self, temp_config_dir):
        manager = PromptManager(config_dir=temp_config_dir)
        export_file = temp_config_dir / "export.txt"

        success = manager.export_templates(export_file, format="invalid")
        assert success is False

    def test_import_templates(self, temp_config_dir):
        manager = PromptManager(config_dir=temp_config_dir)
        export_file = temp_config_dir / "import_test.json"

        import_data = {
            "imported_template": {
                "name": "imported_template",
                "template": "Imported: {var}",
                "input_variables": ["var"],
                "description": "Imported",
                "category": "import"
            }
        }

        with open(export_file, "w", encoding="utf-8") as f:
            json.dump(import_data, f, ensure_ascii=False)

        count = manager.import_templates(export_file)
        assert count == 1
        assert "imported_template" in manager.templates

    def test_import_templates_overwrite(self, temp_config_dir):
        manager = PromptManager(config_dir=temp_config_dir)
        manager.add_template("import_overwrite", "Original")

        export_file = temp_config_dir / "import_overwrite.json"
        import_data = {
            "import_overwrite": {
                "name": "import_overwrite",
                "template": "Overwritten",
                "input_variables": [],
                "description": "",
                "category": "default"
            }
        }

        with open(export_file, "w", encoding="utf-8") as f:
            json.dump(import_data, f)

        count = manager.import_templates(export_file, overwrite=True)
        assert count == 1

    def test_import_nonexistent_file(self, temp_config_dir):
        manager = PromptManager(config_dir=temp_config_dir)
        count = manager.import_templates(temp_config_dir / "nonexistent.json")
        assert count == 0

    def test_extract_variables(self, temp_config_dir):
        manager = PromptManager(config_dir=temp_config_dir)
        variables = manager._extract_variables("Hello {name}, today is {day}")
        assert set(variables) == {"name", "day"}

    def test_save_and_load_custom_prompts(self, temp_config_dir):
        manager1 = PromptManager(config_dir=temp_config_dir)
        manager1.add_template("persistent_test", "Persistent template")

        manager2 = PromptManager(config_dir=temp_config_dir)
        assert "persistent_test" in manager2.templates

    def test_add_template_auto_extract_variables(self, temp_config_dir):
        manager = PromptManager(config_dir=temp_config_dir)
        manager.add_template(
            name="auto_var",
            template="Hello {user} from {location}"
        )
        data = manager.get_template_data("auto_var")
        assert set(data.input_variables) == {"user", "location"}

