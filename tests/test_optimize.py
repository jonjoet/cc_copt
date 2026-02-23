"""Basic tests for cc_copt optimization pipeline."""

import tempfile
from pathlib import Path

import pytest

from cc_copt.config import load_config
from cc_copt.io import read_input, write_fasta
from cc_copt.optimize import optimize_sequence
from cc_copt.utils import detect_sequence_type, protein_to_dna

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


def test_detect_protein():
    assert detect_sequence_type("MSKGEELFTGVV") == "protein"


def test_detect_dna():
    assert detect_sequence_type("ATGCGATCGATCG") == "dna"


def test_protein_to_dna_length():
    protein = "MSKGEEL"
    dna = protein_to_dna(protein, stop_codon="TAA")
    # 7 amino acids * 3 + 3 (stop codon) = 24
    assert len(dna) == 24
    assert dna.endswith("TAA")


def test_protein_to_dna_strips_stop():
    dna1 = protein_to_dna("MSKGEEL*", stop_codon="TAA")
    dna2 = protein_to_dna("MSKGEEL", stop_codon="TAA")
    assert len(dna1) == len(dna2)


def test_load_config():
    config = load_config(EXAMPLES_DIR / "config.yaml")
    assert config.species == 196627
    assert config.input_type == "auto"
    assert len(config.constraints) > 0
    assert len(config.objectives) > 0


def test_read_fasta():
    records = read_input(EXAMPLES_DIR / "example.faa")
    assert len(records) == 3
    assert records[0][0] == "GFP"


def test_optimize_short_protein():
    """Round-trip test: optimize a short protein sequence."""
    config = load_config(EXAMPLES_DIR / "config.yaml")
    result = optimize_sequence("test", "MSKGEELFTGVV", config)
    assert result.name == "test"
    assert len(result.optimized_seq) > 0
    # Optimized DNA should be 3x protein length + stop codon
    assert len(result.optimized_seq) == (12 * 3 + 3)
    assert result.constraints_pass


def test_write_fasta_roundtrip():
    """Write FASTA and read it back."""
    records = [("seq1", "ATGCGATCG"), ("seq2", "ATGAAACCC")]
    with tempfile.NamedTemporaryFile(suffix=".fna", mode="w", delete=False) as f:
        path = f.name
    write_fasta(records, path)
    read_back = read_input(path)
    assert len(read_back) == 2
    assert read_back[0][1] == "ATGCGATCG"
    Path(path).unlink()
