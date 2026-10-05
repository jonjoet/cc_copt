# CLI and optional Streamlit coexistence implementation plan

Status: DRAFT FOR INDEPENDENT REVIEW. Planning only; no implementation, merge, commit,
push, PR, deletion, or runtime verification authorized by this document alone.
Revision 03, 2026-10-05: addresses retained review 02's R1 and small optional
recipe/documentation corrections. Prior drafts/evidence remain preserved. Author: `gpt-6-astra (high)`,
verified in this thread's own native `turn_context` records (initial and revision
turns), not inferred from requested settings. Evidence:
`/home/qbk/qbk-code/tmp/cc-copt-streamlit-tier2-20261005T170546Z/revision-02/native-identity.json`.

## 1. Binding contract and snapshots

Work serially under qbk-polly, tier 2, branch/PR mode, with no nested agents.
Repository: `/home/qbk/qbk-code/cc_copt`.
Assigned checkout: `/home/qbk/qbk-code/cc_copt/.worktrees/qbk-polly/streamlit-coexist/feature`.
Assigned branch: `qbk-polly/feature/streamlit-coexist`.

- Main integration base: `d4eb3c53eb9fadd57481893665b3512123970f9a`.
- Selected YAML superset and planning HEAD: `35dd25708a7b58fc3ca1455debddd01920e3e721`.
- Older Streamlit tip (already an ancestor; do not merge separately):
  `35d650e9a14f3cdab348ba8a7735a63d98a63446`.
- Common ancestor: `5d0fe568a37e269c0f2434b5fd7922073c9331bb`.
- Main has four unique commits; the selected feature has seven. Inspect immutable
  objects with `git show`; do not treat a tip-to-tip deletion as intended removal.

Deliver CLI and optional Streamlit together using the same interface-agnostic engine.
Retain two production Dockerfiles: `Dockerfile` for the CLI and
`Dockerfile.streamlit` for the GUI. Reconcile packaging, repair current-settings
YAML import/export, correct documentation/examples, and demonstrate real CLI and
GUI optimization in Docker with meaningful focused regression tests.

No UI redesign, unrelated engine refactor, SLS work, SLS execution or SLS tests,
Nextflow runtime campaign, deployment/authentication project, new CI/caching
project, host package installations, external dataset lookup, uploads, rewriting
published history, force-push, branch deletion, or merge to main in this task.
Preserve main's `tool.yaml` byte-for-byte and carry `claude_context/manifest-spec.md`
unchanged. Preserve the documented CLI image tag `cc_copt:latest`, `WORKDIR /app`,
the examples copy, and `/app/examples/config.yaml` at its current location with
unchanged keys/meaning. `tool.yaml` relies on that tag and `/app` configuration-path
contract; do not rename/move the config or repurpose its contents. Blob equality
and these source checks are preservation only, not SLS compatibility verification.
Parent owns the follow-up SLS issue.

Required workflow: parent obtains independent review of this full plan and the
requirement record, resolves blockers, author receives explicit plan-commit
authorization, then user approves the reviewed summary. A FRESH implementer
receives this plan and a build packet. Only then reconcile the pinned main into
the feature. Implementation approval does not bypass privacy clearance or authorize
publication. Parent coordinates final independent code review, push/draft PR,
and eventual reviewed main merge; no task PR or task merge to main.

Requirement record (context, not a substitute for this contract):
`/home/qbk/qbk-code/tmp/cc-copt-streamlit-tier2-20261005T170546Z/requirements.txt`.
Historical report was read as context at
`/home/qbk/qbk-code/tmp/cc-copt-branch-history-20261005T162828Z/report.md` with its
`RUN.txt` and `messages.txt`. It is not fresh runtime evidence.

## 2. Findings that determine the implementation

Line references in this section refer to selected feature HEAD above.

1. `cc_copt/gui.py:82-103` builds download data before global values are synchronized
   at 169-173 and specification lists at 305-339. A manual edit can therefore leave
   the download payload one render behind. This is a static finding; reproduce it
   through a browser download before the fix and retain the failing result.
2. YAML application at `gui.py:60-74` updates canonical state but does not explicitly
   reset the existing widget keys (`species_input`, `con_<index>_*`, etc.). Applying
   a second config after edits, deleting an earlier spec, or changing spec type can
   reuse stale widget state. Test these transitions, not only initial-state seeding.
3. Unknown types silently become the first registered type at `gui.py:186-188`;
   parameters outside the registry disappear at 216-292. Enum fallbacks can also
   substitute values. `config.py:46-72` accepts broader DnaChisel classes/kwargs.
   GUI fidelity needs an explicit boundary. Atomic rejection of unsupported
   imports is PROPOSED behavior requiring inclusion in the user's plan-approval
   summary; do not treat that behavior as already approved.
4. Optional numbers are already toggled at `gui.py:225-276`; disabled means omitted,
   not zero. Preserve this. Test unset/zero/positive minima and integer/float YAML
   types. Current iteration widget minimum is 100; the GUI must reject values it
   cannot render instead of crashing or silently clamping them.
5. Commit `35d650e9a14f3cdab348ba8a7735a63d98a63446` removed the duplicate
   `MatchTargetCodonUsage` registry entry, not its README mention. README:136 still
   advertises it. Keep the single `CodonOptimize(method="match_codon_usage")` form
   choice; document that replacement. Do not restrict CLI class lookup or claim
   all DnaChisel aliases are unsupported by CLI.
6. Main's explicit `[tool.setuptools] packages = ["cc_copt"]` conflicts in intent
   with feature's `packages.find` declaration. There are no package subdirectories
   to discover. Retain main's explicit package list and feature's optional extra.
   `.[dev]` is pytest only; `tests/test_gui.py:7` currently imports Streamlit
   unconditionally, so README:151-156 cannot run all tests from its stated install.
7. `Dockerfile` installs base dependencies, copies examples, has no CLI entrypoint,
   and includes procps for existing pipeline use. Preserve that command contract.
   `Dockerfile.streamlit` installs `.[streamlit]`, runs the app on 8501 and disables
   usage statistics. Keep it. Do not add a third production Dockerfile.
8. There are eight static `test_*` functions in `tests/test_gui.py`, and eight in
   `tests/test_optimize.py`. These are NOT collected cases or passing tests.
   Existing GUI tests cover boot, defaults, button existence, serializer state,
   and add actions; none exercise real upload/download/optimization. Bare imports
   of the app for serializer tests execute top-level Streamlit code.
9. README advertises broad GUI/CLI config equivalence without explaining
   unrenderable CLI configurations and retains a stale specification list.
   `examples/config.yaml` is an organism-specific example, not the offline test
   fixture. Keep it and the owner-cleared reporter example as primary quickstart;
   verify its table-fetch requirements in the later container inspection before
   documenting them. Nextflow files and behavior are outside this change.

## 3. Privacy findings, owner attestation and publication gate

The repository is private per the owner's dispatch; this worker has not queried
hosting visibility. Local remote-tracking refs, not a fresh network query, show
both historic feature tips already on origin. The initial sweep covered main's
tip plus every one of seven `BASE..HEAD` commit trees, 42 unique blobs total.
The seven commits are `9fa1678`, `0d5eaf9`, `f9ca9fd`, `3ec0e41`, `35d650e`,
`662c9a7`, and `35dd257` (full IDs in the scanner output). None of the initially
flagged content is newly exposed by this proposed PR: every flagged blob is
already reachable from main history AND from the locally observed origin refs.
“In main tip” and “reachable from main history” are different facts. The old
`privacy-summary.json` field `present_on_main` meant tip presence only; do not
reuse it as a history-reachability conclusion.

