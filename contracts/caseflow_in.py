# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""Caseflow IN: a source-linked evidence assessment contract.

An append-only public claim register. Consensus classifies a claim against
the claimant's cited public source; deterministic code stores the agreed
result and never presents it as legal, financial, or professional advice.
"""

from genlayer import *

import hashlib
import json
import re


MAX_CLAIMS = 100
MAX_TEXT = 500
MAX_URL = 500
MAX_QUOTE = 500
VERDICTS = {"SUPPORTED", "REFUTED", "INCONCLUSIVE"}


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def valid_https_url(value: object) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"https://[^\s]{1,492}", value))


def validate_result(value: object) -> dict:
    if not isinstance(value, dict) or set(value) != {"verdict", "confidence", "quote"}:
        raise gl.vm.UserError("result schema")
    if value["verdict"] not in VERDICTS:
        raise gl.vm.UserError("verdict")
    if type(value["confidence"]) is not int or not 0 <= value["confidence"] <= 100:
        raise gl.vm.UserError("confidence")
    if not isinstance(value["quote"], str) or not 1 <= len(value["quote"]) <= MAX_QUOTE:
        raise gl.vm.UserError("quote")
    return {"verdict": value["verdict"], "confidence": value["confidence"],
            "quote": value["quote"]}


class CaseflowIN(gl.Contract):
    claim_count: u256
    assessment_count: u256
    claims: TreeMap[str, str]
    assessments: TreeMap[str, str]

    def __init__(self):
        if int(gl.message.chain_id) != 61999:
            raise gl.vm.UserError("Studionet chain required")
        self.claim_count = u256(0)
        self.assessment_count = u256(0)
        self.claims = TreeMap()
        self.assessments = TreeMap()

    def _claim(self, claim_id: int) -> dict:
        raw = self.claims.get(str(claim_id), "")
        if not raw:
            raise gl.vm.UserError("claim not found")
        return json.loads(raw)

    @gl.public.write
    def submit_claim(self, statement: str, source_url: str) -> int:
        if not isinstance(statement, str) or not 1 <= len(statement) <= MAX_TEXT:
            raise gl.vm.UserError("statement")
        if not valid_https_url(source_url):
            raise gl.vm.UserError("https source required")
        if self.claim_count >= MAX_CLAIMS:
            raise gl.vm.UserError("claim register full")
        self.claim_count += 1
        claim_id = int(self.claim_count)
        claim = {
            "id": claim_id,
            "statement": statement,
            "source_url": source_url,
            "submitter": str(gl.message.sender_address),
            "assessment_count": 0,
            "created_at": gl.message_raw["datetime"],
        }
        self.claims[str(claim_id)] = canonical(claim)
        return claim_id

    @gl.public.write
    def assess_claim(self, claim_id: int) -> int:
        claim = self._claim(claim_id)

        def review_source() -> str:
            try:
                page = gl.nondet.web.render(claim["source_url"], mode="text")
                if not isinstance(page, str) or not 100 <= len(page) <= 120000:
                    return canonical({"available": False, "source_digest": "", "result": None})
                source_digest = digest(page)
                prompt = (
                    "Review one public source against one claim. Return JSON with exactly "
                    "verdict, confidence, quote. verdict must be SUPPORTED when the source "
                    "directly supports the statement, REFUTED when it directly contradicts "
                    "it, and INCONCLUSIVE when the source is insufficient. confidence is an "
                    "integer 0-100. quote must be a short verbatim excerpt from the source. "
                    "Do not infer facts beyond the source. Claim: " + claim["statement"] +
                    "\nSource:\n" + page
                )
                result = validate_result(json.loads(gl.nondet.exec_prompt(prompt)))
                if result["quote"] not in page:
                    return canonical({"available": False, "source_digest": source_digest, "result": None})
                return canonical({"available": True, "source_digest": source_digest, "result": result})
            except Exception:
                return canonical({"available": False, "source_digest": "", "result": None})

        try:
            agreed = gl.eq_principle.prompt_comparative(
                review_source,
                "Agree only on the same availability, source digest, verdict, confidence, and quote. "
                "Reject unsupported or invented excerpts.",
            )
            envelope = json.loads(agreed)
            if not isinstance(envelope, dict) or set(envelope) != {"available", "source_digest", "result"}:
                raise gl.vm.UserError("consensus schema")
            if type(envelope["available"]) is not bool:
                raise gl.vm.UserError("availability")
            if envelope["available"]:
                if not re.fullmatch(r"[0-9a-f]{64}", envelope["source_digest"]):
                    raise gl.vm.UserError("source digest")
                result = validate_result(envelope["result"])
            else:
                result = None
        except Exception:
            envelope = {"available": False, "source_digest": "", "result": None}
            result = None

        claim["assessment_count"] += 1
        self.assessment_count += 1
        assessment_id = int(self.assessment_count)
        assessment = {
            "id": assessment_id,
            "claim_id": claim_id,
            "source_digest": envelope["source_digest"],
            "status": result["verdict"] if result else "SOURCE_UNAVAILABLE",
            "confidence": result["confidence"] if result else 0,
            "quote": result["quote"] if result else "",
            "claim_revision": claim["assessment_count"],
            "assessed_at": gl.message_raw["datetime"],
        }
        self.assessments[str(assessment_id)] = canonical(assessment)
        self.claims[str(claim_id)] = canonical(claim)
        return assessment_id

    @gl.public.view
    def get_claim(self, claim_id: int) -> str:
        return self.claims.get(str(claim_id), "")

    @gl.public.view
    def get_assessment(self, assessment_id: int) -> str:
        return self.assessments.get(str(assessment_id), "")

    @gl.public.view
    def get_counts(self) -> str:
        return canonical({"claims": int(self.claim_count), "assessments": int(self.assessment_count)})

    @gl.public.view
    def get_protocol(self) -> str:
        return canonical({"name": "Caseflow IN", "version": "0.1.0", "chain_id": 61999,
                          "purpose": "public evidence provenance", "admin": False, "custody": False})
