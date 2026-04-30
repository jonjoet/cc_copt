# Manifest Specification

This document defines the manifest formats that the Sequence Launch System hub uses to discover and run tools. It is the contract between the hub and tool repositories — tool developers should reference this when adapting their repos.

## Overview

The hub scans a configurable tools directory (`TOOLS_DIR`) for subdirectories containing manifest files. Each subdirectory is treated as a tool repo. The hub recognizes three manifest formats:

| File | Category | Description |
|------|----------|-------------|
| `tool.yaml` | `tool` or `static` | Containerized tools and static HTML tools |
| `nextflow_schema.json` | `pipeline` | Nextflow pipelines (nf-core schema format) |
| `workflow.yaml` | `workflow` | Multi-tool chains (lives in `WORKFLOWS_DIR`) |

A directory without a recognized manifest is silently ignored. A directory with a malformed manifest is skipped with a logged warning.

---

## tool.yaml

Used for containerized tools (`category: tool`) and static HTML tools (`category: static`).

### Full schema

```yaml
schema_version: 1              # required — integer, currently 1

name: my-tool                  # required — unique identifier, used in URLs
description: What this tool does  # required — shown on the tool card
category: tool                 # required — "tool" or "static"

# --- Containerized tools only (category: tool) ---

container:
  image: my-tool:latest        # required for category: tool — pre-built Docker image

command: python /app/run.py    # required for category: tool — entrypoint command

parameters:                    # optional — list of input parameters
  - name: sequence             # required — CLI arg name, passed as --sequence <value>
    type: textarea             # required — one of: text, textarea, select, file, number, checkbox
    label: Input Sequence      # required — human-readable label for the form
    options: [a, b, c]         # required if type is select — list or {label: value} dict
    extensions: [.fa, .fasta]  # optional, only for type: file — allowed file extensions
    default: some_value        # optional — default value
    required: true             # optional — defaults to true
    exclusive_group: group_name # optional — mutually exclusive with other params sharing this value
    resolve_paths: false       # optional — if true, select values are repo-relative file paths
    cli_arg: name              # optional — override the CLI flag (default: use name)

outputs:                       # optional — map of output names to output specs
  result:
    path: output/result.txt    # required — path relative to job output dir
    label: Result file         # required — human-readable label
    type: file                 # optional — defaults to "file"

# --- Static tools only (category: static) ---

entry: index.html              # required for category: static — HTML file to serve

# --- Benchling integration (optional, any category) ---

benchling:
  fetch:
    entity_type: custom_entity
    schema: Schema Name
    field_mapping:
      param_name: benchling_field_name
  push:
    field_mapping:
      output_name: benchling_field_name
```

### Container layout

Every containerized tool runs with the following mounts and working directory:

| Container path | Host path | Access |
|----------------|-----------|--------|
| `/app` (workdir) | — | — |
| `/app/inputs` | `{job_dir}/inputs` | read-only to tool |
| `/app/output` | `{job_dir}/outputs` | read-write |

Uploaded files and resolved config files are placed in `/app/inputs`. The tool should write all output files to `/app/output/`. The `command` field should hardcode these paths:

```yaml
command: python /app/run.py -i /app/inputs/samplesheet.csv -o /app/output/result.txt
```

The `outputs` section references paths relative to the job directory (host side), so use `output/` not `/app/output/`:

```yaml
outputs:
  result:
    path: output/result.txt
    label: Result file
```

### Parameter types

| Type | NiceGUI widget | CLI arg format |
|------|---------------|----------------|
| `text` | Text input | `--name value` |
| `textarea` | Multi-line text area | `--name value` |
| `select` | Dropdown | `--name value` |
| `file` | File upload | `--name /path/to/file` |
| `number` | Number input | `--name value` |
| `checkbox` | Checkbox | `--name` (flag, present if true) |

### Select with mapped values

By default, `options` is a flat list where the display label and submitted value are the same. You can also use a `{label: value}` dict so the dropdown shows human-readable labels while submitting different values:

```yaml
- name: organism
  type: select
  label: Target Organism
  options:
    E. coli: e_coli
    C. glutamicum: c_glutamicum
    S. cerevisiae: s_cerevisiae
```

#### Preset config files (`resolve_paths`)

When `resolve_paths: true`, the dict values are treated as file paths relative to the tool repo. At submission time, the hub copies the selected file into the job's inputs directory and passes the resolved path to the tool. The config files live in the tool repo alongside `tool.yaml`.

