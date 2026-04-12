# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**virtuoso-bridge-lite** is a Python bridge for remotely controlling Cadence Virtuoso via SKILL execution over SSH tunnels. It enables LLM agents to automate analog/mixed-signal design tasks across schematic editing, layout generation, Maestro simulation setup, and standalone Spectre simulation.

Key architectural decisions:
- **String-based SKILL execution** rather than Pythonic object mapping (unlike skillbridge)
- **SSH-first design** with automatic tunnel management and jump host support
- **Context manager-based editing APIs** for layout/schematic (`with client.layout.edit() as layout:`)
- **AI-native CLI** (`virtuoso-bridge start/status/restart`) with skill files in `skills/`

## Common Development Commands

### Setup and Installation
```bash
# Create virtual environment and install (use uv, never global Python)
uv venv .venv && source .venv/bin/activate  # Windows: source .venv/Scripts/activate
uv pip install -e ".[dev]"

# Initialize configuration
virtuoso-bridge init  # Creates .env template
```

### Testing
```bash
# Run all tests
pytest

# Run a single test file
pytest tests/test_bridge.py

# Run with verbose output
pytest -v
```

### CLI Usage (while developing)
```bash
# Start/stop/restart SSH tunnel
virtuoso-bridge start
virtuoso-bridge status  # Shows tunnel + daemon + Spectre status
virtuoso-bridge restart
virtuoso-bridge stop

# Multi-profile (connect to multiple servers)
virtuoso-bridge start -p worker1
virtuoso-bridge status -p worker1

# Spectre simulation management
virtuoso-bridge license          # Check Spectre license
virtuoso-bridge sim-jobs         # List running simulations
virtuoso-bridge sim-cancel <id>  # Cancel a job

# X11 dialog recovery (when SKILL channel is blocked)
virtuoso-bridge dismiss-dialog
```

### Environment Variables (.env file)
```bash
VB_REMOTE_HOST=my-server        # SSH host alias from ~/.ssh/config
VB_REMOTE_USER=username         # SSH username
VB_REMOTE_PORT=65081            # Remote daemon port
VB_LOCAL_PORT=65082             # Local forwarded port
VB_JUMP_HOST=jump-host          # Optional bastion/jump host
VB_CADENCE_CSHRC=/path/.cshrc   # For Spectre PATH setup
```

For multi-profile setups, append profile suffix: `VB_REMOTE_HOST_worker1`, `VB_REMOTE_USER_worker1`, etc.

## High-Level Architecture

### Three-Layer Design

```
┌─────────────────────────────────────────────────────────────┐
│  Application Layer                                           │
│  ├── VirtuosoClient (SKILL execution)                       │
│  ├── LayoutOps / SchematicOps (context managers)            │
│  ├── Maestro session (read_config, write, run_sim)          │
│  └── SpectreSimulator (standalone simulation)               │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│  Transport Layer (SSHClient)                                 │
│  ├── SSH tunnel with ControlMaster (persistent connection)  │
│  ├── Port forwarding (-L local:remote)                      │
│  ├── File transfer (rsync/scp via SSHRunner)                │
│  └── Remote command execution                               │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│  Daemon Layer (on remote host)                               │
│  ├── ramic_daemon.py (TCP server, relays SKILL to stdout)   │
│  └── Virtuoso CIW with ramic_bridge.il loaded               │
└─────────────────────────────────────────────────────────────┘
```

### Two Operating Modes

**Remote Mode** (production):
- SSH tunnel auto-established via `virtuoso-bridge start`
- Daemon deployed to remote, loaded in Virtuoso CIW
- All traffic flows through encrypted tunnel

**Local Mode** (development/testing):
- No SSH, no .env required
- Load `core/ramic_bridge.il` directly in local Virtuoso
- `VirtuosoClient.local(port=65432)`

### SKILL Bridge Protocol

The communication protocol between Python and Virtuoso uses delimited messages:

```
Request (JSON over TCP):  {"skill": "1+2", "timeout": 30}

Response format:
  Success: \x02<result>\x1e
  Error:   \x15<error_message>\x1e
```

Markers: `\x02` (STX = success), `\x15` (NAK = error), `\x1e` (RS = end of record)

