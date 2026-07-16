# Held-Out Access Control

This family is a newly authored, self-authored pre-tuning held-out candidate. It is not independently blind.

Before P1.3 acceptance, access is permitted only for fixture-validity review. Acceptance activates logical read-only protection for every scenario input, expected asset, catalog, fault matrix, relationship golden, hash, and freeze record.

During P2 and P3 implementation, producers and evaluator implementers must not inspect this directory. The benchmark custodian stages only producer/evaluator-visible package inputs for the first held-out execution after the development gate and evaluator commit are frozen.

Any inspection after freeze that informs rules, tolerances, normalization, or implementation contaminates the family. Preserve it, record contamination, move useful cases to development, and author a materially distinct replacement before making held-out claims.
