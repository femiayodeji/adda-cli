import os
import unittest

from adda.config import (
    CONFIG_FILE,
    Config,
    load_config,
    save_config,
    set_model,
    set_provider,
    set_stream,
    show_config,
)

class TestConfig(unittest.TestCase):
    def test_load_config_defaults(self):
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
        config = load_config()
        self.assertEqual(config.provider, Config.provider)
        self.assertEqual(config.model, Config.model)
        self.assertEqual(config.stream, Config.stream)

    def test_save_and_load_config(self):
        config = Config(provider="groq", model="llama3.1", stream=False, groq_api_key="abc123")
        save_config(config)
        loaded_config = load_config()
        self.assertEqual(loaded_config.provider, "groq")
        self.assertEqual(loaded_config.model, "llama3.1")
        self.assertFalse(loaded_config.stream)
        self.assertEqual(loaded_config.groq_api_key, "abc123")

    def test_set_provider(self):
        set_provider("groq")
        config = load_config()
        self.assertEqual(config.provider, "groq")

    def test_set_model(self):
        set_model("llama3.1")
        config = load_config()
        self.assertEqual(config.model, "llama3.1")

    def test_set_stream(self):
        set_stream(False)
        config = load_config()
        self.assertFalse(config.stream)

    def test_set_groq_api_key(self):
        os.environ["GROQ_API_KEY"] = "sk-test"
        config = load_config()
        self.assertEqual(config.groq_api_key, "sk-test")

    def test_show_config(self):
        output = show_config()
        self.assertIn("Config file", output)
        self.assertIn("Provider", output)
        self.assertIn("Model", output)
        self.assertIn("Stream", output)
        self.assertIn("Groq API key", output)

if __name__ == "__main__":
    unittest.main()