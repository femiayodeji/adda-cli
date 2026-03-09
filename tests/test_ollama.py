import unittest
from unittest.mock import Mock, patch
from adda.ollama import _parse_response, OllamaResponse, check_ollama_running, check_model_available

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

    @patch("adda.ollama.requests.post")
    def test_chat_non_streaming(self, mock_post):
        from adda.ollama import chat

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "message": {"content": "COMMAND: pwd\nREASON: Show current directory"}
        }
        mock_post.return_value = mock_response

        response = chat(
            model="llama3.1",
            system_prompt="system",
            history=[],
            user_message="where am i",
        )

        self.assertEqual(response.kind, "command")
        self.assertEqual(response.command, "pwd")
        self.assertEqual(response.reason, "Show current directory")
        _, kwargs = mock_post.call_args
        self.assertFalse(kwargs["json"]["stream"])

    @patch("adda.ollama.requests.post")
    def test_chat_streaming(self, mock_post):
        from adda.ollama import chat

        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.iter_lines.return_value = [
            '{"message":{"content":"COMMAND: pwd\\n"},"done":false}',
            '{"message":{"content":"REASON: Show current directory"},"done":false}',
            '{"done":true}',
        ]
        mock_post.return_value = mock_response

        seen_tokens: list[str] = []
        response = chat(
            model="llama3.1",
            system_prompt="system",
            history=[],
            user_message="where am i",
            stream=True,
            on_token=seen_tokens.append,
        )

        self.assertEqual(response.kind, "command")
        self.assertEqual(response.command, "pwd")
        self.assertEqual(response.reason, "Show current directory")
        self.assertEqual(
            seen_tokens,
            ["COMMAND: pwd\n", "REASON: Show current directory"],
        )
        _, kwargs = mock_post.call_args
        self.assertTrue(kwargs["json"]["stream"])
        self.assertTrue(kwargs["stream"])

    @patch("adda.ollama.get_groq_api_key", return_value=None)
    def test_chat_groq_missing_key(self, _):
        from adda.ollama import chat

        response = chat(
            model="llama-3.3-70b-versatile",
            system_prompt="system",
            history=[],
            user_message="where am i",
            provider="groq",
        )

        self.assertEqual(response.kind, "error")
        self.assertIn("GROQ_API_KEY", response.raw)

    @patch.dict("adda.ollama.os.environ", {}, clear=True)
    @patch("adda.config.load_config")
    def test_get_groq_api_key_falls_back_to_config(self, mock_load_config):
        from adda.ollama import get_groq_api_key

        mock_load_config.return_value = type("Cfg", (), {"groq_api_key": "cfg-key"})()
        self.assertEqual(get_groq_api_key(), "cfg-key")

if __name__ == "__main__":
    unittest.main()
