# Installing Sillok from Claude Code — a prompt that works

Asking Claude Code to "install this open source project" from a blog link
produces a half-working install: the MCP tools never appear, and the agent
usually concludes "restart Claude Code" — which does not help, because the
server cannot start at all.

Paste the prompt below instead. It pins the three things an agent cannot
guess, and ends with a verification step, so you find out inside the same
session whether it worked.

---

## The prompt

> Install the Sillok OS open-source harness (https://github.com/sillok-os/sillok)
> and wire it into this project as an MCP server. Follow these steps exactly —
> the published docs contain several stale commands, so do not substitute your
> own.
>
> **1. Clone to a stable path** (not inside this project):
> `D:/sillok-os` on Windows, `~/sillok-os` on macOS/Linux.
>
> **2. Create a dedicated virtualenv inside the clone** and install into it:
>
> ```
> python -m venv <clone>/.venv
> <clone>/.venv/bin/pip install --pre "sillok[mcp]" "mcp<2"
> ```
>
> On Windows the interpreter is `<clone>/.venv/Scripts/python.exe`.
>
> Three constraints that are not optional:
> - `--pre` is required. Plain `pip install sillok` resolves to the `0.0.1`
>   name-reservation placeholder, which contains no submodules.
> - `"mcp<2"` is required. MCP SDK 2.0 removed `mcp.server.fastmcp`, which
>   the Sillok bridge imports; with 2.x the server exits immediately.
> - Install into the venv, not globally, so the `mcp<2` pin cannot collide
>   with other projects.
>
> **3. Verify the CLI before touching any config.** Set `PYTHONIOENCODING=utf-8`
> for every terminal command you run — on a Korean Windows console the default
> code page is `cp949`, which cannot encode the em dash and arrows Sillok
> prints, and the command dies with `UnicodeEncodeError` before doing anything
> wrong:
>
> ```
> # PowerShell
> $env:PYTHONIOENCODING="utf-8"; <venv-python> -m sillok.tongsa tools
> # bash / zsh
> PYTHONIOENCODING=utf-8 <venv-python> -m sillok.tongsa tools
> ```
>
> Expect three lines: `sillok.list_packs`, `sillok.route`, `sillok.search`.
> If this fails, stop and report the error — do not proceed to step 4.
>
> **4. Write `.mcp.json` in this project's root** (not `.claude/mcp.json`,
> not `settings.json` — Claude Code does not read `mcpServers` from either).
> Use forward slashes in the path even on Windows:
>
> ```json
> {
>   "mcpServers": {
>     "sillok": {
>       "command": "D:/sillok-os/.venv/Scripts/python.exe",
>       "args": [
>         "-c",
>         "import os;os.chdir('D:/sillok-os');from sillok.tongsa.__main__ import cli;cli()",
>         "serve", "--transport", "stdio"
>       ],
>       "env": { "PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8" }
>     }
>   }
> }
> ```
>
> The `os.chdir` wrapper is load-bearing on the currently published release:
> the wheel ships code but not the pack registry, and the registry is read
> from a path relative to the working directory. An MCP server inherits *this*
> project's directory, so without the chdir it raises
> `FileNotFoundError: packs/registry.yaml`. Drop the wrapper only once you are
> on a release whose wheel bundles `sillok/_packs/`.
>
> **5. Prove the tools actually answer before declaring success** — run the
> same entry point the MCP config uses, so a failure shows up here rather than
> after the restart:
>
> ```
> # PowerShell
> $env:PYTHONIOENCODING="utf-8"
> <venv-python> -c "import os;os.chdir('D:/sillok-os');from sillok.tongsa.__main__ import cli;cli()" smoke
> ```
>
> Expect a pack count (25 on the current release) and at least one routed pack
> with reason codes. `FileNotFoundError: packs/registry.yaml` here means the
> chdir path is wrong.
>
> **6. Then tell me to restart Claude Code.** MCP servers connect at startup,
> so the `sillok.*` tools will not appear in this session no matter what you
> do. Do not report the install as complete while claiming the tools are
> available — say explicitly that a restart is required, and what I should see
> after it.

---

## Why the naive prompt fails

| What the agent sees | What is actually wrong |
|---|---|
| `pip install sillok` succeeds | Installed `0.0.1`, a placeholder with no submodules |
| `pip install sillok[mcp]` "already satisfied" | `mcp` 2.x is installed; the bridge needs 1.x |
| `ImportError: requires the optional 'mcp' package` | Misleading — `mcp` *is* installed, just incompatible |
| `.mcp.json` exists and looks right | Server exits before registering any tool |
| "MCP not registered — restart needed" | Restarting changes nothing; the server never starts |
| CLI fallback also dies | `UnicodeEncodeError: 'cp949' ... '\u2014'` on Korean Windows |

Each of these is fixed in the repository; the prompt above is what you need
until a release carrying those fixes is published to PyPI.
