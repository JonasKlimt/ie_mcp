# GitHub Copilot Instructions for ie-mcp

These instructions apply whenever you are working in this repository or using the
**ie-mcp** MCP server from any workspace.

---

## Automatic ie-mcp usage for tracked packages

If the user asks about any package that is tracked by this server, or if the current
question/code clearly concerns a tracked package, use the **ie-mcp** MCP tools by
default even when the user did not explicitly ask to use ie-mcp.

Do not wait for explicit user wording such as "use ie-mcp" when package intent is
already clear from the question or code context.

### Keyword routing map (automatic triggers)

If trigger terms appear in the user request, code context, stack traces, or variable
names, route via **ie-mcp** automatically.

- **Core Brightway LCA workflow**
  - Triggers: `LCA`, `life cycle assessment`, `LCI`, `LCIA`, `activity`,
    `activities`, `exchange`, `exchanges`, `biosphere`, `technosphere`,
    `inventory`, `database`, `functional unit`, `characterization`,
    `impact assessment`, `impact category`, `normalization`, `weighting`,
    `allocation`, `system boundary`, `contribution analysis`, `hotspot`
  - Check first: `brightway25` (or `brightway2` for legacy), then `bw2data`,
    `bw2calc`, `bw2io`, `bw2analyzer`

- **Scenario / prospective LCA**
  - Triggers: `prospective`, `scenario`, `future`, `IAM`, `transformation`,
    `premise`, `wurst`, `pathway`
  - Check first: `premise`, `wurst`, `pathways`, `randonneur`, `randonneur_data`,
    `ecoinvent_migrate`

- **Temporal / dynamic LCA**
  - Triggers: `dynamic LCA`, `time-dependent`, `temporal`, `timeline`,
    `dynamic characterization`, `time-explicit`
  - Check first: `bw_temporalis`, `bw_timex`, `dynamic_characterization`

- **Regionalized / spatial LCA**
  - Triggers: `regionalized`, `spatial`, `location-specific`, `region`, `geo`
  - Check first: `brightway2_regional`, `simple_regional`, `regioinvent`, `edges`

- **IO / hybrid / MRIO workflows**
  - Triggers: `MRIO`, `EXIOBASE`, `input-output`, `hybrid LCA`, `footprint`,
    `trade-embodied`
  - Check first: `pymrio`, `bw_exiobase`, `brightway_hybrid`,
    `mrio_common_metadata`

- **Uncertainty / Monte Carlo / parameters**
  - Triggers: `Monte Carlo`, `uncertainty`, `distribution`, `pedigree matrix`,
    `sensitivity`, `Sobol`, `parameterization`
  - Check first: `stats_arrays`, `bw2parameters`, `pedigree_matrix`,
    `lca_algebraic`

- **Import/export and format conversion**
  - Triggers: `import ecoinvent`, `SimaPro`, `ILCD`, `EcoSpold`, `migration`,
    `mapping`, `openLCA`
  - Check first: `bw2io`, `bw_simapro_csv`, `pyecospold`, `pyilcd`,
    `bw_migrations`, `simapro_ecoinvent_elementary_flows`, `brightway_olca`,
    `ecoinvent_interface`

- **Graph / network analysis**
  - Triggers: `graph traversal`, `supply chain graph`, `path analysis`, `network`
  - Check first: `bw_graph_tools`, `bw_simple_graph`, `bw2analyzer`

- **MFA (non-Brightway primary route)**
  - Triggers: `material flow analysis`, `MFA`, `stock-flow`, `cohort`, `ODYM`,
    `flodym`, `RECC`
  - Check first: `odym`, `flodym`, `recc_odym`

Routing rules:
- If any trigger group matches, use ie-mcp without waiting for explicit user wording.
- If LCA terms match but package is unclear, assume Brightway packages are needed and
  start with `brightway25` + core components.
- If multiple groups match, prioritize explicit package names first, then the most
  specific matching group.

---

## Environment check before version-sensitive lookups

When a user asks about a **function, method, or API** of a package that is registered
in the ie-mcp server, and they have **not specified a version**:

1. Call `get_installed_package_version(package)` **first**.
2. Use the returned `installed_version` for all subsequent `get_function_source` and
   `get_doc_section` calls.
3. Always tell the user which version you are looking up and which Python environment
   was checked (the `python_executable` field in the response).

If the tool returns `status: "not_installed"`:
- Tell the user the package was not found in the active MCP environment.
- Show them the `python_executable` path so they can verify whether it is the right
  interpreter.
- Ask whether they want to fall back to the **latest** version, or whether they want
  to update `.vscode/mcp.json` first.

---

## Environment audit

When a user asks "what packages do I have installed?" or "is X available in my
environment?", call `get_server_environment()`. This returns the Python executable,
Python version, and the installed version of every ie-mcp-tracked package in one call.

---

## Wrong environment warning

If `python_executable` in any tool response does **not** match the interpreter the
user expects (e.g. a different conda env, a system Python, or a venv), surface a
clear warning:

> ⚠️ The ie-mcp server is running under `<python_executable>`. If this is not the
> environment where you installed `<package>`, update the `"command"` field in
> `.vscode/mcp.json` and restart the MCP server.

---

## General ie-mcp routing policy

- For **named function / method questions**: check installed version → fetch source
  at that version via `get_function_source`.
- For **conceptual / how-to questions**: check installed version → fetch the matching
  doc section via `get_doc_section`.
- For **version-explicit questions** (user states a version): skip the installed
  version check and use the user-provided version directly.
- Only fall back to `latest` when the package is confirmed not installed and the user
  accepts the fallback.
