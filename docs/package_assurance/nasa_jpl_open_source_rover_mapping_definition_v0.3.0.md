# NASA/JPL Open Source Rover Mapping Definition v0.3.0

## Control Status

- **WBS:** P2.3 controlled public-package mapping definition
- **Status:** Ready for CEO review
- **Package:** NASA/JPL Open Source Rover v4.0.0
- **Source archive SHA-256:** `8bcf4985904cdbabcd0b48c77e68aac66ea069947aad60fa7bc50ac283e77a7b`
- **Mapping only:** No source file has been converted and no audit has been run

## Decision Requested

Accept the bounded package configuration, the proposed authority choices, and
the explicit missing-authority findings below. Acceptance would authorize a
separate block to create a local working copy and populate the shared
transformation-and-assumption log. It would not approve engineering content,
publisher intent, or an audit result.

## Bounded Trial Configuration

The proposed trial object is the **base mechanical rover build contained in
the official v4.0.0 tag archive**.

Proposed package ID:
`public-nasa-jpl-open-source-rover-v4.0.0-mechanical`

In scope:

- the exact v4.0.0 archive recorded above;
- `README.md` for package identity and declared build scope;
- `parts_list/parts_list.csv` as the mechanical parts-list source;
- `parts_list/README.md` as a generated, human-readable secondary view;
- `mechanical/README.md` and the body, rocker-bogie, and wheel-assembly
  documentation beneath `mechanical/`;
- mechanical STEP, STL, SolidWorks, and DXF paths beneath `mechanical/`, by
  filename and file existence only; and
- the archive license and disclaimer records.

Out of scope:

- software and external software repositories;
- electrical design, wiring, PCB, and Digikey BOM material;
- `electrical/PCB_old` and every versioned PCB subdirectory;
- community builds and optional modifications;
- the external Onshape model, because it is not preserved in the controlled
  archive; and
- PDF or CAD content extraction, geometry interpretation, or engineering
  validation.

The source parts list has 58 rows across body, corner, drive-wheel, general,
and rocker-bogie assemblies. Every row has a part number. Two part numbers
occur in more than one assembly; they remain separate item occurrences rather
than being silently combined.

## Source-to-Audit Mapping

`Direct` means the publisher supplied the value. `Derived` means a reversible,
deterministic preparation rule supplies it. `Missing` means no acceptable
source was found. `Not applicable` is used only where the concept truly does
not apply; it is not used to bypass a mandatory audit source.

| Audit target | Class | Proposed source or rule | Control note |
|---|---|---|---|
| Manifest `schema_version` | Derived | Fixed trial contract value `0.3.0` | Product contract value, not a publisher claim. |
| Manifest `package_id` | Derived | Publisher, product, tag, and mechanical-scope slug | Must be logged exactly. |
| Manifest `package_title` | Direct + derived | Root README title plus accepted mechanical-scope suffix | Suffix prevents the trial from claiming electrical/software coverage. |
| Manifest `created_date` | Derived | Working-package preparation date | Must not be described as the design or release date. |
| Manifest `synthetic` | Derived | `false` | This is public third-party source material. |
| Seven mandatory source declarations | Derived | Fixed v0.3.0 package contract | Declaration does not prove native source authority. |
| Allowed file root | Derived | Exact contract root `files` | All copied artifacts remain beneath this root. |
| Document inventory | Direct + derived | In-scope archive paths plus deterministic document IDs | Paths prove existence only; IDs are trial constructs. |
| File references | Direct + derived | In-scope archive paths, copied bytes, hashes, and deterministic IDs | File existence is testable without opening CAD content. |
| Drawing register records | Missing | No publisher drawing register identified | A header-only trial file may record the absence but cannot become authority. |
| Drawing metadata records | Missing | Models exist, but no accepted drawing metadata dataset exists | A model filename is not a drawing number or current revision. |
| BOM `item_id` | Derived | Normalized assembly plus part number, with stable occurrence suffix if needed | Original row and values remain in the log. |
| BOM item description | Direct | `long name`, with `short name` retained as an alias | No title enrichment from vendor sites. |
| BOM part/material ID | Direct | `part #` | Preserve punctuation and leading zeroes. |
| BOM quantity | Derived | Exact decimal multiplication of `# req in assy` by `assembly multiplier` | Preserve both source operands and the result. |
| BOM quantity unit | Derived | `each` | Trial representation of a parts-list count. |
| BOM item type | Direct | `assembly` | Preserve the original assembly label. |
| BOM equipment scope | Derived | Proposed top-level tag `OSR-MECH-001` | Means “belongs to this rover mechanical build,” not a publisher equipment tag. |
| BOM drawing, datasheet, and specification IDs | Missing | No row-level authoritative mappings identified | Leave blank; do not infer from names or links. |
| BOM required-for-release flag | Direct + derived | Parts-list README states the list contains parts needed for the full documented robot; apply `true` within the accepted mechanical scope | Requires CEO acceptance as a scope rule. |
| Datasheet metadata | Missing | Vendor links are product pages, not preserved controlled datasheets | Do not fetch or promote them during preparation. |
| Specification metadata | Missing | No package specification register identified | Build prose is not converted into requirements. |
| Package revision | Direct | Official release tag `v4.0.0` | Controls the archived package only. |
| Document/item revision history | Missing | No package-level or document-level revision-history dataset identified | Folder versions in excluded PCB material do not control this scope. |
| Authority map | Derived | Package-specific proposal below | Remains proposed until reviewed. |
| Item-to-equipment declarations | Derived | Each in-scope item maps to `OSR-MECH-001` | Scope relationship only. |
| Document-to-file declarations | Direct + derived | One declaration per retained document/file identity | Does not claim drawing authority. |
| Equipment-to-drawing/datasheet declarations | Missing | No accepted source relationship exists | Must not be fabricated to make checks pass. |

