"""YAML config parsing and validation for codon optimization."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import dnachisel
import yaml


@dataclass
class OptConfig:
    """Parsed optimization configuration."""

    species: Any = None  # TaxID (int), name (str), or codon table dict
    input_type: str = "auto"  # "protein", "dna", or "auto"
    stop_codon: str = "TAA"
    max_random_iters: int = 50000
    constraints: list = field(default_factory=list)
    objectives: list = field(default_factory=list)


# DnaChisel spec classes that accept a 'species' parameter
_SPECIES_AWARE = {"AvoidRareCodons", "CodonOptimize"}


def _resolve_species(raw_species):
    """Resolve species value: int TaxID, string name, or JSON file path."""
    if raw_species is None:
        return None
    if isinstance(raw_species, int):
        return raw_species
    if isinstance(raw_species, str):
        if raw_species.endswith(".json"):
            with open(raw_species) as f:
                return json.load(f)
        # Try int conversion for string TaxIDs like "196627"
        try:
            return int(raw_species)
        except ValueError:
            return raw_species
    return raw_species


def _build_spec(spec_dict: dict, species, module=dnachisel):
    """Build a DnaChisel specification object from a config dict entry.

    Args:
        spec_dict: Dict with 'type' key and kwargs.
        species: Top-level species value to inject if needed.
        module: Module to look up class names from.

    Returns:
        Instantiated DnaChisel specification object.
    """
    spec_dict = dict(spec_dict)  # copy to avoid mutation
    type_name = spec_dict.pop("type")

    cls = getattr(module, type_name, None)
    if cls is None:
        raise ValueError(f"Unknown DnaChisel specification: {type_name}")

    # Inject species for specs that need it, unless already provided
    if type_name in _SPECIES_AWARE and "species" not in spec_dict and species is not None:
        # If species is a dict (custom table), pass as codon_usage_table
        if isinstance(species, dict):
            spec_dict["codon_usage_table"] = species
        else:
            spec_dict["species"] = species

    return cls(**spec_dict)


def load_config(config_path: str | Path) -> OptConfig:
    """Load and validate a YAML config file.

    Args:
        config_path: Path to YAML config file.

    Returns:
        Parsed OptConfig dataclass.
    """
    with open(config_path) as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ValueError("Config file must be a YAML mapping")

    species = _resolve_species(raw.get("species"))
    input_type = raw.get("input_type", "auto")
    stop_codon = raw.get("stop_codon", "TAA")
    max_random_iters = raw.get("max_random_iters", 50000)

    constraints = [
        _build_spec(c, species) for c in raw.get("constraints", [])
    ]
    objectives = [
        _build_spec(o, species) for o in raw.get("objectives", [])
    ]

    return OptConfig(
        species=species,
        input_type=input_type,
        stop_codon=stop_codon,
        max_random_iters=max_random_iters,
        constraints=constraints,
        objectives=objectives,
    )
