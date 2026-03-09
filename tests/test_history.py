import unittest

from convo.history import CONFIG_DIR, _ensure_config_dir, append_exchange, clear_history
from convo.history import clear_history, append_exchange, save_history, load_history

class TestHistory(unittest.TestCase):
    def test_history_ensure_config_dir(self):
        _ensure_config_dir()
        self.assertTrue(CONFIG_DIR.exists())
    
    def test_history_load_and_save(self):
        clear_history()

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        save_history(messages)

        loaded_messages = load_history()
        self.assertEqual(messages, loaded_messages)

    def test_history_load_empty(self):
        clear_history()
        loaded_messages = load_history()
        self.assertEqual(loaded_messages, [])
    
    def test_history_load_corrupted(self):
        _ensure_config_dir()
        (CONFIG_DIR / "session.json").write_text("not a valid json")
        loaded_messages = load_history()
        self.assertEqual(loaded_messages, [])
    
    def test_history_append_exchange(self):
        history = []
        history = append_exchange(history, "What is the date?", "The date is 2024-06-01.")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "What is the date?")
        self.assertEqual(history[1]["role"], "assistant")
        self.assertEqual(history[1]["content"], "The date is 2024-06-01.")

if __name__ == "__main__":
    unittest.main()