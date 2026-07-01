# ie-mcp

Using the ie_mcp server makes coding with Industrial Ecology packages, especially Brightway, much easier. It guides GitHub Copilot to the right package documentation for your question, so you avoid mixed package versions, wrong references, and hallucinated answers.

An MCP (Model Context Protocol) server that explains Industrial Ecology Python packages through their documentation. Ask it anything about a registered package — installation, usage, API, concepts — directly from VS Code Copilot.

An MCP server is a bridge between Copilot and trusted external information. In VS Code Agent mode, Copilot can call this server to check package docs, source code, and versions before it answers.

**Currently supported packages:** The full **Brightway LCA ecosystem**, and additional industrial ecology tools — **56 packages total** (see [Brightway ecosystem](#brightway-ecosystem) and [Additional packages](#additional-packages) below)

## Why this is needed

For modelling work, you need reliable help that matches your real environment and package versions. This server gives environment- and version-relevant explanations for both single functions and complete IE package workflows. This makes going through pages of package documentation and checking its GitHub pages redundant. Just as Copilot about the package and get relevant explantion/coding help for the exact package version you are using.

## Example questions

- "How do I do a basic LCA in Brightway from setup to first result?"
- "How do I use premise for prospective LCA scenarios?"
- "How do I use the function [...]?
- "Explain what arguments the function takes in the package version that is currently installed in my environment."
- ...

---

## Prerequisites

Run the following in your environment:

```bash
pip install "mcp[cli]>=1.0.0" "httpx>=0.27.0" "beautifulsoup4>=4.12.0" "markdownify>=0.13.0"
```
---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/JonasKlimt/ie_mcp.git
cd ie-mcp
```

### 2. Connect to your AI client

#### VS Code (Copilot agent mode)

The `.vscode/mcp.json` file is already configured. Open **this folder** as your workspace root in VS Code and Copilot agent mode picks up the server automatically — no manual startup needed.

> **Other workspaces / projects:** To use the server from a different project, add it to your VS Code user settings (`settings.json`) with an absolute path:
>
> ```json
> {
>   "mcp.servers": {
>     "ie-mcp": {
>       "type": "stdio",
>       "command": "/absolute/path/to/your/environment/python.exe",
>       "args": ["run", "/absolute/path/to/ie-mcp/server.py"],
>       "env": {
>          "GITHUB_TOKEN" : ""
>       }
>     }
>   }
> }
> ```

### 3. Point the server at the right Python environment

The server checks your **installed package versions** to look up the correct documentation and source code. It can only see packages installed in the Python interpreter specified in `mcp.json` (or user `settings.json`).

**Rule of thumb:** set `command` to the same Python executable you use for your work.

| Situation | What to set as `command` |
|---|---|
| conda env named `bw` | `C:\Users\you\miniconda3\envs\bw\python.exe` (Windows) or `/home/you/miniconda3/envs/bw/bin/python` (Linux/macOS) |
| venv in project folder | `./venv/Scripts/python.exe` (Windows) or `./venv/bin/python` (Linux/macOS) |
| uv project | `uv run python` (set `type: "stdio"` and prefix args accordingly) |

Copilot will call `get_server_environment()` and return a full list of tracked packages with their installed versions, plus the active Python executable path. If a package shows **"not installed"**, update `command` in `mcp.json` and restart the server.

For best results, also add the instruction file (`.github/copilot-instructions.md`) in the .github folder to you repository. An instruction file is a short set of project-specific rules for Copilot (what tools to prefer, how to answer, what context matters most). This makes ie_mcp more efficient because Copilot is guided to use the server consistently and query package docs/versions in the way you want.

---

## GitHub token (optional)

The `search_source` and `get_function_source` tools use the GitHub REST API. Without a token, GitHub allows **60 requests/hour** — enough for light use. Add a free personal access token to raise the limit to **5 000 requests/hour**.

1. Go to [github.com → Settings → Developer settings → Personal access tokens → Tokens (classic)](https://github.com/settings/tokens)
2. Click **Generate new token (classic)**, give it a name, set an expiry — **no scopes needed** for public repos.
3. Add the token to your client config:

**VS Code** — paste into `.vscode/mcp.json`:

```json
{
  "mcp.servers": {
    "ie-mcp": {
      "type": "stdio",
      "command": "/absolute/path/to/your/environment/python.exe",
      "args": ["run", "/absolute/path/to/ie-mcp/server.py"],
      "env": {
        "GITHUB_TOKEN" : "ghp_your_token"
      }
    }
  }
}

```


> **Important:** Do not commit `.vscode/mcp.json` after adding your token. The empty-token version is checked in so other users get a working starting point; your filled-in version is for local use only.


## How the server works

1. It checks your active Python environment and installed package versions.
2. It fetches official documentation pages when needed and keeps a local cache for faster repeated use.
3. For version-specific questions, it checks GitHub tags first and then fetches matching source code.
4. When versioned docs are available (for example on ReadTheDocs), it can fetch those too.
5. If versioned docs are not available, it still answers from the matching versioned source code.

This keeps answers reliable, version-correct, and grounded in official docs or source.

---

## Brightway ecosystem

[Brightway](https://brightway.dev) is an open-source Python framework for life cycle assessment (LCA). All packages from the [`brightway-lca` GitHub organisation](https://github.com/brightway-lca) are registered:

### Meta-packages

| Package key | PyPI / install | Description |
|---|---|---|
| `brightway25` | `pip install brightway25` | Brightway 2.5 — current stable meta-package |
| `brightway2` | `pip install brightway2` | Brightway 2 — legacy stable meta-package |

### Brightway 2.5 core components

These are the direct dependencies installed by `pip install brightway25`:

| Package key | PyPI name | Role |
|---|---|---|
| `bw2data` | bw2data | Project & database management |
| `bw2calc` | bw2calc | LCA matrix calculations |
| `bw2io` | bw2io | Import / export (ecoinvent, SimaPro, …) |
| `bw2analyzer` | bw2analyzer | Contribution analysis & supply chain traversal |
| `bw2parameters` | bw2parameters | Parameter storage & formula evaluation |
| `bw_processing` | bw_processing | Structured NumPy datapackages |
| `matrix_utils` | matrix_utils | MappedMatrix building from datapackages |
| `bw_migrations` | bw_migrations | Migration files between ecoinvent versions |
| `bw_simapro_csv` | bw_simapro_csv | SimaPro CSV parsing |
| `ecoinvent_interface` | ecoinvent_interface | Programmatic ecoinvent download |
| `multifunctional` | multifunctional | Multi-output / allocation handling |
| `randonneur` | randonneur | Flexible dataset transformation engine |
| `randonneur_data` | randonneur_data | Transformation data files for randonneur |
| `stats_arrays` | stats_arrays | Uncertain parameter arrays & Monte Carlo |
| `mrio_common_metadata` | mrio_common_metadata | MRIO datapackage schema |

### Additional brightway-lca packages

| Package key | Description |
|---|---|
| `bw_temporalis` | Time-explicit LCA (Brightway 2.5) |
| `bw_timex` | Advanced time-explicit LCA |
| `dynamic_characterization` | Dynamic (time-dependent) characterization factors |
| `bw_graph_tools` | Supply chain graph traversal utilities |
| `bw_exiobase` | EXIOBASE MRIO import |
| `bw_recipe_2016` | ReCiPe 2016 LCIA method |
| `bw_aggregation` | Aggregated process support |
| `bw_campaigns` | Named datapackage campaign management |
| `bw_hestia_bridge` | HESTIA API bridge |
| `bw_interface_schemas` | Pydantic interface schemas |
| `bw_simple_graph` | Lightweight graph backend (no bw2data) |
| `edge_of_the_world` | Experimental backend for richer exchange descriptions beyond standard matrix structure |
| `brightway2_regional` | Regionalized LCA calculations |
| `brightway_olca` | openLCA IPC server integration |
| `brightway_hybrid` | Hybrid IO/process LCA |
| `ecoinvent_migrate` | Randonneur migration file generator |
| `pedigree_matrix` | Pedigree-matrix uncertainty adaptation |
| `pyecospold` | EcoSpold1/2 XML ↔ Python round-trip |
| `pyilcd` | ILCD XML ↔ Python round-trip |
| `simapro_ecoinvent_elementary_flows` | SimaPro ↔ ecoinvent flow mappings |
| `simple_regional` | Lightweight regionalized LCA |
| `brightway2_speedups` | Cython performance extensions for BW2 |
| `brightway2_ui` | CLI tool for Brightway2 |

---

## Additional packages

### LCA tools

| Package key | GitHub | Docs | Description |
|---|---|---|---|
| `edges` | [edges](https://github.com/Laboratory-for-Energy-Systems-Analysis/edges) | [readthedocs](https://edges.readthedocs.io/en/stable/) | Edge-based LCIA for Brightway: context-sensitive characterization factors applied to exchanges, not just flows. Includes AWARE 2.0, ImpactWorld+, GeoPolRisk, GLAM3. |
| `lca_algebraic` | [lca_algebraic](https://github.com/oie-mines-paristech/lca_algebraic) | [readthedocs](https://lca-algebraic.readthedocs.io/en/stable/) | Parametric LCA inventories with fast Monte Carlo and Sobol sensitivity analysis, using Sympy expressions. Built on Brightway2/2.5. |
| `pathways` | [pathways](https://github.com/polca/pathways) | [readthedocs](https://pathways.readthedocs.io/en/latest/index.html) | Scenario-driven transformations for LCI datasets and workflows, designed for prospective and pathway-based LCA use cases. |
| `regioinvent` | [Regioinvent](https://github.com/CIRAIG/Regioinvent) | GitHub README | Automatically regionalizes ecoinvent by connecting it to the BACI trade database, creating national production processes and consumption markets. |

### Material flow analysis (MFA)

| Package key | GitHub | Docs | Description |
|---|---|---|---|
| `flodym` | [flodym](https://github.com/pik-piam/flodym) | [readthedocs](https://flodym.readthedocs.io/en/latest/) | Flexible Open Dynamic Material Systems Model — Python library for dynamic MFA with dimension-aware arrays (FlodymArray), stock accumulation with age-cohort tracking, and Pydantic-typed system setup. Adaptation of ODYM. |
| `odym` | [ODYM](https://github.com/IndEcol/ODYM) | [readthedocs](https://odym.readthedocs.io/en/latest/) | Open Dynamic Material Systems Model — Python framework for dynamic material flow analysis with object-based system description and dynamic stock modeling. |
| `recc_odym` | [RECC-ODYM](https://github.com/IndEcol/RECC-ODYM) | GitHub README | Resource Efficiency–Climate Change mitigation model built on ODYM. Dynamic MFA of vehicles and buildings across SSP scenarios; assesses 10 material efficiency strategies. |

### Environmentally extended input output analysis

| Package key | GitHub | Docs | Description |
|---|---|---|---|
| `pymrio` | [pymrio](https://github.com/IndEcol/pymrio) | [readthedocs](https://pymrio.readthedocs.io/en/latest/) | Multi-regional input-output (EE MRIO) analysis: auto-download and parse EXIOBASE, WIOD, EORA26, OECD, GLORIA; calculate footprints, trade-embodied impacts. |

---

## Adding a new package

Let us know if you are missing any package!
You can also add an addtional package yourself:

1. Create `packages/{name}/` with an `__init__.py`.
2. Create `packages/{name}/metadata.py` with a `METADATA` dict. Copy `packages/premise/metadata.py` as a template — the key fields are:
   - `name`, `description`, `github_url`, `github_repo`, `readthedocs_slug`, `docs_url`, `install`, `sections`
   - Each section needs `id`, `title`, `url`, `description`.
3. Run the fetch script: `python scripts/fetch_docs.py --package {name}`
4. Restart the server — the new package is discovered automatically.

No changes to `server.py` or any core file are needed.

---

## License

BSD-3-Clause