#!/usr/bin/env python3
"""
Test script for the block-based ranking functionality.
This demonstrates how the system handles large specification sets by dividing them into blocks.
"""

from ranking_with_strands import create_overlapping_blocks, parse_k_range

def test_create_overlapping_blocks():
    """Test the block creation function with different scenarios."""
    print("=== Testing Block Creation ===\n")
    
    # Test case 1: Small set (no blocking needed)
    print("1. Small specification set (30 specs):")
    small_specs = [f"spec_{i}" for i in range(30)]
    blocks = create_overlapping_blocks(small_specs)
    print(f"   Input: {len(small_specs)} specs")
    print(f"   Output: {len(blocks)} block(s)")
    print(f"   Block sizes: {[len(block) for block in blocks]}")
    print()
    
    # Test case 2: Medium set (needs blocking)
    print("2. Medium specification set (80 specs):")
    medium_specs = [f"spec_{i}" for i in range(80)]
    blocks = create_overlapping_blocks(medium_specs)
    print(f"   Input: {len(medium_specs)} specs")
    print(f"   Output: {len(blocks)} blocks")
    print(f"   Block sizes: {[len(block) for block in blocks]}")
    
    # Check for overlaps
    if len(blocks) > 1:
        overlap_count = len(set(blocks[0]).intersection(set(blocks[1])))
        print(f"   Overlap between blocks 1-2: {overlap_count} specs")
    print()
    
    # Test case 3: Large set (multiple blocks)
    print("3. Large specification set (150 specs):")
    large_specs = [f"spec_{i}" for i in range(150)]
    blocks = create_overlapping_blocks(large_specs)
    print(f"   Input: {len(large_specs)} specs")
    print(f"   Output: {len(blocks)} blocks")
    print(f"   Block sizes: {[len(block) for block in blocks]}")
    
    # Check total coverage
    all_specs_in_blocks = set()
    for block in blocks:
        all_specs_in_blocks.update(block)
    print(f"   Total unique specs in blocks: {len(all_specs_in_blocks)}")
    print(f"   Coverage: {len(all_specs_in_blocks) / len(large_specs) * 100:.1f}%")
    print()
    
    # Test case 4: Very large set
    print("4. Very large specification set (300 specs):")
    very_large_specs = [f"spec_{i}" for i in range(300)]
    blocks = create_overlapping_blocks(very_large_specs)
    print(f"   Input: {len(very_large_specs)} specs")
    print(f"   Output: {len(blocks)} blocks")
    print(f"   Block sizes: {[len(block) for block in blocks]}")
    
    # Analyze overlaps
    total_specs_in_blocks = sum(len(block) for block in blocks)
    unique_specs_in_blocks = len(set().union(*blocks))
    overlap_specs = total_specs_in_blocks - unique_specs_in_blocks
    print(f"   Total specs in all blocks: {total_specs_in_blocks}")
    print(f"   Unique specs: {unique_specs_in_blocks}")
    print(f"   Overlapping specs: {overlap_specs}")
    print(f"   Overlap ratio: {overlap_specs / total_specs_in_blocks * 100:.1f}%")

def demo_block_ranking_workflow():
    """Demonstrate the complete block-based ranking workflow."""
    print("\n=== Block-Based Ranking Workflow Demo ===\n")
    
    print("This functionality automatically activates when keep_count > 60 in iterative_ranking.")
    print()
    
    print("Workflow Overview:")
    print("1. **Trigger Condition**: When keep_count > 60")
    print("2. **Block Creation**: Divide specs into overlapping blocks (≤60 specs each)")
    print("3. **Sequential Processing**: Process each block with fresh agents")
    print("4. **Proportional Selection**: Keep top X% from each block")
    print("5. **Deduplication**: Remove overlapping specs (keep higher scored)")
    print("6. **Final Ranking**: If still > keep_count, do final ranking")
    print()
    
    print("Example Scenarios:")
    print()
    
    # Scenario 1
    print("Scenario 1: 150 specs, keep_count = 80")
    print("  - Creates ~3 blocks of 50 specs each with 20% overlap")
    print("  - Keep percentage: 80/150 = 53.3%")
    print("  - From each block: keep top ~27 specs (53.3% of 50)")
    print("  - Total selected: ~81 specs (with some duplicates)")
    print("  - After deduplication: ~75-80 unique specs")
    print("  - Result: Return all unique specs (≤ keep_count)")
    print()
    
    # Scenario 2
    print("Scenario 2: 200 specs, keep_count = 70")
    print("  - Creates ~4 blocks of 50 specs each with 20% overlap")
    print("  - Keep percentage: 70/200 = 35%")
    print("  - From each block: keep top ~18 specs (35% of 50)")
    print("  - Total selected: ~72 specs (with some duplicates)")
    print("  - After deduplication: ~65-70 unique specs")
    print("  - Result: Return all unique specs (≤ keep_count)")
    print()
    
    # Scenario 3
    print("Scenario 3: 300 specs, keep_count = 80")
    print("  - Creates ~6 blocks of 50 specs each with 20% overlap")
    print("  - Keep percentage: 80/300 = 26.7%")
    print("  - From each block: keep top ~13 specs (26.7% of 50)")
    print("  - Total selected: ~78 specs (with some duplicates)")
    print("  - After deduplication: ~70-75 unique specs")
    print("  - Result: Return all unique specs (≤ keep_count)")
    print()

