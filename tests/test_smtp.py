import os
import sys
import unittest
from unittest.mock import patch

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))

import smtp


class TestSockets(unittest.TestCase):
    def setUp(self):
        self.smtp = smtp.SMTP()

    @patch('smtp.socket.socket.connect')
    def test_raises_exception_for_invalid_server(self, patched_connect):
        patched_connect.side_effect = OSError
        with self.assertRaises(smtp.SMTPException):
            self.smtp.connect('a', 888)

    @patch('smtp.socket.socket.connect')
    def test_connects_to_server(self, patched_connect):
        self.smtp.connect('smtp.gmail.com', 587)
        patched_connect.assert_called_with(('smtp.gmail.com', 587))


if __name__ == '__main__':
    unittest.main()
