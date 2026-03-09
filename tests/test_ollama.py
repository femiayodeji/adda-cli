import unittest
from convo.ollama import _parse_response, OllamaResponse, check_ollama_running, check_model_available

class TestOllama(unittest.TestCase):
    def test_ollama_running(self):
        self.assertTrue(check_ollama_running(), "Ollama server should be running for tests.")
    
    def test_model_available(self):
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

if __name__ == "__main__":
    unittest.main()