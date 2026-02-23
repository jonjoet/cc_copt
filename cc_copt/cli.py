"""Click-based CLI entrypoint for cc_copt."""

import sys
from multiprocessing import Pool
from pathlib import Path

import click

from .config import load_config
from .io import read_input, write_fasta, write_tsv
from .optimize import optimize_sequence


def _optimize_one(args):
    """Worker function for multiprocessing. Unpacks args tuple."""
    name, seq, config = args
    return optimize_sequence(name, seq, config)


@click.group()
@click.version_option()
def main():
    """cc_copt - Batch codon optimization using DnaChisel."""


@main.command()
@click.option("-i", "--input", "input_path", required=True, type=click.Path(exists=True),
              help="Input FASTA (.fa/.faa/.fasta/.fna) or CSV/TSV file.")
@click.option("-c", "--config", "config_path", required=True, type=click.Path(exists=True),
              help="YAML configuration file.")
@click.option("-o", "--output", "output_path", default=None, type=click.Path(),
              help="Output FASTA path (default: stdout).")
@click.option("-t", "--table", "table_path", default=None, type=click.Path(),
              help="Output TSV summary path.")
@click.option("--threads", default=1, type=int, show_default=True,
              help="Number of parallel workers.")
def optimize(input_path, config_path, output_path, table_path, threads):
    """Optimize sequences from INPUT using CONFIG."""
    config = load_config(config_path)
    sequences = read_input(input_path)

    if not sequences:
        click.echo("No sequences found in input file.", err=True)
        sys.exit(1)

    click.echo(f"Optimizing {len(sequences)} sequence(s)...", err=True)

    if threads > 1:
        args_list = [(name, seq, config) for name, seq in sequences]
        with Pool(threads) as pool:
            results = pool.map(_optimize_one, args_list)
    else:
        results = [optimize_sequence(name, seq, config) for name, seq in sequences]

    # Write output FASTA
    fasta_records = [(r.name, r.optimized_seq) for r in results]
    write_fasta(fasta_records, output_path)

    # Write optional TSV summary
    if table_path:
        rows = [
            {
                "id": r.name,
                "original_seq": r.original_seq,
                "optimized_seq": r.optimized_seq,
                "constraints_pass": r.constraints_pass,
                "constraints_summary": r.constraints_summary,
                "objectives_summary": r.objectives_summary,
            }
            for r in results
        ]
        write_tsv(rows, table_path)

    click.echo("Done.", err=True)
