import os
import sys
import unittest
from unittest.mock import patch

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))

import smtp


class TestSMTP(unittest.TestCase):
    def setUp(self) -> None:
        self.smtp = smtp.SMTP()

    @patch('smtp.socket')
    def test_exception_when_wrong_server(self, patched_socket):
        patched_socket.connect.side_effect = OSError
        with self.assertRaises(smtp.SMTPException):
            self.smtp.connect('a', 555)
        patched_socket.connect.assert_called()


if __name__ == '__main__':
    unittest.main()
