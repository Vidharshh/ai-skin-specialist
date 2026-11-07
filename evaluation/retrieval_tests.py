import unittest

from rag.retriever import retrieve_knowledge


class RetrievalTests(unittest.TestCase):
    def test_scar_question_ranks_scars_first(self):
        results = retrieve_knowledge(
            "Can you please check if my scar on the hand can be removed?"
        )
        self.assertTrue(results)
        self.assertEqual(results[0]["id"], "medlineplus-scars")

    def test_itchy_rash_question_retrieves_eczema(self):
        results = retrieve_knowledge("I have dry itchy skin and a rash")
        self.assertTrue(results)
        self.assertIn("medlineplus-eczema", {item["id"] for item in results})

    def test_unrelated_query_returns_no_sources(self):
        self.assertEqual(retrieve_knowledge("weather forecast for tomorrow"), [])

    def test_limit_is_respected(self):
        results = retrieve_knowledge("skin scars and acne", limit=1)
        self.assertLessEqual(len(results), 1)


if __name__ == "__main__":
    unittest.main()
