import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
import sys

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

FILENAME = "iterative_ranking_results_latest.json"
# Benchmark name mappings for better display
row_label_maps = {
    'Kermit2PC': '2PC-CC',
    'JournalLeaderElection': 'DynamoDB-LE', 
    'ClockBound': 'ClockBound',
    'Raft_hint': 'Raft',
    'paxos_hint': 'Paxos',
    'vertical_paxos': 'Vertical Paxos',
    'distributed_lock': 'Distributed Lock',
    'ring_leader': 'Ring Leader',
    'sharded_kv': 'Sharded KV',
    'lockserver': 'Lock Server',
    'ChainReplication': 'Chain',
    '2PC': '2PC',
    'firewall': 'Whitelist',
    'consensus': 'Toy Consensus'
}

def compute_price(num_input_tokens, num_output_tokens):
    price_per_million_input = 3
    price_per_million_output = 15
    input_cost = (num_input_tokens / 1_000_000) * price_per_million_input
    output_cost = (num_output_tokens / 1_000_000) * price_per_million_output
    return input_cost + output_cost

def load_results(filename):
    try:
        with open(filename, 'r') as file:
            results = json.load(file)
        return results
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None
    
def compute_summary(results):
    """Compute summary statistics for iterative ranking results"""
    summary = {}
    rank_summary = {}
    
    for benchmark, data in results.items():
        confirmed = set(data["confirmed_found_list"])
        final_ranking = data["final_rankings"]
        final_ranking = sorted(final_ranking, key=lambda x: x['overall_score'], reverse=True)
        
        # Initialize summary for this benchmark
        rank_summary[benchmark] = []
        summary[benchmark] = {
            'num_confirmed': len(confirmed),
            'total_confirmed_specs': data.get("confirmed_specs_total", 0),
            'coverage_percentage': data.get("coverage_percentage", 0.0),
            'num_input_tokens': 0,
            'num_output_tokens': 0,
            'total_tokens': data.get("total_tokens", 0),
            'iterations': data.get("iterations", 1),
            'final_spec_count': data.get("final_spec_count", len(final_ranking)),
            'avg_score': data.get("score_statistics", {}).get("avg_score", 0.0),
            'median_score': data.get("score_statistics", {}).get("median_score", 0.0)
        }
        
        # Sum up tokens from all iterations
        if "iteration_stats" in data:
            for iteration_stat in data["iteration_stats"]:
                if "agent_tokens" in iteration_stat:
                    summary[benchmark]['num_input_tokens'] += iteration_stat['agent_tokens']['num_input_tokens']
                    summary[benchmark]['num_output_tokens'] += iteration_stat['agent_tokens']['num_output_tokens']
        else:
            # If no iteration stats, use total tokens directly
            summary[benchmark]['num_input_tokens'] = data.get('total_input_tokens', 0)
            summary[benchmark]['num_output_tokens'] = data.get('total_output_tokens', 0)
        
        # Try to get total specs from pruned_invariants.txt
        try:
            with open(os.path.join(benchmark, "pruned_invariants.txt"), 'r') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
                summary[benchmark]['total_specs'] = len(lines)
        except FileNotFoundError:
            # If file doesn't exist, use final_spec_count as fallback
            summary[benchmark]['total_specs'] = summary[benchmark]['final_spec_count']
        
        # Calculate cost
        summary[benchmark]['cost'] = compute_price(
            summary[benchmark]['num_input_tokens'],
            summary[benchmark]['num_output_tokens']
        )
        
        # Calculate how many confirmed specs are found in top-k rankings
        found = 0
        i = 0
        for spec in final_ranking:
            i += 1
            if spec['specification'] in confirmed:
                rank_summary[benchmark].append(i)
                found += 1
            summary[benchmark][i] = found
            # if found == summary[benchmark]['num_confirmed'] and benchmark not in converged_at:
            #     converged_at[benchmark] = i
    
    return summary, rank_summary

