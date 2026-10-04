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

The verified Caseflow IN Studionet deployment is `0xBac9E6e8D32794608EaaAb8fB70F6AC3881ecc38` on chain `61999`. Its deployment transaction is [`0x2ee48f10ba7462930f531201971f53ac5d04f7963165b98a355a224c85e8596f`](https://explorer-studio.genlayer.com/tx/0x2ee48f10ba7462930f531201971f53ac5d04f7963165b98a355a224c85e8596f), finalized with `MAJORITY_AGREE`. The local source SHA-256 after line-ending normalization is `68bd4d7f879d15e0646ef9d29e161c449b3b8682395e8d596356f1d03e19cf7d`.

The repository is intentionally contract-only; no Caseflow files or dependencies are included.
