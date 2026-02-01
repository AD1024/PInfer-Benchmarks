import os
import json
import subprocess
from tabulate import tabulate

benchmarks = ['ring_leader',
              'consensus', '2PC', 'sharded_kv', 'paxos_hint', 'distributed_lock', 'vertical_paxos', 'firewall', 'lockserver', 'ChainReplication', 'Raft']
# merge with the following
merge = {'Raft': 'Raft_hint'}
no_smt = {}

NumInvsTotal = 'NumInvsTotal'
NumInvsPrunedBySubsumption = 'NumInvsPrunedBySubsumption'
NumInvsPrunedByTauto = 'NumInvsPrunedByTauto'
NumInvsPrunedByTautoSem = 'NumInvsPrunedByTautoSem'
NumInvsPrunedBySubsumptionSem = 'NumInvsPrunedBySubsumptionSem'
NumInvsPrunedByGrammar = 'NumInvsPrunedByGrammar'
NumInvsPrunedBySymmetry = 'NumInvsPrunedBySymmetry'
NumInvsPrunedBySanitizing = 'NumInvsPrunedBySanitizing'
TimeElapsed = 'TimeElapsed'
TimeMining = 'TimeMining'
TimePruning = 'TimePruning'
TimeSMT = 'TimeSMT'
TimeSearchEventCombination = 'TimeSearchEventCombination'
TimeCandidateTemplateGen = 'TimeCandidateTemplateGen'
NumGoalsLearnedWithHints = 'NumGoalsLearnedWithHints'
NumGoalsLearnedWithoutHints = 'NumGoalsLearnedWithoutHints'
NumGoals = 'NumGoals'
NumDaikonInvocations = 'NumDaikonInvocations'
NumEventCombinations = 'NumEventCombinations'
NumActivatedGuards = 'NumActivatedGuards'
NumAllGuards = 'NumAllGuards'
NumInvsLearnedWithHints = 'NumGoalsLearnedWithHints'
NumInvsLearnedWithoutHints = 'NumGoalsLearnedWithoutHints'
NumIndInvsLearned = 'NumIndInvsLearned'
NumIndInvs = 'NumIndInvs'
NumOutputInvs = 'NumOutputInvs'


def get_pruning_stats(benchmark, no_rerun=False):
    stats = {}
    if os.path.exists(benchmark):
        os.chdir(benchmark)
        if os.path.exists('PInferOutputs'):
            files = os.listdir('PInferOutputs')
            files.sort()
            latest = files[-1]
            if os.path.isdir(os.path.join('PInferOutputs', latest)):
                print(f'[{benchmark}] Replaying ...')
                if not no_rerun:
                    subprocess.run(['p', 'infer', '--action', 'pruning', '-pi', os.path.join('PInferOutputs', latest), '-z3'], stdout=subprocess.DEVNULL)
                # if process.returncode == 0:
                stats= json.load(open('pruned_stats.json', 'r'))
                if os.path.exists('pruned_stats_10000.json'):
                    stats_10000 = json.load(open('pruned_stats_10000.json', 'r'))
                    stats[TimeElapsed] = stats_10000[TimeElapsed]
                num_invs_learned = None
                if os.path.exists('invariants_10000.txt'):
                    with open('invariants_10000.txt', 'r') as f:
                        num_invs_learned = len(list(filter(lambda x: len(x.strip()) > 0, f.readlines())))
                if os.path.exists('pruned_invariants.txt'):
                    with open('pruned_invariants.txt', 'r') as f:
                        pruned_invs = len(list(filter(lambda x: len(x.strip()) > 0, f.readlines())))
                        num_invs_learned = min(num_invs_learned, pruned_invs) if num_invs_learned is not None else pruned_invs
                stats[NumOutputInvs] = num_invs_learned
                os.chdir('..')
                return stats
    os.chdir('..')
    return None

def load_data():
    stats = {}
    for benchmark in benchmarks:
        stats[benchmark] = {}

