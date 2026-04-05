---
name: spectre
description: "Run Cadence Spectre simulations remotely via virtuoso-bridge: upload netlists, execute, parse PSF results. TRIGGER when the user wants to run a SPICE/Spectre simulation from a netlist file, do transient/AC/PSS/pnoise analysis outside Virtuoso GUI, parse PSF waveform data, or mentions Spectre APS/AXS modes. Use this for standalone netlist-driven simulation — for GUI-based ADE Maestro simulation, use the virtuoso skill instead."
---

# Spectre Skill

## How it works

`SpectreSimulator` uploads a `.scs` netlist to a remote machine via SSH, runs Spectre there, downloads the PSF results, and parses them into Python dicts. You write the netlist locally, the simulation runs remotely — no Virtuoso GUI needed. SSH is managed automatically by `SpectreSimulator.from_env()` — just configure `.env` with the remote host and Cadence environment path.

`SpectreSimulator` is independent of `VirtuosoClient` (see the **virtuoso** skill). You can run standalone Spectre simulations without a Virtuoso GUI session.

The typical workflow:
1. Write or prepare a `.scs` netlist (see `references/netlist_syntax.md` for syntax)
2. Create a `SpectreSimulator` instance
3. Call `sim.run_simulation(netlist, options)` — returns a result object with parsed waveforms
4. Analyze `result.data` (dict of signal name → list of float)

## Before you start

1. **Check connection**: `virtuoso-bridge status` — shows Spectre path, version, and license info.
2. **Check examples first**: look at `examples/02_spectre/` below — if similar functionality exists, use it as a basis.
3. **Env requirement**: `VB_CADENCE_CSHRC` must be set in `.env` to source the Cadence environment on the remote machine.

## Core pattern

```python
from virtuoso_bridge.spectre.runner import SpectreSimulator, spectre_mode_args

sim = SpectreSimulator.from_env(
    spectre_args=spectre_mode_args("ax"),  # APS extended (recommended)
    work_dir="./output",
    output_format="psfascii",
)
result = sim.run_simulation("my_netlist.scs", {})

# Check status
if result.ok:
    time = result.data["time"]
    vout = result.data["VOUT"]
else:
    print(result.errors)
```

### With Verilog-A include files

```python
result = sim.run_simulation("tb_adc.scs", {
    "include_files": ["adc_ideal.va", "dac_ideal.va"],
})
```

## Result object

| Attribute | Type | Content |
|-----------|------|---------|
| `result.ok` | bool | Whether simulation succeeded |
| `result.status` | enum | `SUCCESS` / `FAILURE` / `ERROR` |
| `result.data` | dict | Signal name → list of float (parsed waveforms) |
| `result.errors` | list | Error messages from Spectre log |
| `result.warnings` | list | Warning messages |
| `result.metadata["timings"]` | dict | Upload, exec, download, parse durations |
| `result.metadata["output_dir"]` | str | Local path to downloaded `.raw` directory |
| `result.metadata["output_files"]` | list | PSF files in the raw directory |

### Parsing PSF files directly

When you have raw PSF files without going through `run_simulation`:

```python
from virtuoso_bridge.spectre.parsers import parse_psf_ascii_directory
data = parse_psf_ascii_directory("output/tb.raw")
# data = {"time": [...], "VOUT": [...], "VIN": [...]}

# Or a single PSF file (e.g. PSS results)
from virtuoso_bridge.spectre.parsers import parse_spectre_psf_ascii
result = parse_spectre_psf_ascii("output/tb.raw/pss.td.pss")
```

## Simulation modes

Choose based on license availability and performance needs:

```python
spectre_mode_args("spectre")  # basic Spectre (least license demand)
spectre_mode_args("aps")      # APS
spectre_mode_args("ax")       # APS extended (recommended)
spectre_mode_args("cx")       # Spectre X custom
```

## Parallel simulation

Submit multiple simulations that run concurrently. Each gets its own remote directory — no file conflicts. SSH ControlMaster is shared automatically.

### Fire-and-forget with `submit()`

