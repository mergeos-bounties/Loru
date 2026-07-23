"""Export vocabulary CSV for teachers."""

import csv
from pathlib import Path
from loru.config import SAMPLES_DIR
from loru.data.loader import list_sample_files

def export_vocab_csv(output_path):
    """Export gloss vocabulary with sample availability."""
    files = list_sample_files()
    
    vocab = []
    for path in files:
        gloss = path.stem
        vocab.append({
            'gloss': gloss,
            'has_sample': True,
            'file': path.name
        })
    
    # Add missing glosses from default vocab
    from loru.models.vocab import DEFAULT_GLOSS
    existing = {v['gloss'] for v in vocab}
    for g in DEFAULT_GLOSS:
        if g not in existing:
            vocab.append({'gloss': g, 'has_sample': False, 'file': ''})
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['gloss', 'has_sample', 'file'])
        writer.writeheader()
        writer.writerows(vocab)
    
    return output_path