def create_iterative_ranking_table(results):
    """Create a table showing iterative ranking results similar to the smoke test visualization"""
    
    # Get summary data
    summary, _ = compute_summary(results)
    kvalues = [10, 20, 30, 40, 50]
    
    # Prepare data for table
    table_data = []
    row_labels = []
    
    # Separate benchmarks into proprietary and non-proprietary
    proprietary_benchmarks = {'Kermit2PC', 'JournalLeaderElection', 'ClockBound'}
    
    # Sort benchmarks
    benchmarks = sorted(results.keys())
    non_proprietary = [b for b in benchmarks if b not in proprietary_benchmarks]
    proprietary = [b for b in benchmarks if b in proprietary_benchmarks]
    
    # Process non-proprietary benchmarks first
    for benchmark in non_proprietary:
        if benchmark in summary:
            data = summary[benchmark]
            
            # Create row data showing confirmed specs found in top-k
            row_data = []
            for k in kvalues:
                found_at_k = data.get(k, data['num_confirmed'])  # Use total found if k not available
                total_confirmed = data['total_confirmed_specs']
                row_data.append(f"{found_at_k}/{total_confirmed}")
            
            # Add cost column
            row_data.append(f"${data['cost']:.2f}")
            
            table_data.append(row_data)
            
            # Create row label
            benchmark_name = row_label_maps.get(benchmark, benchmark.replace("_", " ").title())
            row_labels.append(f"{benchmark_name} ({data['total_specs']})")
    
    # Process proprietary benchmarks
    for benchmark in proprietary:
        if benchmark in summary:
            data = summary[benchmark]
            
            # Create row data showing confirmed specs found in top-k
            row_data = []
            for k in kvalues:
                found_at_k = data.get(k, data['num_confirmed'])  # Use total found if k not available
                total_confirmed = data['total_confirmed_specs']
                row_data.append(f"{found_at_k}/{total_confirmed}")
            
            # Add cost column
            row_data.append(f"${data['cost']:.2f}")
            
            table_data.append(row_data)
            
            # Create row label
            benchmark_name = row_label_maps.get(benchmark, benchmark.replace("_", " ").title())
            row_labels.append(f"{benchmark_name} ({data['total_specs']})")
    
    # Calculate summary row
    summary_row = []
    percentage_row = []
    for k in kvalues:
        total_found_at_k = 0
        total_confirmed_specs = 0
        for benchmark in summary:
            data = summary[benchmark]
            found_at_k = data.get(k, data['num_confirmed'])
            total_found_at_k += found_at_k
            total_confirmed_specs += data['total_confirmed_specs']
        summary_row.append(f"{total_found_at_k}/{total_confirmed_specs}")
        percentage_row.append(f"{(total_found_at_k / total_confirmed_specs) * 100:.1f}%" if total_confirmed_specs > 0 else "0.0%")
    
    # Add total cost to summary rows
    total_cost = sum(data['cost'] for data in summary.values())
    summary_row.append(f"${total_cost:.2f}")
    percentage_row.append("-")  # No percentage for cost
    
    table_data.append(summary_row)
    row_labels.append("Overall")
    table_data.append(percentage_row)
    row_labels.append("Coverage (%)")
    
    # Create figure for table
    fig, ax = plt.subplots(figsize=(7, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # Column headers showing k values and cost
    col_labels = [f"k={k}" for k in kvalues] + ["Cost"]
    
    # Create table
    table = ax.table(cellText=table_data,
                    rowLabels=row_labels,
                    colLabels=col_labels,
                    cellLoc='center',
                    loc='center',
                    bbox=[0, 0, 1, 1])
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(12)  # Smaller font size for single column
    table.scale(1, 1)  # Much more aggressive row compression for minimal cell height
    
    # Color coding for better readability
    non_proprietary_count = len(non_proprietary)
    proprietary_count = len(proprietary)
    total_benchmark_count = non_proprietary_count + proprietary_count
    
    # Color benchmark rows based on performance
    for i in range(total_benchmark_count):
        for j in range(len(kvalues)):
            cell = table[(i+1, j)]  # +1 because row 0 is header
            
            # Parse the found/total format
            cell_text = table_data[i][j]
            if "/" in cell_text:
                found, total = cell_text.split('/')
                found_int = int(found)
                total_int = int(total)
                
                if total_int > 0:
                    percentage = (found_int / total_int) * 100
                    
                    # Color code based on percentage
                    if percentage == 100:
                        cell.set_facecolor('#90EE90')  # Light green for 100%
                    elif percentage >= 75:
                        cell.set_facecolor('#FFFFE0')  # Light yellow for 75-99%
                    elif percentage >= 50:
                        cell.set_facecolor('#FFE4B5')  # Light orange for 50-74%
                    elif percentage > 0:
                        cell.set_facecolor('#FFB6C1')  # Light pink for 1-49%
                    else:
                        cell.set_facecolor('#F0F0F0')  # Light gray for 0%
                else:
                    cell.set_facecolor('#F0F0F0')  # Light gray for no data
    
    # Style the summary row (last row)
    summary_row_idx = total_benchmark_count + 1
    for j in range(len(col_labels)):  # Include cost column
        for row_idx in [summary_row_idx, summary_row_idx + 1]:
            cell = table[(row_idx, j)]
            cell.set_facecolor('#D3D3D3')  # Light gray background for summary
            cell.set_text_props(weight='bold', color='black')
    
    # Style header row
    for j in range(len(col_labels)):  # Include cost column
        cell = table[(0, j)]
        cell.set_facecolor('#4472C4')
        cell.set_text_props(weight='bold', color='white')
    
    # Style row labels with different colors for proprietary vs non-proprietary
    for i in range(len(row_labels)):
        cell = table[(i+1, -1)]
        if i == len(row_labels) - 1 or i == len(row_labels) - 2:  # Summary row
            cell.set_facecolor('#D3D3D3')
            cell.set_text_props(weight='bold', color='black')
        elif i < non_proprietary_count:  # Non-proprietary benchmarks
            cell.set_facecolor('#4472C4')  # Blue for non-proprietary
            cell.set_text_props(weight='bold', color='white')
        else:  # Proprietary benchmarks
            cell.set_facecolor('#8B4513')  # Brown for proprietary
            cell.set_text_props(weight='bold', color='white')
    
    # plt.title('', 
    #           fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    
    # Save in both formats
    png_filename = 'iterative_ranking_table.png'
    pdf_filename = 'iterative_ranking_table.pdf'
    plt.savefig(png_filename, dpi=300, bbox_inches='tight')
    plt.savefig(pdf_filename, bbox_inches='tight')
    print(f"Saved table: {png_filename}, {pdf_filename}")
    
    plt.show()
    
    return summary

def load_baseline(benchmarks):
    summary = {}
    rank_summary = {}
    num_specs = {}
    for benchmark in benchmarks:
        summary[benchmark] = {
        }
        rank_summary[benchmark] = []
        try:
            with open(os.path.join(benchmark, "pruned_invariants.txt"), "r") as f:
                specs = [line.strip() for line in f.readlines() if line.strip()]
                num_specs[benchmark] = len(specs)
            with open(os.path.join(benchmark, "confirmed_specs.txt"), "r") as f:
                confirmed = [line.strip() for line in f.readlines() if line.strip()]
            i = 0
            found = 0
            for learned in specs:
                i += 1
                if learned in confirmed:
                    rank_summary[benchmark].append(i)
                    found += 1
                summary[benchmark][i] = found
                # if found == len(confirmed) and benchmark not in converged_at:
                #     converged_at[benchmark] = i
        except:
            print(f"Failed to load pruned invariants for {benchmark}. Skipping.")
            continue
    return summary, rank_summary, num_specs

def draw_converged_at_comparisons(baseline_ranks, iterative_ranks, num_confirmed):
    """Draw box plots for benchmarks with >1 specs and table for single-spec benchmarks"""
    import numpy as np
    
    # Separate benchmarks by number of confirmed specs
    multi_spec_benchmarks = []
    single_spec_benchmarks = []
    
    for benchmark in sorted(baseline_ranks.keys()):
        if (benchmark in iterative_ranks and len(iterative_ranks[benchmark]) > 1) or \
           (benchmark in baseline_ranks and len(baseline_ranks[benchmark]) > 1):
            multi_spec_benchmarks.append(benchmark)
        else:
            single_spec_benchmarks.append(benchmark)
    
    # Create separate figures for box plots and table
    
    # Box plot for multi-spec benchmarks
    if multi_spec_benchmarks:
        plt.clf()
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        
        # Prepare data for box plots
        box_data = []
        positions = []
        colors = []
        
        pos = 1
        for benchmark in multi_spec_benchmarks:
            # Add iterative ranking data
            if benchmark in iterative_ranks and iterative_ranks[benchmark]:
                box_data.append(iterative_ranks[benchmark])
                positions.append(pos)
                colors.append('#4ECDC4')
                pos += 1
            
            # Add baseline data
            if benchmark in baseline_ranks and baseline_ranks[benchmark]:
                box_data.append(baseline_ranks[benchmark])
                positions.append(pos)
                colors.append('#FF6B6B')
                pos += 1
            
            pos += 1.5  # Add space between benchmarks
        
        # Create the box plot
        bp = ax1.boxplot(box_data, positions=positions, patch_artist=True,
                        boxprops=dict(alpha=0.8),
                        medianprops=dict(color='black', linewidth=2),
                        whiskerprops=dict(linewidth=1.5),
                        capprops=dict(linewidth=1.5),
                        flierprops=dict(marker='o', markersize=3, alpha=0.6),
                        widths=0.8)
        
        # Color the boxes
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
        
        # Set up x-axis labels and ticks
        benchmark_positions = []
        benchmark_labels = []
        pos = 1
        for benchmark in multi_spec_benchmarks:
            center_pos = pos + 0.5  # Center between the two boxes
            benchmark_positions.append(center_pos)
            benchmark_labels.append(row_label_maps.get(benchmark, benchmark.replace("_", " ").title()))
            pos += 3.5  # Move to next benchmark (2 boxes + 1 space)
        
        ax1.set_xticks(benchmark_positions)
        ax1.set_xticklabels(benchmark_labels, rotation=45, ha='center', fontsize=14)
        
        # Customize the plot
        ax1.set_ylabel('Ranking', fontsize=16, fontweight='bold')
        ax1.set_title('Known Specification Ranking Distribution', 
                     fontsize=16, fontweight='bold')
        ax1.tick_params(axis='y', which='major', labelsize=12)
        ax1.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor='#4ECDC4', alpha=0.8, label='Ours'),
                          Patch(facecolor='#FF6B6B', alpha=0.8, label='Baseline')]
        ax1.legend(handles=legend_elements, fontsize=14, loc='upper left', frameon=True, fancybox=True, shadow=True)
        
        # Add some styling
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_linewidth(0.5)
        ax1.spines['bottom'].set_linewidth(0.5)
        
        plt.tight_layout()
        
        # Save the box plot
        boxplot_png = 'convergence_boxplot.png'
        boxplot_pdf = 'convergence_boxplot.pdf'
        plt.savefig(boxplot_png, dpi=300, bbox_inches='tight')
        plt.savefig(boxplot_pdf, bbox_inches='tight')
        print(f"Saved box plot: {boxplot_png}, {boxplot_pdf}")
        plt.show()
    
    # Table for single-spec benchmarks
    if single_spec_benchmarks:
        plt.clf()
        fig2, ax2 = plt.subplots(figsize=(9.5, 2))
        ax2.axis('tight')
        ax2.axis('off')
        
        # Prepare table data
        table_data = []
        col_labels = []
        
        # Get baseline and iterative ranks for single-spec benchmarks
        baseline_row = []
        iterative_row = []
        
        for benchmark in single_spec_benchmarks:
            label = row_label_maps.get(benchmark, benchmark.replace("_", " ").title())
            col_labels.append(label if len(label) <= 10 else label.replace(" ", "\n"))
            
            # Get baseline rank (should be single value)
            if benchmark in baseline_ranks and baseline_ranks[benchmark]:
                baseline_row.append(str(baseline_ranks[benchmark][0]))
            else:
                baseline_row.append("-")
            
            # Get iterative rank (should be single value)
            if benchmark in iterative_ranks and iterative_ranks[benchmark]:
                iterative_row.append(str(iterative_ranks[benchmark][0]))
            else:
                iterative_row.append("-")
        
        table_data = [baseline_row, iterative_row]
        row_labels = ['Baseline', 'Ours']
        
        # Create table
        table = ax2.table(cellText=table_data,
                         rowLabels=row_labels,
                         colLabels=col_labels,
                         cellLoc='center',
                         loc='center',
                         bbox=[0, 0, 1, 1])
        
        # Style the table
        table.auto_set_font_size(False)
        table.set_fontsize(14)
        table.scale(1, 2)
        
        # Color the rows
        for i in range(len(col_labels)):
            # Baseline row (red)
            table[(1, i)].set_facecolor('#FFE4E1')
            # Ours row (teal)
            table[(2, i)].set_facecolor('#E0F6F6')
        
        # Style header row
        for i in range(len(col_labels)):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Style row labels
        table[(1, -1)].set_facecolor('#FF6B6B')
        table[(1, -1)].set_text_props(weight='bold', color='white')
        table[(2, -1)].set_facecolor('#4ECDC4')
        table[(2, -1)].set_text_props(weight='bold', color='white')
        
        # ax2.set_title('Confirmed Specification Ranks (Single-Spec Benchmarks)', 
        #              fontsize=14, fontweight='bold', pad=15)
        
        plt.tight_layout()
        
        # Save the table
        table_png = 'convergence_table.png'
        table_pdf = 'convergence_table.pdf'
        plt.savefig(table_png, dpi=300, bbox_inches='tight')
        plt.savefig(table_pdf, bbox_inches='tight')
        print(f"Saved table: {table_png}, {table_pdf}")
        plt.show()
    
    # Print summary statistics
    print(f"\nRank Distribution Statistics by Benchmark:")
    print("-" * 80)
    
    if multi_spec_benchmarks:
        print("\nMulti-Specification Benchmarks:")
        for benchmark in multi_spec_benchmarks:
            print(f"\n{row_label_maps.get(benchmark, benchmark)}:")
            
            if benchmark in iterative_ranks and iterative_ranks[benchmark]:
                iter_ranks = iterative_ranks[benchmark]
                iter_median = np.median(iter_ranks)
                iter_q1 = np.percentile(iter_ranks, 25)
                iter_q3 = np.percentile(iter_ranks, 75)
                print(f"  Ours: Median={iter_median:.1f}, Q1={iter_q1:.1f}, Q3={iter_q3:.1f}, Count={len(iter_ranks)}")
            
            if benchmark in baseline_ranks and baseline_ranks[benchmark]:
                base_ranks = baseline_ranks[benchmark]
                base_median = np.median(base_ranks)
                base_q1 = np.percentile(base_ranks, 25)
                base_q3 = np.percentile(base_ranks, 75)
                print(f"  Baseline: Median={base_median:.1f}, Q1={base_q1:.1f}, Q3={base_q3:.1f}, Count={len(base_ranks)}")
    
    if single_spec_benchmarks:
        print("\nSingle-Specification Benchmarks:")
        for benchmark in single_spec_benchmarks:
            print(f"\n{row_label_maps.get(benchmark, benchmark)}:")
            
            if benchmark in iterative_ranks and iterative_ranks[benchmark]:
                print(f"  Ours: Rank={iterative_ranks[benchmark][0]}")
            
            if benchmark in baseline_ranks and baseline_ranks[benchmark]:
                print(f"  Baseline: Rank={baseline_ranks[benchmark][0]}")

