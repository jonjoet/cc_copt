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

### Docker

```bash
docker run --rm -v "$PWD":/data cc_copt:latest cc_copt optimize \
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

Protein sequences are automatically reverse-translated before optimization.

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
streamlit run cc_copt/gui.py

# Docker
docker build -f Dockerfile.streamlit -t cc_copt-streamlit:latest .
docker run -p 8501:8501 cc_copt-streamlit:latest
```

Then open `http://localhost:8501` in your browser.

### Features

- **Upload sequences** — FASTA or CSV/TSV, same formats as the CLI
- **Upload a YAML config** — same format as the CLI; pre-populates all settings in the GUI
- **Configure manually** — set species, input type, stop codon, and iteration limit
- **Add constraints and objectives** — pick from any supported DnaChisel specification type, with dynamically rendered parameter forms. Add as many as you need.
- **View results** — per-sequence constraint pass/fail and objective scores
- **Download** — optimized FASTA and summary TSV

### Available Specifications

**Constraints:** AvoidPattern, EnforceGCContent, EnforceTranslation, AvoidRareCodons, AvoidHairpins, AvoidStopCodons, EnforceSequence, AvoidChanges, EnforceTerminalGCContent, SequenceLengthBounds

**Objectives:** CodonOptimize, MaximizeCAI, MatchTargetCodonUsage, UniquifyAllKmers, EnforceGCContent (with target), EnforceChanges, EnforcePatternOccurence

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
pip install -e ".[dev]"
pytest tests/
```

## Dependencies

- [DnaChisel](https://github.com/Edinburgh-Genome-Foundry/DnaChisel) — optimization engine
- [Biopython](https://biopython.org/) — sequence I/O
- [Click](https://click.palletsprojects.com/) — CLI framework
- [PyYAML](https://pyyaml.org/) — config parsing
- [pandas](https://pandas.pydata.org/) — CSV/TSV I/O
- [Streamlit](https://streamlit.io/) — web GUI (optional)
