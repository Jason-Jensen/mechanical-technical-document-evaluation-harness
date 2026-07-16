# P1.2 Development Fixture Review

## Fixture Identity

- Scenario: `SCN-DEV-PUMP-SKID-CLEAN-001`
- Package: `PKG-DEV-PUMP-SKID-001`
- Family: `FAM-DEV-PUMP-SKID-001`
- Split: `development`
- Scenario type: `clean`
- Provenance: fully synthetic and self-authored for this repository
- Review state: author-reviewed and pending user acceptance

## Package Coverage

The package represents a small pump-skid release with two drawings, a pump and
motor equipment list, two datasheets, two minimum-requirement specifications,
revision history, a package-specific application of the accepted authority
map, and nine transparent controlled-artifact stubs.

The package declares 20 required relationships:

- nine document-to-file relationships;
- three drawing-to-equipment relationships;
- two item-to-equipment relationships;
- two item-to-drawing relationships;
- two equipment-to-datasheet relationships; and
- two equipment-to-specification relationships.

The hidden `expected/golden_relationships.json` records the same semantic
relationships with exact CSV or JSON evidence locators. The expected finding
set is empty and the expected package state is `automatic_pass` with CLI exit
code 0. Human engineering and release approval remain required.

## Producer Boundary

Producer-visible inputs are the manifest, declared structured sources,
authority map, and controlled-file stubs. The `expected/` directory is a
benchmark-custodian oracle and is not declared by the manifest or available to
a future producing agent. `benchmark_metadata.json`, `fixture_inventory.json`,
and this note are benchmark-control assets outside the executable package root.

## Scope Boundary

The JSON object layouts and CSV columns in this fixture are P1.2 examples for
one development family. They are not accepted general source schemas, runtime
adapter contracts, or evaluator behavior. P1.2 adds no source adapter,
mandatory gate, relationship rule, result router, CLI, report, PDF/CAD logic,
agent integration, API, database, RAG, or frontend implementation.

The `.txt` files under `package/files/` are intentionally transparent stubs.
They support file-existence and reciprocal-reference scenarios without
pretending that PDF or CAD extraction is in v0.3.0 scope.

## Acceptance Checklist

- [x] All seven mandatory package sources are represented.
- [x] Canonical identifiers and current revisions agree across clean sources.
- [x] Every manifest file reference resolves inside `package/files/`.
- [x] Every declared semantic relationship has a hidden golden and evidence locator.
- [x] Expected assets are absent from manifest source and file declarations.
- [x] Fixture provenance, split, scenario type, family, and content-hash protocol are recorded.
- [ ] User accepts P1.2 and authorizes P1.3.

No held-out claim is made. This development family may be used for later rule
tuning only after its P1.2 acceptance state is recorded.