def merge_stats(lhs, rhs):
    if not rhs or not lhs:
        return lhs or rhs
    lhs[NumInvsTotal] += rhs[NumInvsTotal]
    lhs[NumInvsPrunedBySubsumption] += rhs[NumInvsPrunedBySubsumption]
    lhs[NumInvsPrunedByGrammar] += rhs[NumInvsPrunedByGrammar]
    lhs[NumInvsPrunedByTauto] += rhs[NumInvsPrunedByTauto]
    lhs[NumInvsPrunedBySymmetry] += rhs[NumInvsPrunedBySymmetry]
    lhs[NumInvsPrunedBySanitizing] += rhs[NumInvsPrunedBySanitizing]
    lhs[TimeElapsed] += rhs[TimeElapsed]
    lhs[TimeMining] += rhs[TimeMining]
    lhs[TimePruning] += rhs[TimePruning]
    lhs[TimeSearchEventCombination] += rhs[TimeSearchEventCombination]
    lhs[TimeCandidateTemplateGen] += rhs[TimeCandidateTemplateGen]
    lhs[NumGoalsLearnedWithHints] += rhs[NumGoalsLearnedWithHints]
    lhs[NumGoalsLearnedWithoutHints] += rhs[NumGoalsLearnedWithoutHints]
    lhs[NumGoals] += rhs[NumGoals]
    lhs[NumDaikonInvocations] += rhs[NumDaikonInvocations]
    lhs[NumEventCombinations] += rhs[NumEventCombinations]
    lhs[NumActivatedGuards] += rhs[NumActivatedGuards]
    lhs[NumAllGuards] += rhs[NumAllGuards]
    lhs[NumInvsPrunedBySubsumptionSem] += rhs[NumInvsPrunedBySubsumptionSem]
    lhs[NumInvsPrunedByTautoSem] += rhs[NumInvsPrunedByTautoSem]
    if lhs[NumOutputInvs] is not None and rhs[NumOutputInvs] is not None:
        lhs[NumOutputInvs] += rhs[NumOutputInvs]
    return lhs

def load_stats(no_rerun=False, original=False):
    data = {}
    for benchmark in benchmarks:
        if not original:
            stats = get_pruning_stats(benchmark, no_rerun)
        else:
            with open(os.path.join(benchmark, 'pruned_stats_10000.json'), 'r') as f:
                stats = json.load(f)
        if stats is None:
            print(f'{benchmark} not found')
            continue
        if benchmark in merge:
            to_merge = get_pruning_stats(merge[benchmark])
            hinted = f'{benchmark}_hint'
            hinted_stats = {}
            hinted_stats = stats.copy()
            hinted_stats = merge_stats(hinted_stats, to_merge)
            data[hinted] = hinted_stats
        data[benchmark] = stats
    return data

def draw_table_4(no_run=False):
    data = load_stats(no_run)
    headers = ['Benchmark', 'I_pinfer/I_goals', '#UG', 'Time (s)']
    table = []
    num_daikon_invocations = 0
    time_mining = 0
    for benchmark in data:
        if benchmark in merge:
            continue
        stats = data[benchmark]
        entry = [benchmark]
        entry.append(f'{stats[NumGoalsLearnedWithHints]} / {stats[NumGoals]}')
        entry.append(stats[NumInvsLearnedWithHints] - stats[NumGoalsLearnedWithoutHints])
        entry.append(stats[TimeElapsed])
        table.append(entry)
        num_daikon_invocations += stats[NumDaikonInvocations]
        time_mining += stats[TimeMining]
    drew_table = tabulate(table, headers=headers, tablefmt='grid')
    print(drew_table)
    with open('table_4.txt', 'w') as f:
        f.write(drew_table + '\n')
        f.write(f'Total number of Daikon invocations: {num_daikon_invocations}\n'
                f'Total time spent on mining: {time_mining}\n'
                f'Average time per invocation: {time_mining / num_daikon_invocations}\n'
                f'Average number of invs per benchmark: {num_daikon_invocations / len(benchmarks)}\n')

def draw_llm_ranking():
    result = {}
    if os.path.exists('iterative_ranking_results_latest.json'):
        with open('iterative_ranking_results_latest.json', 'r') as f:
            data = json.load(f)
        for benchmark, stats in data.items():
            found = set(stats['confirmed_found_list'])
            final_ranking = stats['final_rankings']
            final_ranking.sort(key=lambda x: x['overall_score'], reverse=True)
            k = 0
            for entry in final_ranking:
                k += 1
                if entry['specification'] in found:
                    found -= {entry['specification']}
                if len(found) == 0:
                    break
            result[benchmark] = k
    return result


