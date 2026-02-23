# cc_copt

Batch codon optimization CLI built on [DnaChisel](https://edinburgh-genome-foundry.github.io/DnaChisel/). Accepts protein or DNA sequences, applies configurable constraints and objectives via a YAML config, and outputs optimized DNA as FASTA and/or a summary TSV.

## Installation

### pip (local)

```bash
pip install -e .
```

### Docker

```bash
docker build -t cc_copt:latest .
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
