"""Tests for the Streamlit GUI using AppTest (headless, no browser required)."""

from pathlib import Path
from unittest.mock import MagicMock

import yaml
from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).parent.parent / "cc_copt" / "gui.py")


def _boot_app(**session_state_overrides) -> AppTest:
    """Boot the Streamlit app with optional session-state overrides."""
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    for k, v in session_state_overrides.items():
        at.session_state[k] = v
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


# ------------------------------------------------------------------
# Basic rendering
# ------------------------------------------------------------------


def test_app_boots_without_error():
    """The app renders its initial state without exceptions."""
    at = _boot_app()
    assert at.title[0].value == "cc_copt — Codon Optimizer"


def test_default_session_state():
    """Default session-state values are set on first run."""
    at = _boot_app()
    assert at.session_state["input_type"] == "auto"
    assert at.session_state["stop_codon"] == "TAA"
    assert at.session_state["max_random_iters"] == 50000
    assert at.session_state["constraints"] == []
    assert at.session_state["objectives"] == []


# ------------------------------------------------------------------
# YAML export
# ------------------------------------------------------------------


def test_yaml_export_button_exists():
    """The sidebar has a YAML download button."""
    at = _boot_app()
    sidebar_downloads = at.sidebar.get("download_button")
    labels = [btn.label for btn in sidebar_downloads]
    assert "Download Config as YAML" in labels


def test_build_config_yaml_default():
    """_build_config_yaml produces valid YAML with default state."""
    # Import the helper after setting up a mock session state
    import streamlit as st

    st.session_state["species"] = ""
    st.session_state["input_type"] = "auto"
    st.session_state["stop_codon"] = "TAA"
    st.session_state["max_random_iters"] = 50000
    st.session_state["constraints"] = []
    st.session_state["objectives"] = []

    from cc_copt.gui import _build_config_yaml

    result = yaml.safe_load(_build_config_yaml())
    assert result["input_type"] == "auto"
    assert result["stop_codon"] == "TAA"
    assert result["max_random_iters"] == 50000
    assert "constraints" not in result
    assert "objectives" not in result


def test_build_config_yaml_with_specs():
    """_build_config_yaml includes constraints and objectives when set."""
    import streamlit as st

    constraints = [
        {"type": "AvoidPattern", "pattern": "BsaI_site"},
        {"type": "EnforceGCContent", "mini": 0.4, "maxi": 0.65, "window": 50},
    ]
    objectives = [
        {"type": "CodonOptimize", "method": "match_codon_usage"},
        {"type": "UniquifyAllKmers", "k": 8},
    ]
    st.session_state["species"] = "196627"
    st.session_state["input_type"] = "protein"
    st.session_state["stop_codon"] = "TGA"
    st.session_state["max_random_iters"] = 10000
    st.session_state["constraints"] = constraints
    st.session_state["objectives"] = objectives

    from cc_copt.gui import _build_config_yaml

    result = yaml.safe_load(_build_config_yaml())
    assert result["species"] == "196627"
    assert result["input_type"] == "protein"
    assert result["stop_codon"] == "TGA"
    assert result["max_random_iters"] == 10000
    assert result["constraints"] == constraints
    assert result["objectives"] == objectives


def test_build_config_yaml_roundtrip_with_example():
    """Exported YAML can be loaded back and matches the original config."""
    import streamlit as st

    example_path = Path(__file__).parent.parent / "examples" / "config.yaml"
    with open(example_path) as f:
        original = yaml.safe_load(f)

    st.session_state["species"] = str(original["species"])
    st.session_state["input_type"] = original["input_type"]
    st.session_state["stop_codon"] = original["stop_codon"]
    st.session_state["max_random_iters"] = original["max_random_iters"]
    st.session_state["constraints"] = original["constraints"]
    st.session_state["objectives"] = original["objectives"]

    from cc_copt.gui import _build_config_yaml

    exported = yaml.safe_load(_build_config_yaml())
    # Species is stringified by the GUI text_input, so compare as strings
    assert str(exported["species"]) == str(original["species"])
    assert exported["input_type"] == original["input_type"]
    assert exported["stop_codon"] == original["stop_codon"]
    assert exported["max_random_iters"] == original["max_random_iters"]
    assert exported["constraints"] == original["constraints"]
    assert exported["objectives"] == original["objectives"]


# ------------------------------------------------------------------
# Add constraint / objective buttons
# ------------------------------------------------------------------


def test_add_constraint_button():
    """Clicking 'Add Constraint' adds an entry to session state."""
    at = _boot_app()
    assert len(at.session_state["constraints"]) == 0
    at.button(key="add_constraint").click().run()
    assert not at.exception, [str(e) for e in at.exception]
    assert len(at.session_state["constraints"]) == 1


def test_add_objective_button():
    """Clicking 'Add Objective' adds an entry to session state."""
    at = _boot_app()
    assert len(at.session_state["objectives"]) == 0
    at.button(key="add_objective").click().run()
    assert not at.exception, [str(e) for e in at.exception]
    assert len(at.session_state["objectives"]) == 1
