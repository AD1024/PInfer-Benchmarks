# Specy (a.k.a. PInfer) OOPSLA Artifact
## Protocol P models
This artifact contains 11 open-sourced P models and *1* proprietary P model of an open-sourced clock synchronization protocol called [ClockBound](https://github.com/aws/clock-bound).

## File Organization

| Directory | Protocol |
|-----------|----------|
| 2PC | Two-Phase Commit |
| ChainReplication | Chain Replication |
| ClockBound | ClockBound |
| consensus | Consensus |
| distributed_lock | Distributed Lock |
| firewall | Firewall |
| lockserver | Lock Server |
| paxos | Paxos |
| paxos_hint | Paxos (with hints) |
| Raft | Raft |
| Raft_hint | Raft (with hints) |
| ring_leader | Ring Leader Election |
| sharded_kv | Sharded Key-Value Store |
| vertical_paxos | Vertical Paxos |

> **Note:** `Timer` is a shared timer library used by multiple protocols.

### Python Scripts

| Script | Description |
|--------|-------------|
| `constants.py` | Configuration file containing benchmark names, test configurations, and event combinations |
| `1_prepare_traces.py` | Generates execution traces for benchmarks using the P compiler and checker |
| `2_run_pinfer.py` | Runs PInfer on generated traces, with optional SLURM cluster support |
| `run_pinfer_sequential.py` | Runs benchmarks sequentially using job scripts |
| `run_mc.py` | Runs model checking (PChecker) to falsify learned specifications |
| `draw_tables.py` | Generates result tables (Tables 4, 5, 6) for the paper from PInfer outputs |
| `cleanup.py` | Cleans up generated files and outputs from benchmarks |

## Run artifact automatically
### Step 1: Run PInfer on benchmarks
First, run `./step_1_draw_tables.sh`. We have tested it on a machine with 16 cores and 256 GB of memory. It takes about 24 hours to finish under this setup.

Next, run `./step_1_draw_tables.sh`. This script will draw the following Tables under `tables` directory:
- Table 4: `table_4.txt`
- Table 5: `table_5.txt`; this shows Table 5 in the paper *without* the last column, will be generated in the next step.
- Table 6: `table_6.txt` shows the number of inductive invariants learned and `table_6_verifier_time.txt` shows the time on PVerifier using the full set of learned specifications v.s. only necessary ones.

You may view the tables by `cat <table>.txt`.

### Step 2: Run the PChecker model checker to try falsifying learned specifications
First, run `./step_2.sh <timeout>`, where `<timeout>` is the time limit for the model checker in seconds. We ran this script with 3600 seconds, which takes about 10 hours in total to finish on all benchmarks. Tuning down may decrease the number of falsified specifications but can finish faster.

Next, run `./step_2_draw_tables.sh`. This will generate `table_5_falsified.txt` under `tables` directory showing the number of falsified specifications for each benchmark and time elapsed. 

---

## Run PInfer manually from scratch on your own P model

First, put your P model under the same directory as this README file.
Note that you can include a `job.slurm` under your benchmark directory with custom arguments to PInfer (shown at the end of README).
Then follow these steps:

### Step 1: Generate Traces

```bash
export PINFER_TRACE_DIR=/path/to/traces
python 1_prepare_traces.py [--trace_dir DIR] [--benchmarks NAME ...] [--num_traces N ...]
```

| Argument | Description |
|----------|-------------|
| `--trace_dir` | Directory to store generated traces (default: `$PINFER_TRACE_DIR`) |
| `--benchmarks` | List of benchmarks to generate traces for (default: all benchmarks) |
| `--num_traces` | Number of traces to generate (default: 10000) |

### Step 2: Run PInfer

```bash
python 2_run_pinfer.py [--trace_dir DIR] [--benchmarks NAME ...] [--num_traces N ...] [--slurm]
```

| Argument | Description |
|----------|-------------|
| `--trace_dir` | Directory containing generated traces (default: `$PINFER_TRACE_DIR`) |
| `--benchmarks` | List of benchmarks to run PInfer on (default: all benchmarks) |
| `--num_traces` | Number of traces to use (default: 10000) |
| `--slurm` | Enable SLURM cluster mode for parallel execution (default: false) |

> Note: this step prioritize running the `job.slurm` script if exists under the benchmark directory.

### Step 3: Generate Result Tables

```bash
python draw_tables.py [--tables TABLE ...] [--no-rerun]
```

| Argument | Description |
|----------|-------------|
| `--tables` | Tables to generate: `4`, `5`, `5-1`, `6` (default: all) |
| `--no-rerun` | Skip re-running the pruning step and use cached results |

Note that `5-1` corresponds to the last column of Table 5 in the paper.
To generate `5-1`, `run_mc.py` needs to be run first.

### Optional step: Falsifying with PChecker

This step uses the PChecker model checker to attempt to falsify the learned specifications.

```bash
python run_mc.py [--benchmarks NAME ...] [--timeout SECONDS]
```

| Argument | Description |
|----------|-------------|
| `--benchmarks` | List of benchmarks to run model checking on (default: all benchmarks) |
| `--timeout` | Time limit in seconds for each benchmark (default: 3600) |

After running this step, you can generate Table 5-1 (the last column of Table 5) by running:

```bash
python draw_tables.py --tables 5-1
```

## Arguments to PInfer

Top level command: `p infer`

Available arguments:
- `--action`: `compile | pruning`; when not specified, PInfer runs `compile` and runs its learning procedure followed by `pruning` automatically.
    + `compile`: generates predicates, terms and the Dynamic Learner Interface (under `PGenerated/PInfer` directory). This option accepts an optional argument `-td` for maximum tree height of the term AST. By default, this is set to 1 (i.e., allowing function calls but disallowing nested function calls). Example usage:
    `p infer --action compile -td 2`
    + `pruning`: runs the pruning procedures only. This action requires the directory containing the learner logs as inputs using argument `-pi`. If PInfer has finished before, then the logs are stored under `PInferOutputs/SpecMining_<n>` where higher `n` means a fresher run. To enable semantic checking, pass `-z3` option at the end. Example usage:
    `p infer --action pruning -pi PInferOutputs/SpecMining -z3`
- `--hint-only`: only run PInfer with event combinations specified in user guidance UG1.
- `-ce`: configuration event; usually these events are announced once at the beginning of the execution, containing the cluster setup (e.g., number of nodes). This is used to learn specifications relating payload with cluster configurations. Example usage: `p infer -t $PINFER_TRACE_DIR/paxos_new/10000 -ce ePaxosConfig`
- `-z3`: This option can also be passed alone in `p infer` mode, which enables the semantic checking in pruning procedures. Example usage: `p infer -t $PINFER_TRACE_DIR/paxos_new/10000 -ce ePaxosConfig -z3`

More examples can be found in `<benchmark>/job.slurm`.