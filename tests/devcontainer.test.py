import unittest
import subprocess

class TestDevContainer(unittest.TestCase):
    def test_container_build(self):
        result = subprocess.run(['docker', 'build', '-f', '.devcontainer/devcontainer.json', '.'], capture_output=True)
        self.assertEqual(result.returncode, 0)

    def test_tools_installed(self):
        result = subprocess.run(['docker', 'run', '--rm', 'your_image_name', 'which', 'your_tool'], capture_output=True)
        self.assertNotEqual(result.stdout, b'')

    def test_extensions_installed(self):
        result = subprocess.run(['docker', 'run', '--rm', 'your_image_name', 'code', '--list-extensions'], capture_output=True)
        self.assertIn(b'your_extension', result.stdout)

if __name__ == '__main__':
    unittest.main()