import os
import unittest
from unittest.mock import Mock, patch
from adda.ollama import _parse_response, OllamaResponse, check_ollama_running, check_model_available, get_groq_api_key

class TestOllama(unittest.TestCase):
    @patch("adda.ollama.requests.get")
    def test_ollama_running(self, mock_get):
        mock_get.return_value = Mock()
        self.assertTrue(check_ollama_running(), "Ollama server should be running for tests.")
    
    @patch("adda.ollama.requests.get")
    def test_model_available(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {"models": [{"name": "llama3.1"}]}
        mock_get.return_value = mock_response

        self.assertTrue(check_model_available("llama3.1"), "Model 'llama3.1' should be available for tests.")
    
    def test_parse_response_command(self):
        text = "COMMAND: ls -la\nREASON: To list all files in long format"
        response = _parse_response(text)
        self.assertEqual(response.kind, "command")
        self.assertEqual(response.command, "ls -la")
        self.assertEqual(response.reason, "To list all files in long format")
    
    def test_parse_response_clarify(self):
        text = "CLARIFY: What directory are you interested in?"
        response = _parse_response(text)
        self.assertEqual(response.kind, "clarify")
        self.assertEqual(response.clarification, "What directory are you interested in?")

    def test_parse_response_error(self):
        text = "This is an unexpected response format."
        response = _parse_response(text)
        self.assertEqual(response.kind, "error")
        self.assertEqual(response.raw, text)
    
    def test_parse_response_partial(self):
        text = "COMMAND: pwd"
        response = _parse_response(text)
        self.assertEqual(response.kind, "command")
        self.assertEqual(response.command, "pwd")
        self.assertIsNone(response.reason)

    def test_parse_response_reason_only_is_humane(self):
        text = "REASON: You're welcome, feel free to ask for more assistance."
        response = _parse_response(text)
        self.assertEqual(response.kind, "humane")
        self.assertEqual(response.reason, "You're welcome, feel free to ask for more assistance.")
        self.assertEqual(response.raw, text)
    
    def test_parse_response_empty(self):
        text = ""
        response = _parse_response(text)
        self.assertEqual(response.kind, "error")
        self.assertEqual(response.raw, text)
    
    def test_parse_response_malformed(self):
        text = "COMMAND ls -la REASON To list files"
        response = _parse_response(text)
        self.assertEqual(response.kind, "error")
        self.assertEqual(response.raw, text)

    @patch.dict("os.environ", {"GROQ_API_KEY": "test-key"})
    def test_groq_api_key_from_env(self):
        key = os.environ.get("GROQ_API_KEY")
        self.assertEqual(key, "test-key")

if __name__ == "__main__":
    unittest.main()
