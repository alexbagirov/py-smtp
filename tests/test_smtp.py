import os
import sys
import unittest
from unittest.mock import patch, Mock

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))

import smtp


class TestSockets(unittest.TestCase):
    @patch('smtp.socket.socket.connect')
    def test_raises_exception_for_invalid_server(self, patched_connect):
        patched_connect.side_effect = OSError
        with self.assertRaises(smtp.SMTPException):
            smtp.SMTP().connect('a', 888)

    @patch('smtp.socket.socket.connect')
    def test_connects_to_server(self, patched_connect):
        smtp.SMTP().connect('smtp.gmail.com', 587)
        patched_connect.assert_called_with(('smtp.gmail.com', 587))

    @patch('smtp.socket.socket.sendall')
    def test_sending_data(self, patched_sendall):
        s = smtp.SMTP()

        patched_sendall.return_value = True
        s.send('ehlo')
        patched_sendall.assert_called_with(b'ehlo\r\n')

        s.encrypted = True
        s.enc_sock = Mock(smtp.socket.socket)
        s.send('ehlo')
        patched_sendall.assert_called_with(b'ehlo\r\n')

    @patch('smtp.socket.socket.recv')
    def test_receive_data(self, patched_recv):
        patched_recv.return_value = b'hi\r\n'
        self.assertEqual(smtp.SMTP().receive(), b'hi\r\n')

    @patch('smtp.socket.socket.recv')
    def test_socket_timeout(self, patched_recv):
        patched_recv.side_effect = smtp.socket.timeout
        with self.assertRaises(smtp.SMTPException):
            smtp.SMTP().receive()


if __name__ == '__main__':
    unittest.main()
