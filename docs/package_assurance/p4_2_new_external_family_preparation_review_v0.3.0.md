# P4.2 New External Family Preparation Review

**Version:** 0.3.0

**Date:** 2026-07-24

**Status:** D-119 complete; D-120 owner review required

**Accepted predecessor:** PR #71 merge `17830bd`

## Executive Result

D-119 produced one genuinely new, entirely synthetic benchmark family under
isolated custody outside Git. The evaluator implementation context received
only a redacted public handoff and did not access any package, target plan,
scenario result, expected value, or authoring record.

The producer reports:

- eight scenarios: exactly one clean and seven protected faults;
- eight authoring-preflight invocations and zero official benchmark
  invocations;
- eight of eight public package-contract validations passed;
- all seven protected targets were reachable with zero unintended earlier
  blockers;
- the clean scenario passed every mandatory gate;
- three rejected revisions were preserved rather than repaired in place; and
- 317 frozen family files plus five inventory files are read-only.

The designated public handoff is SHA-256
`6a89ba93934e42573a984573144d1f5dfde0efde89a99da01942663ecfc623e2`.
Literal-file inspection reproduced that hash and found none of the prohibited
scenario, package, target, expected-value, nonce, source-record, or internal
custody fields.

An independent reviewer reproduced the producer handoff, eight of eight public
contract validations, all freeze hashes, target reachability, rejected-
revision preservation, redaction, and pre/post identity without modifying the
repository or custody set. The reviewer handoff is SHA-256
`37f2e735a53c2da71830cdccdf7738b98c6a1513908b5922d3272c88e3bf916c`.

These are preparation and corrective-control results only. They are not
official benchmark-performance evidence.

## Public Control Result

`VAL-PKG-AUTHORING-001` version 0.3.0 passed all eight frozen scenarios. The
producer reports distinct scenario package identities and exact package-to-
authority scope equality. No relationship result was used to change evaluator
behavior.

`VER-PKG-TARGET-REACHABILITY-001` version 0.3.0 passed:

- scenario count: 8;
- clean scenarios: 1;
- fault scenarios: 7;
- protected targets: 7;
- reachable targets: 7;
- unintended earlier blockers: 0; and
- protected values published: false.

The public reachability attestation is bound by SHA-256
`cd4f044dc90539d48eb37991f63b36a5a08c66f1b959515137a30f282373d742`.
The protected plan and detail remain represented only by salted commitments.

## Rights and Custody

The producer attests that the family is synthetic, self-authored, created from
accepted public contracts, materially distinct from the excluded prior
categories, and prepared without network access. No prior family or protected
value was read, copied, or reused.

Producer, protected, verification, and rejected-revision records remain
outside Git. The public repository records only opaque family identity,
aggregate counts, hashes, commitments, limitations, and decision state.

## Freeze Identity

The opaque family token is `FAM-3178CBE96B77B3E6A998154C`.

The family content aggregate is
`69228bf06f9f1fd3035473082572e1e14b94ee3662bbcc136473f9cc19bbf69f`.
The inventory-set aggregate is
`39aa558fe14310b0f2a8be0968f097c03fc8ab28b3c00d51d016096e12f6afaf`.
The result-set aggregate is
`0b0e2f44a293b2a349375c60cc04fa2ca1b02a62c97a891c08793c7cfdd75bb3`.

The public evidence JSON records the class-level content and inventory hashes
without publishing class contents or custody paths.

## Independent Review

A fresh reviewer who did not author the family or implement the evaluator
passed the independent review. The reviewer reproduced:

- public-handoff identity and redaction;
- package and authority-scope controls;
- public-contract validation;
- protected target reachability;
- rejected-revision preservation;
- rights, provenance, isolation, and no-network evidence;
- read-only inventories and class hashes; and
- pre-review and post-review freeze identity.

The reviewer reran `VAL-PKG-AUTHORING-001` eight times with relationships
disabled; all eight passed. It performed no `audit-package` command, semantic
relationship evaluation, official benchmark invocation, or protected
performance comparison.

The 322-file pre/post tree identity is
`9a986402e1a162829c1d43ab27e0be241b24647f2bacdc9c87cc3c5e534862f8`.
File set, per-file hash, size, write time, attributes, aggregate identity, and
the producer handoff all remained unchanged. No symlink or reparse indirection
was present.

## Nonconformity and Risk

This D-119 result provides independently reproduced effectiveness evidence for
the D-118 authoring controls, but `NC-002` remains contained. Closure still
requires a separately authorized official run, preserved raw evidence,
separate protected comparison, and owner closure review.

`AIR-003`, `AIR-008`, and `AIR-011` remain release holds. No P4.3 work or
release claim is authorized.

## Claims Boundary

D-119 does not establish accuracy, false-positive or false-negative
performance, generalization, engineering correctness, release readiness,
independent external assurance, ISO/IEC 42001 conformity, or certification.

## Next Decision

The proposed
`p4_2_new_external_family_execution_gate_v0.3.0.md` binds the exact family,
evaluator, custody controls, invocation count, raw-evidence freeze,
oracle-blind verification, and protected comparison. Official execution
remains prohibited until the owner accepts D-120.
