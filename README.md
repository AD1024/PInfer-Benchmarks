# Specy (a.k.a. PInfer) OOPSLA Artifact Instructions
## Protocol P Models
This artifact contains all 11 publicly available P models of open-source protocols used in our evaluation.

We apologize that data for proprietary protocols cannot be provided due to the confidentiality of the models and traces.

## File Organization

| Directory | Protocol |
|-----------|----------|
| 2PC | Two-Phase Commit |
| ChainReplication | Chain Replication |
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

## Run Artifact Automatically
These steps serve as *reproducibility* documentation.
Please see the explanations at the end of this section for potential discrepancies in the numbers shown in the tables. However, these discrepancies do not affect the top-level claim of the paper: *all known specifications can be learned by PInfer*.
### Step 1: Run PInfer on Benchmarks
First, run `./step_1.sh`. We have tested this on a machine with 16 cores and 256 GB of memory. Under this setup, it takes about 24 hours to complete. You may use `control + p + q` to detach from the Docker container and let it run in the background.

Next, attach back to the container and run `./step_1_draw_tables.sh`. This script will draw the following tables under the `tables` directory (you can view them via `cat tables/<table_n.txt>`).

#### How to Read the Tables

| Output File | Paper Table | Column in Output | Paper Column | Description |
|-------------|-------------|------------------|--------------|-------------|
| `table_4.txt` | Table 4 | `I_pinfer/I_goals` | `S_goals` | Number of goal specifications in PInfer-learned specifications vs. total number of goal specifications (`S_goals`) |
| `table_4.txt` | Table 4 | `#UG` | N/A | Number of user guidance UG1 and UG2 (not including UG3, which involves code instrumentation), please see footnotes of Table 4 in the paper |
| `table_4.txt` | Table 4 | `Time (s)` | Same | Run time of the benchmark |
| `table_5.txt` | Table 5 | `I_raw` | `S_raw` | Number of raw specifications |
| `table_5.txt` | Table 5 | `I_syn` | `S_syn` | Number of specifications after syntactic pruning |
| `table_5.txt` | Table 5 | `I_smt` | `S_sem` | Number of specifications after semantic pruning |
| `table_5.txt` | Table 5 | `I_raw/I_smt` | `RR` | Reduction ratio (geometric average shown at bottom) |
| `table_6.txt` | Table 6 | `(I_s+I_e)/I_ind` | sum of `I_s` and `I_e` | Number of inductive invariants (`I_s + I_e`) learned by PInfer (left) vs. number of necessary inductive invariants (right) |
| `table_6_verifier_time.txt` | Table 6 | `Time (ms)` | Same | Verifier time on all learned specifications (left) vs. on only necessary inductive invariants (right) |

> **Note:** `table_5.txt` shows Table 5 *without* the last column (`S_false`), which will be generated in Step 2.

### Step 2: Run the PChecker Model Checker to Falsify Learned Specifications
First, run `./step_2.sh <timeout>`, where `<timeout>` is the time limit for the model checker in seconds. For example:

> ./step_2.sh 3600

This command takes about 1-2 hours to finish on all benchmarks on a server with 16 cores. Reducing `<timeout>` will finish faster but may decrease the number of falsified specifications.

Next, run `./step_2_draw_tables.sh`. This will generate `table_5_falsified.txt` in the `tables` directory, showing the number of falsified specifications for each benchmark (**last column, S_false of Table 5**) and time elapsed. 

### Potential Discrepancies from the Paper
You may find some numbers from `table_5.txt` and `table_5_falsified.txt` different from those shown in our paper. The table below explains these potential discrepancies.