Read-only set comparison in revision 02 confirms 12 blobs across seven feature
paths are reachable from HEAD but not BASE history: Dockerfile.streamlit, README.md,
config.py, five gui.py versions, two spec_registry.py versions, pyproject.toml,
and test_gui.py. All twelve had zero hits in the original sequence/secret-pattern
scan; this is triage, not a claim that regex can prove absence. Recheck new
implementation blobs and all introduced commit trees/metadata before publication.

Owner statements, recorded **2026-10-05**, exactly as supplied by the parent:

- `examples/example.faa` contains “three extremely common reporter proteins”.
- Test literals “look made up to me. too short to mean much”.
- “the others look fine to me”.

These are sufficient **owner-attested acceptable fixture/content classifications**.
They are NOT externally verified public accessions or evidence of a documented
synthetic-generation history. Do not demand new documentation for these same
fixtures or relabel the tentative test-literal statement as a proven synthetic
origin. No confirmed proprietary content has been found.

| Existing flagged path / origin | Reachable from BASE history | Already on origin (local refs) | New blob in BASE..HEAD | Classification / evidence |
| --- | --- | --- | --- | --- |
| `examples/example.faa`; `58b9430a1ec3e9bc05b4455eae28789fa7430889` | Yes | Yes | No | Owner-attested acceptable reporter fixtures. Retain primary example unchanged. |
| `tests/test_optimize.py`; same origin | Yes | Yes | No | Owner-attested acceptable short literals; no claim of established generation provenance. Synthetic test rewrites are ordinary focused-test maintenance. |
| Seven tracked `.pyc` files; same origin | Yes | Yes | No | Existing generated artifacts associated with repository sources; owner's “others” attestation applies. Record source association/derivation evidence and carry main's removals. No new exposure or automatic block merely because bytecode is opaque. |
| `.DS_Store`; `2bdb32224d10694d245613e9b72c976fce075132` | Yes | Yes | No | Owner-attested existing metadata; final structural triage checks filename/directory metadata categories, counts only. Carry main's deletion. |
| `claude_context/Cg_codon_optimize.ipynb`; same origin | Yes | Yes | No | Owner-attested acceptable context; parent AST check identifies only the example input and generated output references below, zero saved outputs. No separate dataset identified. |

Parent's narrow AST check at main `d4eb3c53eb9fadd57481893665b3512123970f9a`
found notebook file references only `./example.faa` (cell 2 line 3) and output
`ex_out.fna` (cell 10 line 9), with zero saved outputs. This corrects the original
plan's vague “dataset references” concern. Do not execute the notebook, fetch data,
or ask another provenance question unless a concrete distinct reference is found.

Derived-artifact rule: a `.pyc` with corroborated source association (same historical
commit/source path plus header/source-size or printable-constant correspondence,
where available) inherits the source's owner-attested classification. Record what
was checked and confidence; do not claim identical compiler reproduction if it was
not performed, or infer provenance solely from a filename. In-memory structural
inspection may count standard bytecode metadata, code names and source-associated
constants without logging values. No execution/unmarshalling is needed for this
plan. Owner attestation remains valid even where optional derivation details are
unavailable; escalate only a concrete contradictory or suspicious finding.
For `.DS_Store`, classify as ordinary metadata when structure/printable UTF-8 or
UTF-16 strings are directory entries and standard Finder keys, with no credential
or unrelated payload indicator; record categories/counts. An unexplained pattern
hit is triaged, not automatically called sensitive. Avoid an impossible absolute
zero-unknown standard for old, owner-accepted binary internals.

Original evidence remains in
`/home/qbk/qbk-code/tmp/cc-copt-streamlit-tier2-20261005T170546Z/`.
Revision evidence is in its `revision-02/` directory: `RUN.txt`,
`reachability.json`, updated scanner output, owner-attestation ledger and plan
snapshot. Original “BLOCK” ledgers describe the superseded draft, not this ruling.

**Remaining privacy gate:** complete the final candidate/history sweep and resolve
any concrete unclassified or suspicious findings, especially genuinely new blobs.
Owner-attested entries need no further provenance question absent contradictory
new evidence. Publication waits for that sweep and review; **local Docker builds
and tests do not publish** and are permitted after build authorization. Use only
the local daemon, no remote builders, registry pushes, dataset uploads or raw
biological literals in reports, tool output, PR/issue text. Synthetic test files
and logs with generation provenance may be retained locally.

If confirmed sensitive history is later found, pause publication of the affected
candidate and present specific paths/commits plus remediation choices to the
parent. Distinguish old main exposure from new content. The parent's conditional
question about whether confirmed pre-existing sensitive data should block merge
is unanswered and not needed now: there is no such finding. Do not assert a new
permanent main-merge policy, rewrite history, delete refs, or start a clean branch
strategy without explicit authorization. A tip cleanup cannot change historical
objects, and holding this PR cannot undo their prior availability.

## 4. Allowed files for the fresh implementation packet

Planning currently permits ONLY this plan plus evidence in the assigned run.
The following is the proposed build allowlist, effective only after approved plan
and a fresh dispatch. No other product files may be changed without a ruling.

| File set | Concrete change |
| --- | --- |
| `pyproject.toml` | Keep explicit `packages = ["cc_copt"]`, remove competing find table, preserve CLI script and base dependencies. Keep `streamlit` optional and `dev = ["pytest"]`. Do not add browser tooling to production dependencies. |
| `cc_copt/gui.py` | Synchronize before export; atomic supported-config application (subject to user approval); reset stale widget keys on apply/type/remove; catch missing/unreadable table path during species resolution inside the guarded optimization setup. Preserve layout and engine call. |
| `cc_copt/gui_config.py` (new) | Small pure parse/normalize/export helper for the GUI boundary, including library-equivalent imported defaults. No Streamlit imports, general validation framework or changes to CLI acceptance. Pure helpers provide the cheap unit-test seam. |
| `cc_copt/spec_registry.py` | Narrow field/default metadata corrections based on actual installed-library signatures. Preserve curated scope. Report unbuildable registered types/options for explicit disposition; do not silently expand engine species handling or add new features. |
| `cc_copt/config.py` | Carry feature's public `build_spec`/`resolve_species` and main behavior. Changes beyond that only if required for shared config construction without UI imports; no general validation rewrite. |
| `Dockerfile`, `Dockerfile.streamlit` | Preserve two distinct production images/launch contracts. Only adjust install/copy details if reconciliation requires it; retain procps, GUI port and telemetry opt-out. No broad container refactor. |
| `.dockerignore` | Exclude `.worktrees`, `.codex`, build/test/cache outputs as needed so unrelated checkouts/artifacts are not sent as context. Retain existing exclusions, especially `claude_context` and bytecode. |
| `tests/test_gui.py`, `tests/test_gui_config.py` (new) | AppTest covers widget/state/numeric/no-input behavior with a shared deployed APP_PATH. Pure helper tests cover broader config rejection/omission/default/registry cases cheaply; GUI module alone skips if optional Streamlit is absent. |
| `tests/test_gui_e2e.py` (new) | Real browser upload/apply/edit/download/optimization against installed app in GUI container, real shared engine and result parsing. |
| `tests/test_cli.py` (new) | Focused installed CLI subprocess cases: protein FASTA at workers 1/2, one DNA case, one mixed-failure case; semantic output checks and reusable offline example checker. CSV/TSV matrix belongs in cheap I/O tests. |
| `tests/test_optimize.py`, `tests/conftest.py` (new if needed) | Rework tests to invoke the single example generator and use its synthetic table/inputs offline, preserving engine coverage. This is already in focused-test scope, no extra owner permission. Add cheap CSV/TSV I/O checks. Lazy browser dependencies; shared APP_PATH/argv helper for GUI tests. |
| `examples/generate_synthetic.py` (new), `examples/README.md` (new) | Deterministic generator/provenance and exact offline example commands; write generated data ONLY to explicit user-selected output directory. No embedded biological sequences. |
| `examples/example.faa`, `examples/config.yaml` | Preservation only: owner-cleared primary example and current organism configuration remain byte-identical. Add a separate generated offline recipe; no location/key/meaning changes. |
| `README.md` | Correct optional install/tests, source-checkout GUI invocation, supported import subset, YAML export, two Docker launch recipes, generated offline examples/provenance. Remove stale duplicate choice and document equivalent form setting. |
| This plan | Update only when parent authorizes resolving review findings/scope; status/diff/log/re-read immediately before editing. |

