import unittest
from convo.cli import _display_clarification, _display_command, _preflight_checks

class TestCLI(unittest.TestCase):
    def test_cli__preflight_checks(self):
        self.assertTrue(_preflight_checks("llama3.1"), "Preflight checks should pass with valid model and Ollama running.")
    
    def test_cli__preflight_checks_invalid_model(self):
        self.assertFalse(_preflight_checks("nonexistent-model"), "Preflight checks should fail with an invalid model.")
    
    def test_cli__preflight_checks_ollama_not_running(self):
        self.assertFalse(_preflight_checks("llama3.1"), "Preflight checks should fail if Ollama is not running.")
    
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

if __name__ == "__main__":
    unittest.main()

