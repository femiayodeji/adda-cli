import unittest
from unittest.mock import patch
from typer.testing import CliRunner

from adda.cli import app, _display_clarification, _display_command, _display_humane, _preflight_checks


runner = CliRunner()

class TestCLI(unittest.TestCase):
    @patch("adda.cli.check_model_available", return_value=True)
    @patch("adda.cli.check_ollama_running", return_value=True)
    def test_cli__preflight_checks(self, _mock_running, _mock_model):
        self.assertTrue(
            _preflight_checks("ollama", "llama3.1"),
            "Preflight checks should pass with valid model and Ollama running.",
        )
    
    @patch("adda.cli.check_model_available", return_value=False)
    @patch("adda.cli.check_ollama_running", return_value=True)
    def test_cli__preflight_checks_invalid_model(self, _mock_running, _mock_model):
        self.assertFalse(
            _preflight_checks("ollama", "nonexistent-model"),
            "Preflight checks should fail with an invalid model.",
        )
    
    @patch("adda.cli.check_ollama_running", return_value=False)
    def test_cli__preflight_checks_ollama_not_running(self, _mock_running):
        self.assertFalse(
            _preflight_checks("ollama", "llama3.1"),
            "Preflight checks should fail if Ollama is not running.",
        )

    @patch("adda.cli.check_groq_model_available", return_value=True)
    @patch("adda.cli.check_groq_api_key", return_value=True)
    def test_cli__preflight_checks_groq(self, _mock_key, _mock_model):
        self.assertTrue(
            _preflight_checks("groq", "llama-3.3-70b-versatile"),
            "Preflight checks should pass with Groq key and valid model.",
        )

    @patch("adda.cli.set_model")
    def test_config_command_sets_model(self, mock_set_model):
        mock_set_model.return_value = type("Cfg", (), {"model": "llama3.2"})()
        result = runner.invoke(app, ["config", "--model", "llama3.2"])
        self.assertEqual(result.exit_code, 0)
        mock_set_model.assert_called_once_with("llama3.2")

    @patch("adda.cli.set_groq_api_key")
    def test_config_command_sets_api_key(self, mock_set_api_key):
        result = runner.invoke(app, ["config", "--api-key", "sk-test"])
        self.assertEqual(result.exit_code, 0)
        mock_set_api_key.assert_called_once_with("sk-test")

    @patch("adda.cli.set_groq_api_key")
    def test_config_command_clears_api_key_when_empty(self, mock_set_api_key):
        result = runner.invoke(app, ["config", "--api-key", ""])
        self.assertEqual(result.exit_code, 0)
        mock_set_api_key.assert_called_once_with(None)
    
    def test_display_command(self):
        try:
            _display_command("ls -la", "To list all files in long format")
        except Exception as e:
            self.fail(f"_display_command raised an exception: {e}")
    
    def test_display_command_no_reason(self):
        try:
            _display_command("pwd", None)
        except Exception as e:
            self.fail(f"_display_command raised an exception when reason is None: {e}")
    
    def test_display_command_empty_reason(self):
        try:
            _display_command("pwd", "")
        except Exception as e:
            self.fail(f"_display_command raised an exception when reason is empty: {e}")
            
    def test_display_command_empty_command(self):
        try:
            _display_command("", "Reason for empty command")
        except Exception as e:
            self.fail(f"_display_command raised an exception when command is empty: {e}")

    def test_display_command_none_command(self):
        try:
            _display_command(None, "Reason for None command")
        except Exception as e:
            self.fail(f"_display_command raised an exception when command is None: {e}")

    def test_display_clarification(self):
        try:
            _display_clarification("What directory are you interested in?")
        except Exception as e:
            self.fail(f"_display_clarification raised an exception: {e}")

    def test_display_clarification_empty(self):
        try:
            _display_clarification("")
        except Exception as e:
            self.fail(f"_display_clarification raised an exception when question is empty: {e}")
    
    def test_display_clarification_whitespace(self):
        try:
            _display_clarification("   ")
        except Exception as e:
            self.fail(f"_display_clarification raised an exception when question is whitespace: {e}")

    def test_display_clarification_none(self):
        try:
            _display_clarification(None)
        except Exception as e:
            self.fail(f"_display_clarification raised an exception when question is None: {e}")
    
    def test_display_clarification_long_question(self):
        long_question = "What is the meaning of life, the universe, and everything?" * 10
        try:
            _display_clarification(long_question)
        except Exception as e:
            self.fail(f"_display_clarification raised an exception with a long question: {e}")
    
    def test_display_clarification_special_characters(self):
        special_question = "What about special characters like !@#$%^&*()?"
        try:
            _display_clarification(special_question)
        except Exception as e:
            self.fail(f"_display_clarification raised an exception with special characters: {e}")

    def test_display_humane(self):
        try:
            _display_humane("You're welcome, feel free to ask for more assistance.")
        except Exception as e:
            self.fail(f"_display_humane raised an exception: {e}")

if __name__ == "__main__":
    unittest.main()

