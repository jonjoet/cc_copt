"""FASTA and CSV/TSV reading and writing."""

import re
import sys
from pathlib import Path
from typing import TextIO

import pandas as pd
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord


def _detect_columns(df: pd.DataFrame) -> tuple[str, str]:
    """Auto-detect ID and sequence columns from a DataFrame.

    Looks for columns matching common name patterns (case-insensitive).

    Returns:
        Tuple of (id_column, seq_column) names.
    """
    id_patterns = re.compile(r"^(id|name|accession|gene|locus)$", re.IGNORECASE)
    seq_patterns = re.compile(
        r"^(seq|sequence|protein|dna|aa|nucleotide|orf)$", re.IGNORECASE
    )

    id_col = None
    seq_col = None
    for col in df.columns:
        if id_patterns.match(col) and id_col is None:
            id_col = col
        if seq_patterns.match(col) and seq_col is None:
            seq_col = col

    if id_col is None:
        raise ValueError(
            f"Could not detect ID column. Columns: {list(df.columns)}. "
            "Expected a column matching: id, name, accession, gene, locus"
        )
    if seq_col is None:
        raise ValueError(
            f"Could not detect sequence column. Columns: {list(df.columns)}. "
            "Expected a column matching: seq, sequence, protein, dna, aa, nucleotide, orf"
        )
    return id_col, seq_col


def read_input(path: str | Path) -> list[tuple[str, str]]:
    """Read sequences from a FASTA, CSV, or TSV file.

    Args:
        path: Input file path.

    Returns:
        List of (id, sequence) tuples.
    """
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix in (".fa", ".faa", ".fasta", ".fna"):
        records = []
        for rec in SeqIO.parse(str(path), "fasta"):
            records.append((rec.id, str(rec.seq)))
        return records

    if suffix == ".csv":
        df = pd.read_csv(path)
    elif suffix == ".tsv":
        df = pd.read_csv(path, sep="\t")
    else:
        raise ValueError(f"Unsupported file format: {suffix}")

    id_col, seq_col = _detect_columns(df)
    return list(zip(df[id_col].astype(str), df[seq_col].astype(str)))


def write_fasta(records: list[tuple[str, str]], output: str | Path | None):
    """Write sequences as FASTA.

    Args:
        records: List of (id, sequence) tuples.
        output: Output file path, or None for stdout.
    """
    seq_records = [
        SeqRecord(Seq(seq), id=name, description="")
        for name, seq in records
    ]

    if output is None:
        SeqIO.write(seq_records, sys.stdout, "fasta")
    else:
        SeqIO.write(seq_records, str(output), "fasta")


def write_tsv(rows: list[dict], output: str | Path):
    """Write summary TSV.

    Args:
        rows: List of dicts with summary data.
        output: Output file path.
    """
    df = pd.DataFrame(rows)
    df.to_csv(output, sep="\t", index=False)