def draw_pruning_steps(no_rerun=False):
    data = load_stats(no_rerun)
    # headers = ['Benchmark', 'I_mined', 'R_sa', 'R_gm', 'R_tauto', 'R_sub', 'R_sym', 'I_likely', 't_SMT (ms)']
    headers = ['Benchmark', 'I_raw', 'I_asm', 'I_syn', 'I_smt', 'I_raw/I_smt', 'Time (ms)']
    table = []

    ratio = 0
    ratios = []
    total_time = 0
    num_liklies = {}

    for benchmark in data:
        if benchmark in merge:
            continue
        stats = data[benchmark]
        entry = [benchmark]
        entry.append(stats[NumInvsTotal])
        I_raw = stats[NumInvsTotal] - stats[NumInvsPrunedBySanitizing] - stats[NumInvsPrunedByGrammar]
        entry.append(f'{stats[NumInvsTotal] - stats[NumInvsPrunedBySanitizing] - stats[NumInvsPrunedByGrammar]}')
        I_syn = I_raw - stats[NumInvsPrunedByTauto] - stats[NumInvsPrunedBySubsumption] - stats[NumInvsPrunedBySymmetry]
        entry.append(f'{I_syn}')
        I_likely = I_syn - stats[NumInvsPrunedByTautoSem] - stats[NumInvsPrunedBySubsumptionSem] if stats[NumOutputInvs] is None else stats[NumOutputInvs]
        num_liklies[benchmark] = I_likely
        entry.append(f'{I_likely}')
        entry.append(stats[NumInvsTotal] / I_likely)
        entry.append(stats[TimePruning])
        ratio += stats[NumInvsTotal] / I_likely
        ratios.append(stats[NumInvsTotal] / I_likely)
        table.append(entry)
        total_time += stats[TimePruning]
    r = 1
    for rat in ratios:
        r *= rat
    r = r ** (1 / len(ratios))
    llm_results = draw_llm_ranking()
    running_ratio = 1
    if llm_results:
        headers.append('LLM Top-k')
        for entry in table:
            benchmark = entry[0]
            if benchmark in llm_results:
                entry.append(f'{llm_results[benchmark]} ({((llm_results[benchmark] / num_liklies[benchmark])*100):.2f}%)')
                running_ratio *= ((llm_results[benchmark] / num_liklies[benchmark]) * 100)
            else:
                entry.append('N/A')
    drew_table = tabulate(table, headers=headers, tablefmt='grid')
    print(drew_table)
    with open('table_5.txt', 'w') as f:
        f.write(drew_table + '\n')
        f.write(f'Average ratio: {ratio / len(benchmarks)}\n')
        f.write(f'Geometric Avg: {r}\n')
        f.write(f'LLM ranked percentage (Geo-Mean): {running_ratio ** (1 / len(benchmarks))}\n')
        f.write(f'Min ratio: {min(ratios)}\n')
        f.write(f'Max ratio: {max(ratios)}\n')
        f.write(f'Average time: {total_time / len(benchmarks)}\n')

def draw_prune_by_pchecker():
    headers = ['Benchmark', 'I_false', 'Time (s)']
    table = []
    for benchmark in benchmarks:
        ckpt = os.path.join(benchmark, 'PTst', 'PInferCheckpoint.json')
        output = os.path.join(benchmark, 'prune_after_mc.txt')
        entry = []
        entry.append(benchmark)
        time = 'TO'
        if os.path.exists(ckpt):
            with open(ckpt, 'r') as f:
                checkpoint_data = json.load(f)
                entry.append(len(checkpoint_data['falsified_monitors']))
                time = checkpoint_data['time']
        else:
            entry.append('RE')
        if not os.path.exists(output):
            time = 'TO'
        entry.append(time)
        table.append(entry)
    drew_table = tabulate(table, headers=headers, tablefmt='grid')
    print(drew_table)
    with open('table_5_falsified.txt', 'w') as f:
        f.write(drew_table + '\n')

def draw_table_6(no_rerun=False):
    data = load_stats(no_rerun)
    headers = ['Benchmark', '(I_s+I_e)/I_ind']
    table = []
    sub_experiments = ['ring_leader', 'consensus', 'distributed_lock', 'lockserver', 'firewall', 'sharded_kv']
    for benchmark in sub_experiments:
        if benchmark not in data:
            print(f'no data recorded for {benchmark}, try run PInfer first')
            continue
        stats = data[benchmark]
        entry = [benchmark]
        entry.append(f'{stats[NumIndInvsLearned]}/{stats[NumIndInvs]}')
        table.append(entry)
    drew_table = tabulate(table, headers=headers, tablefmt='grid')
    print(drew_table)
    with open('table_6.txt', 'w') as f:
        f.write(drew_table + '\n')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--tables', type=str, nargs='+', default=benchmarks)
    parser.add_argument('--no-rerun', action='store_true')
    args = parser.parse_args()
    no_rerun = args.no_rerun
    if '4' in args.tables:
        draw_table_4(no_run=args.no_rerun)
        if not args.no_rerun:
            no_rerun = True
    if '5' in args.tables:
        draw_pruning_steps(no_rerun=no_rerun)
        if not args.no_rerun:
            no_rerun = True    
    if '5-1' in args.tables:
        draw_prune_by_pchecker()
    if '6' in args.tables:
        draw_table_6(no_rerun=no_rerun)