# Running a benchmark on HPC (Slurm or PBS)

The skill generates **generic Slurm or PBS** scripts, tuned per machine and per benchmark:
- the job scripts know nothing about any cluster or software stack;
- cluster facts come from a **machine profile**;
- the benchmark's own software-stack settings and fixes come from **`stack.sh`**.

NERSC Perlmutter is one worked, verified profile (the one axess-benchmark ran on), **not
the default**. OLCF Frontier (Slurm) and ALCF Aurora (PBS) have profiles drafted from the
genesis HPC skills that **haven't been verified by a run yet** (see "Site profiles").

**Load the genesis HPC skills on demand.** As soon as the user says they run on a machine,
load its genesis skill (`perlmutter`, `frontier`, `aurora`) and the scheduler skill
(`slurm` or `pbs`), at their latest version (`references/genesis-skills.md`). They are the
source for site facts (queues, limits, GPUs, filesystems, modules) and for submitting,
monitoring and troubleshooting jobs. This file covers what they don't: how the benchmark's
pipeline maps onto jobs, and which answers only the user and the benchmark can give.

Templates: `assets/hpc/common/` (scheduler-neutral) plus `assets/hpc/slurm/` or
`assets/hpc/pbs/`. A benchmark's `<hpc>/` directory gets the common files plus one
scheduler's files:

```
<hpc>/                       e.g. slurm/ or pbs/ (or one dir per cluster family; axess uses perlmutter/)
├── env.sh                   (common) paths with overridable defaults, activation functions; sources profile + stack.sh
├── stack.sh                 (common) this benchmark's stack: environment settings, post-install fixes, import checks
├── setup.sh                 (common) login node: build venvs, download data + weights (sha256-checked)
├── profiles/<machine>.sh    cluster facts: scheduler syntax, filesystems, network, GPUs, modules (one per machine)
├── submit.sh                -A <account>: Slurm (sbatch --dependency) or PBS (qsub -W depend=) chain
└── jobs/                    *.sbatch for Slurm, *.pbs for PBS
    ├── featurize            (optional) CPU: dataset → cache, only if the benchmark has a cache step
    ├── train                (optional) only when the benchmark includes training
    ├── infer_gpu            accelerator models
    ├── infer_cpu            CPU-only models
    └── score                scripts/score_all.sh: truth, metrics, leaderboard, Codabench zips
```

Rename the `BENCH_`/`bench_` prefix and the `benchpkg` package to the benchmark's own, set
the model lists in the job scripts, and drop the jobs this benchmark doesn't need. Slurm
profiles set per-job resources in `BENCH_SB_*` (sbatch arguments), PBS profiles in
`BENCH_QS_*` (qsub arguments).

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
cluster.** If they name more than one, generate one profile per machine. Then, per machine:

1. **Load the genesis skills for it** (site + scheduler, latest version). Pre-fill the
   profile from them, starting from the site profile here if there is one, else
   `profiles/generic.sh` for that scheduler.
2. **Ask the user only what's left**: their account/allocation, the benchmark's stack, and
   anything the skills don't cover. Each site profile marks those gaps with `<...>`.
3. **If neither the skill nor the user knows**, look it up in the site's public user docs.
4. **Record where each value came from** in `docs/<MACHINE>.md`: the genesis skill and the
   commit you loaded, the site docs page, or the user. When a skill and the site's docs
   disagree, the docs win; note the disagreement.

### What to ask per machine