Integration-only effects: carry main's `.gitignore`, `tool.yaml`,
`claude_context/manifest-spec.md` unchanged and carry deletion of `.DS_Store` and
seven tracked `.pyc` files. These are existing main changes, not new SLS work or
new cleanup scope. Do not edit the notebook or other `claude_context` files;
privacy remediation there requires an explicit expanded packet. Keep
`cc_copt/optimize.py`, `cc_copt/io.py`, `cc_copt/utils.py`, `cc_copt/cli.py`,
`cc_copt/__init__.py`, LICENSE and both `examples/nextflow/main.nf` and
`examples/nextflow/nextflow.config` unchanged; a new failure
requiring engine/CLI fixes is reported for scope, not silently repaired.

## 5. Behavioral choices and important wording

### Packaging and the engine boundary

Base package and CLI image must install/import/run without Streamlit installed.
GUI image installs the existing `.[streamlit]` extra. Full Python tests use
`.[dev,streamlit]`; browser tests additionally need Playwright in a disposable
verification image. Keep pytest-only `dev` for CLI users. Use `pytest.importorskip`
at GUI test module boundaries so CLI-only discovery works; the GUI gate asserts
its dependencies exist and requires zero unexpected skips. README must distinguish
intentional CLI-only skips from full GUI coverage. Python 3.11 is the container
target used by both existing Dockerfiles; do not claim a broader tested version
matrix or a verified minimum Streamlit version from a single resolved install.
The existing `requires-python >=3.9` metadata versus evaluated union annotations
is a parent backlog observation, not a packaging-version correction here. README
must not newly advertise Python 3.9 as tested/supported by this reconciliation.

Both front ends continue using `OptConfig`, `build_spec`, `resolve_species`,
`read_input`, and `optimize_sequence`. No dependency on Streamlit may enter these
shared engine/config/I/O modules. Retain serial GUI execution; no new GUI worker
control. CLI retains `--threads` and its current error/exit contract.

### Config state and import fidelity (proposed atomic rejection)

The user summary must explicitly present atomic rejection of unsupported GUI YAML
as a PROPOSED behavior. User approval of that summary is still required. Limit
validation to protecting this editor's existing field/round-trip contract; no
schema framework or comprehensive DnaChisel validation engine is authorized.

Define one canonical plain-data snapshot for export and optimization. Render all
controls and collect values before generating download bytes; use a sidebar
placeholder if needed to retain placement. Do not require an extra click, rerun,
widget edit or optimization to refresh the downloadable YAML. Enter/blur commits
an edited widget and is part of that edit. Tests wait for the resulting script run
to finish before downloading; they must not trigger an unrelated second rerun.
Test served download bytes, not just a helper reading canonical state.

Parse with `yaml.safe_load`, validate in a temporary mapping, then apply atomically.
On successful apply reset relevant widget keys or advance a form-generation key
namespace before rendering; also clear prior results/errors. Handle YAML parse
errors, nonmapping roots, invalid enums/numeric types/bounds, nonspec lists and
nondict entries with a concise error, preserving the previous valid config.
Reject booleans as numeric values and nonfinite floats. Optional null/missing
numeric values with genuine “unset” semantics are omitted on export; explicitly
enabled zero is retained where permitted. Do not conflate an omitted constructor
argument with an explicit null when the actual library distinguishes them. GUI-global iteration limit is an integer >=100; CLI acceptance stays
unchanged. Normalize numeric TaxID text semantically through `resolve_species`;
YAML key ordering/quote differences need not be identical.

Supported GUI import is exactly the four globals (`species`, `input_type`,
`stop_codon`, `max_random_iters`), `constraints`/`objectives`, registered types in
their permitted categories, and declared parameters with renderable values.
Omitted globals use defaults. Species may be a string/integer; retain an explicit
local JSON-table path string for trusted local use, and normalize absent/null
species to the empty UI default. Export omits `species` when empty, so the CLI
receives no species rather than an empty-string injection. Move `resolve_species`
inside GUI's guarded setup; a missing/unreadable/malformed local table produces a
safe error, no exception panel and no echo of path contents. Inline table mappings, unknown top-level keys,
unknown type/parameter, non-renderable enums, per-spec override/location kwargs,
and unregistered aliases are rejected with guidance to use CLI; do not drop them
or automatically substitute a spec. `MatchTargetCodonUsage` import should explain
the supported `CodonOptimize`/`match_codon_usage` form alternative, not silently
rewrite additional parameters. The CLI remains able to accept its existing broader
DnaChisel configuration contract. This is the least disruptive explicit boundary;
if user requires arbitrary CLI YAML editing in the GUI, seek scope before building
an advanced/raw editor.

**Omitted spec parameters:** on import, initialize each omitted declared parameter
to the constructor's actual default when its control can represent that value.
Otherwise leave the control clearly unset (empty text, optional number off, or a
“library default” marker) and omit that argument so the constructor supplies it.
The displayed control state must always match what Run and export use. Export may
emit a representable actual default explicitly; no per-key edit tracking is needed.
Manual add and type-switch continue using explicit registry defaults and export
them explicitly, subject to the existing documented deviation/parity rules.

Later container checks must inspect actual callable signatures and construct real
specs, not rely on recollections about CodonOptimize.method or
EnforceTranslation.start_codon. For each registry type using only required fields,
compare original-vs-round-tripped effective parameters (including omitted defaults)
using a named comparison of relevant constructor state, not string repr. Registry
parameter names must be accepted by the resolved constructor, including documented
forwarded factory kwargs; registry defaults must match it or appear in a short
explicit deviation list for manual creation only. Exercise each selectable method
with the synthetic table/required operands. Specifically investigate MaximizeCAI
species handling and harmonize_rca's required inputs without assuming either is
broken. An unbuildable advertised option is a reported gate finding requiring a
scoped fix/disable decision; do not silently xfail it, weaken tests, or broaden
shared engine species injection.

