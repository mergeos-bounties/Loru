import unittest
from unittest.mock import patch
from src.gloss_coverage import generate_gloss_coverage_heatmap

class TestGlossCoverage(unittest.TestCase):
    @patch('src.gloss_coverage.get_default_glosses')
    @patch('src.gloss_coverage.get_sample_coverage')
    @patch('matplotlib.pyplot.show')
    def test_generate_gloss_coverage_heatmap(self, mock_show, mock_coverage, mock_glosses):
        # Setup mock data
        mock_glosses.return_value = ['hello', 'world', 'test']
        mock_coverage.return_value = {'hello': 5, 'world': 0, 'test': 3}

        # Call the function
        generate_gloss_coverage_heatmap()

        # Verify the function behaves as expected
        mock_glosses.assert_called_once()
        mock_coverage.assert_called_once_with(['hello', 'world', 'test'])
        mock_show.assert_called_once()

    @patch('src.gloss_coverage.get_default_glosses')
    @patch('src.gloss_coverage.get_sample_coverage')
    @patch('matplotlib.pyplot.savefig')
    def test_generate_gloss_coverage_heatmap_with_output(self, mock_save, mock_coverage, mock_glosses):
        # Setup mock data
        mock_glosses.return_value = ['hello', 'world', 'test']
        mock_coverage.return_value = {'hello': 5, 'world': 0, 'test': 3}

        # Call the function with output path
        output_path = 'test_heatmap.png'
        generate_gloss_coverage_heatmap(output_path)

        # Verify the function behaves as expected
        mock_glosses.assert_called_once()
        mock_coverage.assert_called_once_with(['hello', 'world', 'test'])
        mock_save.assert_called_once_with(output_path)

if __name__ == '__main__':
    unittest.main()