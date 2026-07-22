import unittest
from unittest.mock import patch
from src.cli import main

class TestCLI(unittest.TestCase):
    @patch('argparse.ArgumentParser.parse_args')
    @patch('src.cli.generate_gloss_coverage_heatmap')
    def test_gloss_coverage_command(self, mock_heatmap, mock_args):
        # Setup mock arguments
        mock_args.return_value = argparse.Namespace(command='gloss-coverage', output='test.png')

        # Call the main function
        main()

        # Verify the function behaves as expected
        mock_args.assert_called_once()
        mock_heatmap.assert_called_once_with('test.png')

if __name__ == '__main__':
    unittest.main()