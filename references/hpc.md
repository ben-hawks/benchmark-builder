# Running a benchmark on HPC (Slurm)

The skill generates **generic Slurm** scripts, tuned per machine and per benchmark:
- the job scripts know nothing about any cluster or software stack;
- cluster facts come from a **machine profile**;
- the benchmark's own software-stack settings and fixes come from **`stack.sh`**.

NERSC Perlmutter is one worked profile (the one axess-benchmark ran on), **not the
default**.

Templates: `assets/hpc/slurm/`

```
<hpc>/                       e.g. slurm/ (or one dir per cluster family; axess uses perlmutter/)
├── env.sh                   paths with overridable defaults, activation functions; sources profile + stack.sh
├── profiles/<machine>.sh    cluster facts: scheduler syntax, filesystems, network, GPUs, modules (one per machine)
├── stack.sh                 this benchmark's stack: environment settings, post-install fixes, import checks
├── setup.sh                 login node: build venvs, download data + weights (sha256-checked)
├── submit.sh                -A <account>: Slurm dependency chain
└── jobs/
    ├── featurize.sbatch     (optional) CPU: dataset → cache, only if the benchmark has a cache step
    ├── train.sbatch         (optional) only when the benchmark includes training
    ├── infer_gpu.sbatch     accelerator models
    ├── infer_cpu.sbatch     CPU-only models
    └── score.sbatch         scripts/score_all.sh: truth, metrics, leaderboard, Codabench zips
```

Rename the `BENCH_`/`bench_` prefix and the `benchpkg` package to the benchmark's own, set
the model lists in the job scripts, and drop the jobs this benchmark doesn't need.

## Machine facts vs the benchmark's stack

Keep the two apart. That's what lets a profile be reused by another benchmark, and stops
one benchmark's workaround from becoming everyone's default.

- **Machine profile:** what's true of the cluster for any benchmark. Partition and qos
  names, GPU request syntax, filesystems and purge policy, internet access, GPU vendor,
  available modules.
- **`stack.sh`:** what's true of *this benchmark's* software on that cluster. Its hooks
  are empty by default. Fill them only with problems you actually hit with this
  benchmark's stack, and record each one (symptom, cause, fix) in `docs/<MACHINE>.md`.
  The template shows axess's fixes as commented examples; don't enable them unless this
  benchmark hits the same problem.
  - `bench_stack_env`: environment variables the stack needs in every job;
  - `bench_post_install`: fixes applied after installing requirements;
  - `bench_check_env`: an import check, so a broken environment fails in `setup.sh`
    rather than in a queued job.
- **Job resources** (`BENCH_SB_*`) sit in the profile because their syntax is the
  machine's, but their sizes come from this benchmark's measured needs. Size them per
  benchmark; never copy another benchmark's.

## Ask which machine(s) first

**Ask the user which machine(s) they'll run on. Don't assume Perlmutter or any other
cluster.** If they name more than one, generate one profile per machine. Then ask what
the materials and the site docs don't already answer. If the user doesn't know an answer,
look it up in the site's public user docs and say where the value came from.

### What to ask per machine

| Area | Questions | Goes into |
|---|---|---|
| Scheduler | partition and/or qos names for CPU, GPU, debug; `--constraint` values; is there an account/allocation flag; GPU request syntax (`--gpus=N`, `--gres=gpu:N`, `--gpus-per-node=N`); shared vs exclusive nodes; wall-time limits per qos | `BENCH_SB_*` syntax, `BENCH_REQUIRE_ACCOUNT` |
| Software | module names and versions; conda vs venv vs a container runtime (podman-hpc, Apptainer/Singularity, Shifter); does the site provide a tuned build of the benchmark's framework that a venv should layer on | `BENCH_*_MODULE`, `bench_load_*` functions, `BENCH_VENV_SYSTEM_SITE`, `BENCH_PYTHON` (default `python3`) |
| Filesystems | scratch vs project/home paths; purge policy and quota; where caches, results, venvs belong | `BENCH_ROOT`, `docs/<MACHINE>.md` |
| Network | do compute nodes have internet? | where downloads happen (always `setup.sh` on a login node if not) |
| Hardware | GPU vendor, model and count per node; CPU cores and memory per node | `BENCH_GPU_DEVICE`, `bench_gpu_info`, job sizes, whether training needs multi-node |

### What to ask about the benchmark's stack

| Question | Goes into |
|---|---|
| Which frameworks do the reference models need, and do any conflict (e.g. two frameworks pinning different versions of a shared dependency)? | `requirements*.txt`, one venv per conflicting stack |
| Which device name does the code take for the machine's accelerators? | `BENCH_GPU_DEVICE` |
| How much memory, time and how many cores does each step need on this data? Measure a small run. | `BENCH_SB_*` sizes |

Write what was assumed for each machine, and where each answer came from, into
`docs/<MACHINE>.md`. That file covers:
- paths and one-time setup;
- the golden test;
- the job table (resources and expected wall time);
- the results layout and "scoring your own model";
- interactive use;
- troubleshooting, including every `stack.sh` fix and why it's there.

