import os
import argparse
import subprocess
from constants import benchmarks

all_benchmarks = benchmarks + ['Raft_hint']

def start(benchmarks):
    for benchmark in benchmarks:
        os.chdir(benchmark)
        _ = subprocess.call(['bash', 'job.slurm'], shell=True)
        os.chdir('..')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--benchmarks', type=str, nargs='+', default=all_benchmarks)
    args = parser.parse_args()
    start(args.benchmarks)
