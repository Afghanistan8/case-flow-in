# Caseflow IN

Caseflow IN is a standalone GenLayer intelligent contract for turning public claims into reviewable, source-linked assessments.

A user submits a short statement and an HTTPS source URL. An assessment fetches that source inside GenLayer's nondeterministic web path. Validators independently review the same claim and source, then comparative consensus agrees on a bounded result: `SUPPORTED`, `REFUTED`, `INCONCLUSIVE`, or `SOURCE_UNAVAILABLE`. Caseflow IN stores the source digest, confidence, verbatim supporting quote, timestamp, and append-only assessment ID.

Caseflow IN is useful for researchers, journalists, civic groups, educators, and protocol builders who need a public trail showing what source was checked and what validators agreed about it. It does not replace expert review, establish legal liability, or guarantee that a source is complete or current.

## Why this is an intelligent contract

The external source and language assessment are nondeterministic. They run inside a comparative equivalence callback, where validators compare the same structured envelope. Deterministic contract code validates the envelope, rejects invented quotes, assigns the final status, and persists the record. A failed fetch, malformed answer, or failed consensus becomes `SOURCE_UNAVAILABLE` instead of an invented verdict.

## Methods

- `submit_claim(statement, source_url)` creates an append-only claim.
- `assess_claim(claim_id)` fetches and assesses the cited source through consensus.
- `get_claim`, `get_assessment`, `get_counts`, and `get_protocol` expose public readbacks.

The contract is Studionet-only, has no admin or custody capability, accepts no value, and has no withdrawal path.

## Local verification

```sh
python -m unittest discover -s tests -p test_caseflow_in.py -v
```

## Deployment

The verified Caseflow IN Studionet deployment is `0xaC96fC8D6fE65050Acf5656B676909F0832cC482` on chain `61999`. Its deployment transaction is [`0xa13b173fcd95f073ee373a057b8c499d0fbd352328134e8e592bd4f09189d160`](https://explorer-studio.genlayer.com/tx/0xa13b173fcd95f073ee373a057b8c499d0fbd352328134e8e592bd4f09189d160), finalized with `MAJORITY_AGREE`. The normalized local/on-chain source SHA-256 is `0ac9dd449ed148d20fb8ae736a994f40801eb1ef3d820111ff60b69563bb803b`.

The repository is intentionally contract-only; no files from the other Caseflow repository are included.
