import json
from typing import List, Dict

def load_gloss_file(file_path: str) -> List[Dict]:
    """
    Load a gloss file and return its frame data.

    Args:
        file_path: Path to gloss file

    Returns:
        List of frame dictionaries
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data.get('frames', [])

def compare_frame_sequences(seq1: List[Dict], seq2: List[Dict]) -> float:
    """
    Compare two frame sequences and return a similarity score.

    Args:
        seq1: First frame sequence
        seq2: Second frame sequence

    Returns:
        Similarity score between 0 and 1
    """
    if not seq1 or not seq2:
        return 0.0

    # Simple implementation - can be enhanced with more sophisticated comparison
    min_len = min(len(seq1), len(seq2))
    matches = 0

    for i in range(min_len):
        frame1 = seq1[i]
        frame2 = seq2[i]

        # Compare key landmarks (simplified)
        if (frame1.get('landmarks') == frame2.get('landmarks') and
            frame1.get('gloss') == frame2.get('gloss')):
            matches += 1

    return matches / min_len