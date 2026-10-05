# Examples

`example.faa` and `config.yaml` remain the primary reporter/organism quickstart.
The owner cleared the existing reporter fixtures; no exact public accession is
claimed here. TaxID 196627 requires table download in the resolved package.

For an offline acceptance example, generate three artificial proteins and DNA,
equivalent FASTA/CSV/TSV inputs, a complete synthetic codon table, and configuration:

```bash
docker build -t cc_copt:latest .
mkdir -p synthetic-output
docker run --rm --network none --user "$(id -u):$(id -g)" \
  -v "$PWD/synthetic-output":/data cc_copt:latest \
  python /app/examples/generate_synthetic.py --out-dir /data --seed 1729
docker run --rm --network none --user "$(id -u):$(id -g)" \
  -v "$PWD/synthetic-output":/data cc_copt:latest cc_copt optimize \
  -i /data/protein.faa -c /data/config.yaml \
  -o /data/optimized.fna -t /data/summary.tsv --threads 2
```

Keep the same `/data` mount for both commands: config species contains the
absolute table path inside that environment. The generated example is synthetic,
not an organism model, and uses translation preservation plus best-codon usage.

Generation uses Python `random.Random(seed).choice` over the sorted standard-code
amino-acid alphabet, with an initial methionine and lengths 72, 81 and 90. DNA
uses each amino acid's lexically first standard-code synonym and a TAA stop.
The table includes all 64 codons, assigning positive, unequal synonymous rank
weights normalized within each amino acid. `PROVENANCE.json` records the seed,
algorithm, no biological source and generated file SHA256 hashes. No external
sequence data is retrieved; output is written only to the explicit `--out-dir`.

The focused tests reuse this generator. Their semantic checker verifies record
order/count, translation, stop/length, constraint PASS flags, objective scores
and agreement between FASTA and TSV. Optimizer DNA is not expected to be byte
identical across randomized runs.
