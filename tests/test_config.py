import unittest
from convo.config import load_config, save_config, set_model, show_config, Config, CONFIG_FILE

class TestConfig(unittest.TestCase):
    def test_load_config_defaults(self):
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
        config = load_config()
        self.assertEqual(config.model, Config.model)

    def test_save_and_load_config(self):
        config = Config(model="test-model")
        save_config(config)
        loaded_config = load_config()
        self.assertEqual(loaded_config.model, "test-model")

    def test_set_model(self):
        set_model("new-model")
        config = load_config()
        self.assertEqual(config.model, "new-model")

    def test_show_config(self):
        output = show_config()
        self.assertIn("Config file", output)
        self.assertIn("Model", output)

if __name__ == "__main__":
    unittest.main()