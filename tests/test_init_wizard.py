import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "init_wizard", pathlib.Path(__file__).parent.parent / "scripts" / "init_wizard.py"
)
wiz = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wiz)


def test_normalize():
    assert wiz.normalize("8080", "int") == "8080"
    assert wiz.normalize("-1", "int") is None
    assert wiz.normalize("yes", "bool") == "True"
    assert wiz.normalize("maybe", "bool") is None
    assert wiz.normalize("JSON", "choice:text|json") == "json"
    assert wiz.normalize("xml", "choice:text|json") is None


def test_defaults_write_env_and_refuse_overwrite(tmp_path):
    out = tmp_path / ".env"
    assert wiz.main(["--defaults", "--output", str(out)]) == 0
    text = out.read_text()
    assert "PORT=5000" in text and "LOG_FORMAT=text" in text
    assert wiz.main(["--defaults", "--output", str(out)]) == 1


def test_interactive_answers(tmp_path, monkeypatch):
    out = tmp_path / ".env"
    answers = iter(["0.0.0.0", "abc", "8080"] + [""] * 20)
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    assert wiz.main(["--output", str(out)]) == 0
    text = out.read_text()
    assert "HOST=0.0.0.0" in text and "PORT=8080" in text
