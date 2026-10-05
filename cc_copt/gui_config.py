"""Pure, conservative YAML boundary for the curated GUI editor.

CLI acceptance is unchanged. Normalize in temporary data before any live state
is updated; error messages name structural paths, never uploaded values.
"""
from copy import deepcopy
import inspect
import math

import dnachisel
import yaml

from cc_copt.spec_registry import SPEC_REGISTRY, spec_dict_from_form

GLOBALS = dict(species="", input_type="auto", stop_codon="TAA", max_random_iters=50000)
UNSUPPORTED = ("This configuration uses settings the GUI cannot edit. Nothing was applied. "
               "Use the CLI, or adjust the unsupported settings.")


class GuiConfigError(ValueError):
    pass


def _reject(path):
    raise GuiConfigError(f"{UNSUPPORTED} Field: {path}.")


def _value(param, value, path):
    if value is None:
        if param.required:
            _reject(path)
        return None
    if param.type in ("int", "float"):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            _reject(path)
        if param.type == "int" and not isinstance(value, int):
            _reject(path)
        try:
            finite = math.isfinite(value)
        except OverflowError:
            finite = False
        if not finite or (param.type == "int" and abs(value) > 2**53 - 1):
            _reject(path)
        if param.min_value is not None and value < param.min_value:
            _reject(path)
        if param.max_value is not None and value > param.max_value:
            _reject(path)
        return int(value) if param.type == "int" else float(value)
    if param.type in ("str", "select"):
        if not isinstance(value, str) or (param.required and not value):
            _reject(path)
        if param.type == "select" and value not in param.options:
            _reject(path)
        return value
    if param.type == "bool" and isinstance(value, bool):
        return value
    _reject(path)


def normalize_gui_config(raw):
    if not isinstance(raw, dict):
        raise GuiConfigError("Could not read this YAML configuration. Nothing was applied.")
    if any(k not in {*GLOBALS, "constraints", "objectives"} for k in raw):
        _reject("top-level keys")
    result = deepcopy(GLOBALS)
    species = raw.get("species")
    if species is not None and (isinstance(species, bool) or not isinstance(species, (str, int))):
        _reject("species")
    result["species"] = str(species) if species is not None else ""
    for name, options in (("input_type", ("auto", "protein", "dna")), ("stop_codon", ("TAA", "TAG", "TGA"))):
        value = raw.get(name, GLOBALS[name])
        if not isinstance(value, str) or value not in options:
            _reject(name)
        result[name] = value
    iters = raw.get("max_random_iters", GLOBALS["max_random_iters"])
    if isinstance(iters, bool) or not isinstance(iters, int) or iters < 100 or iters > (2**53 - 1):
        _reject("max_random_iters")
    result["max_random_iters"] = iters
    for group, category in (("constraints", "constraint"), ("objectives", "objective")):
        entries = raw.get(group, [])
        if not isinstance(entries, list):
            _reject(group)
        result[group] = []
        for i, entry in enumerate(entries):
            path = f"{group}[{i}]"
            if not isinstance(entry, dict) or not isinstance(entry.get("type"), str):
                _reject(path + ".type")
            name = entry["type"]
            if name not in SPEC_REGISTRY:
                alternatives = {"MatchTargetCodonUsage": "CodonOptimize/match_codon_usage",
                                "MaximizeCAI": "CodonOptimize/use_best_codon"}
                if name in alternatives:
                    raise GuiConfigError(f"{UNSUPPORTED} Field: {path}.type. Supported alternative: {alternatives[name]}.")
                _reject(path + ".type")
            definition = SPEC_REGISTRY[name]
            if definition.category not in (category, "both"):
                _reject(path + ".type")
            if any(k not in {"type", *(p.name for p in definition.params)} for k in entry):
                _reject(path + ".parameters")
            signature = inspect.signature(getattr(dnachisel, name))
            values = {}
            for param in definition.params:
                if param.name in entry:
                    value = entry[param.name]
                    # Null means unset only if the library itself accepts an unset default.
                    if value is None and signature.parameters[param.name].default is not None:
                        _reject(path + "." + param.name)
                else:
                    default = signature.parameters[param.name].default
                    if param.required or default is inspect.Parameter.empty:
                        _reject(path + "." + param.name)
                    value = default
                values[param.name] = _value(param, value, path + "." + param.name)
            result[group].append(spec_dict_from_form(name, values))
    return result


def parse_gui_config(content):
    try:
        raw = yaml.safe_load(content)
    except (yaml.YAMLError, UnicodeError, ValueError):
        raise GuiConfigError("Could not read this YAML configuration. Nothing was applied.") from None
    return normalize_gui_config(raw)


def export_gui_config(state):
    """Serialize the current canonical snapshot, omitting genuinely unset fields."""
    result = {k: deepcopy(state[k]) for k in GLOBALS if k != "species"}
    if state["species"]:
        result["species"] = str(state["species"])
    for group in ("constraints", "objectives"):
        if state[group]:
            result[group] = [spec_dict_from_form(s["type"], {k: v for k, v in s.items() if k != "type"})
                             for s in state[group]]
    return yaml.safe_dump(result, sort_keys=False)