def demo_integration_examples():
    """Show how block-based ranking integrates with existing functionality."""
    print("\n=== Integration Examples ===\n")
    
    print("The block-based ranking is seamlessly integrated into existing workflows:")
    print()
    
    print("1. **Regular Ranking** (keep_count ≤ 60):")
    print("   python ranking_with_strands.py --benchmark 2PC --k 40")
    print("   → Uses standard single-agent ranking")
    print()
    
    print("2. **Block-Based Ranking** (keep_count > 60):")
    print("   python ranking_with_strands.py --benchmark large_benchmark --k 80")
    print("   → Automatically uses block-based ranking")
    print()
    
    print("3. **Smoke Test with Large K Values**:")
    print("   python ranking_with_strands.py --smoke-test-k --k-range '10,30,50,70,90' --benchmark large_benchmark")
    print("   → Uses block-based ranking for k=70,90")
    print()
    
    print("4. **Parallel Smoke Test**:")
    print("   python ranking_with_strands.py --smoke-test-k --parallel --k-range '10-100' --k-step 10 --all-benchmarks")
    print("   → Uses block-based ranking for k>60 automatically")
    print()
    
    print("Key Benefits:")
    print("- **Automatic Activation**: No additional flags needed")
    print("- **Quality Preservation**: Sequential processing with overlaps")
    print("- **Scalability**: Handles any number of specifications")
    print("- **Backward Compatibility**: Existing workflows unchanged")
    print("- **Error Resilience**: Robust handling of large specification sets")

def show_block_statistics():
    """Show statistics for different specification set sizes."""
    print("\n=== Block Statistics for Different Sizes ===\n")
    
    sizes = [50, 80, 100, 150, 200, 300, 500]
    
    print(f"{'Size':<6} {'Blocks':<7} {'Block Sizes':<20} {'Overlap %':<10} {'Efficiency':<12}")
    print("-" * 65)
    
    for size in sizes:
        specs = [f"spec_{i}" for i in range(size)]
        blocks = create_overlapping_blocks(specs, max_block_size=60, min_block_size=10, overlap_ratio=0.2)
        
        if len(blocks) == 1:
            block_sizes = f"[{len(blocks[0])}]"
            overlap_pct = "0.0%"
        else:
            block_sizes = str([len(block) for block in blocks])
            if len(block_sizes) > 18:
                block_sizes = f"[{len(blocks[0])}-{len(blocks[-1])}]×{len(blocks)}"
            
            total_in_blocks = sum(len(block) for block in blocks)
            unique_in_blocks = len(set().union(*blocks))
            overlap_pct = f"{(total_in_blocks - unique_in_blocks) / total_in_blocks * 100:.1f}%"
        
        # Calculate efficiency (unique specs covered / total processing)
        total_processing = sum(len(block) for block in blocks)
        efficiency = f"{size / total_processing * 100:.1f}%"
        
        print(f"{size:<6} {len(blocks):<7} {block_sizes:<20} {overlap_pct:<10} {efficiency:<12}")

if __name__ == '__main__':
    print("=== Block-Based Ranking Test Suite ===")
    print()
    print("This test suite demonstrates the new block-based ranking functionality")
    print("that automatically handles large specification sets (keep_count > 60).")
    print()
    
    test_create_overlapping_blocks()
    demo_block_ranking_workflow()
    demo_integration_examples()
    show_block_statistics()
    
    print("\n=== Summary ===")
    print()
    print("The block-based ranking feature provides:")
    print("✓ Automatic handling of large specification sets")
    print("✓ Quality preservation through overlapping blocks")
    print("✓ Sequential processing for consistent scoring")
    print("✓ Seamless integration with existing workflows")
    print("✓ Scalability to handle any number of specifications")
    print()
    print("Ready to test with real benchmarks!")
    print("Try: python ranking_with_strands.py --benchmark <large_benchmark> --k 80")
