# Private local REA assistant (starter)

A single-user browser UI using a local Ollama model, with a separate explicit
REA static JavaScript/Electron analysis action. No Python packages, cloud
accounts, paid APIs, or changes to REA core are required. This is not a new
trained model or a Mythos-equivalent system.

## Windows setup

1. Install Python 3.11+, a Node version supported by this checkout (pinned:
   24.22.1), and Ollama from their official distributions. Ensure `python`,
   `node`, and `ollama` work in a new PowerShell terminal.
2. Install REA and download the model (these steps need internet):

   ```powershell
   npm.cmd install --global rea-agents@6.9.0
   ollama pull qwen2.5-coder:7b
   ```

   Model choice is configurable; the 7B default is a starting point, not a
   guarantee of speed or compatibility with your hardware. Model license terms
   still apply. There are no model API fees, but electricity/hardware cost money.
3. Keep Ollama running. If it is not already running via the desktop app, start
   `ollama serve` in another terminal. Keep its default loopback binding.
4. From this repository root:

   ```powershell
   python examples/private-assistant/server.py --analysis-root "$HOME\REA-Targets"
   ```

   Create `REA-Targets` first, or use an existing folder you deliberately choose
   for analysis. Alternatively run `./examples/private-assistant/start-windows.ps1`,
   which creates that folder if missing (subject to your local script policy).
5. Open **http://127.0.0.1:8787** and enter the random access key printed in the
   terminal. Keep that terminal open. Ctrl+C stops the assistant.

For a smaller or different installed model, append `--model MODEL_NAME`.
If REA's global entry cannot be found, set an explicit trusted launcher path:

```powershell
$env:REA_ENTRY = "C:\path\to\node_modules\rea-agents\scripts\rea.mjs"
```

To find your global package directory, run `npm.cmd root -g`. Set `REA_ENTRY`
to `rea-agents\scripts\rea.mjs` within that directory. Windows invocations use
Node directly rather than executing a command shell with target-path arguments.

## Use

- Chat uses Ollama's local API at `127.0.0.1:11434`. The model must already be
  downloaded. No model tool calling is enabled.
- Put an extracted JavaScript/Electron application or ASAR in your analysis
  folder. Enter its relative path in the REA panel and click **Run REA analysis**.
- Inspect the report, then optionally attach it to your next model message.
  Reports and conversations are size-limited. Large investigations should use
  REA directly. No Ghidra installation is needed for this particular action.
- Chat/report data is held in browser/server memory, not intentionally saved.
  Reload clears the displayed conversation. This is not a secure-erasure
  guarantee: OS swap, browser extensions, and other local software may observe it.

## Security and limitations

- Binds only to **127.0.0.1**. Do not expose through a public proxy, port forward,
  or change the binding. Remote phone access is not implemented in this starter.
- Random per-start access key, HttpOnly/SameSite cookie, strict local Host/Origin
  checks, no registration, no external frontend assets, and no shell tool.
  HTTP cookies are used only on loopback; this is not an internet deployment.
- The key is shown in the terminal. Local administrators/processes are outside
  this application's threat boundary. Ollama has its own local API; this login
  does not secure other local services.
- REA analysis resolves paths under the configured root, rejects outside paths,
  and is limited to one fixed static CLI command. It does not intentionally
  execute the target, but parsers still process untrusted files. This folder
  restriction is not an OS sandbox, and must not be treated as one. Do not
  analyze actively hostile artifacts or concurrently replace paths; use a
  disposable VM for untrusted samples. Do not place secrets in the analysis root.
- The model cannot run commands or autonomously invoke REA. Native EXE/DLL,
  Ghidra, uploads, persistent history, and remote access are not implemented.
- Work is serialized. REA output is capped at 2 MB and 120 seconds; this is a
  starter for bounded local tasks, not a job supervisor for arbitrary workloads.

## Checks

```powershell
python -m unittest discover -s examples/private-assistant -p "test_*.py" -v
```

Tests cover HTTP authorization/origin handling, path checks, and mocked model/REA
routes. Real Windows, Ollama inference, and REA end-to-end execution require the
installed tools on your own machine.