| Area | Questions | Goes into |
|---|---|---|
| Scheduler | Slurm or PBS; partition/qos (Slurm) or queue (PBS) names for CPU, GPU, debug; `--constraint` values; is there an account/allocation flag; GPU request syntax (`--gpus=N`, `--gres=gpu:N`, `--gpus-per-node=N`, or PBS `select=...:ngpus=N`); site-required resources (e.g. Aurora's `-l filesystems=`); shared vs exclusive nodes; wall-time and job-count limits per qos/queue | `BENCH_SB_*` / `BENCH_QS_*` syntax, `BENCH_REQUIRE_ACCOUNT` |
| Software | module names and versions; conda vs venv vs a container runtime (podman-hpc, Apptainer/Singularity, Shifter); does the site provide a tuned build of the benchmark's framework that a venv should layer on | `BENCH_*_MODULE`, `bench_load_*` functions, `BENCH_VENV_SYSTEM_SITE`, `BENCH_PYTHON` (default `python3`) |
| Filesystems | scratch vs project/home paths; purge policy and quota; where caches, results, venvs belong | `BENCH_ROOT`, `docs/<MACHINE>.md` |
| Network | do compute nodes have internet? | where downloads happen (always `setup.sh` on a login node if not) |
| Hardware | GPU vendor, model and count per node; CPU cores and memory per node | `BENCH_GPU_DEVICE`, `bench_gpu_info`, job sizes, whether training needs multi-node |

### What to ask about the benchmark's stack

| Question | Goes into |
|---|---|
| Which frameworks do the reference models need, and do any conflict (e.g. two frameworks pinning different versions of a shared dependency)? | `requirements*.txt`, one venv per conflicting stack |
| Which device name does the code take for the machine's accelerators? | `BENCH_GPU_DEVICE` |
| How much memory, time and how many cores does each step need on this data? Measure a small run. | `BENCH_SB_*` / `BENCH_QS_*` sizes |

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

- **Neither `#SBATCH` nor `#PBS` lines can expand variables.** That's why resources and the
  account go on the `sbatch`/`qsub` command line from `submit.sh` (from the profile's
  `BENCH_SB_*`/`BENCH_QS_*`), and the job scripts carry only a job name and output option.
- **The job script doesn't run from where it was submitted.** Slurm runs a spooled copy,
  so `$(dirname $0)` points into the spool directory; PBS starts the job in `$HOME`.
  `submit.sh` passes the repo path through `--export=ALL,BENCH_REPO=...,BENCH_HPC=...`
  (Slurm) or `qsub -v BENCH_REPO=...,BENCH_HPC=...` (PBS; values can't contain commas),
  and the jobs source `$BENCH_REPO/$BENCH_HPC/env.sh`.
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
    to `sbatch`/`qsub` (e.g. `-q debug`).
  - Check the site's per-queue job limits before submitting a whole chain to a debug
    queue. Aurora's `debug` allows one running and one queued job per user.
- **Multi-process launchers are per site.** Slurm sites use `srun`; Aurora uses `mpiexec`
  (there is no `srun`). Take the launcher and GPU-binding options for `train` from the
  site skill.
- **After the run**, compare against `reference_results/` (every `metrics.json` cell) and
  record the job IDs, exit codes and max relative difference in `docs/VALIDATION.md`.
  Add accelerator timings to `reference_solution/README.md`.

## Experiment tracking from jobs (AmSC MLflow)

If the user tracks runs in AmSC MLflow (the `amsc-mlflow` skill,
`references/genesis-skills.md`):
- **Log scored results after the chain finishes, from a login node.** Run
  `log_benchmark_results.py --results $BENCH_RESULTS` there. Nothing in the job needs a
  token or outbound access.
- **When a job must log itself** (training metrics):
  - source the skill's `assets/mlflow_job_env.sh` in that job, or in `stack.sh`'s
    `bench_stack_env`. It sets the site proxy (Frontier and ALCF compute nodes need one;
    Perlmutter doesn't), the multipart-upload settings, and reads the token from a chmod-600
    file;
  - never pass the token through `sbatch --export` or `qsub -v`;
  - record the proxy settings that worked in `docs/<MACHINE>.md`.

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

## Site profiles

| Profile | Scheduler | Status |
|---|---|---|
| `slurm/profiles/perlmutter.sh` | Slurm | **verified** 2026-10-02 with axess-benchmark (below) |
| `slurm/profiles/frontier.sh` | Slurm | **unverified**: drafted from the genesis `frontier` skill (`b7e8434`) |
| `pbs/profiles/aurora.sh` | PBS | **unverified**: drafted from the genesis `aurora` skill (`b7e8434`) |
| `slurm/profiles/generic.sh`, `pbs/profiles/generic.sh` | either | templates for any other machine |

An unverified profile is a starting point, not a fact sheet:
- reload the site skill at its latest version and the site's docs, and re-check every
  value;
- fill its `<...>` placeholders (the skills don't cover compute-node internet, Python or
  ML framework modules, or the exact scratch path form) from the user and the site docs;
- run the golden tests and a full chain on the machine.

Only then change its header to "verified <date> with <benchmark> (jobs ...)" and add its
row to this table. Never copy one site's values to another machine.

### Notes on the genesis HPC skills

These were found while drafting the profiles. Check whether they still hold in the latest
version before acting on them.

- The `pbs` skill documents `-t 1-100` and `$PBS_ARRAY_INDEX` for job arrays. In OpenPBS
  and PBS Pro (Aurora, Polaris), arrays use `-J 1-100`; `-t` with `$PBS_ARRAYID` is
  Torque's syntax. The templates here don't use arrays, but if a benchmark adds them,
  confirm the syntax with `man qsub` on the machine.
- The `frontier` skill's storage table gives `$MEMBERWORK` as
  `/lustre/orion/<proj>/scratch/user`. Check the per-project directory form against OLCF's
  docs before setting `BENCH_ROOT`.
- The `perlmutter` skill and `slurm/profiles/perlmutter.sh` agree on the facts the profile
  uses (`-C cpu|gpu`, the `shared`/`regular`/`debug` QOS, `$SCRATCH`'s 8-week purge, a
  required `-A`).

### Worked profile: NERSC Perlmutter

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

For any other machine, start from the scheduler's `profiles/generic.sh` (or an unverified
site profile above) and fill every value from the genesis site skill and the questions
above. Don't copy Perlmutter's values to a machine they weren't verified on.
