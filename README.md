# ie_mcp

![Python](https://img.shields.io/badge/python-%E2%89%A53.10-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-BSD--3--Clause-green)
![MCP](https://img.shields.io/badge/MCP-server-blueviolet)
![Packages](https://img.shields.io/badge/packages-56-orange)

Using the **ie_mcp** server makes coding with AI agents and Industrial Ecology packages, especially Brightway, much easier. It reads the source code of the package version **installed in your own environment** and the matching documentation, so you avoid mixed package versions, wrong references, and hallucinated answers. Ask it anything about a registered package (installation, usage, API, concepts) from GitHub Copilot in VS Code, Claude Code or Codex.

> [!TIP]
> **Quick start: let your AI agent install it.** Paste the link to this repository (`https://github.com/JonasKlimt/ie_mcp`) into a chat with Claude Code, Codex or GitHub Copilot (Agent mode in VS Code) and write: *"Install this MCP server for me, for all my projects."* The agent reads the section [Install (instructions for AI agents)](#install-instructions-for-ai-agents) below and does the rest. Afterwards you restart the app once.

> [!NOTE]
> **What is an MCP server?**
>
> An MCP (Model Context Protocol) server is a bridge between an AI assistant and trusted external information. Check this link to learn more about MCP servers: https://modelcontextprotocol.io/docs/getting-started/intro. In the case of the ie_mcp server the assistant can call this server to check package docs, source code, and versions before it answers.

**Currently supported packages:** The full Brightway LCA ecosystem, and additional industrial ecology tools — 56 packages total (see [Brightway ecosystem](#brightway-ecosystem) and [Additional packages](#additional-packages) below)

<details>
<summary>📋 Table of contents</summary>

- [Install (instructions for AI agents)](#install-instructions-for-ai-agents)
- [Manual setup](#manual-setup)
- [Why?](#why)
- [Example questions](#example-questions)
- [Configuration](#configuration)
- [Every answer shows its source](#every-answer-shows-its-source)
- [GitHub token (optional)](#github-token-optional)
- [How the server works](#how-the-server-works)
- [Brightway ecosystem](#brightway-ecosystem)
- [Additional packages](#additional-packages)

</details>

---

## Install (instructions for AI agents)

**Audience: an AI coding agent (Claude Code, Codex, GitHub Copilot) that was given the link to this repository by a user.** Humans can skip to [Manual setup](#manual-setup).

**Goal:** register the MCP server `ie-mcp` once, at **user level**, so it is available in **all** of the user's projects. Install it for the client you are running in. Install it for other clients only if the user asks.

**Rules:**

- Do **not** clone this repository, do **not** `pip install` anything into the user's Python environments, and do **not** create project-level config files (`.mcp.json`, `.vscode/mcp.json`, `.codex/`). The server is started on demand by `uvx` in its own isolated environment.
- Do **not** commit, push or change files in the user's current project.
- Back up a config file before editing it, keep all existing content, and write valid JSON or TOML.
- Never claim that the server works until step 6 succeeded. Say what you could not verify.

### The server definition

Every client registers the same thing:

| Field | Value |
|---|---|
| name | `ie-mcp` |
| transport | `stdio` |
| command | `uvx` |
| args | `--from`, `git+https://github.com/JonasKlimt/ie_mcp`, `ie-mcp` |
| env | none needed |

### Step 1: Check the prerequisites

Run `uvx --version` and `git --version`. Both must work. (`uv` provides `uvx`; Git is needed because the server is fetched from GitHub.)

If `uv` is missing, tell the user and ask for permission before you install it, because the installer is a script downloaded from the internet. Then run:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

(first line for Windows, second for macOS and Linux). If `git` is missing, ask the user to install it from https://git-scm.com/downloads. A freshly installed `uvx` is often not on the `PATH` of the running session yet. Use its absolute path in the next steps (Windows: `%USERPROFILE%\.local\bin\uvx.exe`; macOS and Linux: `~/.local/bin/uvx`).

### Step 2: Choose the `command` value

- Desktop apps (Claude Code desktop app, Codex app, VS Code) often do **not** inherit the shell `PATH`, especially on Windows. Use the **absolute path** of `uvx` as `command` (find it with `where uvx` on Windows or `which uvx` elsewhere).
- If you are certain the client starts servers from a shell that has `uvx` on its `PATH`, plain `uvx` is fine.

Below, `<UVX>` means the value you chose.

### Step 3: Check whether it is already installed

Look for an existing `ie-mcp` entry (`claude mcp list`, `codex mcp list`, or open the config file from step 4). If it exists and points to this repository, do not add a duplicate; tell the user it is already installed and go to step 6. If it exists with different arguments, update that entry.

### Step 4: Register the server at user level

Use the part for the client you are running in.

#### Claude Code

Preferred, if the `claude` command exists:

```bash
claude mcp add --scope user --transport stdio ie-mcp -- <UVX> --from git+https://github.com/JonasKlimt/ie_mcp ie-mcp
```

If there is no `claude` command (for example in the desktop app), edit `~/.claude.json` (Windows: `%USERPROFILE%\.claude.json`). Back it up first. Keep every existing key. Add `ie-mcp` to the **top-level** `mcpServers` object (create it if missing; do not put it inside `projects`):

```json
"mcpServers": {
  "ie-mcp": {
    "type": "stdio",
    "command": "<UVX>",
    "args": ["--from", "git+https://github.com/JonasKlimt/ie_mcp", "ie-mcp"],
    "env": {}
  }
}
```

In JSON, write backslashes in Windows paths twice (`C:\\Users\\you\\.local\\bin\\uvx.exe`).

#### Codex (app, IDE extension or terminal)

Preferred, if the `codex` command exists:

```bash
codex mcp add ie-mcp -- <UVX> --from git+https://github.com/JonasKlimt/ie_mcp ie-mcp
```

Otherwise add this block to `~/.codex/config.toml` (Windows: `%USERPROFILE%\.codex\config.toml`; or `$CODEX_HOME/config.toml` if that variable is set). The app, the IDE extension and the terminal share this file. `startup_timeout_sec` is raised because the very first start downloads the server:

```toml
[mcp_servers.ie-mcp]
command = "<UVX>"
args = ["--from", "git+https://github.com/JonasKlimt/ie_mcp", "ie-mcp"]
startup_timeout_sec = 120
```

In TOML, write a Windows path as a literal string in single quotes: `command = 'C:\Users\you\.local\bin\uvx.exe'`. If `codex mcp add` was used, add the `startup_timeout_sec = 120` line to the new block afterwards.

#### GitHub Copilot (VS Code)

Edit the **user-level** MCP file `mcp.json` (create it if missing). Do not use `.vscode/mcp.json` in the project.

| System | Path |
|---|---|
| Windows | `%APPDATA%\Code\User\mcp.json` |
| macOS | `~/Library/Application Support/Code/User/mcp.json` |
| Linux | `~/.config/Code/User/mcp.json` |

For VS Code Insiders, replace `Code` with `Code - Insiders`; for a non-default VS Code profile, the user can open the right file with the Command Palette command **MCP: Open User Configuration**. Add the entry under the top-level `servers` object and keep other servers:

```json
{
  "servers": {
    "ie-mcp": {
      "type": "stdio",
      "command": "<UVX>",
      "args": ["--from", "git+https://github.com/JonasKlimt/ie_mcp", "ie-mcp"]
    }
  }
}
```

If you cannot write the file, tell the user to run **MCP: Open User Configuration** in the Command Palette and paste this content.

### Step 5: Download the server once (warm-up and test)

The first start downloads the server from GitHub and can take up to a minute, which may exceed a client's start-up time-out. Run the server once by hand so it is cached. It reads one JSON line on stdin, so this command ends by itself.

Bash (macOS, Linux, Git Bash):

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"check","version":"0"}}}' | <UVX> --from git+https://github.com/JonasKlimt/ie_mcp ie-mcp
```

PowerShell:

```powershell
'{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"check","version":"0"}}}' | & <UVX> --from git+https://github.com/JonasKlimt/ie_mcp ie-mcp
```

Success: the output is one JSON line that contains `"serverInfo":{"name":"ie-mcp"`. If it fails: `git` missing from `PATH`, no internet or a proxy blocks `github.com` and `pypi.org`, or `uvx` is not found (then fix the path from step 2).

### Step 6: Verify and report to the user

- Where the client offers a check, run it: `claude mcp list` or `codex mcp list`. In VS Code the user can see the server state in the Command Palette under **MCP: List Servers**.
- A running session usually does not see a newly added server. **Tell the user to restart the app (Claude Code, Codex) or run MCP: List Servers → ie-mcp → Start (VS Code), and to open a new chat/session.**
- Report: which client you configured, which file you changed (and where the backup is), the `command` you used, and the result of step 5.
- Give the user this test question for the new session: *"Use ie-mcp to show which Python environment it inspects."* The answer must name a Python interpreter and list installed package versions.

You do not need to ask the user for a Python environment. Once the server runs, its own instructions tell the assistant how to find the right environment for each project.

---

## Manual setup

Prefer to do it yourself? Two steps: install `uv` once, then add the server to your AI app. You do not have to clone this repository, and nothing is installed into your research environment. Each way below registers the server once for **all** your projects.

### Step 1: Install uv

[uv](https://docs.astral.sh/uv/) starts the server in its own small environment. Open a terminal and run the line for your system.

Windows (PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

macOS and Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then **close and reopen your AI app** (and the terminal), so it can find the new `uvx` command. Check with `uvx --version`. You also need [Git](https://git-scm.com/downloads); check with `git --version`.

### Step 2: Add the server to your AI app

In every app you register the same start command:

```bash
uvx --from git+https://github.com/JonasKlimt/ie_mcp ie-mcp
```

Do not run this line yourself. Your AI app runs it in the background. Below is where to put it.

#### Claude Code (Code tab of the desktop app, or terminal)

Run this once in a terminal (PowerShell, Terminal). It needs the `claude` command of the Claude Code CLI:

```bash
claude mcp add --scope user --transport stdio ie-mcp -- uvx --from git+https://github.com/JonasKlimt/ie_mcp ie-mcp
```

Then start a new session. Check with `claude mcp list`. Without the `claude` command, paste this repository's link into Claude Code and ask it to install the server (see the quick start at the top).

#### Codex (desktop app, IDE extension or terminal)

In the desktop app:

1. Open **Settings** and select **MCP servers**.
2. Select **Add server**.
3. Name: `ie-mcp`. Type: **STDIO**. Command: `uvx`. Arguments: `--from`, `git+https://github.com/JonasKlimt/ie_mcp`, `ie-mcp`.
4. Save, then select **Restart**.

In the IDE extension the same form is under the gear menu → **MCP servers**. In a terminal, this command does the same:

```bash
codex mcp add ie-mcp -- uvx --from git+https://github.com/JonasKlimt/ie_mcp ie-mcp
```

The app, the IDE extension and the terminal share one configuration (`~/.codex/config.toml`), so you only do this once and it applies to all your projects.

#### VS Code (GitHub Copilot)

Open the Command Palette (`Ctrl+Shift+P`, on macOS `Cmd+Shift+P`), run **MCP: Open User Configuration**, and paste this content into the `mcp.json` file that opens. If the file already has servers, add only the `ie-mcp` entry inside `servers`:

```json
{
  "servers": {
    "ie-mcp": {
      "type": "stdio",
      "command": "uvx",
      "args": ["--from", "git+https://github.com/JonasKlimt/ie_mcp", "ie-mcp"]
    }
  }
}
```

Save the file and click **Start** above the server name. The server is now available in Copilot Chat (Agent mode) in every folder you open.

> [!NOTE]
> For best results with Copilot, also copy the instruction file (`.github/copilot-instructions.md`) into the `.github` folder of a project. It tells Copilot when to use ie_mcp and how to handle versions. This file works per project.

### Step 3: Check that it works

Ask your assistant: *"Use ie-mcp to show which Python environment it inspects."* The answer names the Python interpreter and the installed version of every registered package.

---

## Why?

For modelling work, you need reliable help that matches your real environment and package versions. This server gives environment- and version-relevant explanations for both single functions and complete IE package workflows. This makes going through pages of package documentation and checking its GitHub pages redundant. Copilot can access information about the package and get relevant explantion/coding help for the exact package version you are using.

## Example questions

- "How do I do a basic LCA in Brightway from setup to first result?"
- "How do I use premise for prospective LCA scenarios?"
- "How do I use the function [...]?
- "Explain what arguments the function takes in the package version that is currently installed in my environment."
- ...

---

## Configuration

### How the server finds your environment

You do not have to configure your Python environment. The assistant looks up the interpreter of the file, notebook or project you are working on and passes it to the server. If it cannot tell which environment you use, it asks you. You can also just say it: *"Use my conda environment `bw` for ie-mcp."*

Without that, the server uses an environment that was active when your AI app started, or a `.venv` folder in your project. Every answer shows the interpreter that was inspected, so you can always check. The server only reads the environment; it never imports your packages and never installs anything.

### Optional settings

These are environment variables for the server. Most users need none of them. They go in the `env` block of the server entry (`"env": {"NAME": "value"}`), in Codex in an `[mcp_servers.ie-mcp.env]` table of `config.toml` (or the environment variables of the server form), and in the `claude mcp add` command as `--env NAME=value` before the `--`.

| Variable | Meaning |
|---|---|
| `IE_MCP_TARGET_PYTHON` | Always start with this Python executable as the environment to inspect, for example `C:/Users/you/miniconda3/envs/bw/python.exe`. The assistant can still switch to another one. |
| `IE_MCP_CACHE_DIR` | Folder for downloaded docs and source files. Default: `~/.cache/ie_mcp`. |
| `GITHUB_TOKEN` | Optional, see below. |

> [!NOTE]
> The server finds packages installed in the environment itself (conda, venv, `pip install`, `pip install -e`). Packages that are only reachable through `PYTHONPATH` or a `pip install --user` folder are not seen.

---

## Every answer shows its source

Results of the source tools state where the information comes from:

| Field | Meaning |
|---|---|
| `source` | `local` (your installed files), `pypi` (a release downloaded from PyPI) or `github` |
| `version` | the exact version the code comes from |
| `installed_version` | what is installed in your environment (or `null`) |
| `file` | the file the code was read from |
| `python_executable` | the interpreter that was inspected |

Documentation results state the `docs_version` that was read and your `installed_version`, with a warning if they differ. Many packages only publish docs for their latest version, so this is a common cause of wrong answers (for example mixed Brightway 2 and 2.5 syntax).

---

## GitHub token (optional)

> [!TIP]
> You usually do not need a token. Your installed version is read from disk, and other released versions are downloaded from PyPI. GitHub is only used for versions that are **not on PyPI** (for example `HEAD` or an unreleased branch) and for listing tags. Without a token GitHub allows **60 requests/hour**, enough for light use. A free personal access token raises the limit to **5 000 requests/hour**.

1. Go to [github.com → Settings → Developer settings → Personal access tokens → Tokens (classic)](https://github.com/settings/tokens)
2. Click **Generate new token (classic)**, give it a name, set an expiry. **No scopes are needed** for public repos.
3. Add it to the server entry of your configuration:

```json
"ie-mcp": {
  "command": "uvx",
  "args": ["--from", "git+https://github.com/JonasKlimt/ie_mcp", "ie-mcp"],
  "env": {
    "GITHUB_TOKEN": "ghp_your_token"
  }
}
```

> [!IMPORTANT]
> Do not commit a configuration file that contains your token.


## How the server works

1. **Your environment first.** The assistant tells the server which Python environment your project uses, and the server asks that Python which package versions are installed. If you do not mention a version, this is the version it answers for.
2. **Local source code.** Functions, methods and classes are read directly from the installed files on your disk. This is fast, needs no internet, and always matches your version.
3. **Other versions from PyPI.** If you ask about another version, that exact release is downloaded from PyPI once and cached.
4. **GitHub as the last resort.** Only versions that are not on PyPI (for example `HEAD`) are read from GitHub, at that exact tag or branch.
5. **Docs for context.** Official documentation pages are fetched when needed and cached. They provide workflows and examples; signatures come from the source code. A version mismatch between docs and installed code is reported.
6. **Not installed?** The server says so and shows which interpreter it inspected. The assistant checks that this is the right environment and asks you before it falls back to the latest version.

This keeps answers reliable, version-correct, and grounded in official docs or source.

### Development

```bash
pip install -e ".[dev]"
pytest              # offline tests
pytest -m network   # tests that need PyPI and GitHub
```

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

<details>
<summary>Show all 23 packages</summary>

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

</details>

---

## Additional packages

### LCA tools

<details>
<summary>Show 4 packages</summary>

| Package key | GitHub | Docs | Description |
|---|---|---|---|
| `edges` | [edges](https://github.com/Laboratory-for-Energy-Systems-Analysis/edges) | [readthedocs](https://edges.readthedocs.io/en/stable/) | Edge-based LCIA for Brightway: context-sensitive characterization factors applied to exchanges, not just flows. Includes AWARE 2.0, ImpactWorld+, GeoPolRisk, GLAM3. |
| `lca_algebraic` | [lca_algebraic](https://github.com/oie-mines-paristech/lca_algebraic) | [readthedocs](https://lca-algebraic.readthedocs.io/en/stable/) | Parametric LCA inventories with fast Monte Carlo and Sobol sensitivity analysis, using Sympy expressions. Built on Brightway2/2.5. |
| `pathways` | [pathways](https://github.com/polca/pathways) | [readthedocs](https://pathways.readthedocs.io/en/latest/index.html) | Scenario-driven transformations for LCI datasets and workflows, designed for prospective and pathway-based LCA use cases. |
| `regioinvent` | [Regioinvent](https://github.com/CIRAIG/Regioinvent) | GitHub README | Automatically regionalizes ecoinvent by connecting it to the BACI trade database, creating national production processes and consumption markets. |

</details>

### Material flow analysis (MFA)

<details>
<summary>Show 3 packages</summary>

| Package key | GitHub | Docs | Description |
|---|---|---|---|
| `flodym` | [flodym](https://github.com/pik-piam/flodym) | [readthedocs](https://flodym.readthedocs.io/en/latest/) | Flexible Open Dynamic Material Systems Model — Python library for dynamic MFA with dimension-aware arrays (FlodymArray), stock accumulation with age-cohort tracking, and Pydantic-typed system setup. Adaptation of ODYM. |
| `odym` | [ODYM](https://github.com/IndEcol/ODYM) | [readthedocs](https://odym.readthedocs.io/en/latest/) | Open Dynamic Material Systems Model — Python framework for dynamic material flow analysis with object-based system description and dynamic stock modeling. |
| `recc_odym` | [RECC-ODYM](https://github.com/IndEcol/RECC-ODYM) | GitHub README | Resource Efficiency–Climate Change mitigation model built on ODYM. Dynamic MFA of vehicles and buildings across SSP scenarios; assesses 10 material efficiency strategies. |

</details>

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

Contibutions are welcome!

---

## License

BSD-3-Clause