Use pure `parse_gui_config`/`export_gui_config`-style helpers as the unit seam
(names may follow local conventions). AppTest exercises keyed widget edits and
add/remove/type transitions; actual upload→Apply→edit→second Apply is in the
browser test, since AppTest uploader support is not assumed. No test-only UI
control or fake optimizer is required.

Required user-facing wording (or equally precise wording):

- Upload help: “Loads settings supported by this GUI. Configurations using other
  DnaChisel types or parameters can be run with the CLI.”
- Unsupported config: “This configuration uses settings the GUI cannot edit.
  Nothing was applied. Use the CLI, or adjust the unsupported settings.” Identify
  structural field paths/types, never echo uploaded values or whole YAML.
- Invalid YAML: “Could not read this YAML configuration. Nothing was applied.”
  Do not print parser context containing user-supplied sequence values.
- Export help: “Download the current settings, constraints, and objectives for
  reuse in the GUI or CLI.”

Retain existing file format choices and result downloads. Test removal of the
first of multiple same-type specs, then editing the remaining one; type switches
must discard only the switched spec's old fields. Successful import must replace
all supported settings even when widgets previously held conflicting values.
Do not redesign stale-result presentation beyond clearing results on config apply.

### Synthetic fixtures and examples

Create deterministic fixtures using code, not biological input literals or
external accessions. Generator command contract:

```
python examples/generate_synthetic.py --out-dir /chosen/output --seed 1729
```

Generate three named synthetic proteins of at least 72 residues from a fixed,
documented pseudorandom algorithm over the sorted standard amino-acid alphabet,
with a start methionine; derive DNA with a deterministic standard-code codon map
and stop. Generate equivalent FASTA, CSV and TSV, plus `synthetic-codons.json` and
`config.yaml`. Build the complete synthetic codon-frequency table from Biopython's
standard code, including stop-codon entries if required by the installed API;
assign deterministic positive, unequal synonymous weights normalized per amino
acid. It is a synthetic table, not an organism model. Emit explicit provenance
(seed, algorithm, no biological source) in `PROVENANCE.json`, with file hashes.
Synthetic fixture files, downloads and ordinary assertion output may be retained
in local test evidence with that provenance; no bespoke assertion-redaction
framework is needed. Do not copy biological/non-synthetic/unresolved literals to
tool output/reports, and keep all sequence payloads out of handoff/PR text. Use filenames `protein.faa`, `dna.fna`,
`protein.csv`, `protein.tsv`. Set generated config species to the codon-table path
inside the execution environment, input type auto, and a simple attainable
`EnforceTranslation` constraint plus `CodonOptimize(method="use_best_codon")`
objective. Add a named restriction-site avoidance case separately. Do not make
randomized optimizer byte-for-byte output a test expectation; assert translation,
constraints, lengths, scores, records and output agreement. Seed Python/NumPy in
tests where used and run acceptance containers with no network. Tests invoke
`examples/generate_synthetic.py`; do not maintain a second test generator.

Keep the existing owner-cleared organism/reporter quickstart primary. Inspect the
resolved table package in a later container to establish whether its TaxID needs
network, then document that requirement accurately; do not assume all tables are
bundled or all are fetched. Add a separate offline synthetic section, not a
replacement primary example. Its generate and optimize steps must mount the same
host output directory at the same container path, because generated config holds
a table path in that namespace. Use uid/gid-owned mounted output.

## 6. Acceptance gates and proportional test responsibilities

All gates refer to an exact snapshot. Report collected cases, executed cases,
skips and static functions separately; eight existing GUI functions is not a
coverage target. No SLS or Nextflow tests are included. Expand cheap unit coverage
where useful without multiplying expensive end-to-end combinations.

| Gate | Required assertion / file |
| --- | --- |
| G0 Preservation/scope | Pinned main ancestor; allowed diff only; unchanged tool.yaml, manifest doc, engine/CLI, both Nextflow files, example.faa and config.yaml; CLI `cc_copt:latest`, `/app`, examples copy/config path contract retained by source inspection. No SLS invocation. |
| G1 Privacy | Final tree and all BASE..CANDIDATE commit trees plus commit metadata; mechanically distinguish base-history-reachable, already-on-origin and genuinely new blobs. Apply owner-attested/derived/nondata/synthetic classifications and triage concrete findings. Final sweep/review before push/PR; local tests may proceed. |
| G2 Packaging | Build both production images locally. Base imports/CLI help without Streamlit; GUI extra imports. pip check, package module inventory, Python/resolved versions/image IDs. GUI tests drive `/app/cc_copt/gui.py` with `/app` imports, same app/argv as production. |
| G3 Focused core/CLI | Real CLI protein FASTA with --threads 1 and 2; one DNA case; one mixed valid/invalid case with partial success and nonzero exit. Check record order/count, translation/length/stop, PASS flags, objective score columns and output semantics, not merely exit/file existence. Broader CSV/TSV parsing at `read_input` unit layer in test_optimize.py. Synthetic offline table for all optimization tests. |
| G4 GUI state | AppTest defaults, widget edit/export state, add/remove first of same-type specs, type switch, optional window unset→minimum→unset and target unset→zero→positive→unset, valid integer/float types, no-input error. After importing an omitted representable parameter, assert the displayed control value equals the effective constructor default and its export builds an equivalent spec. Same deployed APP_PATH, optional GUI collection skip only without Streamlit. |
| G5 Pure config/registry | test_gui_config.py uses pure helper seam for malformed/nonmapping YAML, supported bounds/enums/shapes, unsupported types/fields/categories, no partial mutation, empty species omission, missing-vs-null, omitted defaults. Also parse the shipped `examples/config.yaml` successfully through the pure GUI import helper without resolving species or making network calls. Signature parity/deviation ledger plus construction for every advertised registry type/option, original required-only mapping vs exported effective parameters. Report unsupported library option failures for scope; no engine expansion. GUI missing table path handled safely (AppTest or focused boundary test). |
| G6 Browser round trip | Actual upload→Apply after prior edits→widget edits (commit via Enter/blur, await finished run)→download current YAML. Same-session second Apply and fresh-session reimport replace widgets. Feed actual downloaded config to installed CLI and validate results. One red pre-fix stale-download regression, not a full baseline suite. |
| G7 Browser optimization | One real protein-FASTA GUI optimization using the synthetic table and edited/imported config. Actual shared engine; UI success/constraint/score checks; actual FASTA/TSV downloads parsed against synthetic input invariants. No exception panel. G6/G7 may share one flow to avoid duplicate expensive runs. No-input and broad format cases stay at cheaper layers; mixed-failure behavior is required at CLI layer. |
| G8 Docs/examples | Existing primary examples preserved; separate offline generator+CLI recipe executed with identical mounts and semantic output checker. README optional dependency/test instructions, config subset proposal (after approval), YAML export, duplicate-choice correction, two Docker launch recipes accurate. No runtime claim for primary organism data unless actually run, and no SLS/Nextflow claims. |

Cheap config tests live in `tests/test_gui_config.py` and need no Streamlit import.
AppTest lives in `tests/test_gui.py`; browser controls/downloads in
`tests/test_gui_e2e.py`. Pure tests verify nonmutation of input mappings; browser
rejection/reapply verifies live-state atomicity. GUI acceptance has no unexpected
skips; base-only collection may intentionally skip GUI/browser modules. Preserve
useful original scenarios without preserving redundant side-effectful tests.

