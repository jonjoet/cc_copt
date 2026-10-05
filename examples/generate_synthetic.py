"""Generate deterministic offline fixtures; no biological source data.

Python random.Random(seed).choice over the sorted standard amino-acid alphabet,
with a leading methionine and lengths 72, 81, 90. DNA uses the lexically first
standard-code synonym; table weights are synonym rank / sum of ranks.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import random

from Bio.Data import CodonTable
import yaml


def generate(out_dir, seed=1729):
    out = Path(out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    code = CodonTable.unambiguous_dna_by_name["Standard"]
    synonyms = {}
    for codon, aa in sorted(code.forward_table.items()):
        synonyms.setdefault(aa, []).append(codon)
    synonyms["*"] = sorted(code.stop_codons)
    table = {aa: {codon: (i + 1) / sum(range(1, len(codons) + 1))
                  for i, codon in enumerate(codons)} for aa, codons in sorted(synonyms.items())}
    rng = random.Random(seed)
    alphabet = sorted(set(code.forward_table.values()))
    proteins = [(f"synthetic_{i + 1}", "M" + "".join(rng.choice(alphabet) for _ in range(n - 1)))
                for i, n in enumerate((72, 81, 90))]
    dna = [(name, "".join(synonyms[aa][0] for aa in seq) + "TAA") for name, seq in proteins]
    for filename, records in (("protein.faa", proteins), ("dna.fna", dna)):
        (out / filename).write_text("".join(f">{name}\n{seq}\n" for name, seq in records))
    for filename, delimiter in (("protein.csv", ","), ("protein.tsv", "\t")):
        with (out / filename).open("w", newline="") as f:
            writer = csv.writer(f, delimiter=delimiter)
            writer.writerow(["id", "sequence"])
            writer.writerows(proteins)
    (out / "synthetic-codons.json").write_text(json.dumps(table, indent=2) + "\n")
    config = dict(species=str(out / "synthetic-codons.json"), input_type="auto", stop_codon="TAA",
                  max_random_iters=50000, constraints=[dict(type="EnforceTranslation")],
                  objectives=[dict(type="CodonOptimize", method="use_best_codon")])
    (out / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=False))
    provenance = dict(seed=seed, source="No biological source; algorithmically generated synthetic fixtures",
                      algorithm="Python random.Random.choice; sorted standard amino-acid alphabet; leading M; lengths 72/81/90",
                      dna="Lexically first standard-code synonym plus TAA",
                      table="All 64 standard-code codons; positive synonym-rank weights normalized per amino acid; not an organism model",
                      hashes={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())
                              if p.is_file() and p.name != "PROVENANCE.json"})
    (out / "PROVENANCE.json").write_text(json.dumps(provenance, indent=2) + "\n")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--seed", type=int, default=1729)
    args = parser.parse_args()
    generate(args.out_dir, args.seed)
