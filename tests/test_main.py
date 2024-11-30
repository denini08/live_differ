"""
Tests for the __main__ module.
"""
import os
import sys
from unittest.mock import patch

def test_main_entry_point():
    with patch('live_differ.cli.cli') as mock_cli:
        # We need to import __main__ after mocking to ensure the mock is in place
        import live_differ.__main__
        
        # Since __name__ != "__main__" in the test environment,
        # cli() won't be called automatically, so we verify the import worked
        assert hasattr(live_differ.__main__, 'cli')

def test_main_execution():
    with patch('live_differ.cli.cli') as mock_cli:
        # Add the parent directory to sys.path so relative imports work
        parent_dir = os.path.dirname(os.path.dirname(__file__))
        sys.path.insert(0, parent_dir)
        
        # Execute the module as script
        main_file = os.path.join(parent_dir, 'live_differ', '__main__.py')
        namespace = {
            '__name__': '__main__',
            '__file__': main_file,
            '__package__': 'live_differ'
        }
        with open(main_file) as f:
            code = compile(f.read(), main_file, 'exec')
            exec(code, namespace)
        
        # Clean up sys.path
        sys.path.pop(0)
        
        # Verify cli was called
        mock_cli.assert_called_once()
