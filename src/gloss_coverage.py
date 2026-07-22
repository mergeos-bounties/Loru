from .data_processor import get_default_glosses, get_sample_coverage
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def generate_gloss_coverage_heatmap(output_path=None):
    """
    Generate a heatmap showing which DEFAULT_GLOSS entries lack samples.

    Args:
        output_path (str, optional): Path to save the heatmap image. If None, displays the plot.
    """
    glosses = get_default_glosses()
    coverage = get_sample_coverage(glosses)

    # Create a DataFrame for the heatmap
    df = pd.DataFrame({
        'Gloss': glosses,
        'Sample Count': [coverage[gloss] for gloss in glosses]
    })

    # Create the heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(df.set_index('Gloss').T, cmap='YlGnBu', annot=True, fmt='d')
    plt.title('Gloss Sample Coverage Heatmap')
    plt.xlabel('Glosses')
    plt.ylabel('Sample Count')

    if output_path:
        plt.savefig(output_path)
        print(f"Heatmap saved to {output_path}")
    else:
        plt.show()