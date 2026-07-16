# P1.3 Held-Out Family Review

## Identity and Claim

- Family: `FAM-HO-INSTRUMENT-AIR-001`
- Split: `held_out`
- Provenance: fully synthetic and newly authored before P2 implementation or tuning
- Claim: self-authored pre-tuning held-out candidate; not independently blind
- Status: author-reviewed, hash-stable freeze candidate pending user acceptance

## Scenario Coverage

The family contains one clean package, six single-fault packages, and one compound package. The controlled conditions are missing required drawing file, superseded drawing revision, orphan equipment tag, quantity conflict, wrong datasheet association, ambiguous tag normalization, and a compound superseded-revision plus review-routed title conflict.

All seven fault scenarios contain release holds, the ambiguity scenario routes to `evaluator_uncertainty`, and the compound scenario retains both `automatic_fail` and `engineering_review_required` while package precedence selects `automatic_fail`.

## Boundaries

Every scenario is a complete package instance. Mutation descriptors are protected audit records, not evaluator inputs. Expected findings, states, fault IDs, scenario catalog, check IDs, and relationship goldens are producer-hidden. No evaluator, gate, rule, CLI, report, PDF/CAD, agent, API, database, RAG, or frontend behavior is implemented here.

## Acceptance Checklist

- [x] One clean held-out baseline is present.
- [x] At least six controlled variants are present.
- [x] At least four variants are release-blocking.
- [x] A non-automatic-fail blocking state is present.
- [x] A compound precedence scenario is present.
- [x] Exact protected findings, states, evidence locators, and check IDs are recorded.
- [x] Material distinction, hashes, contamination status, and access controls are recorded.
- [ ] User accepts P1.3 and activates the pre-tuning freeze.