def draw_comparisons_with_baseline(results):
    """Draw line plot comparing iterative ranking with baseline approach"""
    baseline_summary, baseline_ranks, num_specs = load_baseline(results.keys())
    iterative_summary, iterative_ranks = compute_summary(results)
    num_benchmarks = len(iterative_summary)
    
    plt.clf()
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Define k values to plot
    k_values = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

    # Aggregate data across all benchmarks
    baseline_totals = []
    iterative_totals = []
    
    iterative_all_covered = k_values[-1]  # Start with max k
    baseline_all_covered = k_values[-1]

    for k in k_values:
        baseline_total = 0
        for benchmark in baseline_summary:
            baseline_total += (baseline_summary[benchmark].get(k, iterative_summary[benchmark]['num_confirmed']) == iterative_summary[benchmark]['num_confirmed'])  # Use total found if k not available
        baseline_totals.append(baseline_total)
        if baseline_total == num_benchmarks:
            print(f"Baseline full coverage at k={k}")
            baseline_all_covered = min(baseline_all_covered, k)
        
        # Calculate iterative ranking total at top-k
        iterative_total = 0
        for benchmark in iterative_summary:
            data = iterative_summary[benchmark]
            iterative_total += (data.get(k, data['num_confirmed']) == data['num_confirmed'])  # Use total found if k not available
        iterative_totals.append(iterative_total)
        if iterative_total == num_benchmarks:
            iterative_all_covered = min(iterative_all_covered, k)
    
    # Plot the lines
    ax.plot(k_values, iterative_totals, 's-', linewidth=3, markersize=8, 
            label='Ours', color='#4ECDC4', alpha=0.8)
    ax.plot(k_values, baseline_totals, 'o-', linewidth=3, markersize=8, 
            label='Baseline', color='#FF6B6B', alpha=0.8)
    
    # Customize the plot
    ax.set_xlabel('Number of Specifications (Top-k)', fontsize=16, fontweight='bold')
    ax.set_ylabel('Number of benchmarks fully covered', fontsize=16, fontweight='bold')
    ax.set_title('Distilling with LLMs (Ours) vs Predicate Frequency (Baseline)', 
                fontsize=16, fontweight='bold', pad=20)
    
    ax.set_xticks(k_values)
    ax.tick_params(axis='both', which='major', labelsize=14)
    ax.tick_params(axis='both', which='minor', labelsize=14)
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Customize legend
    ax.legend(fontsize=14, loc='lower right', frameon=True, fancybox=True, shadow=True)
    
    # Set axis limits and ticks
    ax.set_xlim(0, max(k_values) + 1)
    ax.set_ylim(0, max(max(baseline_totals), max(iterative_totals)) * 1.1)
    
    # Add some styling
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(0.5)
    ax.spines['bottom'].set_linewidth(0.5)
    
    # Add annotations for key points
    max_baseline = max(baseline_totals)
    max_iterative = max(iterative_totals)
    
    # if max_iterative > max_baseline:
    #     improvement = ((max_iterative - max_baseline) / max_baseline) * 100
    #     ax.annotate(f'Iterative Ranking\n+{improvement:.1f}% improvement', 
    #                xy=(k_values[-1], max_iterative), xytext=(k_values[-5], max_iterative * 0.8),
    #                arrowprops=dict(arrowstyle='->', color='#4ECDC4', lw=1.5),
    #                fontsize=10, ha='center', 
    #                bbox=dict(boxstyle="round,pad=0.3", facecolor='#4ECDC4', alpha=0.2))
    ax.annotate(f'full coverage @ k={baseline_all_covered}',
                xy=(baseline_all_covered, num_benchmarks), xytext=(60, 8),
                arrowprops=dict(arrowstyle='->', color='#FF6B6B', lw=1.5),
                fontsize=14, ha='left',bbox=dict(boxstyle="round", facecolor='#FF6B6B', alpha=0.2))
    ax.annotate(f'full coverage @ k={iterative_all_covered}',
                xy=(iterative_all_covered, num_benchmarks), xytext=(40, 6),
                arrowprops=dict(arrowstyle='->', color='#4ECDC4', lw=1.5),
                fontsize=14, ha='left', bbox=dict(boxstyle="round", facecolor='#4ECDC4', alpha=0.2))
    
    plt.tight_layout()
    
    # Save the plot
    png_filename = 'iterative_vs_baseline_comparison.png'
    pdf_filename = 'iterative_vs_baseline_comparison.pdf'
    plt.savefig(png_filename, dpi=300, bbox_inches='tight')
    plt.savefig(pdf_filename, bbox_inches='tight')
    print(f"Saved comparison plot: {png_filename}, {pdf_filename}")
    
    plt.show()
    
    # Print summary statistics
    print("\n" + "="*60)
    print("BASELINE VS ITERATIVE RANKING COMPARISON")
    print("="*60)
    print(f"At k=50:")
    print(f"  Baseline (Sequential): {baseline_totals[-1]} confirmed specs")
    print(f"  Iterative Ranking: {iterative_totals[-1]} confirmed specs")
    if baseline_totals[-1] > 0:
        improvement = ((iterative_totals[-1] - baseline_totals[-1]) / baseline_totals[-1]) * 100
        print(f"  Improvement: {improvement:+.1f}%")
    print("="*60)

    draw_converged_at_comparisons(baseline_ranks, iterative_ranks, num_specs)


