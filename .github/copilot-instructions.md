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

## Version and source rules

The version that matters is the one installed in the user's environment, unless
the user names another one. Follow these rules in order.

0. **Choose the user's environment first (once per task or project).**
   - Find the Python interpreter of the file, notebook or project the user works
     on: the selected interpreter or kernel, or run
     `python -c "import sys; print(sys.executable)"` in the project's environment.
     Call `set_python_environment(path)`.
   - If you cannot find it, or the question is not about a specific file or
     project, call `get_server_environment()`. If it has a `hint`, or the
     interpreter is clearly not the user's, ask the user which environment to use.

1. **No version mentioned (default).**
   - Call `get_installed_package_version(package)`.
   - Function, method, class or signature questions: call
     `get_function_source(package, name)` **without** a version. It reads the
     installed files (`source: "local"`). Use `Class.method` for methods and
     `detail="signature"` when signature and docstring are enough.
   - Workflow, how-to and concept questions: use `get_package_info` to pick a
     section, then `get_doc_section`; use `search_docs` only if no section fits.
     Confirm key functions with `get_function_source`.
   - Docs results state `docs_version` and `installed_version`. If they differ,
     tell the user and trust the installed source code for signatures.

2. **The user names a specific other version.**
   - Call `get_function_source(package, name, version=...)` or
     `search_source(package, query, version=...)`. The code comes from PyPI
     (`source: "pypi"`), or from GitHub (`source: "github"`) if that version is
     not on PyPI. Use `list_source_versions(package)` if the version is unclear.
   - For docs of that version, call `list_doc_versions(package)`. If there are
     no versioned docs, say that legacy documentation is not available and
     answer from the versioned source code.

3. **The package is not installed (`status: "not_installed"`).**
   - First check that the inspected `python_executable` is the user's
     environment (rule 0). If it is, tell the user, show the `python_executable`,
     and ask before using the latest version. Do not fall back silently.

4. **"Latest" only on request.** Use `version="latest"` or `fetch_latest_docs`
   only when the user asks for the latest version or agreed to it under rule 3.

5. **Always state the basis of the answer:** which version, and which source
   (`local`, `pypi`, `github`, and the docs version).

---

## Environment audit

When a user asks "what packages do I have installed?" or "is X available in my
environment?", call `get_server_environment()`. It returns the inspected Python
interpreter, where it came from (`python_executable_origin`), and the installed
version of every ie-mcp-tracked package. Pass `refresh=True` after the user
installed or upgraded a package.

---

## Wrong environment

If `python_executable` in a tool response is not the interpreter of the user's
file or project (e.g. a different conda env, a system Python, or the server's
own Python), call `set_python_environment` with the right one and repeat the
call. If you do not know the right one, ask the user:

> ⚠️ ie-mcp inspected `<python_executable>`. Which Python environment do you
> use for this project?