## 7. Reproducible implementation gates (NOT executed during planning)

After retained plan review, authorized plan commit and user summary approval, a
fresh build worker rechecks branch/status/log/plan. Only then reconcile pinned main
using `git merge --no-commit --no-ff d4eb3c53eb9fadd57481893665b3512123970f9a`.
Resolve package discovery as specified and carry main maintenance; no whole-tree
replacement. Commit only per fresh branch/PR packet, with actual Model/effort and
last Omnigent trailer. New main movement needs parent ruling, not an automatic
merge. Initial tests may use a dirty implementation snapshot with diff/file hashes;
final gates below use a clean authorized implementation commit. Before-fix evidence
is one targeted stale-download red run with its own RUN.txt/snapshot, not these
entire gates rerun on old code.

Dirty red-run recipe: create a separate red-run directory with RUN.txt FIRST
(`dirty: yes`, exact HEAD); record a `snapshot.manifest` containing HEAD, the
SHA256 of `git diff --binary HEAD` and path/SHA256 for every untracked allowed
file. Use `DIRTY_HASH=$(sha256sum "$RUN/snapshot.manifest" | cut -d' ' -f1)` and
`TAG="dirty-${DIRTY_HASH:0:12}"`, never the clean SHA tag. Reuse the local-builder
preflight, gate wrapper, GUI production/test-image build lines, COMMON and GUI_ENV
from the program below in that one diagnostic shell; skip its clean-tree gate.
Define the single browser regression as `test_latest_yaml_download`, and replace
the full pytest invocation with `python -m pytest -p no:cacheprovider -q --tb=short
--basetemp=/evidence/pytest-red --junitxml=/evidence/junit-red.xml
/src/tests/test_gui_e2e.py::test_latest_yaml_download` inside the GUI test image.
Record its expected nonzero result via the same wrapper and retain output; a
setup/browser failure is not proof of the stale-download bug. Do not run the full
old-code suite or commit just to make this diagnostic tree clean.

The following is **one complete Bash program**, not separate shell cells. Execute
it in one `exec_command` after implementation, or save it as gates.sh in an already
initialized evidence directory and execute with `bash`. It creates its own fresh
run and RUN.txt first, saves the exact recipe and absolute path in execution.json,
and wraps commands so failures retain log/command/exit status. Do not split the
program across agent shell calls expecting variables to persist. Host `python3`
means stdlib-only Python >=3.8; packages/installations occur only in containers.
The privacy scanner is extracted from section 8 by the program itself, so no
cross-cell `$RUN` state or hand-copied scanner is required.

Local Docker builds/tests are allowed even while a final privacy sweep is pending.
Use a local Unix-socket daemon, no remote builder or registry push; build contexts
are sent only to that local daemon. Existing private biological fixtures must not
be echoed in logs. New tests use the synthetic generator; synthetic diagnostic
payloads are allowed locally. SHA-derived image tags are unique to candidate,
not generic `:candidate`; preserve public documentation's CLI `cc_copt:latest` tag.
Test-only Dockerfiles live in evidence, not a third production Dockerfile.

