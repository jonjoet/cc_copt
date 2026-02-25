"""Click-based CLI entrypoint for cc_copt."""

import os
import sys
from multiprocessing import Pool
from pathlib import Path

import click

from .config import load_config
from .io import read_input, write_fasta_record
from .optimize import optimize_sequence

# ---------------------------------------------------------------------------
# Multiprocessing helpers
#
# DnaChisel specification objects (AvoidPattern, CodonOptimize, …) stored
# inside OptConfig may not survive a pickle round-trip.  multiprocessing.Pool
# pickles every argument passed through pool.map / pool.imap, so sending the
# full config object to workers can silently fail or raise PicklingErrors.
#
# Fix: each worker re-loads the YAML config (a plain string path) once via an
# initializer, building its own DnaChisel objects locally.  Only simple
# strings are sent through the task queue.
# ---------------------------------------------------------------------------

_worker_config = None


def _init_worker(config_path):
    """Initialise each pool worker with its own loaded config."""
    global _worker_config
    # Suppress verbose stdout/stderr from DnaChisel in worker processes
    sys.stdout = open(os.devnull, "w")
    sys.stderr = open(os.devnull, "w")
    _worker_config = load_config(config_path)


class _Failure:
    """Sentinel returned by a worker when optimisation fails for one sequence."""

    __slots__ = ("name", "error")

    def __init__(self, name, error):
        self.name = name
        self.error = error


def _optimize_one(args):
    """Worker function for multiprocessing. Unpacks (name, seq) tuple."""
    name, seq = args
    try:
        return optimize_sequence(name, seq, _worker_config)
    except Exception as e:
        return _Failure(name, str(e))


# Column order for the optional TSV summary.
_TSV_COLUMNS = (
    "id",
    "original_seq",
    "optimized_seq",
    "constraints_pass",
    "constraints_summary",
    "objectives_summary",
)


def _write_result(r, fasta_fh, tsv_fh):
    """Write a single OptimizationResult to the open FASTA / TSV handles."""
    write_fasta_record(fasta_fh, r.name, r.optimized_seq)
    if tsv_fh is not None:
        vals = (
            r.name,
            r.original_seq,
            r.optimized_seq,
            r.constraints_pass,
            r.constraints_summary,
            r.objectives_summary,
        )
        tsv_fh.write("\t".join(str(v) for v in vals) + "\n")
        tsv_fh.flush()


@click.group()
@click.version_option()
def main():
    """cc_copt - Batch codon optimization using DnaChisel."""


@main.command()
@click.option(
    "-i",
    "--input",
    "input_path",
    required=True,
    type=click.Path(exists=True),
    help="Input FASTA (.fa/.faa/.fasta/.fna) or CSV/TSV file.",
)
@click.option(
    "-c",
    "--config",
    "config_path",
    required=True,
    type=click.Path(exists=True),
    help="YAML configuration file.",
)
@click.option(
    "-o",
    "--output",
    "output_path",
    default=None,
    type=click.Path(),
    help="Output FASTA path (default: stdout).",
)
@click.option(
    "-t",
    "--table",
    "table_path",
    default=None,
    type=click.Path(),
    help="Output TSV summary path.",
)
@click.option(
    "--threads",
    default=1,
    type=int,
    show_default=True,
    help="Number of parallel workers.",
)
def optimize(input_path, config_path, output_path, table_path, threads):
    """Optimize sequences from INPUT using CONFIG."""
    config = load_config(config_path)
    sequences = read_input(input_path)

    if not sequences:
        click.echo("No sequences found in input file.", err=True)
        sys.exit(1)

    n = len(sequences)
    click.echo(f"Optimizing {n} sequence(s)...", err=True)

    # Open output handles up-front so results are flushed to disk
    # as each sequence completes, rather than buffered in memory.
    fasta_fh = open(output_path, "w") if output_path else sys.stdout
    tsv_fh = None
    succeeded = 0
    failed = 0

    try:
        if table_path:
            tsv_fh = open(table_path, "w")
            tsv_fh.write("\t".join(_TSV_COLUMNS) + "\n")
            tsv_fh.flush()

        if threads > 1:
            # imap preserves input order and yields results one at a time,
            # letting us stream each record to disk immediately.
            with Pool(
                threads, initializer=_init_worker, initargs=(config_path,)
            ) as pool:
                for i, r in enumerate(pool.imap(_optimize_one, sequences), 1):
                    if isinstance(r, _Failure):
                        failed += 1
                        click.echo(
                            f"  [{i}/{n}] {r.name} FAILED: {r.error}",
                            err=True,
                        )
                    else:
                        succeeded += 1
                        _write_result(r, fasta_fh, tsv_fh)
                        click.echo(f"  [{i}/{n}] {r.name}", err=True)
        else:
            for i, (name, seq) in enumerate(sequences, 1):
                try:
                    r = optimize_sequence(name, seq, config)
                except Exception as e:
                    failed += 1
                    click.echo(
                        f"  [{i}/{n}] {name} FAILED: {e}", err=True
                    )
                    continue
                succeeded += 1
                _write_result(r, fasta_fh, tsv_fh)
                click.echo(f"  [{i}/{n}] {r.name}", err=True)
    finally:
        if fasta_fh is not sys.stdout:
            fasta_fh.close()
        if tsv_fh:
            tsv_fh.close()

    click.echo(f"Done. {succeeded} succeeded, {failed} failed.", err=True)
    if failed:
        sys.exit(1)