Model it on axess-benchmark's `docs/PERLMUTTER.md`.

## How the pieces fit

- **#SBATCH lines can't expand variables.** That's why resources and the account go on
  the `sbatch` command line from `submit.sh` (from the profile's `BENCH_SB_*`), and the
  job scripts carry only `--job-name` and `--output`.
- **Slurm runs a spooled copy of the job script.** So `$(dirname $0)` points into the
  spool directory. `submit.sh` passes the repo path through
  `--export=ALL,BENCH_REPO=...,BENCH_HPC=...`, and the jobs source
  `$BENCH_REPO/$BENCH_HPC/env.sh`.
- **One venv per stack that has to stay separate**, and only when stacks really conflict.
  (axess on Perlmutter: a venv layered on NERSC's PyTorch module with
  `--system-site-packages`, plus a separate plain venv for TensorFlow and rule4ml so their
  own torch couldn't shadow the module's.)
- **All downloads happen in `setup.sh` on a login node**, even where compute nodes do have
  internet. Jobs never download.
- **Run the golden tests on the machine before submitting anything:**
  ```bash
  source <hpc>/env.sh && bench_activate
  BENCH_WEIGHTS=$BENCH_WEIGHTS python -m pytest tests -q                                       # CPU, login node is fine
  BENCH_WEIGHTS=$BENCH_WEIGHTS BENCH_TEST_DEVICE=$BENCH_GPU_DEVICE python -m pytest tests -q   # on an accelerator node
  ```
  A pass means the weights, derived artifacts and preprocessing reproduce the validated
  outputs on this machine and device.
- **The chain:**
  - `[featurize]`, then `[train]`, then `infer_gpu`; `infer_cpu` runs in parallel after
    `featurize`;
  - `score` runs after all inference jobs;
  - `submit.sh` flags: `--train`, `--no-gpu`, `--no-cpu`. Anything else passes through
    to `sbatch` (e.g. `-q debug`).
- **After the run**, compare against `reference_results/` (every `metrics.json` cell) and
  record the job IDs, exit codes and max relative difference in `docs/VALIDATION.md`.
  Add accelerator timings to `reference_solution/README.md`.

## Generic gotchas

These apply whatever the benchmark:

- **CRLF line endings** from Windows-authored scripts fail with `$'\r': command not
  found`. Ship `.gitattributes` with `* text=auto eol=lf`.
- **Purged scratch.** Many sites purge scratch (Perlmutter: files not accessed in 8 weeks).
  Copy results worth keeping to a project filesystem, or point `BENCH_ROOT` there.
- **Stale caches.** If the benchmark has a cache step, a cache written by an earlier
  version of the code must still load, or a rerun on the cluster fails on old files.
- **Site module versions change.** Make module names profile defaults that can be
  overridden, and say how to list what's installed (e.g. `module avail`).

## Stack-specific problems: found per benchmark

Problems that come from a particular software stack belong in that benchmark's
`stack.sh` and `docs/<MACHINE>.md`, after you've reproduced them. They don't go in the
templates. Example from axess-benchmark on Perlmutter: importing `torch_geometric` pulled
in `torch._dynamo` → `triton`, which segfaulted on CPU-only nodes. axess fixed it in its
own scripts (uninstall triton in the CPU-only venv; `TORCHDYNAMO_DISABLE=1`), and the
template's `stack.sh` shows that only as a commented example. A benchmark without that
stack must not inherit the fix.

## Worked profile: NERSC Perlmutter

`assets/hpc/slurm/profiles/perlmutter.sh` holds the cluster facts verified with
axess-benchmark on 2026-10-02 (Slurm jobs 59209565–68: all exit 0, results matched the
CPU reference to ≤2.4e-4 relative). Job sizes and modules are left as placeholders for
each benchmark to set.

| Setting | Value |
|---|---|
| Account | required, `-A <nersc_project>` on the command line |
| CPU jobs | `--constraint=cpu --qos=shared` |
| GPU jobs | `--constraint=gpu`, `--qos=shared` (`--gpus=N`) or `--qos=regular` (`--gpus-per-node=N`, multi-node); NVIDIA A100 |
| Paths | `$SCRATCH/<benchmark>`; CFS for anything to keep |
| Downloads | login node (`setup.sh`); compute nodes do have internet |
| Modules | site `python` and framework modules (`module avail`) |

For scale only, not as defaults, axess's measured job layout (about 103k samples
preprocessed) was:

| Job | Resources | Wall time |
|---|---|---|
| featurize | 64 cores | a few minutes |
| GPU inference (two models) | 1 A100 | a few minutes |
| CPU inference (two models, TensorFlow venv) | 32 cores | 30–60 min |
| score | 4 cores | < 5 min |

axess's stack on Perlmutter (its own choice):
- a main venv on `module load pytorch/2.6.0` with `--system-site-packages`;
- a separate TensorFlow venv on `module load python`;
- the triton fix above.

For any other machine, start from `profiles/generic.sh` and fill every value from the
questions above. Don't copy Perlmutter's values to a machine they weren't verified on.
