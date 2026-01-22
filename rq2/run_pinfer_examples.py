import os
import subprocess
import time
import glob
import tabulate


def run_example(smp_file):
    """Run a single .smp file through the pipeline and measure execution time."""
    print(f"\nRunning {os.path.basename(smp_file)}...")

    start_time = time.time()

    # Run: dune exec smpc <file> | z3 -in
    smpc_process = subprocess.Popen(
        ["dune", "exec", "smpc", smp_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    z3_process = subprocess.Popen(
        ["z3", "-in"],
        stdin=smpc_process.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Allow smpc_process to receive SIGPIPE if z3_process exits
    smpc_process.stdout.close()

    # Wait for z3 to complete
    z3_output, z3_error = z3_process.communicate()

    end_time = time.time()
    execution_time_ms = (end_time - start_time) * 1000

    print(f"Execution time: {execution_time_ms:.2f} ms")

    # Print output
    if z3_output:
        print(f"Output:\n{z3_output.decode('utf-8')}")

    if z3_error:
        print(f"Error:\n{z3_error.decode('utf-8')}")

    return execution_time_ms


def main():
    # Find all .smp files in pinfer_examples directory
    smp_files = sorted(glob.glob("pinfer_examples/*.smp"))

    if not smp_files:
        print("No .smp files found in pinfer_examples/")
        return

    print(f"Found {len(smp_files)} example file(s)")

    total_time = 0
    header = ["Filename", "Time (ms)"]
    table = []
    results = {}
    for smp_file in smp_files:
        exec_time = run_example(smp_file)
        total_time += exec_time
        benchmark_name = smp_file.replace("pinfer_examples/", "").replace(".smp", "")
        if "_vanilla" in benchmark_name:
            benchmark_name = benchmark_name.replace("_vanilla", "")
            if benchmark_name not in results:
                results[benchmark_name] = {}
            results[benchmark_name]['vanilla'] = f"{exec_time:.2f}"
        else:
            if benchmark_name not in results:
                results[benchmark_name] = {}
            results[benchmark_name]['pinfer'] = f"{exec_time:.2f}"
    
    for benchmark in results.keys():
        bench_results = results[benchmark]
        ratio = float(bench_results['pinfer']) / float(bench_results['vanilla'])
        table.append([benchmark, f"{bench_results['pinfer']} / {bench_results['vanilla']} ({ratio}x)"])
        # table.append([benchmark_name, f"{exec_time:.2f}"])

    print(f"\n{'='*60}")
    print(f"Total execution time: {total_time:.2f} ms")
    print(f"Average execution time: {total_time/len(smp_files):.2f} ms")

    print("\nExecution Times:")
    print(tabulate.tabulate(table, headers=header, tablefmt="grid"))

if __name__ == "__main__":
    main()
