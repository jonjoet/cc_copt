"""Pure GUI boundary and installed-library default/constructor contract."""
from copy import deepcopy
import inspect
import json
from pathlib import Path

import dnachisel
import pytest
import yaml
from cc_copt.config import build_spec, resolve_species
from cc_copt.gui_config import GuiConfigError, parse_gui_config, normalize_gui_config, export_gui_config
from cc_copt.io import read_input
from cc_copt.spec_registry import SPEC_REGISTRY


@pytest.mark.parametrize("content", ["[", "a: [", "scalar", "[]", "null", "42", "!!python/object:os.system {}"])
def test_bad_yaml(content):
    with pytest.raises(GuiConfigError, match="Nothing was applied"):
        parse_gui_config(content)


@pytest.mark.parametrize("raw", [
    {"unknown": "private-value"}, {"species": {}}, {"species": True},
    {"input_type": "other"}, {"stop_codon": None}, {"max_random_iters": 99},
    {"max_random_iters": True}, {"max_random_iters": 100.0}, {"max_random_iters": 2**60},
    {"constraints": None}, {"constraints": {}}, {"objectives": ["CodonOptimize"]},
    {"constraints": [{}]}, {"constraints": [{"type": "CodonOptimize"}]},
    {"objectives": [{"type": "AvoidPattern", "pattern": "BsaI_site"}]},
    {"constraints": [{"type": "AvoidPattern"}]},
    {"constraints": [{"type": "EnforceTranslation", "location": [0, 3]}]},
    {"objectives": [{"type": "MaximizeCAI"}]},
    {"objectives": [{"type": "MatchTargetCodonUsage"}]},
    {"objectives": [{"type": "CodonOptimize", "method": "harmonize_rca"}]},
    {"constraints": [{"type": "EnforceGCContent", "mini": None}]},
    {"constraints": [{"type": "EnforceGCContent", "mini": True}]},
    {"constraints": [{"type": "EnforceGCContent", "target": float("nan")}]},
    {"constraints": [{"type": "EnforceGCContent", "target": float("inf")}]},
    {"constraints": [{"type": "EnforceGCContent", "target": 1.01}]},
    {"constraints": [{"type": "EnforceGCContent", "window": 0}]},
    {"constraints": [{"type": "EnforceGCContent", "window": 2.0}]},
    {"constraints": [{"type": "EnforceGCContent", "window": 2**60}]},
])
def test_rejection_is_nonmutating(raw):
    before = deepcopy(raw)
    with pytest.raises(GuiConfigError, match="Nothing was applied") as error:
        normalize_gui_config(raw)
    assert "private-value" not in str(error.value)
    # NaN intentionally isn't self-equal, so compare the serialized structural snapshot.
    assert yaml.safe_dump(raw) == yaml.safe_dump(before)


@pytest.mark.parametrize("species", [None, "", 196627, "196627", "/local/table.json"])
def test_species_and_defaults(species):
    cfg = normalize_gui_config({"species": species})
    exported = yaml.safe_load(export_gui_config(cfg))
    assert cfg["max_random_iters"] == 50000
    if species in (None, ""):
        assert "species" not in exported
    else:
        assert exported["species"] == str(species)
        if str(species).isdigit():
            assert resolve_species(exported["species"]) == int(species)


@pytest.mark.parametrize("target,window", [(None, None), (0, 1), (0.45, 50)])
def test_optional_numbers(target, window):
    cfg = normalize_gui_config({"constraints": [dict(type="EnforceGCContent", target=target, window=window)]})
    spec = yaml.safe_load(export_gui_config(cfg))["constraints"][0]
    assert isinstance(spec["mini"], float)
    if target is None:
        assert "target" not in spec and "window" not in spec
    else:
        assert spec["target"] == target and isinstance(spec["target"], float)
        assert spec["window"] == window and isinstance(spec["window"], int)


def test_shipped_example_is_supported():
    path = Path(__file__).resolve().parents[1] / "examples/config.yaml"
    assert parse_gui_config(path.read_bytes())["constraints"]


CASES = [(name, method) for name, definition in SPEC_REGISTRY.items()
         for method in (next((p.options for p in definition.params if p.name == "method"), [None]))]


def named_state(spec, definition):
    state = {"class": type(spec).__name__}
    for param in definition.params:
        if param.name == "method":
            continue  # factory selection is checked by the resolved class above
        value = getattr(spec, param.name)
        if param.name == "pattern":
            value = {"class": type(value).__name__, "expression": value.expression, "size": value.size}
        state[param.name] = value
    if definition.species_aware:
        state["codon_usage_table"] = spec.codon_usage_table
        state["species"] = spec.species
    return state


@pytest.mark.parametrize("name,method", CASES)
def test_registry_signature_defaults_and_roundtrip(synthetic, name, method):
    definition = SPEC_REGISTRY[name]
    signature = inspect.signature(getattr(dnachisel, name))
    raw = {"type": name}
    for param in definition.params:
        assert param.name in signature.parameters
        actual = signature.parameters[param.name].default
        if not param.required:
            assert param.default == actual, (name, param.name, actual)
        else:
            raw[param.name] = ("BsaI_site" if param.name == "pattern" else
                               read_input(synthetic / "dna.fna")[0][1][:12] if param.name == "sequence" else param.default)
    if method:
        raw["method"] = method
    group = "objectives" if definition.category == "objective" else "constraints"
    table = json.loads((synthetic / "synthetic-codons.json").read_text())
    original = build_spec(raw, table)
    cfg = normalize_gui_config({group: [raw]})
    restored_raw = yaml.safe_load(export_gui_config(cfg))[group][0]
    restored = build_spec(restored_raw, table)
    assert named_state(original, definition) == named_state(restored, definition)
    (synthetic / "registry-contract.json").write_text(json.dumps(dict(
        type=name, method=method, signature=str(signature), deviations=[],
        manual_defaults={p.name: p.default for p in definition.params},
        effective_fields=list(named_state(restored, definition))), indent=2))


def test_omitted_factory_and_translation_defaults(synthetic):
    table = json.loads((synthetic / "synthetic-codons.json").read_text())
    cfg = normalize_gui_config(dict(constraints=[dict(type="EnforceTranslation")],
                                    objectives=[dict(type="CodonOptimize")]))
    assert cfg["objectives"][0]["method"] == "use_best_codon"
    assert "start_codon" not in cfg["constraints"][0]
    assert build_spec(cfg["constraints"][0], table).start_codon is None
    assert type(build_spec(cfg["objectives"][0], table)).__name__ == "MaximizeCAI"