```bash
set -Eeuo pipefail
REPO=/home/qbk/qbk-code/cc_copt/.worktrees/qbk-polly/streamlit-coexist/feature
BASE=d4eb3c53eb9fadd57481893665b3512123970f9a
cd "$REPO"
CANDIDATE=$(git rev-parse HEAD)
RUN="$HOME/qbk-code/tmp/cc-copt-coexist-${CANDIDATE:0:12}-$(date -u +%Y%m%dT%H%M%SZ)-$$"
mkdir "$RUN"
DIRTY=no
if test -n "$(git status --porcelain=v1)"; then DIRTY=yes; fi
printf 'commit: %s   dirty: %s\nstarted: %s\npurpose: focused CLI GUI acceptance\n' \
  "$CANDIDATE" "$DIRTY" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$RUN/RUN.txt"
GUI_CID=
finish() {
  rc=$?
  trap - EXIT
  set +e
  if test -n "$GUI_CID"; then
    docker logs "$GUI_CID" > "$RUN/gui-startup.log" 2>&1
    docker rm -f "$GUI_CID" > "$RUN/gui-cleanup.log" 2>&1
  fi
  git status --porcelain=v1 --untracked-files=all > "$RUN/status-after.txt"
  git rev-parse HEAD > "$RUN/head-after.txt"
  printf '%s\n' "$rc" > "$RUN/overall.exit"
  printf 'Evidence: %s (exit %s)\n' "$RUN" "$rc"
  exit "$rc"
}
trap finish EXIT
gate() {
  name=$1; shift
  printf '%q ' "$@" > "$RUN/$name.command"
  printf '\n' >> "$RUN/$name.command"
  if "$@" > "$RUN/$name.log" 2> "$RUN/$name.stderr.log"; then rc=0; else rc=$?; fi
  printf '%s\n' "$rc" > "$RUN/$name.exit"
  return "$rc"
}
gate clean-tree test "$DIRTY" = no
gate branch test "$(git branch --show-current)" = qbk-polly/feature/streamlit-coexist
gate ancestor git merge-base --is-ancestor "$BASE" "$CANDIDATE"
gate preserved git diff --quiet "$BASE" "$CANDIDATE" -- \
  tool.yaml claude_context/manifest-spec.md cc_copt/cli.py cc_copt/optimize.py \
  cc_copt/io.py cc_copt/utils.py cc_copt/__init__.py examples/example.faa \
  examples/config.yaml examples/nextflow/main.nf examples/nextflow/nextflow.config
# Above is file preservation only: no SLS command/test is invoked.
gate snapshot-meta python3 - "$REPO" "$RUN" "$BASE" "$CANDIDATE" <<'PYMETA'
import sys, pathlib, json, re
repo, run, base, candidate = sys.argv[1:]
p = pathlib.Path(repo)/'docs/plans/2026-10-05-streamlit-coexist.md'
s = p.read_text()
section7 = s.split('\n## 7. ',1)[1].split('\n## 8. ',1)[0]
section8 = s.split('\n## 8. ',1)[1].split('\n## 9. ',1)[0]
r = pathlib.Path(run)
(r/'gates-recipe.sh').write_text(re.search(r'```bash\n(.*?)\n```',section7,re.S).group(1)+'\n')
(r/'privacy_scan.py').write_text(re.search(r'```python\n(.*?)\n```',section8,re.S).group(1)+'\n')
(r/'execution.json').write_text(json.dumps(dict(repo=repo,run=run,base=base,candidate=candidate),indent=2)+'\n')
PYMETA
gate docker-context docker context inspect
# Inspect docker-context.log: chosen endpoint must be local Unix socket.
# Environment endpoint overrides also must not target a remote daemon.
gate local-daemon python3 - "$RUN/docker-context.log" <<'PYDOCKER'
import json,sys,os
context=json.load(open(sys.argv[1]))[0]
endpoints=[context['Endpoints']['docker']['Host']]
if os.environ.get('DOCKER_HOST'): endpoints.append(os.environ['DOCKER_HOST'])
assert all(e.startswith('unix://') for e in endpoints), 'Select a local Docker Unix socket; no remote builder'
PYDOCKER
gate builder-name docker context show
LOCAL_BUILDER=$(cat "$RUN/builder-name.log")
gate builder-inspect docker buildx inspect "$LOCAL_BUILDER"
gate builder-local python3 - "$RUN/builder-inspect.log" "$LOCAL_BUILDER" <<'PYBUILDER'
import re,sys
text=open(sys.argv[1]).read()
assert re.search(r'^Driver:\s+docker\s*$',text,re.M), 'Use the local context builder with docker driver'
endpoints=re.findall(r'^Endpoint:\s+(\S+)\s*$',text,re.M)
assert endpoints and all(e==sys.argv[2] for e in endpoints), 'Builder must use the inspected local context'
PYBUILDER
TAG="coexist-${CANDIDATE:0:12}"
CLI="cc-copt-cli:$TAG"; GUI="cc-copt-gui:$TAG"
CLI_TEST="cc-copt-cli-test:$TAG"; GUI_TEST="cc-copt-gui-test:$TAG"
gate build-cli docker buildx build --builder "$LOCAL_BUILDER" --load -f Dockerfile -t "$CLI" "$REPO"
gate build-gui docker buildx build --builder "$LOCAL_BUILDER" --load -f Dockerfile.streamlit -t "$GUI" "$REPO"
# Explicit context-backed docker driver; do not select a remote/custom builder.
printf 'FROM %s\nRUN pip install --no-cache-dir pytest\nENTRYPOINT []\n' \
  "$CLI" > "$RUN/Dockerfile.test-cli"
cat > "$RUN/Dockerfile.test-gui" <<DOCKER
FROM $GUI
RUN pip install --no-cache-dir pytest playwright
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers
RUN python -m playwright install --with-deps chromium && chmod -R a+rX /opt/pw-browsers
ENTRYPOINT []
DOCKER
gate build-test-cli docker buildx build --builder "$LOCAL_BUILDER" --load -f "$RUN/Dockerfile.test-cli" -t "$CLI_TEST" "$RUN"
gate build-test-gui docker buildx build --builder "$LOCAL_BUILDER" --load -f "$RUN/Dockerfile.test-gui" -t "$GUI_TEST" "$RUN"
gate image-ids docker image inspect "$CLI" "$GUI" "$CLI_TEST" "$GUI_TEST"
COMMON=(--rm --network none --user "$(id -u):$(id -g)"
  -e PYTHONDONTWRITEBYTECODE=1 -e HOME=/evidence -e XDG_CACHE_HOME=/evidence/cache
  -e STREAMLIT_BROWSER_GATHER_USAGE_STATS=false -e STREAMLIT_SERVER_HEADLESS=true
  -v "$REPO:/src:ro" -v "$RUN:/evidence" -w /evidence)
GUI_ENV=(-e CC_COPT_APP_PATH=/app/cc_copt/gui.py -e PYTHONPATH=/app)
gate base-import docker run "${COMMON[@]}" "$CLI" python -c \
  'import importlib.util; import cc_copt.config,cc_copt.io,cc_copt.optimize; assert importlib.util.find_spec("streamlit") is None'
gate cli-help docker run "${COMMON[@]}" "$CLI" cc_copt optimize --help
gate gui-import docker run "${COMMON[@]}" "${GUI_ENV[@]}" --entrypoint python "$GUI" -c \
  'import pathlib,streamlit,cc_copt.config; assert pathlib.Path("/app/cc_copt/gui.py").is_file(); assert pathlib.Path(cc_copt.config.__file__).parent == pathlib.Path("/app/cc_copt")'
for kind in cli gui; do
  if test "$kind" = cli; then PROD=$CLI; TEST=$CLI_TEST; else PROD=$GUI; TEST=$GUI_TEST; fi
  gate "pip-check-$kind" docker run "${COMMON[@]}" --entrypoint python "$PROD" -m pip check
  gate "package-files-$kind" docker run "${COMMON[@]}" --entrypoint python "$PROD" -m pip show -f cc_copt
  gate "versions-$kind" docker run "${COMMON[@]}" "$TEST" python -m pip freeze
  gate "python-$kind" docker run "${COMMON[@]}" "$TEST" python --version
done
# Base test file set includes pure GUI-boundary tests, without importing Streamlit.
CORE=(/src/tests/test_optimize.py /src/tests/test_cli.py /src/tests/test_gui_config.py)
ALL=("${CORE[@]}" /src/tests/test_gui.py /src/tests/test_gui_e2e.py)
gate collect-core docker run "${COMMON[@]}" "$CLI_TEST" python -m pytest \
  -p no:cacheprovider --collect-only -q "${CORE[@]}"
gate test-core docker run "${COMMON[@]}" "$CLI_TEST" python -m pytest \
  -p no:cacheprovider -q -ra --tb=short --basetemp=/evidence/pytest-core \
  --junitxml=/evidence/junit-core.xml "${CORE[@]}"
gate collect-base-optional docker run "${COMMON[@]}" "$CLI_TEST" python -m pytest \
  -p no:cacheprovider --collect-only -q "${ALL[@]}"
gate gui-test-deps docker run "${COMMON[@]}" "$GUI_TEST" python -c \
  'import streamlit.testing.v1,playwright.sync_api'
gate collect-full docker run "${COMMON[@]}" "${GUI_ENV[@]}" "$GUI_TEST" python -m pytest \
  -p no:cacheprovider --collect-only -q "${ALL[@]}"
gate test-full docker run "${COMMON[@]}" "${GUI_ENV[@]}" --shm-size=1g "$GUI_TEST" python -m pytest \
  -p no:cacheprovider -q -ra --tb=short --basetemp=/evidence/pytest-full \
  --junitxml=/evidence/junit-full.xml "${ALL[@]}"
gate case-counts python3 - "$RUN/junit-core.xml" "$RUN/junit-full.xml" <<'PYCOUNT'
import sys,xml.etree.ElementTree as E
for p in sys.argv[1:]:
    cases=E.parse(p).findall('.//testcase')
    assert cases, 'No executed cases'
    assert not any(c.find(t) is not None for c in cases for t in ('failure','error','skipped'))
    print(p, 'executed cases:', len(cases))
PYCOUNT
# Offline documentation recipe: identical /evidence namespace in both commands.
gate example-generate docker run "${COMMON[@]}" "$CLI" python /app/examples/generate_synthetic.py \
  --out-dir /evidence/example --seed 1729
gate example-cli docker run "${COMMON[@]}" "$CLI" cc_copt optimize \
  -i /evidence/example/protein.faa -c /evidence/example/config.yaml \
  -o /evidence/example/optimized.fna -t /evidence/example/summary.tsv --threads 2
# Implement this module entrypoint as a thin reuse of the same semantic checks
# in test_cli.py, not an independent second output checker.
gate example-verify docker run "${COMMON[@]}" "$CLI_TEST" python /src/tests/test_cli.py \
  --check-example /evidence/example
# Actual production entrypoint, unchanged argv; health supplements real browser flow.
gate gui-start docker run -d --network none --user "$(id -u):$(id -g)" \
  -e HOME=/tmp -e STREAMLIT_SERVER_HEADLESS=true -e STREAMLIT_BROWSER_GATHER_USAGE_STATS=false "$GUI"
GUI_CID=$(cat "$RUN/gui-start.log")
gate gui-health docker exec "$GUI_CID" python -c '
import time,urllib.request
end=time.monotonic()+40
while True:
    try:
        with urllib.request.urlopen("http://127.0.0.1:8501/_stcore/health",timeout=2) as r:
            assert r.status==200
            print("GUI health status: 200")
            break
    except Exception:
        if time.monotonic()>=end: raise SystemExit("GUI did not become healthy")
        time.sleep(0.5)
'
gate privacy-scan python3 "$RUN/privacy_scan.py" "$REPO" "$BASE" "$CANDIDATE"
# privacy-scan.log is structured JSON; semantic ledger/review in section 8 remains required.
gate whitespace git diff --check "$BASE" "$CANDIDATE"
gate same-head test "$(git rev-parse HEAD)" = "$CANDIDATE"
gate final-clean test -z "$(git status --porcelain=v1)"
```

