import os
import sys
from pathlib import Path
from loru.vocab import DEFAULT_GLOSS

def get_existing_samples(samples_dir: str = "data/samples") -> set:
    """
    Scans the samples directory recursively and returns a set of gloss names found.
    """
    existing_glosses = set()
    base_path = Path(samples_dir)
    
    if not base_path.exists():
        return existing_glosses

    for file_path in base_path.rglob("*.json"):
        # We take the stem (filename without extension) as the gloss name
        # e.g., 'data/samples/asl/fingerspell_a.json' -> 'fingerspell_a'
        existing_glosses.add(file_path.stem)
    
    return existing_glosses

def generate_heatmap():
    """
    Prints a heatmap of DEFAULT_GLOSS coverage.
    """
    existing = get_existing_samples()
    
    print("\n=== Loru Gloss Coverage Heatmap ===")
    print(f"Legend: [X] Sample Exists  [ ] Missing\n")
    
    covered_count = 0
    total_count = len(DEFAULT_GLOSS)
    
    # Sort glosses for a predictable grid
    sorted_glosses = sorted(DEFAULT_GLOSS)
    
    # Grid configuration
    cols = 3
    for i, gloss in enumerate(sorted_glosses):
        is_covered = gloss in existing
        if is_covered:
            covered_count += 1
            status = "[X]"
            # ANSI Green for covered
            color_start = "\033[92m"
            color_end = "\033[0m"
        else:
            status = "[ ]"
            # ANSI Red for missing
            color_start = "\033[91m"
            color_end = "\033[0m"
            
        entry = f"{color_start}{status} {gloss.ljust(20)}{color_end}"
        
        print(entry, end="\t")
        if (i + 1) % cols == 0:
            print()
            
    if (len(sorted_glosses)) % cols != 0:
        print()
        
    percentage = (covered_count / total_count) * 100 if total_count > 0 else 0
    print(f"\nSummary: {covered_count}/{total_count} glosses covered ({percentage:.1f}%)")
    
    if covered_count < total_count:
        missing = [g for g in DEFAULT_GLOSS if g not in existing]
        print(f"Missing: {', '.join(missing[:5])}{'...' if len(missing) > 5 else ''}")

if __name__ == "__main__":
    generate_heatmap()
