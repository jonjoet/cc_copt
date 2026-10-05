"""Installed CLI semantics and the offline documentation output checker."""
import argparse
import csv
import math
from pathlib import Path
import subprocess

from Bio.Seq import Seq
from Bio.Data import CodonTable
import pytest
import yaml
from cc_copt.io import read_input


def check_outputs(protein_file, fasta, summary, *, input_dna=None):
    expected = read_input(protein_file)
    actual = read_input(fasta)
    assert [n for n, _ in actual] == [n for n, _ in expected]
    with Path(summary).open() as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    assert [r["id"] for r in rows] == [n for n, _ in expected]
    assert len(rows) == len(actual) == len(expected)
    for (name, protein), (_, dna), row in zip(expected, actual, rows):
        assert str(Seq(dna).translate()) == protein + "*"
        assert len(dna) == 3 * (len(protein) + 1)
        assert dna[-3:] in CodonTable.unambiguous_dna_by_name["Standard"].stop_codons
        assert row["optimized_dna_seq"] == dna
        assert row["protein_seq"] == protein
        assert row["input_dna_seq"] == (dict(input_dna)[name] if input_dna else "")
        assert row["all_constraints_pass"] == "True"
        constraints = [v for k, v in row.items() if k.startswith("constraint:")]
        scores = [v for k, v in row.items() if k.startswith("objective:")]
        assert constraints and all(v == "PASS" for v in constraints)
        assert scores and all(math.isfinite(float(v)) for v in scores)


def run_cli(directory, input_file, config_file=None, threads=1, prefix="optimized"):
    directory = Path(directory)
    fasta, summary = directory / (prefix + ".fna"), directory / (prefix + ".tsv")
    result = subprocess.run(["cc_copt", "optimize", "-i", str(input_file),
                             "-c", str(config_file or directory / "config.yaml"),
                             "-o", str(fasta), "-t", str(summary), "--threads", str(threads)],
                            text=True, capture_output=True, timeout=90)
    (directory / (prefix + ".stdout.log")).write_text(result.stdout)
    (directory / (prefix + ".stderr.log")).write_text(result.stderr)
    assert result.returncode == 0, result.stderr
    return fasta, summary


@pytest.mark.parametrize("threads", [1, 2])
def test_protein_cli(synthetic, threads):
    fasta, summary = run_cli(synthetic, synthetic / "protein.faa", threads=threads)
    check_outputs(synthetic / "protein.faa", fasta, summary)


def test_dna_cli(synthetic):
    fasta, summary = run_cli(synthetic, synthetic / "dna.fna")
    check_outputs(synthetic / "protein.faa", fasta, summary, input_dna=read_input(synthetic / "dna.fna"))


def test_mixed_failure(synthetic):
    good = read_input(synthetic / "protein.faa")[0]
    bad = synthetic / "mixed.faa"
    bad.write_text(f">{good[0]}\n{good[1]}\n>invalid_synthetic\n!\n")
    cfg = yaml.safe_load((synthetic / "config.yaml").read_text())
    cfg["input_type"] = "protein"
    config = synthetic / "mixed.yaml"
    config.write_text(yaml.safe_dump(cfg))
    fasta, summary = synthetic / "mixed.fna", synthetic / "mixed.tsv"
    result = subprocess.run(["cc_copt", "optimize", "-i", str(bad), "-c", str(config),
                             "-o", str(fasta), "-t", str(summary), "--threads", "2"],
                            text=True, capture_output=True, timeout=90)
    (synthetic / "mixed.stderr.log").write_text(result.stderr)
    assert result.returncode != 0 and "1 succeeded, 1 failed" in result.stderr
    expected = synthetic / "valid.faa"
    expected.write_text(f">{good[0]}\n{good[1]}\n")
    check_outputs(expected, fasta, summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-example", required=True, type=Path)
    directory = parser.parse_args().check_example
    check_outputs(directory / "protein.faa", directory / "optimized.fna", directory / "summary.tsv")
    print("Offline example semantic checks passed")