## Proposed Authority Choices

| Controlled fact | Proposed authority | Allowed secondary evidence | Refusal boundary |
|---|---|---|---|
| Package release identity | Official v4.0.0 release and archived tag | Root README | Repository “latest” links do not supersede the pinned tag. |
| Mechanical item name and part number | `parts_list/parts_list.csv` | Generated `parts_list/README.md` | Vendor pages do not override the archived list. |
| Row quantity inputs | `parts_list/parts_list.csv` | Generated parts-list README | Cost, package size, and purchasing advice are not quantity authority. |
| Mechanical build scope | Root and mechanical READMEs | In-scope directory paths | Electrical, software, old PCB, and community content remain excluded. |
| Controlled file existence | Archive central-directory path plus copied-byte hash | Documentation link | Existence does not establish technical correctness or revision. |
| Drawing number/revision | None identified | None | Do not infer from filename, folder, model metadata, or Onshape. |
| Datasheet/specification authority | None identified | Vendor links only as non-controlled references | Do not treat a link as a controlled datasheet or requirement. |

The package authority map may encode only the accepted rows above. Where no
authority exists, it must preserve `missing_authoritative_information`; it may
not copy the synthetic pump-skid hierarchy by analogy.

## Canonical Identifier Rules

- Preserve all original values and source locators before normalization.
- Build `item_id` from the normalized assembly label and part number. Use a
  stable occurrence suffix only if that pair is duplicated.
- Use one derived package-scope equipment tag, `OSR-MECH-001`, for membership
  relationships. Do not present it as a publisher tag or component identity.
- Build document and file-reference IDs from the in-scope relative path and a
  stable hash suffix. File names remain evidence, not identity authority.
- Treat `v4.0.0` as an explicit package revision value. Do not assign it as a
  document revision where the publisher did not do so.
- Do not collapse equal part numbers across different assembly occurrences.

## Expected Holds and Product Learning

An honest first working package is expected to expose
`missing_authoritative_information`, not `automatic_pass`, because drawing,
datasheet/specification, and document-revision authority are absent.

This trial also exposes a product-model mismatch: the current evaluator is
centered on tagged equipment and controlled drawings, while this public source
is a product-assembly repository. A header-only mandatory source can record an
absence, but the audit must not interpret that empty file as proof that no
drawings are required. Working-package review must therefore confirm that the
final state and reports preserve the missing-authority truth before any audit
result is accepted. This reusable product risk is tracked as `IMP-016`.

## Preparation Acceptance Checks

The later preparation block is complete only when:

1. the source archive hash still matches the accepted intake;
2. only the in-scope paths are copied to a separate local working area;
3. all 58 source rows have one traceable mapping disposition;
4. both repeated part numbers remain separate assembly occurrences;
5. every derived quantity retains both operands and the exact decimal rule;
6. every generated identifier and the top-level equipment tag is logged;
7. no drawing, revision, datasheet, specification, or equipment authority is
   invented;
8. no PDF/CAD content is extracted or interpreted;
9. the source archive remains unchanged and outside Git; and
10. the prepared package is reviewed before `audit-package` is run.

## Explicit Exclusions

This definition does not authorize source conversion, schema or evaluator
changes, a generic loader, PDF/CAD extraction, vendor-site scraping, source
editing, engineering conclusions, or audit execution.
