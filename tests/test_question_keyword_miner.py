import tempfile
import unittest
from pathlib import Path

import pandas as pd
from click.testing import CliRunner

from question_keyword_miner import cli, core

EXAMPLES = Path(__file__).parent.parent / "examples"


class TypeTest(unittest.TestCase):
    def test_question_types(self):
        self.assertEqual(core.question_type("how to make bread"), "how")
        self.assertEqual(core.question_type("Is sourdough healthy"), "yes/no")
        self.assertEqual(core.question_type("whats a banneton"), "what")
        self.assertEqual(core.question_type("flour for starter?"), "other")
        self.assertIsNone(core.question_type("sourdough recipe"))
        self.assertIsNone(core.question_type("however bakery"))       # first word must match exactly

    def test_action_by_position(self):
        self.assertTrue(core.action(2.5, 100).startswith("Top 3"))
        self.assertTrue(core.action(8, 100).startswith("Page one"))
        self.assertTrue(core.action(15, 100).startswith("Page two"))
        self.assertTrue(core.action(40, 100).startswith("Far back"))
        self.assertTrue(core.action(0, 0).startswith("Not ranking"))


class MineTest(unittest.TestCase):
    def test_autocomplete_uses_fetch_and_keeps_questions(self):
        calls = []

        def fake(q, **kw):
            calls.append(q)
            return [q + " at home", "sourdough near me"] if q.startswith("how") else []

        df = core.autocomplete(["sourdough"], fetch=fake, delay=0)
        self.assertEqual(len(calls), len(core.AUTOCOMPLETE_PREFIXES))
        self.assertEqual(df["question"].tolist(), ["how sourdough at home"])

    def test_merge_sources_and_overview(self):
        gsc = pd.DataFrame({"query": ["how to feed a starter", "sourdough"], "clicks": [5, 9],
                            "impressions": [100, 900], "position": [4.0, 2.0]})
        sugg = pd.DataFrame({"question": ["how to feed a starter", "why is my bread flat"],
                             "seed": ["starter", "bread"]})
        q = core.mine(gsc, sugg, ["starter"]).set_index("question")
        self.assertEqual(q.at["how to feed a starter", "source"], "gsc + autocomplete")
        self.assertEqual(q.at["why is my bread flat", "source"], "autocomplete")
        self.assertEqual(q.at["how to feed a starter", "seed"], "starter")
        ov = core.overview(gsc, q.reset_index())
        self.assertEqual((ov["gsc_queries"], ov["gsc_questions"], ov["question_share_pct"]), (2, 1, 50.0))

    def test_empty(self):
        q = core.mine(pd.DataFrame({"query": ["bread"], "clicks": [1], "impressions": [1], "position": [1]}), None)
        self.assertTrue(q.empty)
        self.assertTrue(core.type_summary(q).empty)


class CliTest(unittest.TestCase):
    def test_example_writes_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "q"
            res = CliRunner().invoke(cli.main, ["--gsc", str(EXAMPLES / "gsc_queries.csv"), "--seed", "sourdough",
                                                "-o", str(out)])
            self.assertEqual(res.exit_code, 0, res.output)
            self.assertIn("Question keyword report", out.with_suffix(".html").read_text(encoding="utf-8"))
            self.assertTrue(out.with_suffix(".xlsx").exists())

    def test_needs_an_input(self):
        res = CliRunner().invoke(cli.main, ["--seed", "bread"])
        self.assertNotEqual(res.exit_code, 0)


if __name__ == "__main__":
    unittest.main()
