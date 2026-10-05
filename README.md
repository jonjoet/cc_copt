# cc_copt

Batch codon optimization built on [DnaChisel](https://edinburgh-genome-foundry.github.io/DnaChisel/). Accepts protein or DNA sequences, applies configurable constraints and objectives, and outputs optimized DNA as FASTA and/or a summary TSV. Available as a **CLI** for scripting/pipelines and as a **Streamlit web GUI** for interactive use.

## Installation

### pip (local)

```bash
pip install -e .
```

### Docker (CLI)

```bash
docker build -t cc_copt:latest .
```

### Docker (Streamlit GUI)

```bash
docker build -f Dockerfile.streamlit -t cc_copt-streamlit:latest .
```

## Quick Start

### Local

```bash
cc_copt optimize \
  -i examples/example.faa \
  -c examples/config.yaml \
  -o optimized.fna \
  -t summary.tsv
```

The retained reporter example uses TaxID 196627. In the resolved
`python_codon_tables` package this TaxID downloads its table, so the primary
quickstart needs network access. It was retained without a runtime acceptance
claim. For an executed offline example, see [examples/README.md](examples/README.md).

### Docker

```bash
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD":/data cc_copt:latest cc_copt optimize \
  -i /data/examples/example.faa \
  -c /data/examples/config.yaml \
  -o /data/optimized.fna \
  -t /data/summary.tsv
```

## CLI Usage

```
cc_copt optimize -i INPUT -c CONFIG [-o OUTPUT] [-t TABLE] [--threads N]
```

| Flag | Description |
|------|-------------|
| `-i/--input` | Input FASTA (`.fa`, `.faa`, `.fasta`, `.fna`) or CSV/TSV file |
| `-c/--config` | YAML configuration file |
| `-o/--output` | Output FASTA path (default: stdout) |
| `-t/--table` | Output TSV summary with sequences and constraint/objective reports |
| `--threads` | Number of parallel workers (default: 1) |

### Supported Input Formats

- **FASTA** — protein (`.faa`) or DNA (`.fna`, `.fa`, `.fasta`)
- **CSV/TSV** — auto-detects ID and sequence columns by header name (matches patterns like `id`, `name`, `accession` and `seq`, `sequence`, `protein`, `dna`)

Protein sequences are automatically reverse-translated before optimization. `stop_codon` sets the initial terminal codon; optimization can replace it with a synonymous stop while preserving translation.

## Configuration

The YAML config maps directly to DnaChisel specification classes. Example for *C. glutamicum* (see `examples/config.yaml`):

```yaml
species: 196627        # TaxID, species name string, or path to a .json codon table
input_type: auto       # "protein", "dna", or "auto"
stop_codon: TAA
max_random_iters: 50000

constraints:
  - type: AvoidPattern
    pattern: BsaI_site
  - type: EnforceGCContent
    mini: 0.4
    maxi: 0.65
    window: 50
  - type: EnforceTranslation
    start_codon: keep
  - type: AvoidRareCodons
    min_frequency: 0.1
  - type: AvoidHairpins
    stem_size: 16
    hairpin_window: 200

objectives:
  - type: CodonOptimize
    method: match_codon_usage
  - type: UniquifyAllKmers
    k: 8
```

- `type` maps to a DnaChisel class name (e.g. `AvoidPattern`, `CodonOptimize`)
- All other keys are passed as kwargs to the class constructor
- Top-level `species` is automatically injected into specs that need it (`AvoidRareCodons`, `CodonOptimize`) unless overridden per-spec
- `EnforceTranslation` is auto-added as a safety net if not listed

## Web GUI (Streamlit)

A Streamlit-based web interface is available for interactive use without the command line.

### Running

```bash
# Local
pip install ".[streamlit]"
python -m streamlit run cc_copt/gui.py

# Docker
docker build -f Dockerfile.streamlit -t cc_copt-streamlit:latest .
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp \
  -p 127.0.0.1:8501:8501 cc_copt-streamlit:latest
```

Run the local command from this source checkout. Then open `http://localhost:8501` in your browser. The GUI is intended for trusted local use. For local JSON codon tables, mount the table directory into the GUI container and enter its container path in Species.

### Features

- **Upload sequences** — FASTA or CSV/TSV, same formats as the CLI
- **Upload a YAML config** — loads supported GUI settings atomically; replaces earlier settings and clears results
- **Configure manually** — set species, input type, stop codon, and iteration limit
- **Add constraints and objectives** — pick from the curated types listed below, with dynamically rendered parameter forms. Add as many as you need.
- **View results** — per-sequence constraint pass/fail and objective scores
- **Download** — current configuration YAML, optimized FASTA and summary TSV

### Configuration import and export

The GUI accepts `species` (TaxID/name/local JSON-table path), `input_type`,
`stop_codon`, integer `max_random_iters >= 100`, and lists of the curated types
with their displayed parameters. Unsupported types, methods, extra fields,
inline tables, per-spec species overrides and location arguments are rejected
without changing existing settings. Run broader DnaChisel configurations with
the CLI. Invalid YAML also leaves the existing settings intact.

Omitted fields use effective library defaults; optional numeric controls omit
unset arguments and retain enabled zero where allowed. Download Config as YAML
exports the current settings after committed edits (Enter or blur), ready for
GUI reimport or CLI use.

Use `CodonOptimize` with `match_codon_usage` for `MatchTargetCodonUsage` behavior,
or `use_best_codon` for the equivalent MaximizeCAI behavior. The redundant
MaximizeCAI GUI type is omitted. `harmonize_rca` needs source-species information
and is deferred in the GUI ([issue #5](https://github.com/jonjoet/cc_copt/issues/5));
the CLI continues accepting its broader supported constructor kwargs.

### Available Specifications

**Constraints:** AvoidPattern, EnforceGCContent, EnforceTranslation, AvoidRareCodons, AvoidHairpins, AvoidStopCodons, EnforceSequence, AvoidChanges, EnforceTerminalGCContent, SequenceLengthBounds

**Objectives:** CodonOptimize, UniquifyAllKmers, EnforceGCContent (with target), EnforceChanges, EnforcePatternOccurence

## Nextflow Integration

An example DSL2 workflow is provided in `examples/nextflow/`. It uses the `cc_copt:latest` Docker image by default — build the image first, then run:

```bash
docker build -t cc_copt:latest .

nextflow run examples/nextflow/main.nf \
  --input examples/example.faa \
  --config examples/config.yaml \
  --outdir results
```

## Running Tests

```bash
# CLI/core and pure config tests; GUI modules intentionally skip without Streamlit.
pip install -e ".[dev]"
python -m pytest -p no:cacheprovider tests/test_optimize.py tests/test_cli.py tests/test_gui_config.py

# Full GUI/AppTest/browser suite (Python 3.11 containers used for verification).
pip install -e ".[dev,streamlit]"
pip install playwright
python -m playwright install --with-deps chromium
PYTHONDONTWRITEBYTECODE=1 python -m pytest -p no:cacheprovider tests/
```

Tests generate synthetic fixtures offline with `examples/generate_synthetic.py`.
Browser tests run the real app and optimizer, upload/reapply settings and inspect
actual downloads. AppTest and browser tests use `CC_COPT_APP_PATH` when set,
defaulting to this checkout's `cc_copt/gui.py`. Verification dependencies belong
in a disposable container or a project environment; they are not production deps.

## Dependencies

- [DnaChisel](https://github.com/Edinburgh-Genome-Foundry/DnaChisel) — optimization engine
- [Biopython](https://biopython.org/) — sequence I/O
- [Click](https://click.palletsprojects.com/) — CLI framework
- [PyYAML](https://pyyaml.org/) — config parsing
- [pandas](https://pandas.pydata.org/) — CSV/TSV I/O
- [Streamlit](https://streamlit.io/) — web GUI (optional)
