import unittest

from convo.prompt import build_system_prompt

class TestPrompt(unittest.TestCase):
    def test_prompt(self):
        system_prompt = build_system_prompt()
        self.assertIn("You are a Linux command assistant", system_prompt)

if __name__ == "__main__":
    unittest.main()