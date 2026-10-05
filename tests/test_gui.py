"""Optional AppTest regression coverage of deployed widget/state behavior."""
import json

import pytest
pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest

from conftest import APP_PATH
from cc_copt.config import build_spec
from cc_copt.gui_config import normalize_gui_config, export_gui_config
import yaml


def boot(raw=None):
    app = AppTest.from_file(str(APP_PATH), default_timeout=15)
    if raw is not None:
        for key, value in normalize_gui_config(raw).items():
            app.session_state[key] = value
    app.run()
    assert not app.exception
    return app


def widget_key(app, name):
    if name.startswith(("con_", "obj_")):
        group, index, field = name.split("_", 2)
        prefix = f"form_{app.session_state['form_generation']}_{group}_{app.session_state[group + '_generation']}_{index}"
        if field not in ("type", "rm"):
            spec = app.session_state["constraints" if group == "con" else "objectives"][int(index)]
            prefix += "_" + spec["type"]
        return prefix + "_" + field
    return f"form_{app.session_state['form_generation']}_{name}"


def test_boot_defaults_and_export_edit():
    app = boot()
    assert app.title[0].value == "cc_copt — Codon Optimizer"
    assert app.session_state["input_type"] == "auto"
    assert app.session_state["max_random_iters"] == 50000
    app.text_input(key=widget_key(app, "species_input")).set_value("12345").run()
    assert yaml.safe_load(export_gui_config(app.session_state))["species"] == "12345"
    assert app.sidebar.get("download_button")


@pytest.mark.parametrize("button,group", [("add_constraint", "constraints"), ("add_objective", "objectives")])
def test_add(button, group):
    app = boot()
    app.button(key=button).click().run()
    assert len(app.session_state[group]) == 1
    assert not app.exception


def test_remove_first_then_edit_remaining():
    app = boot({"constraints": [dict(type="AvoidPattern", pattern="BsaI_site"),
                                dict(type="AvoidPattern", pattern="EcoRI_site")]})
    app.button(key=widget_key(app, "con_0_rm")).click().run()
    assert len(app.session_state["constraints"]) == 1
    assert app.text_input(key=widget_key(app, "con_0_pattern")).value == "EcoRI_site"
    app.text_input(key=widget_key(app, "con_0_pattern")).set_value("BsmBI_site").run()
    assert app.session_state["constraints"][0]["pattern"] == "BsmBI_site"


def test_type_switch_resets_shared_fields_only():
    app = boot({"constraints": [dict(type="EnforceGCContent", mini=0.4),
                                dict(type="AvoidPattern", pattern="EcoRI_site")]})
    app.selectbox(key=widget_key(app, "con_0_type")).set_value("EnforceTerminalGCContent").run()
    assert app.number_input(key=widget_key(app, "con_0_mini")).value == 0.0
    assert app.text_input(key=widget_key(app, "con_1_pattern")).value == "EcoRI_site"
    app.selectbox(key=widget_key(app, "con_0_type")).set_value("AvoidPattern").run()
    assert app.session_state["constraints"][0] == {"type": "AvoidPattern"}
    assert not app.exception


@pytest.mark.parametrize("field,minimum,positive", [("window", 1, 50), ("target", 0.0, 0.45)])
def test_optional_numeric_transitions(field, minimum, positive):
    app = boot({"constraints": [dict(type="EnforceGCContent")]})
    toggle = f"con_0_{field}_toggle"
    key = f"con_0_{field}"
    assert field not in app.session_state["constraints"][0]
    app.checkbox(key=widget_key(app, toggle)).check().run()
    assert app.number_input(key=widget_key(app, key)).value == minimum
    assert app.session_state["constraints"][0][field] == minimum
    app.number_input(key=widget_key(app, key)).set_value(positive).run()
    value = app.session_state["constraints"][0][field]
    assert value == positive and isinstance(value, int if field == "window" else float)
    app.checkbox(key=widget_key(app, toggle)).uncheck().run()
    assert field not in app.session_state["constraints"][0]
    assert not app.exception


def test_imported_omitted_defaults_display_and_build(synthetic):
    app = boot(dict(constraints=[dict(type="EnforceTranslation")], objectives=[dict(type="CodonOptimize")]))
    assert app.text_input(key=widget_key(app, "con_0_start_codon")).value == ""
    assert app.text_input(key=widget_key(app, "con_0_genetic_table")).value == "default"
    assert app.selectbox(key=widget_key(app, "obj_0_method")).value == "use_best_codon"
    table = json.loads((synthetic / "synthetic-codons.json").read_text())
    exported = yaml.safe_load(export_gui_config(app.session_state))
    assert build_spec(exported["constraints"][0], table).start_codon is None
    assert type(build_spec(exported["objectives"][0], table)).__name__ == "MaximizeCAI"


def test_no_input_error():
    app = boot()
    app.button(key="run_optimize").click().run()
    assert any("upload a sequence" in e.value for e in app.error)
    assert not app.exception
