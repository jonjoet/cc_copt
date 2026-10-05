"""Focused offline engine/I/O checks using the one documented generator."""
import random

from Bio.Seq import Seq
import numpy as np
import pytest
from cc_copt.config import load_config, build_spec
from cc_copt.io import read_input, write_fasta
from cc_copt.optimize import optimize_sequence
from cc_copt.utils import detect_sequence_type, protein_to_dna


def test_sequence_detection(synthetic):
    assert detect_sequence_type(read_input(synthetic / "protein.faa")[0][1]) == "protein"
    assert detect_sequence_type(read_input(synthetic / "dna.fna")[0][1]) == "dna"


@pytest.mark.parametrize("trailing_stop", [False, True])
def test_reverse_translation(synthetic, trailing_stop):
    protein = read_input(synthetic / "protein.faa")[0][1]
    dna = protein_to_dna(protein + ("*" if trailing_stop else ""))
    assert len(dna) == 3 * (len(protein) + 1)
    assert str(Seq(dna).translate()) == protein + "*"


@pytest.mark.parametrize("filename", ["protein.faa", "protein.csv", "protein.tsv"])
def test_input_formats(synthetic, filename):
    assert read_input(synthetic / filename) == read_input(synthetic / "protein.faa")


def test_write_fasta(synthetic):
    records = read_input(synthetic / "protein.faa")
    output = synthetic / "roundtrip.faa"
    write_fasta(records, output)
    assert read_input(output) == records


def test_real_optimization_and_restriction_site(synthetic):
    random.seed(1729)
    np.random.seed(1729)
    cfg = load_config(synthetic / "config.yaml")
    cfg.constraints.append(build_spec(dict(type="AvoidPattern", pattern="BsaI_site"), cfg.species))
    name, protein = read_input(synthetic / "protein.faa")[0]
    result = optimize_sequence(name, protein, cfg)
    assert result.constraints_pass and all(c["passes"] for c in result.constraint_results)
    assert str(Seq(result.optimized_dna_seq).translate()) == protein + "*"
    assert len(result.optimized_dna_seq) == 3 * (len(protein) + 1)
    from dnachisel import DnaOptimizationProblem, AvoidPattern
    assert DnaOptimizationProblem(result.optimized_dna_seq, constraints=[AvoidPattern("BsaI_site")], logger=None).all_constraints_pass()
    assert result.objective_results
