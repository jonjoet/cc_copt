"""Core optimization logic wrapping DnaChisel."""

from dataclasses import dataclass, field

import dnachisel
from dnachisel import DnaOptimizationProblem, EnforceTranslation

from .config import OptConfig
from .utils import detect_sequence_type, protein_to_dna, translate_dna


@dataclass
class OptimizationResult:
    """Result of optimizing a single sequence."""

    name: str
    protein_seq: str
    input_dna_seq: str | None
    optimized_dna_seq: str
    constraints_pass: bool
    constraint_results: list[dict] = field(default_factory=list)
    objective_results: list[dict] = field(default_factory=list)


def optimize_sequence(name: str, sequence: str, config: OptConfig) -> OptimizationResult:
    """Optimize a single sequence given parsed config.

    Args:
        name: Sequence identifier.
        sequence: Input sequence (protein or DNA).
        config: Parsed optimization config.

    Returns:
        OptimizationResult with optimized sequence and structured results.
    """
    # Determine sequence type
    if config.input_type == "auto":
        seq_type = detect_sequence_type(sequence)
    else:
        seq_type = config.input_type

    # Reverse-translate protein to DNA
    if seq_type == "protein":
        protein_seq = sequence.rstrip("*")
        input_dna_seq = None
        dna_seq = protein_to_dna(sequence, config.stop_codon)
    else:
        input_dna_seq = sequence
        dna_seq = sequence
        protein_seq = translate_dna(sequence)

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

    # Build structured constraint results
    constraint_results = [
        {"label": str(ev.specification), "passes": ev.passes}
        for ev in problem.constraints_evaluations()
    ]

    # Build structured objective results
    objective_results = [
        {"label": str(ev.specification), "score": ev.score}
        for ev in problem.objectives_evaluations()
    ]

    return OptimizationResult(
        name=name,
        protein_seq=protein_seq,
        input_dna_seq=input_dna_seq,
        optimized_dna_seq=problem.sequence,
        constraints_pass=problem.all_constraints_pass(),
        constraint_results=constraint_results,
        objective_results=objective_results,
    )
