# Fix: multiprocessing output writing

## Problem

When running with `--threads > 1`, no output files (FASTA or TSV) were written.

## Root cause

`cli.py` passed the full `OptConfig` object — which contains instantiated DnaChisel
spec objects (`AvoidPattern`, `CodonOptimize`, etc.) — as part of every task tuple
sent to `multiprocessing.Pool.map()`. `pool.map` pickles all arguments to send them
to worker processes. These complex DnaChisel objects can fail the pickle round-trip,
crashing the process before any output is written.

## Changes

### 1. Avoid pickling DnaChisel objects (`cli.py`)

Each worker now receives only the config file **path** (a plain string) via
`Pool(initializer=_init_worker, initargs=(config_path,))` and calls `load_config()`
once to build its own spec objects. The task queue carries only `(name, seq)` string
tuples.

### 2. Stream results to disk (`cli.py`, `io.py`)

Replaced `pool.map` (buffers all results in memory before returning) with `pool.imap`
(yields each result as it finishes). Each record is written and flushed immediately.
This reduces peak memory, saves partial output if the process dies mid-run, and prints
per-sequence progress to stderr.

Output order matches input order (`pool.imap` preserves ordering).
