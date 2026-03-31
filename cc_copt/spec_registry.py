"""Declarative parameter registry for DNAChisel specifications.

Maps each specification type to its user-facing parameters, types, defaults,
and help text.  Used by the Streamlit GUI to dynamically render constraint
and objective forms.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ParamDef:
    """Definition of a single parameter for a DNAChisel specification."""

    name: str
    label: str
    type: str  # "str", "int", "float", "bool", "select"
    default: Any = None
    required: bool = False
    help: str = ""
    options: list[str] = field(default_factory=list)  # for "select" type
    min_value: float | None = None
    max_value: float | None = None


@dataclass
class SpecDef:
    """Definition of a DNAChisel specification type."""

    type_name: str
    label: str
    category: str  # "constraint", "objective", or "both"
    params: list[ParamDef] = field(default_factory=list)
    species_aware: bool = False
    help: str = ""


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

SPEC_REGISTRY: dict[str, SpecDef] = {
    # -- Constraints --------------------------------------------------------
    "AvoidPattern": SpecDef(
        type_name="AvoidPattern",
        label="Avoid Pattern",
        category="constraint",
        help="Ensure a DNA pattern or restriction site is absent.",
        params=[
            ParamDef(
                "pattern",
                "Pattern",
                "str",
                required=True,
                help=(
                    "Pattern to avoid. Use built-in names like BsaI_site, "
                    "BsmBI_site, EcoRI_site, etc., or a raw DNA motif."
                ),
            ),
        ],
    ),
    "EnforceGCContent": SpecDef(
        type_name="EnforceGCContent",
        label="Enforce GC Content",
        category="both",
        help="Constrain or target GC content globally or in sliding windows.",
        params=[
            ParamDef("mini", "Min GC", "float", default=0.0, min_value=0.0, max_value=1.0,
                     help="Minimum GC proportion (0-1)."),
            ParamDef("maxi", "Max GC", "float", default=1.0, min_value=0.0, max_value=1.0,
                     help="Maximum GC proportion (0-1)."),
            ParamDef("target", "Target GC", "float", default=None, min_value=0.0, max_value=1.0,
                     help="Desired GC proportion (objective mode). Leave empty for constraint mode."),
            ParamDef("window", "Window size", "int", default=None, min_value=1,
                     help="Sliding window size in bp. Leave empty for global."),
        ],
    ),
    "EnforceTranslation": SpecDef(
        type_name="EnforceTranslation",
        label="Enforce Translation",
        category="constraint",
        help="Preserve the amino-acid translation of the sequence.",
        params=[
            ParamDef("genetic_table", "Genetic table", "str", default="Standard",
                     help="Translation table name (e.g. Standard, Bacterial)."),
            ParamDef("start_codon", "Start codon", "str", default="keep",
                     help="'keep' preserves original, or specify e.g. ATG."),
        ],
    ),
    "AvoidRareCodons": SpecDef(
        type_name="AvoidRareCodons",
        label="Avoid Rare Codons",
        category="constraint",
        species_aware=True,
        help="Avoid codons below a minimum usage frequency.",
        params=[
            ParamDef("min_frequency", "Min frequency", "float", default=0.1,
                     required=True, min_value=0.0, max_value=1.0,
                     help="Minimum acceptable codon frequency (0-1)."),
        ],
    ),
    "AvoidHairpins": SpecDef(
        type_name="AvoidHairpins",
        label="Avoid Hairpins",
        category="constraint",
        help="Eliminate hairpin secondary structures.",
        params=[
            ParamDef("stem_size", "Stem size", "int", default=20, min_value=1,
                     help="Length of hairpin stem to detect."),
            ParamDef("hairpin_window", "Hairpin window", "int", default=200, min_value=1,
                     help="Window to search for reverse complement."),
        ],
    ),
    "AvoidStopCodons": SpecDef(
        type_name="AvoidStopCodons",
        label="Avoid Stop Codons",
        category="constraint",
        help="Prevent introducing new in-frame stop codons.",
        params=[
            ParamDef("genetic_table", "Genetic table", "str", default="Standard",
                     help="Translation table name."),
        ],
    ),
    "EnforceSequence": SpecDef(
        type_name="EnforceSequence",
        label="Enforce Sequence",
        category="constraint",
        help="Enforce a specific (possibly degenerate) sequence at a location.",
        params=[
            ParamDef("sequence", "Sequence", "str", required=True,
                     help="ATGC sequence, may include IUPAC degeneracy codes."),
        ],
    ),
    "AvoidChanges": SpecDef(
        type_name="AvoidChanges",
        label="Avoid Changes",
        category="constraint",
        help="Prevent modifications to specified regions.",
        params=[
            ParamDef("max_edits", "Max edits", "int", default=0, min_value=0,
                     help="Maximum allowed nucleotide changes."),
            ParamDef("max_edits_percent", "Max edits %", "float", default=None,
                     min_value=0.0, max_value=100.0,
                     help="Maximum edits as percentage of length."),
        ],
    ),
    "EnforceTerminalGCContent": SpecDef(
        type_name="EnforceTerminalGCContent",
        label="Enforce Terminal GC Content",
        category="constraint",
        help="Control GC content at sequence terminals.",
        params=[
            ParamDef("window_size", "Window size", "int", default=50,
                     required=True, min_value=1,
                     help="Size of terminal ends to evaluate."),
            ParamDef("mini", "Min GC", "float", default=0.0, min_value=0.0, max_value=1.0,
                     help="Minimum GC proportion."),
            ParamDef("maxi", "Max GC", "float", default=1.0, min_value=0.0, max_value=1.0,
                     help="Maximum GC proportion."),
        ],
    ),
    "SequenceLengthBounds": SpecDef(
        type_name="SequenceLengthBounds",
        label="Sequence Length Bounds",
        category="constraint",
        help="Enforce minimum and/or maximum sequence length.",
        params=[
            ParamDef("min_length", "Min length", "int", default=0, min_value=0,
                     help="Minimum length in nucleotides."),
            ParamDef("max_length", "Max length", "int", default=None, min_value=0,
                     help="Maximum length (leave empty for no limit)."),
        ],
    ),
    # -- Objectives ---------------------------------------------------------
    "CodonOptimize": SpecDef(
        type_name="CodonOptimize",
        label="Codon Optimize",
        category="objective",
        species_aware=True,
        help="Optimize codon usage for a target organism.",
        params=[
            ParamDef("method", "Method", "select", default="match_codon_usage",
                     options=["match_codon_usage", "use_best_codon", "harmonize_rca"],
                     help="Optimization strategy."),
        ],
    ),
    "MaximizeCAI": SpecDef(
        type_name="MaximizeCAI",
        label="Maximize CAI",
        category="objective",
        species_aware=True,
        help="Maximize Codon Adaptation Index for a target organism.",
        params=[],
    ),
    "MatchTargetCodonUsage": SpecDef(
        type_name="MatchTargetCodonUsage",
        label="Match Target Codon Usage",
        category="objective",
        species_aware=True,
        help="Match the codon usage profile of the target organism.",
        params=[],
    ),
    "UniquifyAllKmers": SpecDef(
        type_name="UniquifyAllKmers",
        label="Uniquify All K-mers",
        category="objective",
        help="Make all sub-sequences of length k unique.",
        params=[
            ParamDef("k", "K-mer size", "int", default=8, required=True, min_value=2,
                     help="Length of k-mers to uniquify."),
        ],
    ),
    "EnforceChanges": SpecDef(
        type_name="EnforceChanges",
        label="Enforce Changes",
        category="objective",
        help="Enforce or optimize nucleotide changes in a region.",
        params=[
            ParamDef("amount", "Target changes", "int", default=None, min_value=0,
                     help="Target number of nucleotide differences."),
            ParamDef("minimum", "Minimum changes", "int", default=None, min_value=0,
                     help="Required minimum number of differences."),
        ],
    ),
    "EnforcePatternOccurence": SpecDef(
        type_name="EnforcePatternOccurence",
        label="Enforce Pattern Occurrence",
        category="objective",
        help="Ensure a pattern occurs a specific number of times.",
        params=[
            ParamDef("pattern", "Pattern", "str", required=True,
                     help="DNA pattern or restriction site name."),
            ParamDef("occurences", "Occurrences", "int", default=1, min_value=0,
                     help="Desired number of occurrences."),
        ],
    ),
}


def get_constraint_specs() -> list[SpecDef]:
    """Return spec definitions usable as constraints."""
    return [s for s in SPEC_REGISTRY.values() if s.category in ("constraint", "both")]


def get_objective_specs() -> list[SpecDef]:
    """Return spec definitions usable as objectives."""
    return [s for s in SPEC_REGISTRY.values() if s.category in ("objective", "both")]


def spec_dict_from_form(type_name: str, form_values: dict) -> dict:
    """Convert GUI form values into a spec dict for build_spec().

    Strips None and empty-string values so only explicitly set parameters
    are passed to the DNAChisel constructor.
    """
    result = {"type": type_name}
    for key, value in form_values.items():
        if value is None or value == "":
            continue
        result[key] = value
    return result