def print_detailed_results(results, summary):
    """Print detailed results for each benchmark"""
    print("\n" + "="*80)
    print("ITERATIVE RANKING DETAILED RESULTS")
    print("="*80)
    
    for benchmark, data in results.items():
        if benchmark in summary:
            print(f"\n{benchmark.replace('_', ' ').title()}:")
            print("-" * 50)
            
            summary_data = summary[benchmark]
            print(f"Total Specifications: {summary_data['total_specs']}")
            print(f"Confirmed Specs Found: {summary_data['num_confirmed']}/{summary_data['total_confirmed_specs']}")
            print(f"Coverage: {summary_data['coverage_percentage']:.1f}%")
            print(f"Iterations: {summary_data['iterations']}")
            print(f"Average Score: {summary_data['avg_score']:.3f}")
            print(f"Median Score: {summary_data['median_score']:.3f}")
            print(f"Total Tokens: {summary_data['total_tokens']:,}")
            print(f"Cost: ${summary_data['cost']:.2f}")
            
            # Show top 5 specifications
            print(f"\nTop 5 Ranked Specifications:")
            for i, spec in enumerate(data['final_rankings'][:5]):
                status = "✓" if spec['specification'] in data['confirmed_found_list'] else "✗"
                print(f"  {i+1}. {status} Score: {spec['overall_score']:.3f}")
                print(f"     {spec['specification'][:100]}...")

