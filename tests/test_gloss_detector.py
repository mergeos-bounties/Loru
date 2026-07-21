import os
import json
import tempfile
import unittest
from src.gloss_detector import GlossFrameDetector

class TestGlossFrameDetector(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.detector = GlossFrameDetector(similarity_threshold=0.9)

    def tearDown(self):
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

    def create_test_file(self, name: str, frames: list):
        path = os.path.join(self.temp_dir, f"{name}.json")
        with open(path, 'w') as f:
            json.dump({"frames": frames}, f)
        return path

    def test_detect_clones(self):
        # Create test files with similar frame sequences
        original_frames = [
            {"landmarks": [1, 2, 3], "gloss": "hello"},
            {"landmarks": [4, 5, 6], "gloss": "world"}
        ]

        # Create clone with slight modifications
        clone_frames = [
            {"landmarks": [1, 2, 3], "gloss": "hello"},
            {"landmarks": [4, 5, 6], "gloss": "world"}
        ]

        self.create_test_file("original", original_frames)
        self.create_test_file("clone", clone_frames)

        clones = self.detector.detect_clones(self.temp_dir)

        # Verify the clone was detected
        self.assertIn(os.path.join(self.temp_dir, "clone.json"), clones)
        self.assertEqual(len(clones[os.path.join(self.temp_dir, "clone.json")]), 1)
        self.assertEqual(clones[os.path.join(self.temp_dir, "clone.json")][0][0],
                        os.path.join(self.temp_dir, "original.json"))

    def test_no_clones(self):
        # Create test files with completely different frame sequences
        file1_frames = [
            {"landmarks": [1, 2, 3], "gloss": "hello"},
            {"landmarks": [4, 5, 6], "gloss": "world"}
        ]

        file2_frames = [
            {"landmarks": [7, 8, 9], "gloss": "different"},
            {"landmarks": [10, 11, 12], "gloss": "sequence"}
        ]

        self.create_test_file("file1", file1_frames)
        self.create_test_file("file2", file2_frames)

        clones = self.detector.detect_clones(self.temp_dir)

        # Verify no clones were detected
        self.assertEqual(len(clones), 0)

if __name__ == '__main__':
    unittest.main()