The daemon (`ramic_daemon.py`) receives TCP, writes SKILL to stdout (Virtuoso's IPC), reads result from stdin, returns via TCP.

## Key Code Patterns

### VirtuosoClient Usage Patterns

```python
from virtuoso_bridge import VirtuosoClient

# Remote mode (uses SSH tunnel from .env)
client = VirtuosoClient.from_env()

# Local mode
client = VirtuosoClient.local(port=65432)

# Execute raw SKILL
result = client.execute_skill("1+2")  # VirtuosoResult with status/output/errors

# File operations
client.upload_file("local.py", "/tmp/remote.py")
client.download_file("/tmp/remote.raw", "local.raw")

# Load IL file (auto-uploads if remote)
client.load_il("my_script.il")
```

### Layout Editing Context Manager

```python
# Pattern: open cellview → queue ops → auto-save on success
with client.layout.edit("myLib", "myCell", mode="w") as layout:
    layout.add(layout_create_rect("M1", "drawing", 0, 0, 10, 10))
    layout.add(layout_create_inst("tsmcN28", "nch_mac", "M0", 0, 0))
# Automatic: dbSave() on success, rollback on exception
```

### Schematic Editing

```python
with client.schematic.edit("myLib", "inv") as sch:
    sch.add(schematic_create_inst_by_master_name("tsmcN28", "pch_mac", "MP0", 0, 1.5, "R0"))
    # Use add_net_label_to_transistor() for MOS wiring, NOT manual add_wire
    sch.add_net_label_to_transistor("MP0", drain_net="OUT", gate_net="IN", source_net="VDD")
```

### Maestro Simulation Workflow

```python
from virtuoso_bridge.virtuoso.maestro import open_session, read_config, close_session

session = open_session(client, "myLib", "myTestbench")  # maeOpenSetup (background)
config = read_config(client, session)  # dict with tests, analyses, variables

# Set variables and run
client.execute_skill(f'maeSetVar("VDD" "0.8" ?session "{session}")')
client.execute_skill(f'maeSaveSetup(... ?session "{session}")')
history = client.execute_skill(f'maeRunSimulation(?session "{session}")').output
client.execute_skill("maeWaitUntilDone('All)", timeout=300)

close_session(client, session)
```

### Spectre Standalone Simulation

```python
from virtuoso_bridge.spectre import SpectreSimulator, spectre_mode_args

sim = SpectreSimulator.from_env(
    spectre_args=spectre_mode_args("ax"),  # APS extended mode
    work_dir="./output"
)

# Run simulation
result = sim.run_simulation("netlist.scs", {"include_files": ["model.va"]})
if result.ok:
    vout = result.data["VOUT"]  # Parsed PSF waveform as list of floats

# Parallel batch
from pathlib import Path
tasks = [sim.submit(Path(f"tb_{i}.scs")) for i in range(10)]
results = [t.result() for t in tasks]
```

## Important Implementation Details

### Connection Retry with Jump Hosts
The bridge implements special retry logic for connections through jump hosts (see `_TUNNEL_CONNECT_GRACE_SECONDS` and `_should_retry_tunnel_connect`). Connection refused errors are retried for up to 3 seconds to account for jump host latency.

### IL File Upload Caching
`load_il()` caches uploaded files by MD5 hash to avoid redundant uploads. Cache stored in `_il_upload_cache: dict[path -> (md5, remote_path)]`.

### Multi-Profile Implementation
Profiles are implemented via environment variable suffixes. `SSHClient.is_running(profile)` reads state files from `~/.virtuoso_bridge/state_*.json`. Each profile has independent SSH tunnel and port.

### Spectre PATH Resolution
On remote hosts, Spectre is located via:
1. Direct `which spectre` (works if already in PATH)
2. Source `VB_CADENCE_CSHRC` in csh sub-shell and retry

This runs fresh for every command since SSH sessions are stateless.

### X11 Dialog Recovery
When a modal dialog blocks CIW, the SKILL channel times out. The `dismiss_dialog()` method bypasses SKILL entirely:
1. SSH to remote
2. Use `xwininfo` to find virtuoso-owned dialog windows
3. Send Enter key via `XTestFakeKeyEvent`

## Testing Without Virtuoso

Most functionality requires a running Virtuoso instance. For unit testing without Virtuoso:
- Mock `VirtuosoClient.execute_skill()` return values
- Test SKILL string composition functions
- Test file path handling and SSH command generation

## Code Style Conventions

- **Type hints**: Required for all public functions
- **SKILL string escaping**: Use `escape_skill_string()` from `virtuoso.ops`
- **Timeout handling**: Always propagate timeout parameter, default 30s
- **Error handling**: Return `VirtuosoResult` with `ExecutionStatus.ERROR`, never raise for expected failures
- **Path handling**: Use `Path.as_posix()` for remote paths (always forward slashes)

## Common Pitfalls

- **CIW output vs return value**: `execute_skill()` returns to Python but doesn't print in CIW. Use `printf()` in SKILL to display in CIW.
- **Blocking operations**: Never use `?waitUntilDone t` in Maestro calls (deadlocks). Use async run + `maeWaitUntilDone()`.
- **Dialog blockage**: If `execute_skill()` times out, a GUI dialog may be blocking. Use `virtuoso-bridge dismiss-dialog` or `client.dismiss_dialog()`.
- **CDF parameters**: Use `schHiReplace()` to set values, then `CCSinvokeCdfCallbacks()` to trigger updates. Never set `param~>value` directly.
- **Local vs remote paths**: `upload_file()`/`download_file()` handle the translation automatically.
