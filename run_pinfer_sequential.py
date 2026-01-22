import os
from constants import benchmarks

# run each benchmark sequentially
for benchmark in benchmarks:
    print(f'=============Running {benchmark}=============')
    os.chdir(benchmark)
    os.system('chmod +x job.slurm')
    os.system('./job.slurm')
    os.chdir('..')