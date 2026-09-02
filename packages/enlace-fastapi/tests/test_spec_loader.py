import json

from enlace_fastapi._spec_loader import load_spec


def test_returns_already_parsed_dict_unchanged():
    spec = {"openapi": "3.0.0"}
    assert load_spec(spec) is spec


def test_parses_a_json_file(tmp_path):
    file = tmp_path / "spec.json"
    file.write_text(json.dumps({"openapi": "3.0.0", "info": {"title": "Test"}}))
    assert load_spec(file) == {"openapi": "3.0.0", "info": {"title": "Test"}}


def test_parses_a_json_file_given_as_str_path(tmp_path):
    file = tmp_path / "spec.json"
    file.write_text(json.dumps({"openapi": "3.0.0"}))
    assert load_spec(str(file)) == {"openapi": "3.0.0"}


def test_parses_a_yaml_file(tmp_path):
    file = tmp_path / "spec.yaml"
    file.write_text("openapi: 3.0.0\ninfo:\n  title: Test\n")
    assert load_spec(file) == {"openapi": "3.0.0", "info": {"title": "Test"}}


def test_parses_a_yml_file(tmp_path):
    file = tmp_path / "spec.yml"
    file.write_text("openapi: 3.0.0\n")
    assert load_spec(file) == {"openapi": "3.0.0"}