```python
sim = SpectreSimulator.from_env()

# Submit simulations as needed — returns Future immediately
t1 = sim.submit(Path("tb_comparator.scs"), {"include_files": ["comp.va"]})
t2 = sim.submit(Path("tb_dac.scs"))

# Do other work while simulations run...

# Check without blocking
if t1.done():
    result = t1.result()

# Block on a specific one
result2 = t2.result()

# Submit more while others are still running
t3 = sim.submit(Path("tb_sar_logic.scs"))

# Wait for a batch
results = SpectreSimulator.wait_all([t1, t2, t3])
```

### Batch with `run_parallel()`

```python
results = sim.run_parallel([
    (Path("tb_comp.scs"), {"include_files": ["comp.va"]}),
    (Path("tb_dac.scs"), {}),
    (Path("tb_logic.scs"), {}),
], max_workers=5)
```

### Concurrency control

```python
sim.set_max_workers(4)  # default is 8, adjust for license/CPU limits
sim.shutdown()           # tear down pool, new one created on next submit
```

## Multi-server simulation

Submit to different servers by creating a simulator per profile:

```python
# .env defines VB_REMOTE_HOST_worker1, VB_REMOTE_HOST_worker2, etc.
sim1 = SpectreSimulator(remote=True, profile="worker1")
sim2 = SpectreSimulator(remote=True, profile="worker2")

t1 = sim1.submit(Path("tb_comp.scs"))
t2 = sim2.submit(Path("tb_dac.scs"))

results = SpectreSimulator.wait_all([t1, t2])
```

## Job management (CLI)

Monitor and control simulations from the terminal:

```bash
# Show all jobs: status, user@host, time, CPU/MEM for running jobs
virtuoso-bridge sim-jobs

# Cancel a running simulation (kills remote Spectre process)
virtuoso-bridge sim-cancel <job-id>
```

`sim-jobs` output example:
```
Simulation Jobs: 2 running, 1 queued, 3 done, 0 failed

● a3f2c1d0  zhangz@zhangz-wei         tb_comp.scs              running  16:45:29 45s  CPU:98.2% MEM:3.1%
● b7e9a412  designer1@wei-worker1     tb_dac.scs               running  16:45:30 12s  CPU:45.7% MEM:1.8%
○ c4d5e6f7  zhangz@zhangz-wei         tb_logic.scs             queued   16:45:35 0s
✓ d8e9f012  zhangz@zhangz-wei         tb_bias.scs              done     16:44:10-16:44:25 15s
```

Finished jobs auto-expire after 10 minutes.

## .env configuration

The `.env` file can live in the virtuoso-bridge-lite directory or in your project root (recommended when virtuoso-bridge-lite is cloned as a subdirectory). Both locations are searched automatically.

```dotenv
# Default connection
VB_REMOTE_HOST=my-server
VB_REMOTE_USER=username
VB_REMOTE_PORT=65081
VB_LOCAL_PORT=65082
VB_CADENCE_CSHRC=/path/to/.cshrc.cadence

# Additional profiles for multi-server
VB_REMOTE_HOST_worker1=eda-node1
VB_REMOTE_USER_worker1=sim_user
VB_REMOTE_PORT_worker1=65432
VB_LOCAL_PORT_worker1=65433
```

## License check

```python
info = sim.check_license()
print(info["spectre_path"])  # which spectre binary
print(info["version"])       # version string
print(info["licenses"])      # license feature availability
```

## References

Load only when needed:

- `references/netlist_syntax.md` — Spectre netlist format, analysis statements, instance syntax, parameterization

## Existing examples

**Always check these before writing new code.**

- `examples/02_spectre/01_inverter_tran.py` — basic inverter transient simulation
- `examples/02_spectre/01_veriloga_adc_dac.py` — 4-bit ADC/DAC transient with Verilog-A
- `examples/02_spectre/02_cap_dc_ac.py` — capacitor DC + AC analysis
- `examples/02_spectre/04_strongarm_pss_pnoise.py` — StrongArm comparator PSS + Pnoise
- Netlists in `examples/02_spectre/assets/`

## Related skills

- **virtuoso** — GUI-based Virtuoso workflow (schematic/layout editing, ADE Maestro simulation). Use when the user is working inside the Virtuoso GUI.
