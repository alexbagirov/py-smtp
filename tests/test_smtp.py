import os
import sys
import unittest
from unittest.mock import patch, Mock, call

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
        patched_recv.side_effect = [b'hi', b' how', b' are', b' you?\r\n']
        self.assertEqual(smtp.SMTP().receive(), b'hi how are you?\r\n')

    @patch('smtp.socket.socket.recv')
    def test_socket_timeout(self, patched_recv):
        patched_recv.side_effect = smtp.socket.timeout
        with self.assertRaises(smtp.SMTPException):
            smtp.SMTP().receive()

    @patch('smtp.socket.socket.recv')
    def test_error_code_raises_exception(self, patched_recv):
        patched_recv.return_value = b'230-hi\r\n'
        with self.assertRaises(smtp.SMTPException):
            smtp.SMTP().check_code(b'220')

    @patch('smtp.socket.socket.sendall')
    @patch('smtp.socket.socket.close')
    def test_disconnect(self, patched_close, patched_sendall):
        smtp.SMTP().disconnect()
        patched_close.assert_called()
        patched_sendall.assert_called_with(b'quit\r\n')

    @patch('smtp.socket.socket.recv')
    @patch('smtp.socket.socket.sendall')
    def test_start_tls(self, patched_sendall, patched_recv):
        patched_recv.side_effect = [b'250-go ahead\r\n',
                                    b'250 go ahead\r\n',
                                    b'220 go ahead\r\n']
        smtp.SMTP().start_tls()
        patched_sendall.assert_called_with(b'starttls\r\n')

    @patch('smtp.socket.socket.recv')
    @patch('smtp.socket.socket.sendall')
    def test_start_tls_error(self, _, patched_recv):
        with self.assertRaises(smtp.SMTPException):
            patched_recv.side_effect = [b'334-tls is not allowed!\r\n']
            smtp.SMTP().start_tls()
        with self.assertRaises(smtp.SMTPException):
            patched_recv.side_effect = [b'250-go ahead\r\n',
                                        b'250 go ahead\r\n',
                                        b'334-error!\r\n']
            smtp.SMTP().start_tls()

    @patch('smtp.ssl.wrap_socket')
    def test_wrap_socket(self, patched_wrap):
        s = smtp.SMTP()
        s.sock = Mock(smtp.socket.socket)
        patched_wrap.return_value = Mock(smtp.socket.socket)
        s.wrap_socket()
        self.assertIsInstance(s.enc_sock, smtp.socket.socket)
        self.assertEqual(s.encrypted, True)

    @patch('smtp.SMTP.start_tls')
    @patch('smtp.SMTP.wrap_socket')
    def test_encrypt(self, patched_wrap, patched_starttls):
        smtp.SMTP().encrypt()
        patched_wrap.assert_called_once()
        patched_starttls.assert_called_once()

    @patch('smtp.socket.socket.sendall')
    @patch('smtp.socket.socket.recv')
    def test_auth(self, patched_recv, patched_sendall):
        patched_recv.side_effect = [b'334-ok\r\n',
                                    b'334-ok\r\n',
                                    b'235-ok\r\n']
        smtp.SMTP().authorize('login', 'password')
        calls = [call(b'auth login\r\n'),
                 call(b'bG9naW4=\r\n'),
                 call(b'cGFzc3dvcmQ=\r\n')]
        patched_sendall.assert_has_calls(calls)

    @patch('smtp.socket.socket.sendall')
    @patch('smtp.socket.socket.recv')
    def test_mail_from(self, patched_recv, patched_send):
        s = smtp.SMTP()
        s.sock = Mock(smtp.socket.socket)
        patched_recv.return_value = b'250-ok\r\n'
        smtp.SMTP().mail_from('someone@gmail.com')
        patched_send.assert_called_with(b'mail from: <someone@gmail.com>\r\n')

    @patch('smtp.socket.socket.sendall')
    @patch('smtp.socket.socket.recv')
    def test_mail_from_error(self, patched_recv, patched_send):
        s = smtp.SMTP()
        s.sock = Mock(smtp.socket.socket)
        patched_recv.return_value = b'334-bad sender\r\n'
        with self.assertRaises(smtp.SMTPException):
            smtp.SMTP().mail_from('someone@gmail.com')
            patched_send.assert_called_with(b'mail from: '
                                            b'<someone@gmail.com>\r\n')

    @patch('smtp.socket.socket.sendall')
    @patch('smtp.socket.socket.recv')
    def test_mail_to(self, patched_recv, patched_send):
        s = smtp.SMTP()
        s.sock = Mock(smtp.socket.socket)
        patched_recv.return_value = b'250-ok\r\n'
        smtp.SMTP().mail_to('someone@gmail.com')
        patched_send.assert_called_with(b'rcpt to: <someone@gmail.com>\r\n')

    @patch('smtp.socket.socket.sendall')
    @patch('smtp.socket.socket.recv')
    def test_mail_to_error(self, patched_recv, patched_send):
        s = smtp.SMTP()
        s.sock = Mock(smtp.socket.socket)
        patched_recv.return_value = b'334-bad sender\r\n'
        with self.assertRaises(smtp.SMTPException):
            smtp.SMTP().mail_to('someone@gmail.com')
            patched_send.assert_called_with(b'rcpt to: '
                                            b'<someone@gmail.com>\r\n')


if __name__ == '__main__':
    unittest.main()
