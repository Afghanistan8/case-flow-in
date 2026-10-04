import importlib.util
import json
import sys
import types
import unittest
from pathlib import Path


class FakePublic:
    write = staticmethod(lambda fn: fn)
    view = staticmethod(lambda fn: fn)


class FakeEq:
    result = None
    def prompt_comparative(self, callback, principle):
        if isinstance(self.result, Exception):
            raise self.result
        return callback() if self.result is None else self.result


def load_contract():
    runtime = types.ModuleType("genlayer")
    runtime.gl = types.SimpleNamespace(
        Contract=object, public=FakePublic, vm=types.SimpleNamespace(UserError=ValueError),
        message=types.SimpleNamespace(sender_address="0xA", chain_id=61999),
        message_raw={"datetime": "2026-10-05T00:00:00Z"}, eq_principle=FakeEq(),
        nondet=types.SimpleNamespace(
            web=types.SimpleNamespace(render=lambda *args, **kwargs: "A public source statement. " * 10),
            exec_prompt=lambda *args: json.dumps({"verdict": "SUPPORTED", "confidence": 90,
                                                   "quote": "A public source statement."}),
        ),
    )
    runtime.TreeMap = dict
    runtime.u256 = int
    runtime.__all__ = ["gl", "TreeMap", "u256"]
    sys.modules["genlayer"] = runtime
    path = Path(__file__).resolve().parents[1] / "contracts" / "caseflow_in.py"
    spec = importlib.util.spec_from_file_location("caseflow_in", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CaseflowINTests(unittest.TestCase):
    def setUp(self):
        self.module = load_contract()
        self.gl = self.module.gl
        self.contract = self.module.CaseflowIN()

    def test_submit_and_assess_claim(self):
        claim_id = self.contract.submit_claim("A public source statement.", "https://example.org/source")
        assessment_id = self.contract.assess_claim(claim_id)
        assessment = json.loads(self.contract.get_assessment(assessment_id))
        self.assertEqual(assessment["status"], "SUPPORTED")
        self.assertEqual(assessment["confidence"], 90)
        self.assertEqual(json.loads(self.contract.get_counts()), {"claims": 1, "assessments": 1})

    def test_unavailable_source_is_explicit(self):
        claim_id = self.contract.submit_claim("A public source statement.", "https://example.org/source")
        self.gl.eq_principle.result = RuntimeError("consensus failed")
        assessment = json.loads(self.contract.get_assessment(self.contract.assess_claim(claim_id)))
        self.assertEqual(assessment["status"], "SOURCE_UNAVAILABLE")
        self.assertEqual(assessment["quote"], "")

    def test_source_digest_ignores_whitespace_layout(self):
        first = self.module.digest(" ".join("source  text\nwith spacing".split()))
        second = self.module.digest(" ".join("source text with   spacing".split()))
        self.assertEqual(first, second)

    def test_rejects_invalid_source_and_chain(self):
        with self.assertRaisesRegex(ValueError, "https"):
            self.contract.submit_claim("A public source statement.", "http://example.org")
        self.gl.message.chain_id = 1
        with self.assertRaisesRegex(ValueError, "Studionet"):
            self.module.CaseflowIN()


if __name__ == "__main__":
    unittest.main()
