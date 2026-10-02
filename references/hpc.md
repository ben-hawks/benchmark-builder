# Running a benchmark on HPC (Slurm)

The skill generates **generic Slurm** scripts, tuned per machine. The job scripts know
nothing about any cluster. Every site-specific value comes from a machine profile. NERSC
Perlmutter is one worked profile (the one axess-benchmark ran on), **not the default**.

Templates: `assets/hpc/slurm/`

```
<hpc>/                       e.g. slurm/ (or one dir per cluster family; axess uses perlmutter/)
├── env.sh                   paths with overridable defaults, activation functions; sources the profile
├── profiles/<machine>.sh    everything cluster-specific (one file per machine)
├── setup.sh                 login node: build venvs, download data + weights (sha256-checked)
├── submit.sh                -A <account>: Slurm dependency chain
└── jobs/
    ├── featurize.sbatch     CPU: dataset → cache
    ├── train.sbatch         (optional) only when the benchmark includes training
    ├── infer_gpu.sbatch     GPU models
    ├── infer_cpu.sbatch     CPU-only models (often a separate venv)
    └── score.sbatch         scripts/score_all.sh: truth, metrics, leaderboard, Codabench zips
```

Rename the `BENCH_`/`bench_` prefix and the `benchpkg` package to the benchmark's own, and
set the model lists in the job scripts.

## Ask which machine(s) first

**Ask the user which machine(s) they'll run on. Don't assume Perlmutter or any other
cluster.** If they name more than one, generate one profile per machine. Then ask what
the materials and the site docs don't already answer. If the user doesn't know an answer,
look it up in the site's public user docs and say where the value came from.

### What to ask per machine

| Area | Questions | Goes into |
|---|---|---|
| Scheduler | partition and/or qos names for CPU, GPU, debug; `--constraint` values; is there an account/allocation flag; GPU request syntax (`--gpus=N`, `--gres=gpu:N`, `--gpus-per-node=N`); shared vs exclusive nodes; wall-time limits per qos | `BENCH_SB_*`, `BENCH_REQUIRE_ACCOUNT` |
| Software | module names and versions (e.g. a site PyTorch module); conda vs venv vs a container runtime (podman-hpc, Apptainer/Singularity, Shifter); is a site torch build preferable to pip wheels (CUDA/NCCL tuned) | `bench_load_*` functions, `BENCH_TORCH_VENV_SYSTEM_SITE` |
| Filesystems | scratch vs project/home paths; purge policy and quota; where caches, results, venvs belong | `BENCH_ROOT`, `docs/<MACHINE>.md` |
| Network | do compute nodes have internet? | where downloads happen (always `setup.sh` on a login node if not) |
| Hardware | GPU type and count per node; CPU cores and memory per node | batch size, `--cpus-per-task`, `--mem`, whether training needs multi-node |

Write what was assumed for each machine, and where each answer came from, into
`docs/<MACHINE>.md`. That file covers paths, one-time setup, the golden test, the job
table (resources and expected wall time), the results layout, "scoring your own model",
interactive use, and troubleshooting. Model it on axess-benchmark's `docs/PERLMUTTER.md`.

## How the pieces fit

- **#SBATCH lines can't expand variables.** That's why resources and the account go on
  the `sbatch` command line from `submit.sh` (from the profile's `BENCH_SB_*`), and the
  job scripts carry only `--job-name` and `--output`.
- **Slurm runs a spooled copy of the job script.** So `$(dirname $0)` points into the
  spool directory. `submit.sh` passes the repo path through
  `--export=ALL,BENCH_REPO=...,BENCH_HPC=...`, and the jobs source
  `$BENCH_REPO/$BENCH_HPC/env.sh`.
- **One venv per stack that has to stay separate.** On Perlmutter:
  - the torch stack is `module load pytorch` + `python -m venv --system-site-packages`,
    which reuses NERSC's CUDA build of torch;
  - TensorFlow/rule4ml live in a **separate** plain-python venv, so their own torch
    dependency can't shadow the module's.
- **All downloads happen in `setup.sh` on a login node**, even where compute nodes do have
  internet. Jobs never download.
- **Run the golden tests on the machine before submitting anything:**
  ```bash
  source <hpc>/env.sh && bench_activate
  BENCH_WEIGHTS=$BENCH_WEIGHTS python -m pytest tests -q                          # CPU, login node is fine
  BENCH_WEIGHTS=$BENCH_WEIGHTS BENCH_TEST_DEVICE=cuda python -m pytest tests -q   # on a GPU node (salloc)
  ```
  A pass means the checkpoints, derived artifacts and preprocessing reproduce the
  validated outputs on this machine and device.
- **The chain:**
  - `featurize`, then `[train]`, then `infer_gpu`; `infer_cpu` runs in parallel after
    `featurize`;
  - `score` runs after all inference jobs;
  - `submit.sh` flags: `--train`, `--no-gpu`, `--no-cpu`. Anything else passes through
    to `sbatch` (e.g. `-q debug`).
- **After the run**, compare against `reference_results/` (every `metrics.json` cell) and
  record the job IDs, exit codes and max relative difference in `docs/VALIDATION.md`.
  Add GPU timings to `reference_solution/README.md`.

## Known gotchas

- **`triton` segfaults on import on CPU-only nodes.** The chain is torch_geometric →
  torch._dynamo → triton. Uninstall triton in CPU-only venvs (`setup.sh` does), and set
  `TORCHDYNAMO_DISABLE=1` (`env.sh` does).
- **CRLF line endings** from Windows-authored scripts fail with `$'\r': command not
  found`. Ship `.gitattributes` with `* text=auto eol=lf`.
- **Purged scratch.** Perlmutter `$SCRATCH` purges files not accessed in 8 weeks. Copy
  results worth keeping to a project filesystem (CFS on NERSC), or point `BENCH_ROOT`
  there.
- **Older caches.** A cache built by an earlier version of `cache.py` must still load
  (optional arrays on read). Otherwise a rerun on the cluster fails on old caches.
- **Site module versions change.** Make the module name a profile default that can be
  overridden (`BENCH_TORCH_MODULE`), and say how to list what's installed
  (`module avail pytorch`).

## Worked profile: NERSC Perlmutter

`assets/hpc/slurm/profiles/perlmutter.sh`, verified with axess-benchmark on 2026-10-02
(Slurm jobs 59209565–68: all exit 0, results matched the CPU reference to ≤2.4e-4
relative).

| Setting | Value |
|---|---|
| Account | required, `-A <nersc_project>` on the command line |
| CPU jobs | `--constraint=cpu --qos=shared`, cores/memory per job |
| GPU inference | `--constraint=gpu --qos=shared --gpus=1` (1 A100 on a shared node) |
| Training (if any) | `--constraint=gpu --qos=regular --gpus-per-node=4`, multi-node possible |
| Torch stack | `module load pytorch/<ver>` + `venv --system-site-packages` |
| Separate stack | `module load python` + plain venv (TensorFlow/rule4ml), triton removed |
| Paths | `$SCRATCH/<benchmark>`; CFS for anything to keep |
| Downloads | login node (`setup.sh`) |

axess's job layout for scale, featurizing about 103k samples:

| Job | Resources | Wall time |
|---|---|---|
| featurize | 64 cores | a few minutes |
| GPU inference (GNN + Transformer) | 1 A100 | a few minutes |
| CPU inference (rule4ml) | 32 cores | 30–60 min |
| score | 4 cores | < 5 min |

For any other machine, start from `profiles/generic.sh` and fill every value from the
questions above. Don't copy Perlmutter's values to a machine they weren't verified on.
