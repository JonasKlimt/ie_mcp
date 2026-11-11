# Install ie-mcp (instructions for AI agents)

**Audience: an AI coding agent (Claude Code, Codex, GitHub Copilot) that was given the link to this repository by a user.** Humans: see [Manual setup in the README](README.md#manual-setup).

**Goal:** register the MCP server `ie-mcp` once, at **user level**, so it is available in **all** of the user's projects. Install it for the client you are running in. Install it for other clients only if the user asks.

**Rules:**

- Do **not** clone this repository, do **not** `pip install` anything into the user's Python environments, and do **not** create project-level config files (`.mcp.json`, `.vscode/mcp.json`, `.codex/`). The server is started on demand by `uvx` in its own isolated environment.
- Do **not** commit, push or change files in the user's current project.
- Back up a config file before editing it, keep all existing content, and write valid JSON or TOML.
- A GitHub token the user gives you is a secret: never repeat it, and write it only into the client's MCP configuration (step 3).
- The only file you may write besides the client's MCP configuration is the optional user-level rule of step 8, and only after the user said yes to it.
- Never claim that the server works until step 7 succeeded. Say what you could not verify.

## The server definition

Every client registers the same thing:

| Field | Value |
|---|---|
| name | `ie-mcp` |
| transport | `stdio` |
| command | `uvx` |
| args | `--from`, `git+https://github.com/JonasKlimt/ie_mcp`, `ie-mcp` |
| env | none required; optional `GITHUB_TOKEN` (step 3) |

## Step 1: Check the prerequisites

Run `uvx --version` and `git --version`. Both must work. (`uv` provides `uvx`; Git is needed because the server is fetched from GitHub.)

If `uv` is missing, tell the user and ask for permission before you install it, because the installer is a script downloaded from the internet. Then run:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

(first line for Windows, second for macOS and Linux). If `git` is missing, ask the user to install it from https://git-scm.com/downloads. A freshly installed `uvx` is often not on the `PATH` of the running session yet. Use its absolute path in the next steps (Windows: `%USERPROFILE%\.local\bin\uvx.exe`; macOS and Linux: `~/.local/bin/uvx`).

## Step 2: Choose the `command` value

- Desktop apps (Claude Code desktop app, Codex app, VS Code) often do **not** inherit the shell `PATH`, especially on Windows. Use the **absolute path** of `uvx` as `command` (find it with `where uvx` on Windows or `which uvx` elsewhere).
- If you are certain the client starts servers from a shell that has `uvx` on its `PATH`, plain `uvx` is fine.

Below, `<UVX>` means the value you chose.

## Step 3: Offer a GitHub token (optional)

Most answers are read from the user's own environment or from PyPI, so a token is not required. GitHub is used for versions that are not on PyPI, for tag lists and for the changelog tool. Without a token GitHub allows only **60 requests per hour**; with a free token **5,000 per hour**. Ask the user **once**, before you register the server, so the token goes into the configuration in step 5. Use this wording (adapt the language to the user):

> Do you want to add a free GitHub token, so that ie-mcp can fetch much more from GitHub (5,000 instead of 60 requests per hour)? It is optional. How to create it:
>
> 1. Open https://github.com/settings/tokens and sign in.
> 2. Click **Generate new token**, then **Generate new token (classic)**.
> 3. Name it `ie-mcp` and choose an expiration date (for example 90 days).
> 4. Leave **all scope boxes unticked**. No permissions are needed, the token can only read public data.
> 5. Click **Generate token** at the bottom and copy the token (it starts with `ghp_` and GitHub shows it only once).
> 6. Paste it here in the chat. Or answer "skip".
>
> Note: a token pasted in the chat is part of the conversation with your AI provider. Because it has no scopes it can only read public data, and you can revoke it at any time at the same page. If you prefer, skip this and add it yourself later (README, section "GitHub token").

What to do with the answer:

- **"skip", no answer, or no token:** continue without a token and do not ask again.
- **A token:** check only that it is one line without spaces and starts with `ghp_` or `github_pat_`; if not, ask the user to check it (do not repeat what they sent). Then put it into the `env` of the `ie-mcp` entry as `GITHUB_TOKEN` when you register the server in step 5 (or into the existing entry if step 4 finds one). Below, `<TOKEN>` means this value.
- **Handle the token as a secret.** Do not repeat it in any message, command you display, log or report (write "token added" instead). Write it only into the client's MCP configuration from step 5, never into a file of the user's project, and never commit it. That configuration file keeps it as plain text, so tell the user which file holds it (step 9).
- A fine-grained token with read-only access to public repositories works as well. If the token expires or is revoked, GitHub requests fail with an authorisation error and the limit falls back to 60 per hour. The user then creates a new token the same way.

## Step 4: Check whether it is already installed

Look for an existing `ie-mcp` entry (`claude mcp list`, `codex mcp list`, or open the config file from step 5). If it exists and points to this repository, do not add a duplicate; tell the user it is already installed and go to step 7 (but add the token from step 3 to its `env`, if the user gave one). If it exists with different arguments, update that entry.

## Step 5: Register the server at user level

Use the part for the client you are running in. If the user gave a token in step 3, add it as shown in each part (`<TOKEN>`); without a token, leave the `env` out (or empty).

### Claude Code

Preferred, if the `claude` command exists:

```bash
claude mcp add ie-mcp --scope user --transport stdio -- <UVX> --from git+https://github.com/JonasKlimt/ie_mcp ie-mcp
```

With a token, add `--env GITHUB_TOKEN=<TOKEN>` before the `--`:

```bash
claude mcp add ie-mcp --scope user --transport stdio --env GITHUB_TOKEN=<TOKEN> -- <UVX> --from git+https://github.com/JonasKlimt/ie_mcp ie-mcp
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

With a token, use `"env": { "GITHUB_TOKEN": "<TOKEN>" }` instead of `"env": {}`.

In JSON, write backslashes in Windows paths twice (`C:\\Users\\you\\.local\\bin\\uvx.exe`).

### Codex (app, IDE extension or terminal)

Preferred, if the `codex` command exists:

```bash
codex mcp add ie-mcp -- <UVX> --from git+https://github.com/JonasKlimt/ie_mcp ie-mcp
```

With a token, add `--env GITHUB_TOKEN=<TOKEN>` right after the name (`codex mcp add ie-mcp --env GITHUB_TOKEN=<TOKEN> -- <UVX> ...`), or add the table shown below to the config file.

Otherwise add this block to `~/.codex/config.toml` (Windows: `%USERPROFILE%\.codex\config.toml`; or `$CODEX_HOME/config.toml` if that variable is set). The app, the IDE extension and the terminal share this file. `startup_timeout_sec` is raised because the very first start downloads the server:

```toml
[mcp_servers.ie-mcp]
command = "<UVX>"
args = ["--from", "git+https://github.com/JonasKlimt/ie_mcp", "ie-mcp"]
startup_timeout_sec = 120

# only if the user gave a token in step 3
[mcp_servers.ie-mcp.env]
GITHUB_TOKEN = "<TOKEN>"
```

In TOML, write a Windows path as a literal string in single quotes: `command = 'C:\Users\you\.local\bin\uvx.exe'`. If `codex mcp add` was used, add the `startup_timeout_sec = 120` line to the new block afterwards.

### GitHub Copilot (VS Code)

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

With a token, add `"env": { "GITHUB_TOKEN": "<TOKEN>" }` to the `ie-mcp` entry, after `args`. If the user does not want a token stored as plain text in this file, VS Code can ask for it itself: add `"inputs": [{ "type": "promptString", "id": "ie-mcp-github-token", "description": "GitHub token for ie-mcp", "password": true }]` next to `servers` and use `"env": { "GITHUB_TOKEN": "${input:ie-mcp-github-token}" }`. VS Code then asks for the token when the server starts, and the user types it there instead of in the chat.

If you cannot write the file, tell the user to run **MCP: Open User Configuration** in the Command Palette and paste this content.

## Step 6: Download the server once (warm-up and test)

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

## Step 7: Verify

- Where the client offers a check, run it: `claude mcp list` or `codex mcp list`. In VS Code the user can see the server state in the Command Palette under **MCP: List Servers**.
- A running session usually does not see a newly added server. Remember to tell the user (step 9) to restart the app (Claude Code, Codex) or run MCP: List Servers → ie-mcp → Start (VS Code), and to open a new chat/session.

## Step 8 (optional): Offer an always-on rule

The server sends its routing rules and trigger terms to the AI client by itself when it connects. Some clients may not pass them on to the model, and a model may still not think of the server for a plain LCA question. A short rule in the user's **user-level** instruction file, which applies to every project, closes that gap. It is optional and it edits a file outside the MCP configuration, so:

1. **Ask first.** Say what you would write and where, for example: *"Do you also want me to add a short rule to `<file>`, so that your assistant uses ie-mcp automatically for Brightway, premise, ecoinvent-tool, LCA and material-flow questions in every project? It adds 5 lines, and I back up the file first."* Continue only on a clear yes. If the user says no or does not answer, skip this step and do not ask again.
2. Pick the file for the client you installed for:

   | Client | User-level file |
   |---|---|
   | Claude Code | `~/.claude/CLAUDE.md` (Windows: `%USERPROFILE%\.claude\CLAUDE.md`) |
   | Codex | `~/.codex/AGENTS.md` (Windows: `%USERPROFILE%\.codex\AGENTS.md`; or `$CODEX_HOME/AGENTS.md`) |
   | GitHub Copilot (VS Code) | A new file `ie-mcp.instructions.md` in the `prompts` folder of the VS Code user profile. Windows: `%APPDATA%\Code\User\prompts\`, macOS: `~/Library/Application Support/Code/User/prompts/`, Linux: `~/.config/Code/User/prompts/` (for VS Code Insiders replace `Code` with `Code - Insiders`). For a non-default profile, or if the folder does not exist, ask the user to run **Chat: New Instructions File…** in the Command Palette, choose the user profile, and paste the rule. |

3. Back up the file first if it exists. Never overwrite it: keep all existing content and append the block.
4. Write this block. In the Copilot file, put these three lines above it: `---`, `applyTo: "**"`, `---`.

   ```markdown
   <!-- ie-mcp:start -->
   ## ie-mcp (Industrial Ecology packages)
   For questions about Brightway, premise, ecoinvent tools, LCA or material flow analysis, and for code that imports such packages, use the `ie-mcp` MCP tools first, even if I do not mention them. Start by calling `set_python_environment` with the Python of my project, then follow the server instructions. Always say which package version and source an answer is based on.
   <!-- ie-mcp:end -->
   ```

5. If the two marker comments already exist in the file, replace the text between them instead of adding a second block.
6. Tell the user which file you changed, where the backup is, and how to undo it: delete the block between the markers (or delete the Copilot file).

## Step 9: Report to the user

Report:

- which client you configured, which file you changed (and where the backup is), the `command` you used, and the result of step 6;
- whether the optional rule of step 8 was added (and where) or skipped;
- whether a GitHub token was added (say only "token added", never the token itself), which file holds it as plain text, and that the user can revoke or renew it at https://github.com/settings/tokens;
- that the app must be restarted (Claude Code, Codex) or the server started (VS Code), and a new chat opened.

Give the user this test question for the new session: *"Use ie-mcp to show which Python environment it inspects."* The answer must name a Python interpreter and list installed package versions. A second test, without mentioning ie-mcp: *"How do I run a basic LCA in Brightway?"* The assistant should call the ie-mcp tools.

You do not need to ask the user for a Python environment. Once the server runs, its own instructions tell the assistant how to find the right environment for each project.
