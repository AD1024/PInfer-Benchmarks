#!/usr/bin/env python3
"""
Test script for the iterative ranking system with strands agents.
This demonstrates how to use the ranking_with_strands.py script.
"""

import json
from ranking_with_strands import (
    compute_score, 
    iterative_ranking, 
    DEFAULT_WEIGHTS,
    DEFAULT_MODEL_ID
)

def test_compute_score():
    """Test the compute_score function with different scenarios."""
    print("Testing compute_score function...")
    
    # Test with default weights
    score1 = compute_score(0.8, 0.9, 0.7, 0.6)
    print(f"Score with (0.8, 0.9, 0.7, 0.6): {score1}")
    
    # Test with custom weights (safety-critical system)
    safety_weights = {
        'generalization': 0.2,
        'criticality': 0.6,     # Higher weight for safety
        'distinguishability': 0.15,
        'visibility': 0.05
    }
    score2 = compute_score(0.8, 0.9, 0.7, 0.6, safety_weights)
    print(f"Score with safety weights: {score2}")
    
    # Test with user-facing system weights
    user_weights = {
        'generalization': 0.25,
        'criticality': 0.3,
        'distinguishability': 0.2,
        'visibility': 0.25      # Higher weight for user visibility
    }
    score3 = compute_score(0.8, 0.9, 0.7, 0.6, user_weights)
    print(f"Score with user-facing weights: {score3}")
    
    print(f"Default weights: {DEFAULT_WEIGHTS}")
    print()

def demo_usage():
    """Demonstrate different usage patterns."""
    print("=== Iterative Ranking with Strands Agents Demo ===\n")
    
    print("This script implements an iterative specification ranking system with the following features:")
    print("1. **Summarization Agent**: Analyzes P models to extract event flows and system roles")
    print("2. **Ranking Agent**: Scores specifications using 4 metrics (Generalization, Criticality, Distinguishability, Visibility)")
    print("3. **Iterative Filtering**: Progressively removes x% of lowest-scoring specs until k remain")
    print("4. **Compute Score Tool**: Weighted linear combination of the 4 metric scores")
    print("5. **Comprehensive Statistics**: Token usage, score distributions, confirmed spec coverage")
    print()
    
    print("=== Usage Examples ===")
    print()
    
    print("1. Single benchmark with default parameters:")
    print("   python ranking_with_strands.py --benchmark 2PC")
    print()
    
    print("2. Multiple benchmarks with custom k and x:")
    print("   python ranking_with_strands.py --benchmarks 2PC firewall --k 15 --x 25")
    print()
    
    print("3. All benchmarks with custom model:")
    print("   python ranking_with_strands.py --all-benchmarks --model-id us.anthropic.claude-sonnet-4-20250514-v1:0")
    print()
    
    print("4. Custom weights for safety-critical systems:")
    weights_json = '{"generalization": 0.2, "criticality": 0.6, "distinguishability": 0.15, "visibility": 0.05}'
    print(f"   python ranking_with_strands.py --benchmark 2PC --weights '{weights_json}'")
    print()
    
    print("=== Key Parameters ===")
    print("- k: Target number of top specifications (default: 20)")
    print("- x: Percentage of specs to remove each iteration, 1-99 (default: 20)")
    print("- model-id: Strands model ID (default: Claude 3.5 Sonnet)")
    print("- weights: JSON string with custom metric weights")
    print()
    
    print("=== Output ===")
    print("The script generates a JSON file with comprehensive results including:")
    print("- Final ranked specifications with individual metric scores")
    print("- Iteration-by-iteration statistics")
    print("- Token usage and performance metrics")
    print("- Coverage of confirmed specifications")
    print("- Score distributions and statistics")
    print()

def show_algorithm_details():
    """Show the detailed algorithm flow."""
    print("=== Algorithm Flow ===")
    print()
    print("1. **Initialization**:")
    print("   - Load specifications from <benchmark>/pruned_invariants.txt")
    print("   - Load target specs from <benchmark>/confirmed_specs.txt")
    print("   - Read P model from <benchmark>/PSrc/*.p")
    print()
    
    print("2. **P Model Summarization**:")
    print("   - Create summarization agent with P language expertise")
    print("   - Generate structured summary of events, flows, roles, workflow")
    print("   - Use summary to inform ranking agent")
    print()
    
    print("3. **Iterative Ranking Loop**:")
    print("   While len(specs) > k:")
    print("     a. Create fresh ranking agent (clear chat history)")
    print("     b. Score all current specifications using 4 metrics")
    print("     c. Calculate overall scores using compute_score tool")
    print("     d. Sort by overall score (descending)")
    print("     e. Remove bottom x% of specifications")
    print("     f. Track iteration statistics")
    print()
    
    print("4. **Final Ranking**:")
    print("   - Rank remaining specifications")
    print("   - Calculate comprehensive statistics")
    print("   - Analyze confirmed specification coverage")
    print()
    
    print("5. **4-Metric Scoring System**:")
    print("   - **Generalization** (0.0-1.0): Likelihood spec holds on all executions")
    print("   - **Criticality** (0.0-1.0): Severity of violations (safety/correctness)")
    print("   - **Distinguishability** (0.0-1.0): Ability to differentiate correct/incorrect behaviors")
    print("   - **Visibility** (0.0-1.0): How noticeable violations are to end users")
    print()

if __name__ == '__main__':
    demo_usage()
    test_compute_score()
    show_algorithm_details()
    
    print("=== Ready to Run ===")
    print("The ranking_with_strands.py script is ready to use!")
    print("Start with a simple test:")
    print("python ranking_with_strands.py --benchmark 2PC --k 10 --x 30")
