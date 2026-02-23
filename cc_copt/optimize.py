"""Core optimization logic wrapping DnaChisel."""

from dataclasses import dataclass

import dnachisel
from dnachisel import DnaOptimizationProblem, EnforceTranslation

from .config import OptConfig
from .utils import detect_sequence_type, protein_to_dna


@dataclass
class OptimizationResult:
    """Result of optimizing a single sequence."""

    name: str
    original_seq: str
    optimized_seq: str
    constraints_pass: bool
    constraints_summary: str
    objectives_summary: str


def optimize_sequence(name: str, sequence: str, config: OptConfig) -> OptimizationResult:
    """Optimize a single sequence given parsed config.

    Args:
        name: Sequence identifier.
        sequence: Input sequence (protein or DNA).
        config: Parsed optimization config.

    Returns:
        OptimizationResult with optimized sequence and summaries.
    """
    # Determine sequence type
    if config.input_type == "auto":
        seq_type = detect_sequence_type(sequence)
    else:
        seq_type = config.input_type

    # Reverse-translate protein to DNA
    original_protein = None
    if seq_type == "protein":
        original_protein = sequence.rstrip("*")
        dna_seq = protein_to_dna(sequence, config.stop_codon)
    else:
        dna_seq = sequence

    # Copy constraints and ensure EnforceTranslation is present
    constraints = list(config.constraints)
    has_enforce_translation = any(
        isinstance(c, EnforceTranslation) for c in constraints
    )
    if not has_enforce_translation:
        constraints.append(EnforceTranslation(start_codon="keep"))

    objectives = list(config.objectives)

    # Build and solve the optimization problem
    problem = DnaOptimizationProblem(
        sequence=dna_seq,
        constraints=constraints,
        objectives=objectives,
    )
    problem.max_random_iters = config.max_random_iters
    problem.resolve_constraints()
    problem.optimize()

    return OptimizationResult(
        name=name,
        original_seq=sequence,
        optimized_seq=problem.sequence,
        constraints_pass=problem.all_constraints_pass(),
        constraints_summary=problem.constraints_text_summary(),
        objectives_summary=problem.objectives_text_summary(),
    )