The gate wrapper records command text, stdout (`.log`), stderr (`.stderr.log`)
and exit status for each named gate even on failure. Parse only stdout for JSON,
container IDs and builder metadata; warnings on stderr remain separate evidence. EXIT trap records final status and retains startup
logs before disposable-container cleanup. It never deletes evidence. Other
browser/server processes belong to the pytest session fixture, which must retain
logs on failure and terminate its own children. No polling command exceeds 40s.
If a gate fails, inspect saved output; rerun only affected tests under a new run
with matching snapshot identity. Do not tag a changed dirty snapshot with a clean
SHA tag. Runtime Docker/package resolution is unverified by this plan.

Define one shared test APP_PATH from `CC_COPT_APP_PATH` (set above). When unset
for README source-checkout tests, default to that checkout's `cc_copt/gui.py`
(resolved relative to the tests directory), with its parent's parent as server
cwd and import root. Container APP_PATH/cwd remain `/app/cc_copt/gui.py` and `/app`.
Use shared server argv exactly matching `Dockerfile.streamlit`:
`python -m streamlit run cc_copt/gui.py --server.port=8501
--server.address=0.0.0.0 --browser.gatherUsageStats=false`, with cwd `/app`.
The fixture sets headless through the environment, same code/import namespace
as deployed. Keep this argv synchronized with that Dockerfile if it changes.
AppTest uses `/app/cc_copt/gui.py`; it must not execute `/src/gui.py` while loading
other modules from site-packages. Fixed internal port is safe in one serial
session fixture/container; no host port is exposed. Browser tests use loopback,
not mocked HTTP or fake optimization. `/opt/pw-browsers` is container-only, never
change the host Playwright environment. `--shm-size=1g` is included for Chromium;
report actual browser failures before further environment changes.

