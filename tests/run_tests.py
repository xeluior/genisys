import unittest
import sys

def run_tests():
    """Recursively discover and run tests named as test_*.py"""
    loader = unittest.TestLoader()
    tests = loader.discover(".", pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(tests)
# end run_tests

if __name__ == "__main__":
    sys.exit(0 if run_tests().wasSuccessful() else 1)
