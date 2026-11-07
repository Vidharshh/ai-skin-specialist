import unittest

from agents.vision_agent import VISION_SYSTEM_PROMPT


class SafetyPromptTests(unittest.TestCase):
    def test_prompt_disallows_image_based_diagnosis(self):
        self.assertIn("Do not diagnose", VISION_SYSTEM_PROMPT)
        self.assertIn("from an image", VISION_SYSTEM_PROMPT)

    def test_prompt_limits_claims_to_visible_features(self):
        self.assertIn("Describe only visible features", VISION_SYSTEM_PROMPT)
        self.assertIn("do not infer texture, pain, warmth, duration", VISION_SYSTEM_PROMPT)

    def test_prompt_escalates_urgent_symptoms(self):
        self.assertIn("trouble breathing", VISION_SYSTEM_PROMPT)
        self.assertIn("local emergency services immediately", VISION_SYSTEM_PROMPT)
        self.assertIn("prompt clinical assessment", VISION_SYSTEM_PROMPT)

    def test_prompt_avoids_unqualified_treatment_recommendations(self):
        self.assertIn("do not recommend a specific procedure", VISION_SYSTEM_PROMPT.lower())
        self.assertIn("dermatologist or clinician assessment", VISION_SYSTEM_PROMPT.lower())


if __name__ == "__main__":
    unittest.main()
