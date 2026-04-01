"""Streamlit web interface for cc_copt codon optimization."""

import tempfile
from io import StringIO
from pathlib import Path

import streamlit as st
import yaml

from cc_copt.config import OptConfig, build_spec, resolve_species
from cc_copt.io import read_input
from cc_copt.optimize import OptimizationResult, optimize_sequence
from cc_copt.spec_registry import (
    SPEC_REGISTRY,
    get_constraint_specs,
    get_objective_specs,
    spec_dict_from_form,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(page_title="cc_copt — Codon Optimizer", layout="wide")

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------


def _init_state():
    defaults = {
        "species": "",
        "input_type": "auto",
        "stop_codon": "TAA",
        "max_random_iters": 50000,
        "constraints": [],
        "objectives": [],
        "results": None,
        "errors": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_state()

# ---------------------------------------------------------------------------
# Sidebar — YAML config upload
# ---------------------------------------------------------------------------

st.sidebar.header("Load Configuration")
config_file = st.sidebar.file_uploader(
    "Upload a YAML config file",
    type=["yaml", "yml"],
    help="Same format as the CLI config. Populates all settings below.",
)

if config_file is not None:
    if st.sidebar.button("Apply Config"):
        raw = yaml.safe_load(config_file.getvalue())
        if isinstance(raw, dict):
            st.session_state["species"] = str(raw.get("species", ""))
            st.session_state["input_type"] = raw.get("input_type", "auto")
            st.session_state["stop_codon"] = raw.get("stop_codon", "TAA")
            st.session_state["max_random_iters"] = raw.get("max_random_iters", 50000)
            st.session_state["constraints"] = raw.get("constraints", [])
            st.session_state["objectives"] = raw.get("objectives", [])
            st.session_state["results"] = None
            st.session_state["errors"] = None
            st.rerun()
        else:
            st.sidebar.error("Config file must be a YAML mapping.")

st.sidebar.markdown("---")
st.sidebar.markdown(
    "Or configure settings manually below and add "
    "constraints / objectives in the main panel."
)

# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------

st.title("cc_copt — Codon Optimizer")
st.caption("Web interface for batch codon optimization using DnaChisel")

# ---------------------------------------------------------------------------
# Sequence upload
# ---------------------------------------------------------------------------

st.header("1. Upload Sequences")
seq_file = st.file_uploader(
    "Upload a sequence file",
    type=["fa", "faa", "fasta", "fna", "csv", "tsv"],
    help="FASTA or CSV/TSV with auto-detected ID and sequence columns.",
)

# ---------------------------------------------------------------------------
# Global settings
# ---------------------------------------------------------------------------

st.header("2. Settings")

col1, col2, col3, col4 = st.columns(4)

with col1:
    species_val = st.text_input(
        "Species",
        value=st.session_state["species"],
        help="TaxID (integer) or species name (e.g. e_coli).",
        key="species_input",
    )
with col2:
    input_type_options = ["auto", "protein", "dna"]
    input_type_val = st.selectbox(
        "Input type",
        input_type_options,
        index=input_type_options.index(st.session_state["input_type"]),
        key="input_type_input",
    )
with col3:
    stop_codon_options = ["TAA", "TAG", "TGA"]
    stop_codon_val = st.selectbox(
        "Stop codon",
        stop_codon_options,
        index=stop_codon_options.index(st.session_state["stop_codon"]),
        key="stop_codon_input",
    )
with col4:
    max_iters_val = st.number_input(
        "Max random iters",
        value=st.session_state["max_random_iters"],
        min_value=100,
        step=1000,
        key="max_iters_input",
    )

# Sync back to session state
st.session_state["species"] = species_val
st.session_state["input_type"] = input_type_val
st.session_state["stop_codon"] = stop_codon_val
st.session_state["max_random_iters"] = max_iters_val

# ---------------------------------------------------------------------------
# Helpers — dynamic spec forms
# ---------------------------------------------------------------------------

_CONSTRAINT_TYPES = [s.type_name for s in get_constraint_specs()]
_OBJECTIVE_TYPES = [s.type_name for s in get_objective_specs()]


def _render_spec_block(index: int, spec_dict: dict, key_prefix: str, type_options: list[str]):
    """Render one constraint/objective block.  Returns updated dict or None if removed."""
    cols = st.columns([4, 1])
    current_type = spec_dict.get("type", type_options[0])
    if current_type not in type_options:
        current_type = type_options[0]

    with cols[0]:
        new_type = st.selectbox(
            "Type",
            type_options,
            index=type_options.index(current_type),
            key=f"{key_prefix}_{index}_type",
            label_visibility="collapsed",
        )
    with cols[1]:
        remove = st.button("Remove", key=f"{key_prefix}_{index}_rm")

    if remove:
        return None  # signal removal

    # If type changed, reset params
    if new_type != current_type:
        spec_dict = {"type": new_type}

    spec_def = SPEC_REGISTRY.get(new_type)
    if spec_def is None:
        st.warning(f"Unknown spec type: {new_type}")
        return spec_dict

    if spec_def.help:
        st.caption(spec_def.help)

    form_values = {}
    param_cols = st.columns(max(len(spec_def.params), 1))
    for pi, param in enumerate(spec_def.params):
        col = param_cols[pi % len(param_cols)]
        existing = spec_dict.get(param.name, param.default)
        wkey = f"{key_prefix}_{index}_{param.name}"

        with col:
            if param.type == "str":
                form_values[param.name] = st.text_input(
                    param.label, value=existing or "", key=wkey, help=param.help,
                )
            elif param.type == "int":
                form_values[param.name] = st.number_input(
                    param.label,
                    value=int(existing) if existing is not None else 0,
                    step=1,
                    min_value=int(param.min_value) if param.min_value is not None else None,
                    max_value=int(param.max_value) if param.max_value is not None else None,
                    key=wkey,
                    help=param.help,
                )
                # If the param is optional and user left at 0 / default-ish, check
                if not param.required and existing is None and form_values[param.name] == 0:
                    form_values[param.name] = None
            elif param.type == "float":
                form_values[param.name] = st.number_input(
                    param.label,
                    value=float(existing) if existing is not None else 0.0,
                    step=0.01,
                    min_value=float(param.min_value) if param.min_value is not None else None,
                    max_value=float(param.max_value) if param.max_value is not None else None,
                    format="%.4f",
                    key=wkey,
                    help=param.help,
                )
                if not param.required and existing is None and form_values[param.name] == 0.0:
                    form_values[param.name] = None
            elif param.type == "bool":
                form_values[param.name] = st.checkbox(
                    param.label,
                    value=bool(existing) if existing is not None else False,
                    key=wkey,
                    help=param.help,
                )
            elif param.type == "select":
                opts = param.options
                idx = opts.index(existing) if existing in opts else 0
                form_values[param.name] = st.selectbox(
                    param.label, opts, index=idx, key=wkey, help=param.help,
                )

    return spec_dict_from_form(new_type, form_values)


# ---------------------------------------------------------------------------
# Constraints section
# ---------------------------------------------------------------------------

st.header("3. Constraints")

if st.button("Add Constraint", key="add_constraint"):
    st.session_state["constraints"].append({"type": _CONSTRAINT_TYPES[0]})
    st.rerun()

updated_constraints = []
for i, spec in enumerate(st.session_state["constraints"]):
    with st.expander(f"Constraint {i + 1}: {spec.get('type', '?')}", expanded=True):
        result = _render_spec_block(i, spec, "con", _CONSTRAINT_TYPES)
        if result is not None:
            updated_constraints.append(result)

if len(updated_constraints) != len(st.session_state["constraints"]):
    st.session_state["constraints"] = updated_constraints
    st.rerun()
else:
    st.session_state["constraints"] = updated_constraints

# ---------------------------------------------------------------------------
# Objectives section
# ---------------------------------------------------------------------------

st.header("4. Objectives")

if st.button("Add Objective", key="add_objective"):
    st.session_state["objectives"].append({"type": _OBJECTIVE_TYPES[0]})
    st.rerun()

updated_objectives = []
for i, spec in enumerate(st.session_state["objectives"]):
    with st.expander(f"Objective {i + 1}: {spec.get('type', '?')}", expanded=True):
        result = _render_spec_block(i, spec, "obj", _OBJECTIVE_TYPES)
        if result is not None:
            updated_objectives.append(result)

if len(updated_objectives) != len(st.session_state["objectives"]):
    st.session_state["objectives"] = updated_objectives
    st.rerun()
else:
    st.session_state["objectives"] = updated_objectives

# ---------------------------------------------------------------------------
# Optimize
# ---------------------------------------------------------------------------

st.header("5. Optimize")

if st.button("Run Optimization", type="primary", key="run_optimize"):
    # Validate inputs
    if seq_file is None:
        st.error("Please upload a sequence file first.")
        st.stop()

    if not st.session_state["species"]:
        st.error("Please specify a species (TaxID or name).")
        st.stop()

    # Parse sequences from uploaded file
    suffix = Path(seq_file.name).suffix
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(seq_file.getvalue())
    tmp.close()

    try:
        sequences = read_input(tmp.name)
    except Exception as e:
        st.error(f"Error reading input file: {e}")
        st.stop()
    finally:
        Path(tmp.name).unlink(missing_ok=True)

    if not sequences:
        st.error("No sequences found in the uploaded file.")
        st.stop()

    # Build OptConfig
    species = resolve_species(st.session_state["species"])

    try:
        constraints = [
            build_spec(c, species) for c in st.session_state["constraints"]
        ]
        objectives = [
            build_spec(o, species) for o in st.session_state["objectives"]
        ]
    except Exception as e:
        st.error(f"Error building specifications: {e}")
        st.stop()

    config = OptConfig(
        species=species,
        input_type=st.session_state["input_type"],
        stop_codon=st.session_state["stop_codon"],
        max_random_iters=st.session_state["max_random_iters"],
        constraints=constraints,
        objectives=objectives,
    )

    # Run optimization
    results: list[OptimizationResult] = []
    errors: list[dict] = []
    n = len(sequences)

    progress = st.progress(0, text="Optimizing sequences...")
    status_area = st.empty()

    for i, (name, seq) in enumerate(sequences):
        status_area.text(f"[{i + 1}/{n}] Optimizing {name}...")
        try:
            r = optimize_sequence(name, seq, config)
            results.append(r)
        except Exception as e:
            errors.append({"name": name, "error": str(e)})
        progress.progress((i + 1) / n)

    progress.empty()
    status_area.empty()

    st.session_state["results"] = results
    st.session_state["errors"] = errors
    st.rerun()

# ---------------------------------------------------------------------------
# Results display
# ---------------------------------------------------------------------------

if st.session_state["results"] is not None:
    results: list[OptimizationResult] = st.session_state["results"]
    errors: list[dict] = st.session_state["errors"] or []

    st.header("Results")

    # Summary
    succeeded = len(results)
    failed = len(errors)
    st.success(f"{succeeded} sequence(s) optimized successfully.")
    if failed:
        st.warning(f"{failed} sequence(s) failed.")

    # Failed sequences
    if errors:
        with st.expander("Failed sequences", expanded=False):
            for err in errors:
                st.error(f"**{err['name']}**: {err['error']}")

    # Per-sequence results
    for r in results:
        with st.expander(
            f"{r.name} — {'PASS' if r.constraints_pass else 'FAIL'}",
            expanded=not r.constraints_pass,
        ):
            # Constraint results
            if r.constraint_results:
                st.subheader("Constraints")
                for cr in r.constraint_results:
                    icon = "✅" if cr["passes"] else "❌"
                    st.markdown(f"{icon} {cr['label']}")

            # Objective results
            if r.objective_results:
                st.subheader("Objectives")
                for obj in r.objective_results:
                    st.markdown(f"**{obj['label']}**: {obj['score']:.4f}")

            # Sequences
            st.subheader("Sequences")
            if r.protein_seq:
                st.text_area("Protein", r.protein_seq, height=80,
                             key=f"res_protein_{r.name}", disabled=True)
            if r.input_dna_seq:
                st.text_area("Input DNA", r.input_dna_seq, height=80,
                             key=f"res_indna_{r.name}", disabled=True)
            st.text_area("Optimized DNA", r.optimized_dna_seq, height=80,
                         key=f"res_optdna_{r.name}", disabled=True)

    # Downloads
    st.subheader("Download Results")
    dl_col1, dl_col2 = st.columns(2)

    # FASTA download
    fasta_buf = StringIO()
    for r in results:
        fasta_buf.write(f">{r.name}\n{r.optimized_dna_seq}\n")
    with dl_col1:
        st.download_button(
            "Download Optimized FASTA",
            data=fasta_buf.getvalue(),
            file_name="optimized.fna",
            mime="text/plain",
        )

    # TSV download
    tsv_buf = StringIO()
    header_cols = ["id", "protein_seq", "input_dna_seq", "optimized_dna_seq", "all_constraints_pass"]
    if results:
        header_cols += [f"constraint:{cr['label']}" for cr in results[0].constraint_results]
        header_cols += [f"objective:{obj['label']}" for obj in results[0].objective_results]
    tsv_buf.write("\t".join(header_cols) + "\n")
    for r in results:
        vals = [
            r.name,
            r.protein_seq,
            r.input_dna_seq or "",
            r.optimized_dna_seq,
            str(r.constraints_pass),
        ]
        vals.extend("PASS" if cr["passes"] else "FAIL" for cr in r.constraint_results)
        vals.extend(f"{obj['score']:.4f}" for obj in r.objective_results)
        tsv_buf.write("\t".join(vals) + "\n")
    with dl_col2:
        st.download_button(
            "Download Summary TSV",
            data=tsv_buf.getvalue(),
            file_name="summary.tsv",
            mime="text/tab-separated-values",
        )
