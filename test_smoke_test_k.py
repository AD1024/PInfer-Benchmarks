#!/usr/bin/env python3
"""
Test script for the smoke test k-values functionality.
This demonstrates how to use the new smoke test feature.
"""

from ranking_with_strands import parse_k_range, smoke_test_k_values

def test_parse_k_range():
    """Test the k range parsing function."""
    print("Testing parse_k_range function...")
    
    # Test comma-separated values
    result1 = parse_k_range("10,20,30,40")
    print(f"parse_k_range('10,20,30,40') = {result1}")
    
    # Test range with default step
    result2 = parse_k_range("10-50", 10)
    print(f"parse_k_range('10-50', 10) = {result2}")
    
    # Test range with custom step
    result3 = parse_k_range("10-30", 5)
    print(f"parse_k_range('10-30', 5) = {result3}")
    
    # Test single value
    result4 = parse_k_range("25")
    print(f"parse_k_range('25') = {result4}")
    
    print()

def demo_smoke_test_usage():
    """Demonstrate smoke test usage patterns."""
    print("=== Smoke Test K-Values Demo ===\n")
    
    print("This functionality adds comprehensive smoke testing across multiple k values.")
    print("The system tests different k values (10-70) and organizes results by k value.\n")
    
    print("=== Key Features ===")
    print("1. **Multiple K Values**: Test k=10,20,30,40,50,60,70 systematically")
    print("2. **Organized Results**: JSON structure with k values as top-level keys")
    print("3. **Progress Tracking**: Real-time progress and intermediate saves")
    print("4. **Comprehensive Statistics**: Coverage and token usage by k value")
    print("5. **Error Handling**: Continue testing even if some combinations fail")
    print()
    
    print("=== Usage Examples ===")
    print()
    
    print("1. Basic smoke test with default k range (10-70, step 10):")
    print("   python ranking_with_strands.py --smoke-test-k --benchmarks 2PC firewall")
    print()
    
    print("2. Custom k range with comma-separated values:")
    print("   python ranking_with_strands.py --smoke-test-k --k-range '10,15,20,25,30' --all-benchmarks")
    print()
    
    print("3. Custom k range with step size:")
    print("   python ranking_with_strands.py --smoke-test-k --k-range '10-50' --k-step 5 --benchmarks 2PC")
    print()
    
    print("4. All benchmarks with default range:")
    print("   python ranking_with_strands.py --smoke-test-k --all-benchmarks")
    print()
    
    print("5. Parallel processing with custom workers:")
    print("   python ranking_with_strands.py --smoke-test-k --parallel --max-workers 8 --benchmarks 2PC firewall")
    print()
    
    print("6. Parallel processing with all benchmarks:")
    print("   python ranking_with_strands.py --smoke-test-k --parallel --all-benchmarks")
    print()
    
    print("=== Output JSON Structure ===")
    print("""
{
  "metadata": {
    "x_percentage": 20,
    "model_id": "us.anthropic.claude-sonnet-4-20250514-v1:0",
    "benchmarks_tested": ["2PC", "firewall"],
    "k_values_tested": [10, 20, 30, 40, 50, 60, 70],
    "timestamp": "2025-06-26T06:35:16Z",
    "total_combinations": 14
  },
  "10": {
    "2PC": {
      "benchmark": "2PC",
      "k": 10,
      "confirmed_specs_found": 2,
      "confirmed_specs_total": 2,
      "coverage_percentage": 100.0,
      "total_tokens": 15000,
      "final_rankings": [...]
    },
    "firewall": {...},
    "_summary": {
      "k_value": 10,
      "overall_coverage_percentage": 85.5,
      "total_tokens": 28000,
      "successful_benchmarks": 2
    }
  },
  "20": {...},
  "overall_summary": {
    "total_combinations_tested": 14,
    "successful_runs": 14,
    "coverage_by_k_value": {
      "10": 85.5,
      "20": 92.1,
      "30": 94.8
    },
    "tokens_by_k_value": {
      "10": 28000,
      "20": 35000,
      "30": 42000
    }
  }
}
""")
    
    print("=== Key Benefits ===")
    print("- **Systematic Analysis**: Compare performance across different k values")
    print("- **Optimal K Detection**: Find the best k value for each benchmark")
    print("- **Resource Planning**: Understand token costs for different k values")
    print("- **Coverage Analysis**: See how coverage changes with k")
    print("- **Batch Processing**: Test multiple benchmarks and k values efficiently")
    print()

def show_expected_workflow():
    """Show the expected workflow for smoke testing."""
    print("=== Smoke Test Workflow ===")
    print()
    print("1. **Initialization**:")
    print("   - Parse k range (e.g., 10-70 with step 10)")
    print("   - Set up result structure with k values as keys")
    print("   - Initialize progress tracking")
    print()
    
    print("2. **For each k value:**")
    print("   - Print k value header")
    print("   - For each benchmark:")
    print("     - Run iterative_ranking(benchmark, k, x)")
    print("     - Store results under results[str(k)][benchmark]")
    print("     - Update statistics")
    print("     - Save intermediate results")
    print("   - Calculate k-level summary")
    print()
    
    print("3. **Final Analysis**:")
    print("   - Calculate overall statistics")
    print("   - Generate coverage trends by k value")
    print("   - Compute token usage patterns")
    print("   - Save final comprehensive results")
    print()
    
    print("4. **Progress Tracking**:")
    print("   - [1/14] (7.1%) Processing 2PC with k=10")
    print("   - [2/14] (14.3%) Processing firewall with k=10")
    print("   - ...")
    print("   - K=10 Summary: 2/2 successful, 85.5% coverage, 28,000 tokens")
    print()

if __name__ == '__main__':
    demo_smoke_test_usage()
    test_parse_k_range()
    show_expected_workflow()
    
    print("=== Ready to Test ===")
    print("The smoke test functionality is ready to use!")
    print("Try a small test first:")
    print("python ranking_with_strands.py --smoke-test-k --k-range '10,20' --benchmarks 2PC")
