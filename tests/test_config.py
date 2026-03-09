import unittest
from convo.config import load_config, save_config, set_model, set_stream, show_config, Config, CONFIG_FILE

class TestConfig(unittest.TestCase):
    def test_load_config_defaults(self):
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
        config = load_config()
        self.assertEqual(config.model, Config.model)
        self.assertEqual(config.stream, Config.stream)

    def test_save_and_load_config(self):
        config = Config(model="test-model", stream=False)
        save_config(config)
        loaded_config = load_config()
        self.assertEqual(loaded_config.model, "test-model")
        self.assertFalse(loaded_config.stream)

    def test_set_model(self):
        set_model("new-model")
        config = load_config()
        self.assertEqual(config.model, "new-model")

    def test_set_stream(self):
        set_stream(False)
        config = load_config()
        self.assertFalse(config.stream)

    def test_show_config(self):
        output = show_config()
        self.assertIn("Config file", output)
        self.assertIn("Model", output)
        self.assertIn("Stream", output)

if __name__ == "__main__":
    unittest.main()