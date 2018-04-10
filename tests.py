import unittest
from main import Parser


class TestParser(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = Parser()

    def test_something(self):
        self.assertEqual(5, 5)


if __name__ == '__main__':
    unittest.main()
