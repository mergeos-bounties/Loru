#!/usr/bin/env python3
import hashlib
import sys
from collections import defaultdict

def detect_near_duplicates(frames):
    """Detect near-duplicate gloss frames by hash comparison."""
    frame_hash_map = defaultdict(list)
    
    for offset, frame in enumerate(frames):
        frame_hash = hashlib.sha256(frame.encode('utf-8')).hexdigest()
        frame_hash_map[frame_hash].append(offset)
    
    duplicates = []
    for hash_val, offsets in frame_hash_map.items():
        if len(offsets) > 1:
            duplicates.append({
                'hash': hash_val,
                'offsets': offsets
            })
    
    return duplicates

def main():
    """Main function to process gloss frames and report duplicates."""
    frames = sys.stdin.read().strip().split('\n\n') if not sys.argv[1:] else open(sys.argv[1]).read().strip().split('\n\n')
    duplicates = detect_near_duplicates(frames)
    
    for dup in duplicates:
        print(f"Hash: {dup['hash']}")
        print(f"Offsets: {', '.join(map(str, dup['offsets']))}")
        print()

if __name__ == "__main__":
    main()