from constants import benchmarks
import os
import argparse

def checker_out(benchmark):
    return os.path.join(benchmark, 'PCheckerOutput')

def pgenerated(benchmark):
    return os.path.join(benchmark, 'PGenerated')

def pinfer_out(benchmark):
    return os.path.join(benchmark, 'PInferOutputs')

def pinfer_checkpoint(benchmark):
    return os.path.join(benchmark, 'PTst', 'PInferCheckpoint.json')

def pinfer_specs(benchmark):
    return os.path.join(benchmark, 'PTst', 'PInferSpecs')

def pinfer_generated_test(benchmark):
    return os.path.join(benchmark, 'PTst', 'PInferGeneratedTest.p')

def slurm_out(benchmark):
    return os.path.join(benchmark, '*.out')

def stats(benchmark):
    return os.path.join(benchmark, 'pruned_stats*.json')

def invs(benchmark):
    return os.path.join(benchmark, '*.txt')

def rm(path):
    os.system(f'rm -rf {path}')

def cleanup(benchmarks, spec_only=False):
    for benchmark in benchmarks:
        if os.path.exists(benchmark):
            print(f'Cleaning up {benchmark}')
            rm(pinfer_generated_test(benchmark))
            rm(pinfer_specs(benchmark))
            rm(pinfer_checkpoint(benchmark))
            if not spec_only:
                rm(checker_out(benchmark))
                rm(pgenerated(benchmark))
                rm(pinfer_out(benchmark))
                rm(slurm_out(benchmark))
                rm(stats(benchmark))
                rm(invs(benchmark))
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--benchmarks', type=str, nargs='+', default=benchmarks)
    parser.add_argument('--spec-only', action='store_true')
    args = parser.parse_args()
    cleanup(args.benchmarks, spec_only=args.spec_only)