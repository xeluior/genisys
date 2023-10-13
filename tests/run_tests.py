import unittest

def run_tests():
    loader = unittest.TestLoader()
    tests = loader.discover(".", pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(tests)
# end run_tests

if __name__ == "__main__":
    exit(0 if run_tests().wasSuccessful() else 1)