```yaml
- name: config_preset
  type: select
  label: Configuration Preset
  resolve_paths: true
  options:
    E. coli: configs/e_coli.yaml
    C. glutamicum: configs/c_glutamicum.yaml
    S. cerevisiae: configs/s_cerevisiae.yaml
```

### CLI argument override (`cli_arg`)

By default, the hub uses the parameter `name` as the CLI flag (`--name value`). Set `cli_arg` to override this when the CLI expects a different flag than the form-friendly name:

```yaml
- name: input_sequences
  type: file
  label: Input Sequences
  cli_arg: input               # passed as --input, not --input_sequences

- name: num_threads
  type: number
  label: Number of Threads
  cli_arg: t                   # passed as --t (short flag)
```

This is especially useful with exclusive groups where multiple params need to map to the same CLI flag:

```yaml
- name: config_preset
  type: select
  label: Configuration Preset
  cli_arg: config
  exclusive_group: config_source

- name: config_file
  type: file
  label: Custom Configuration
  cli_arg: config
  exclusive_group: config_source
```

Since only one exclusive group member is submitted, there is no collision.

### Exclusive groups

When two or more parameters share the same `exclusive_group` value, the form presents them as mutually exclusive options — the user picks exactly one. A radio toggle lets the user choose which parameter to fill in; the others are hidden. On submit, only the selected parameter's value is included.

Parameters in an exclusive group should set `required: false` since only the selected one needs a value.

```yaml
parameters:
  - name: config_preset
    type: select
    label: Configuration Preset
    options:
      E. coli: configs/e_coli.yaml
      C. glutamicum: configs/c_glutamicum.yaml
    resolve_paths: true
    required: false
    exclusive_group: config_source
  - name: config_file
    type: file
    label: Custom Configuration
    extensions: [.yaml, .yml]
    required: false
    exclusive_group: config_source
```

### Minimal examples

Containerized tool:

```yaml
schema_version: 1
name: echo-tool
description: Transforms input text
category: tool
container:
  image: echo-tool:latest
command: python /app/transform.py
parameters:
  - name: text
    type: textarea
    label: Input Text
  - name: transform
    type: select
    label: Transform Type
    options: [uppercase, lowercase, reverse]
outputs:
  result:
    path: output/result.txt
    label: Transformed text
    type: file
```

Static tool:

```yaml
schema_version: 1
name: restriction-analyzer
description: Count restriction enzyme cut sites
category: static
entry: resCount.html
```

---

## nextflow_schema.json

The standard [nf-core pipeline schema](https://nf-co.re/tools/#pipeline-schema) format. The hub reads this file and generates a form from the parameter definitions.

The hub extracts:
- `title` and `description` from the root object (used for tool card)
- Parameter definitions from `definitions.<group>.properties` (each becomes a form field)
- Type mapping: `string` -> text input, `integer`/`number` -> number input, `boolean` -> checkbox, `string` with `enum` -> dropdown

No `tool.yaml` is needed alongside `nextflow_schema.json`. The presence of this file is sufficient for the hub to recognize the directory as a pipeline.

The hub assumes `main.nf` exists in the same directory as the entry point.

---

## workflow.yaml

Lives in the workflows directory (`WORKFLOWS_DIR`), not the tools directory. Defines a chain of existing tools.

```yaml
name: edit-resistant-guides
description: Design gRNAs then recode target sites
category: workflow
image: edit-resistant-guides:latest   # optional — container for glue scripts

steps:
  - tool: guide-rna-designer          # references a tool by name
    id: guides
    params:
      target_organism: from_input     # appears on combined form
      pam_type: from_input

  - script: reshape_guides.py         # runs in this workflow's container
    id: reshape
    params:
      input: from_step.guides.guide_sequences

  - tool: dna-chisel
    id: recode
    params:
      sequence: from_input
      avoid_sites: from_step.reshape.output
```

### Parameter resolution

- `from_input` — the parameter appears on the combined form for the scientist to fill in
- `from_step.<step_id>.<output_name>` — wired automatically from a previous step's output

### Glue scripts

Workflows that need data reshaping between steps include a `Dockerfile` and scripts in their directory. Workflows that are pure tool chains don't need a container image.

---

## Discovery rules

1. The hub scans `TOOLS_DIR` on startup and on manual refresh
2. Each immediate subdirectory is checked for `tool.yaml`, then `nextflow_schema.json`
3. The first manifest found wins — a directory should contain only one manifest type
4. Malformed manifests are skipped with a warning (no crash)
5. Directories without a manifest are silently ignored
6. `WORKFLOWS_DIR` is scanned separately for `workflow.yaml` files (Session 7)