| Table | Column | Cause | Impact |
|-------|--------|-------|--------|
| Table 5 | `S_raw` | Daikon non-determinism: Daikon may drop certain properties if certain behaviors of the P model are not triggered sufficiently many times. It may or may not output properties capturing rarely-triggered behaviors. | May cause PInfer to learn fewer/more specifications. Does not affect top-level results (Table 4) since behaviors checked by safety properties are triggered frequently. |
| Table 5 | `S_syn`, `S_sem` | Parallel execution order: We parallelize learning for each event combination. Under different hardware settings, specifications may be generated in different orders depending on core efficiency. | May cause the pruning procedure to output different pruned sets. This does not breach soundness but may leave more redundant specifications. For example, if P, Q, R are learned where P subsumes Q semantically and Q subsumes R syntactically: if Q is pruned before seeing R, then R cannot be pruned since P may not subsume R directly. |
| Table 5 | `S_false` | Randomized state exploration: PChecker implements randomized state exploration. | The number of falsified specifications may differ in each run. |
| Table 4 | `Time (s)` | Hardware differences: We evaluated PInfer on a server with 192 cores. PInfer is optimized to leverage computing resources—more cores lead to faster execution. | Using a node with 16 cores requires about 24 hours to finish all benchmarks sequentially. |
| Table 6 | `Time (ms)` | Z3 behavior: PVerifier generates Z3 queries under the hood. Z3 may behave differently under different hardware setups, and its heuristic choices can vary. | Verification time may differ, but generally, verifying the full set of learned specifications should take longer (>=) than verifying only the necessary ones. |

> **Note:** We use a fairly large number of traces, so the numbers should not differ significantly from those shown in the paper. 

---

## Run PInfer Manually on Your Own P Model
This section serves as *reusability* documentation.

First, place your P model (with `PSrc` and `PTst` directories, for the model and test cases) in the same directory as this README file. You can optionally include a `job.slurm` file in your benchmark directory with custom arguments to PInfer (see the end of this README for examples). Then follow these steps:

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

> **Note:** This step prioritizes running the `job.slurm` script if it exists in the benchmark directory.

### Step 3: Generate Result Tables

```bash
python draw_tables.py [--tables TABLE ...] [--no-rerun]
```

| Argument | Description |
|----------|-------------|
| `--tables` | Tables to generate: `4`, `5`, `5-1`, `6` (default: all) |
| `--no-rerun` | Skip re-running the pruning step and use cached results |

Note that `5-1` corresponds to the last column of Table 5 in the paper.
To generate `5-1`, you must first run `run_mc.py` (described next).

### Optional Step: Falsifying with PChecker

This step uses the PChecker model checker to attempt to falsify learned specifications.

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

Top-level command: `p infer`

### General Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `-t` | Path to the trace directory for the benchmark (generated in Step 1) | `p infer -t <path/to/traces>` |
| `--action` | Specifies the action to run: `compile` or `pruning`. When not specified, PInfer runs `compile` followed by learning and `pruning` automatically. | `p infer --action compile <args>` |
| `--hint-only` | Only run PInfer with event combinations specified in user guidance UG1. | |
| `-ce <event>` | Configuration event: an event announced once at the beginning of execution containing cluster setup (e.g., number of nodes). Used to learn specifications relating payloads to cluster configurations. | `p infer -t <traces> -ce ePaxosConfig` |
| `-z3` | Enables semantic checking in pruning procedures. | `p infer -t <traces> -ce ePaxosConfig -z3` |

### `--action compile` Mode

Generates predicates, terms, and the Dynamic Learner Interface (in the `PGenerated/PInfer` directory).

| Argument | Description | Example |
|----------|-------------|---------|
| `-td <depth>` | Maximum tree height of the term AST. Default: 1 (allowing function calls but disallowing nested calls). | `p infer --action compile -td 2` |

### `--action pruning` Mode

Runs the pruning procedures only on previously generated learner logs.

| Argument | Description | Example |
|----------|-------------|---------|
| `-pi <path>` | Directory containing the learner logs. Logs are stored in `PInferOutputs/SpecMining_<n>` (higher `n` = more recent run). | `p infer --action pruning -pi PInferOutputs/SpecMining` |
| `-z3` | Enables semantic checking in pruning. | `p infer --action pruning -pi PInferOutputs/SpecMining -z3` |

More examples can be found in `<benchmark>/job.slurm`.

## Notes
This artifact uses an older version of PInfer. The latest version is available in the [P GitHub Repository](https://github.com/p-org/P/tree/experimental/pinfer). You may try cloning this latest version, which has lighter-weight dependencies (e.g., all Java runtime components are factored out and inlined in the codegen for Dynamic Learner Interface). This version includes several bug fixes to the Dynamic Learner Interface generator and the pruning procedures (which may result in different numbers of learned specifications in the output), but the arguments and interfaces remain the same. 