def main():
    """Main execution function"""
    # Allow filename to be passed as command line argument
    filename = sys.argv[1] if len(sys.argv) > 1 else FILENAME
    
    # Load results
    print(f"Loading results from {filename}...")
    results = load_results(filename)
    
    if results is None:
        print("Failed to load results. Exiting.")
        return
    
    print(f"Loaded results for {len(results)} benchmarks: {list(results.keys())}")
    
    # Create table visualization
    print("\nCreating iterative ranking table...")
    summary = create_iterative_ranking_table(results)
    
    # Create baseline comparison plot
    print("\nCreating baseline comparison plot...")
    draw_comparisons_with_baseline(results)
    
    # Print detailed results
    print_detailed_results(results, summary)
    
    # Print overall summary
    print("\n" + "="*80)
    print("OVERALL SUMMARY")
    print("="*80)
    
    total_specs = sum(data['total_specs'] for data in summary.values())
    total_found = sum(data['num_confirmed'] for data in summary.values())
    total_confirmed_specs = sum(data['total_confirmed_specs'] for data in summary.values())
    avg_coverage = sum(data['coverage_percentage'] for data in summary.values()) / len(summary)
    total_cost = sum(data['cost'] for data in summary.values())
    total_tokens = sum(data['total_tokens'] for data in summary.values())
    
    print(f"Total Benchmarks: {len(results)}")
    print(f"Total Specifications: {total_specs}")
    print(f"Total Confirmed Specs Found: {total_found}/{total_confirmed_specs}")
    print(f"Average Coverage: {avg_coverage:.1f}%")
    print(f"Total Cost: ${total_cost:.2f}")
    print(f"Total Tokens: {total_tokens:,}")
    
    # Show best and worst performing benchmarks
    best_coverage = max(summary.values(), key=lambda x: x['coverage_percentage'])
    worst_coverage = min(summary.values(), key=lambda x: x['coverage_percentage'])
    
    best_benchmark = [k for k, v in summary.items() if v == best_coverage][0]
    worst_benchmark = [k for k, v in summary.items() if v == worst_coverage][0]
    
    print(f"\nBest Coverage: {best_benchmark} ({best_coverage['coverage_percentage']:.1f}%)")
    print(f"Worst Coverage: {worst_benchmark} ({worst_coverage['coverage_percentage']:.1f}%)")

if __name__ == "__main__":
    main()
