"""Sequence type detection and reverse translation helpers."""

import re

from Bio.Seq import Seq
from dnachisel.biotools import reverse_translate


def detect_sequence_type(sequence: str) -> str:
    """Detect whether a sequence is protein or DNA.

    Args:
        sequence: Input sequence string.

    Returns:
        "protein" or "dna".
    """
    seq_upper = sequence.upper().replace("*", "")
    # DNA uses only A, T, G, C, N (and IUPAC ambiguity codes)
    dna_chars = set("ATGCNRYSWKMBDHV")
    non_dna = set(seq_upper) - dna_chars
    # If sequence contains amino-acid-only letters, it's protein
    if non_dna:
        return "protein"
    # Short sequences that are all DNA chars are ambiguous,
    # but default to DNA since that's valid
    return "dna"


def protein_to_dna(protein_seq: str, stop_codon: str = "TAA") -> str:
    """Reverse-translate a protein sequence to a DNA sequence.

    Uses DnaChisel's reverse_translate (random codon assignment).
    Appends a stop codon.

    Args:
        protein_seq: Amino acid sequence (may end with '*').
        stop_codon: Stop codon to append (default TAA).

    Returns:
        DNA sequence string.
    """
    # Strip trailing stop symbol if present
    clean = protein_seq.rstrip("*")
    dna = reverse_translate(clean)
    return dna + stop_codon


def translate_dna(dna_seq: str) -> str:
    """Translate a DNA sequence to protein (without stop character).

    Args:
        dna_seq: DNA sequence string.

    Returns:
        Protein sequence string (trailing '*' stripped).
    """
    return str(Seq(dna_seq).translate()).rstrip("*")
