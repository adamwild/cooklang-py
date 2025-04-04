import unittest
from pathlib import Path

import yaml
from cooklang import parse

CANONICAL_TESTS_FILE = Path(__file__).parent / "canonical.yaml"


class TestCanonical(unittest.TestCase):
    def test_canonical(self) -> None:
        canonicals = yaml.safe_load(CANONICAL_TESTS_FILE.read_text())

        tests = canonicals['tests']
        test_names = tests.keys()

        reached = False

        for test_name in test_names:
            reached = reached or test_name=="testIngredientNoUnitsNotOnlyString"
            if reached:
                print(test_name)
                print()
                print(tests[test_name])
                print()
                print(tests[test_name]['source'])
                print(tests[test_name]['result'])
                print("-"*50)

        """
        testIngredientNoUnitsNotOnlyString
        for name, test in tests["tests"].items():
            print(tests.keys()[0])
            break"""

if __name__ == '__main__':
    tcano = TestCanonical()
    tcano.test_canonical()