Required evidence contract for tests: fixture-generated files/provenance under
pytest basetemp; per-flow browser downloads and server log in that same test's
`artifacts/` directory; write an `artifacts.json` index containing their exact
absolute host paths (translate `/evidence/...` using execution.json's run path).
Reports link the index AND concrete paths, not a glob. Retain assertion diagnostics
for generated fixtures. Do not output real reporter sequences from existing
examples. Test `--check-example` returns nonzero if any translation/record/order/
constraint/score invariant fails; gate records its result.

In addition to automated gates, inspect package inventories and image metadata,
record registry signature/default/option decisions, verify production tag/path
preservation from source, classify privacy findings, and record explicit outcomes.
The scanner's zero exit is completion, not privacy approval. Final publication
requires parent review of both runtime evidence and classification ledger.

## 8. Reproducible final privacy sweep and decision ledger

The section 7 program extracts and runs this stdlib-only scanner against exact
BASE/CANDIDATE. To run just the scanner in a separate later shell, use absolute
paths and explicit SHAs, not prior shell variables:
`python3 /absolute/run/privacy_scan.py /absolute/repo BASE_SHA CANDIDATE_SHA`.
Create a fresh RUN.txt before that run's output; save JSON plus command/exit status.
No fetch, external dataset search, upload or hosting message is necessary.

Inventory full candidate tree and ALL trees/commit metadata introduced relative
to BASE, including files removed later. Base-history reachability is mechanical
via `git rev-list --objects BASE`; remote reachability uses existing origin refs
and is explicitly dated/stale, not a live-hosting assertion. A blob already on
origin can still be new relative to main; preserve both facts separately. Scan
commit bodies AND author/committer metadata in memory; output counts, no values.
New blobs require focused content review; old owner-attested content is not
reopened solely for lack of an external accession. Short/split/encoded sequences,
lowercase proteins, false-positive code words and unrecognized credentials remain
scanner limitations requiring proportionate semantic review, not automatic guilt.

```python
import sys,subprocess,re,json,datetime
repo,base,candidate=sys.argv[1:]
def git(*args):
    return subprocess.check_output(['git','-C',repo,*args])
def reachable(*refs):
    if not refs: return set()
    return {line.split(b' ',1)[0].decode() for line in git('rev-list','--objects',*refs).splitlines()}
base_objects=reachable(base)
origin_refs=git('for-each-ref','--format=%(refname)','refs/remotes/origin').decode().splitlines()
origin_objects=reachable(*origin_refs)
commits=git('rev-list','--reverse',f'{base}..{candidate}').decode().splitlines()
patterns={
    'dna_like':rb'[ACGTUNacgtun]{12,}',
    'protein_like':rb'(?i:[ACDEFGHIKLMNPQRSTVWY]{18,})',
    'private_key':rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    'token':rb'gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9_-]{24,}',
    'credential_assignment':rb'(?i:(?:password|passwd|api_key|api_token|secret|access_token)\s*[:=]\s*["\x27][^"\x27\r\n]{8,}["\x27])',
}
def hits(data): return {k:len(re.findall(v,data)) for k,v in patterns.items()}
blobs,records,metadata={},[],[]
for commit in dict.fromkeys([base,candidate]+commits):
    metadata.append(dict(commit=commit,
        message_hits=hits(git('show','-s','--format=%B',commit)),
        identity_hits=hits(git('show','-s','--format=%an%n%ae%n%cn%n%ce',commit))))
    for entry in git('ls-tree','-rz','--full-tree',commit).split(b'\0'):
        if not entry: continue
        raw,path=entry.split(b'\t',1)
        mode,kind,oid=raw.decode().split()
        path=path.decode('utf-8','replace')
        row=dict(commit=commit,path=path,mode=mode,kind=kind,blob=oid,
            reachable_from_base=oid in base_objects,already_on_origin=oid in origin_objects,
            new_relative_to_base=oid not in base_objects)
        if kind=='blob':
            if oid not in blobs:
                data=git('cat-file','blob',oid)
                blobs[oid]=dict(size=len(data),binary=b'\0' in data,hits=hits(data),
                    lfs_pointer=data.startswith(b'version https://git-lfs.github.com/spec/'))
            row.update(blobs[oid])
            if path.endswith('.ipynb'):
                try:
                    nb=json.loads(git('cat-file','blob',oid))
                    row['notebook_outputs']=sum(len(c.get('outputs',[])) for c in nb.get('cells',[]))
                except (ValueError,TypeError): row['unparsed_notebook']=True
        row['data_like_path']=path.lower().endswith(('.fa','.faa','.fna','.fasta','.csv','.tsv','.json','.ipynb','.pyc','.pem','.env'))
        records.append(row)
print(json.dumps(dict(base=base,candidate=candidate,
    scanned_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    origin_refs={ref:git('rev-parse',ref).decode().strip() for ref in origin_refs},
    origin_observation='local refs only; no fetch',introduced_commits=commits,
    unique_blobs=len(blobs),new_blob_count=len(set(blobs)-base_objects),
    records=records,commit_metadata=metadata),indent=2))
```

Maintain `privacy-decisions.json` in the exact run. Include path/blob/affected
commits; base-history/origin/new flags; classification (`owner-attested`,
`derived-owner-attested`, `synthetic-generated`, `documented-public`, `nondata`,
`needs-triage`, `sensitive`); evidence reference and reviewer rationale. Carry
2026-10-05 owner wording from section 3 without upgrading it to externally verified
provenance. Inherit accepted source classification for corroborated derived
artifacts and apply the concrete `.DS_Store` criterion there. Do not block solely
because an old owner-attested binary was not exhaustively decoded. Manually
inspect new code/constants and any concrete anomalies with metadata-only output.
Encoded/large/LFS/submodule payloads newly introduced need actual payload review
or explicit bounded finding; never clear inaccessible suspicious content by regex.

The final gate passes when the sweep covers the intended exact tree/history,
ownership classifications and generation recipes are recorded, and every concrete
flag has a documented benign/accepted resolution or an explicit parent ruling.
Confirmed sensitive content or concrete still-unclassified suspicious content
pauses publication for a ruling; theoretical inability to prove universal absence
does not. No confirmed sensitive finding currently exists. Previously cleared
notebook example/output references need no further question.

Before parent push/PR, repeat on the final SHA and intended PR base after any
merge/commit, compare decisions to new blobs, and obtain independent review.
Retain old artifacts unchanged; findings about an older tip do not establish a
final-candidate verdict. Never attach raw datasets/notebooks/evidence dumps to
PRs; report only paths/SHAs/categories and synthetic verification results.

## 9. Serial implementation sequence and review checkpoints

No parallel agents. Logical work packages could be independent, but this approved
mode is serial and shared-state/privacy checks make serial execution appropriate.

1. Independent reviewer reads the complete plan plus requirement record. Resolve
   blockers and proposed atomic-import behavior in the approval summary. Native
   author identity is verified in revision-02 evidence. Authorized plan
   commit contains `Model: <actual model> (<effort>)` in body and ends with a blank
   line then `Co-authored-by: omnigent <noreply@omnigent.ai>`. No push. User approves
   summarized final plan; dispatch a fresh implementer.
2. Fresh worker rechecks status/history/plan, reconciles pinned main and packaging.
   Carry preservation-only files and deletions. Stop on new scope/conflicts.
3. Preserve owner-cleared existing examples; add the single synthetic generator
   and rewrite focused tests for offline use without extra owner permission.
   Local Docker work proceeds; publication awaits the final sweep, not local tests.
4. Capture one red run of the single stale-download browser regression, then fix
   config/state behavior and run focused tests. Cover repeated import in the browser
   and broader numbers/validation cheaply. Store red/green evidence under distinct
   snapshot identities; no full old-code matrix.
5. Complete CLI flow tests, browser real flow and doc/example changes. Narrowly
   correct containers if required. These are serial work packages; do not dispatch
   a tests agent or documentation agent in parallel.
6. Drive G0-G8 green in Docker on final implementation snapshot, retain evidence.
   Run final full-history privacy gate. Parent runs deterministic checks and
   independent review of exact code snapshot/allowed files and evidence. Fix only
   scoped findings; every change invalidates affected gates and snapshot verdict.
7. Feature owner/parent alone handles push and draft PR after clearance and explicit
   packet authority, with tests/limits/provenance status in PR description. Never
   claim SLS re-verification. No deletion of old feature refs during this task.

Parent-owned issue wording: “Re-verify cc_copt SLS compatibility when SLS is
updated. CLI and optional Streamlit now coexist with separate Docker images.
This reconciliation preserves tool.yaml byte-for-byte and deliberately does not
implement or test SLS. On the updated SLS release, verify discovery, CLI container
launch, preset/custom configuration, and output handling using synthetic fixtures.”
Link the final PR when known. Parent already owns issue creation; worker does not
send external messages or open it independently.

## 10. Remaining choices, risks and approval summary

Required user summary before fresh implementation:

1. CLI plus optional Streamlit; two Dockerfiles; engine/CLI contracts and
   tool.yaml/config-path/image-tag preserved; no SLS or Nextflow work/tests.
2. Fix stale YAML export and stale widget import state. **PROPOSED:** reject GUI
   configs containing unsupported fields/types atomically with CLI guidance,
   rather than silently loading a subset. Preserve omitted library defaults;
   validate actual signatures/options in later container checks. **PROPOSED default
   disposition:** if an advertised GUI option cannot run using available GUI fields,
   hide or disable it with a clear explanation and preserve CLI capability, rather
   than expand the engine/API. Record the measured failure and disposition. This
   default is not authorized until the user approves this summary; signature,
   deviation and per-option construction rules above remain unchanged.
3. Focused real CLI/browser flows plus cheap expanded unit cases and synthetic
   offline fixtures. Keep owner-attested primary examples and add an offline recipe.
4. Final tree/history privacy sweep before publication. Existing flagged blobs
   are already in main history/on origin; owner's statements classify them as
   acceptable. No proprietary content is confirmed and no new data exposure is
   alleged. No further notebook provenance question is pending.

Pending real choices: approval of this reviewed plan summary, explicitly including
item 2's atomic rejection and proposed hide/disable disposition. Once approved,
a measured unbuildable option follows that default without a new engine/API scope
expansion; findings outside that disposition still require a ruling. The conditional question about
confirmed old sensitive history is not a present blocker and needs no answer now.
Do not ask for further fixture documentation or permission to rewrite synthetic
tests. Plan commit remains on HOLD until retained independent review and parent
commit authorization; then user approval and a fresh build worker are mandatory.

Risks/limitations:

- No runtime tests collected/run, Docker builds or library-signature checks during
  planning. Dependency defaults and option requirements cited by review were
  recollections, not confirmed facts; report later measured results.
- Strict rejection is a bounded editor contract, not a general validation project.
  Preserve prior config on failure, preserve CLI flexibility and avoid redesign.
- Installed dependencies float. Record versions/IDs; investigate failures before
  broad pinning or engine work. Unbuildable registry options require explicit
  disposition, not silent expansion or unconditional acceptance.
- Owner attestation is sufficient here but is not a documented biological source
  or generation recipe. Historical binary derivation confidence must be stated.
  Scanner patterns are heuristic; classify concrete findings proportionately.
- Python >=3.9 metadata versus current annotations and unrelated Nextflow uid/gid
  guidance are parent backlog observations only; no edits/tests here.
- GUI is documented for trusted local use, with `-p 127.0.0.1:8501:8501` in local
  Docker examples. No authentication redesign. Missing table paths get a safe error.
- Final handoff must name exact RUN.txt, SHA/dirty manifest, plan hash, changed file
  set, command/log/exit files, collected/executed/skipped counts, concrete browser
  download/log paths, image IDs, privacy inventory/ledger and unresolved findings.
  PR URL only if worker owns it. Parent retains publication/merge coordination.
