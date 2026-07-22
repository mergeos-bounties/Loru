import argparse
from .gloss_coverage import generate_gloss_coverage_heatmap

def main():
    parser = argparse.ArgumentParser(description='Loru CLI')
    subparsers = parser.add_subparsers(dest='command')

    # Existing commands...

    # New command for gloss coverage heatmap
    gloss_parser = subparsers.add_parser('gloss-coverage', help='Generate gloss coverage heatmap')
    gloss_parser.add_argument('--output', help='Output file path for the heatmap')

    args = parser.parse_args()

    if args.command == 'gloss-coverage':
        generate_gloss_coverage_heatmap(args.output)
    # Existing command handling...

if __name__ == '__main__':
    main()